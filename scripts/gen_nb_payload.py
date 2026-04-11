"""
Generate a self-contained Fabric notebook payload (nb_payload.json).
Called by the promote-with-schema-validation workflow.

The generated notebook reads data from Dev OneLake (abfss) and writes
incrementally to the target workspace — only new/changed rows and schema
changes (new columns) are applied. Existing data is NOT overwritten.

Env vars (all optional):
  SCHEMA_FILE          Path to schema_discovery.json
  LAKEHOUSE_ID         Target lakehouse GUID
  WORKSPACE_ID         Target workspace GUID
  SOURCE_WORKSPACE_ID  Dev workspace GUID  (source for data reads)
  SOURCE_LAKEHOUSE_ID  Dev lakehouse GUID  (source for data reads)
  OUT_PATH             Output file path (default: /tmp/nb_payload.json)
"""
import json
import base64
import os

SCHEMA_FILE         = os.environ.get("SCHEMA_FILE", "")
LAKEHOUSE_ID        = os.environ.get("LAKEHOUSE_ID", "")
WORKSPACE_ID        = os.environ.get("WORKSPACE_ID", "")
SOURCE_WORKSPACE_ID = os.environ.get("SOURCE_WORKSPACE_ID", "")
SOURCE_LAKEHOUSE_ID = os.environ.get("SOURCE_LAKEHOUSE_ID", "")
LAKEHOUSE_INDEX     = int(os.environ.get("LAKEHOUSE_INDEX", "0"))
NOTEBOOK_DISPLAY_NAME = os.environ.get("NOTEBOOK_DISPLAY_NAME", "00_sync_to_uat")
OUT_PATH            = os.environ.get("OUT_PATH", "/tmp/nb_payload.json")

# ── Load schema / table list ───────────────────────────────────────────────────
# SCHEMA_TABLES: {schema_name: [table_name, ...]}  e.g. {"dbo": ["t1"], "year_2017": ["t2"]}
SCHEMA_TABLES = {}
SCHEMAS_ENABLED = False

if SCHEMA_FILE and os.path.isfile(SCHEMA_FILE):
    disc = json.load(open(SCHEMA_FILE))
    SCHEMA_VERSION = f"live-{disc.get('workspace_id','')[:8]}"

    # New multi-lakehouse format
    if "lakehouses" in disc:
        lh_list = disc["lakehouses"]
        if LAKEHOUSE_INDEX < len(lh_list):
            lh_info = lh_list[LAKEHOUSE_INDEX]
        else:
            print(f"WARNING: LAKEHOUSE_INDEX {LAKEHOUSE_INDEX} out of range ({len(lh_list)} lakehouses)")
            lh_info = lh_list[0] if lh_list else {}

        SCHEMAS_ENABLED = lh_info.get("schemas_enabled", False)
        for schema_name, schema_data in lh_info.get("schemas", {}).items():
            tables = list(schema_data.get("tables", {}).keys())
            if tables:
                SCHEMA_TABLES[schema_name] = tables

        if not SOURCE_LAKEHOUSE_ID:
            SOURCE_LAKEHOUSE_ID = lh_info.get("lakehouse_id", "")
        if not SOURCE_WORKSPACE_ID:
            SOURCE_WORKSPACE_ID = disc.get("workspace_id", "")

        total_tables = sum(len(v) for v in SCHEMA_TABLES.values())
        print(f"Schema source   : {SCHEMA_FILE} (lakehouse #{LAKEHOUSE_INDEX}: {lh_info.get('lakehouse_name', '?')})")
        print(f"  Schemas       : {list(SCHEMA_TABLES.keys())}")
        print(f"  Total tables  : {total_tables}")

    # Legacy single-lakehouse format
    else:
        TABLES = list(disc.get("tables", {}).keys())
        SCHEMAS_ENABLED = disc.get("schemas_enabled", False)
        DEFAULT_SCHEMA = disc.get("default_schema", "dbo")
        if not DEFAULT_SCHEMA or DEFAULT_SCHEMA == "Files":
            DEFAULT_SCHEMA = "dbo"
        SCHEMA_TABLES = {DEFAULT_SCHEMA: TABLES} if SCHEMAS_ENABLED else {"": TABLES}
        if not SOURCE_LAKEHOUSE_ID:
            SOURCE_LAKEHOUSE_ID = disc.get("lakehouse_id", "")
        if not SOURCE_WORKSPACE_ID:
            SOURCE_WORKSPACE_ID = disc.get("workspace_id", "")
        print(f"Schema source   : {SCHEMA_FILE} (legacy format, {len(TABLES)} tables)")
else:
    repo_root = os.path.join(os.path.dirname(__file__), "..")
    registry_path = os.path.join(repo_root, "notebooks", "00_schema_registry.py")
    ns = {}
    exec(open(registry_path).read(), ns)
    SCHEMA_VERSION = ns["SCHEMA_VERSION"]
    TABLES = list(ns["SCHEMAS"].keys())
    SCHEMAS_ENABLED = False
    SCHEMA_TABLES = {"": TABLES}
    print(f"Schema source   : 00_schema_registry.py (static fallback, {len(TABLES)} tables)")

print(f"Source workspace: {SOURCE_WORKSPACE_ID}")
print(f"Source lakehouse: {SOURCE_LAKEHOUSE_ID}")
print(f"Target workspace: {WORKSPACE_ID}")
print(f"Target lakehouse: {LAKEHOUSE_ID}")
print(f"Notebook name   : {NOTEBOOK_DISPLAY_NAME}")

# ── Build PySpark notebook code ────────────────────────────────────────────────
has_source = bool(SOURCE_WORKSPACE_ID and SOURCE_LAKEHOUSE_ID)

if has_source:
    ci_schema_tables_repr = repr(SCHEMA_TABLES)
    schemas_enabled_repr = repr(SCHEMAS_ENABLED)
    inner_code = (
        "# Auto-generated -- Digital Realty Resilient Data Sync\n"
        "# Reads from Dev OneLake -> writes to this workspace lakehouse\n"
        f"# Schema version: {SCHEMA_VERSION}\n"
        "import time as _time\n"
        "import traceback as _tb\n"
        "import re as _re\n"
        "import json as _json\n\n"
        f'DEV_WS_ID = "{SOURCE_WORKSPACE_ID}"\n'
        f'DEV_LH_ID = "{SOURCE_LAKEHOUSE_ID}"\n'
        f"CI_SCHEMA_TABLES = {ci_schema_tables_repr}  # from CI discovery\n"
        f"SCHEMAS_ENABLED = {schemas_enabled_repr}\n\n"

        # ── Spark config for large tables ──
        "# ── Spark config for large tables ──\n"
        "try:\n"
        "    spark.conf.set('spark.sql.adaptive.enabled', 'true')\n"
        "    spark.conf.set('spark.sql.adaptive.coalescePartitions.enabled', 'true')\n"
        "    spark.conf.set('spark.sql.files.maxRecordsPerFile', '500000')\n"
        "    print('Spark AQE + large table config: enabled')\n"
        "except Exception as _ce:\n"
        "    print(f'Spark config warning (non-fatal): {_ce}')\n\n"

        # ── Size thresholds ──
        "SMALL_THRESHOLD  = 100 * 1024 * 1024   # 100 MB\n"
        "LARGE_THRESHOLD  = 1024 * 1024 * 1024   # 1 GB\n"
        "TABLE_TIMEOUT    = 20 * 60              # 20 min per table\n"
        "_CLONE_PATTERN   = _re.compile(r'_clone_\\d{6,}')\n\n"

        # ── Helpers ──
        "def _fmt_bytes(n):\n"
        "    for unit in ['B','KB','MB','GB']:\n"
        "        if abs(n) < 1024: return f'{n:.1f} {unit}'\n"
        "        n /= 1024\n"
        "    return f'{n:.1f} TB'\n\n"

        "def _estimate_size(path):\n"
        "    '''Estimate table size via DESCRIBE DETAIL (O(1), no data scan).'''\n"
        "    try:\n"
        "        detail = spark.sql(f'DESCRIBE DETAIL delta.`{path}`').collect()[0]\n"
        "        return detail['sizeInBytes'] or 0, detail['numFiles'] or 0\n"
        "    except Exception:\n"
        "        try:\n"
        "            entries = mssparkutils.fs.ls(f'{path}/_delta_log')\n"
        "            return -1, len(entries)\n"
        "        except Exception:\n"
        "            return -1, -1\n\n"

        "def _print_schema(label, df, max_cols=50):\n"
        "    cols = df.dtypes\n"
        "    if len(cols) > max_cols:\n"
        "        print(f'  {label} schema: {len(cols)} columns (too many to print)')\n"
        "        return\n"
        "    print(f'  {label} schema ({len(cols)} columns):')\n"
        "    for cn, ct in cols:\n"
        "        print(f'    | {cn:30s} | {ct:15s} |')\n\n"

        "def _print_sample(label, df, n=3, max_size=SMALL_THRESHOLD):\n"
        "    '''Print sample rows only for small tables.'''\n"
        "    try:\n"
        "        rows = df.limit(n).collect()\n"
        "        if rows:\n"
        "            print(f'  {label} sample ({n} rows):')\n"
        "            for r in rows:\n"
        "                vals = ', '.join(f'{k}={v!r}' for k, v in list(r.asDict().items())[:10])\n"
        "                print(f'    {vals}')\n"
        "        else:\n"
        "            print(f'  {label}: (empty)')\n"
        "    except Exception as se:\n"
        "        print(f'  {label} sample: skipped ({se})')\n\n"

        # ── Status tracking ──
        "_sync_status = {'status': 'started', 'tables_synced': [], 'tables_failed': [],\n"
        "    'tables_skipped': [], 'errors': [], 'timestamp': _time.strftime('%Y-%m-%dT%H:%M:%SZ', _time.gmtime())}\n\n"

        "def _write_status():\n"
        "    '''Write sync status to OneLake for external diagnostics.'''\n"
        "    try:\n"
        "        _sync_status['timestamp'] = _time.strftime('%Y-%m-%dT%H:%M:%SZ', _time.gmtime())\n"
        "        status_json = _json.dumps(_sync_status, indent=2)\n"
        "        mssparkutils.fs.put('Files/___sync_status.json', status_json, True)\n"
        "        print(f'  Status marker written: Files/___sync_status.json')\n"
        "    except Exception as we:\n"
        "        print(f'  Status marker write failed (non-fatal): {we}')\n\n"

        # ── Environment diagnostics ──
        '_t0 = _time.time()\n'
        'print("=" * 72)\n'
        'print("DIGITAL REALTY RESILIENT DATA SYNC")\n'
        'print("=" * 72)\n'
        'print(f"Timestamp        : {_time.strftime(\'%Y-%m-%d %H:%M:%S UTC\', _time.gmtime())}")\n'
        'print(f"Source workspace : {DEV_WS_ID}")\n'
        'print(f"Source lakehouse : {DEV_LH_ID}")\n'
        'print(f"Schemas enabled  : {SCHEMAS_ENABLED}")\n'
        'print(f"CI schemas/tables: {len(CI_SCHEMA_TABLES)} schema(s) -> {CI_SCHEMA_TABLES}")\n'
        'print(f"Size thresholds  : small<{_fmt_bytes(SMALL_THRESHOLD)}, large>{_fmt_bytes(LARGE_THRESHOLD)}")\n'
        'try:\n'
        '    print(f"Spark version    : {spark.version}")\n'
        'except Exception:\n'
        '    print("Spark version    : (unavailable)")\n'
        'try:\n'
        '    print(f"mssparkutils     : available ({type(mssparkutils).__name__})")\n'
        'except NameError:\n'
        '    print("mssparkutils     : NOT available")\n'
        'print("")\n\n'

        # ── Runtime discovery ──
        'dev_base_path = f"abfss://{DEV_WS_ID}@onelake.dfs.fabric.microsoft.com/{DEV_LH_ID}/Tables"\n'
        'print(f"OneLake base path: {dev_base_path}")\n\n'
        "_SKIP_DIRS = {'_delta_log', '_schemas', '_temporary', '__checkpoint', 'Files', 'TableMaintenance', 'Tables'}\n\n"

        "def _try_list(path):\n"
        "    try:\n"
        '        print(f"  -> Listing: {path}")\n'
        "        entries = mssparkutils.fs.ls(path)\n"
        "        all_dirs = [e.name.rstrip('/') for e in entries if e.isDir]\n"
        "        filtered = [d for d in all_dirs if d not in _SKIP_DIRS and not d.startswith('_')]\n"
        "        # Filter clone tables dynamically\n"
        "        clean = [d for d in filtered if not _CLONE_PATTERN.search(d)]\n"
        "        clones = set(filtered) - set(clean)\n"
        "        if clones:\n"
        '            print(f"     Filtered {len(clones)} clone(s): {clones}")\n'
        '        print(f"     Found: {clean}  (raw={len(all_dirs)}, filtered={len(clean)})")\n'
        "        return clean\n"
        "    except Exception as ex:\n"
        '        print(f"     FAILED: {ex}")\n'
        "        return []\n\n"

        "SCHEMA_TABLES = {}\n\n"

        # Strategy 1: CI-known schemas
        'print("\\n--- Discovery Strategy 1: CI-known schemas ---")\n'
        "for ci_schema in sorted(CI_SCHEMA_TABLES.keys()):\n"
        "    if ci_schema:\n"
        '        found = _try_list(f"{dev_base_path}/{ci_schema}")\n'
        "        if found:\n"
        "            SCHEMA_TABLES[ci_schema] = found\n"
        '            print(f"  [FOUND] {len(found)} tables via Tables/{ci_schema}/")\n'
        "    else:\n"
        "        found = _try_list(dev_base_path)\n"
        "        if found:\n"
        '            SCHEMA_TABLES[""] = found\n'
        '            print(f"  [FOUND] {len(found)} tables in Tables/ (no schema)")\n\n'

        # Strategy 2: dbo
        "if 'dbo' not in SCHEMA_TABLES:\n"
        '    print("\\n--- Discovery Strategy 2: dbo schema ---")\n'
        '    found = _try_list(f"{dev_base_path}/dbo")\n'
        "    if found:\n"
        "        SCHEMA_TABLES['dbo'] = found\n\n"

        # Strategy 3: enumerate ALL
        "if not SCHEMA_TABLES:\n"
        '    print("\\n--- Discovery Strategy 3: enumerate ALL schema folders ---")\n'
        "    try:\n"
        "        schema_entries = mssparkutils.fs.ls(dev_base_path)\n"
        "        schema_dirs = [e.name.rstrip('/') for e in schema_entries if e.isDir]\n"
        '        print(f"  Schema dirs: {schema_dirs}")\n'
        "        for sd in schema_dirs:\n"
        "            if sd in _SKIP_DIRS or sd.startswith('_'): continue\n"
        '            found = _try_list(f"{dev_base_path}/{sd}")\n'
        "            if found: SCHEMA_TABLES[sd] = found\n"
        "    except Exception as ex:\n"
        '        print(f"  Strategy 3 failed: {ex}")\n\n'

        # Strategy 4: flat Tables/
        "if not SCHEMA_TABLES:\n"
        '    print("\\n--- Discovery Strategy 4: direct Tables/ ---")\n'
        "    found = _try_list(dev_base_path)\n"
        '    if found: SCHEMA_TABLES[""] = found\n\n'

        # Strategy 5: CI fallback
        "if not SCHEMA_TABLES and CI_SCHEMA_TABLES:\n"
        '    print("\\n--- Discovery Strategy 5: CI fallback ---")\n'
        "    SCHEMA_TABLES = dict(CI_SCHEMA_TABLES)\n\n"

        "total_table_count = sum(len(v) for v in SCHEMA_TABLES.values())\n"
        "if total_table_count == 0:\n"
        '    print("\\n" + "!" * 72)\n'
        '    print("NO TABLES FOUND -- nothing to sync.")\n'
        '    print("!" * 72)\n'
        '    print("RESULT: 0 tables synced")\n'
        "    _sync_status['status'] = 'no_tables'\n"
        "    _write_status()\n\n"

        # ── Pre-create schemas ──
        "if total_table_count > 0:\n"
        "    # Dynamically create ALL non-default schemas discovered at runtime\n"
        "    _all_schemas = sorted(set(s for s in SCHEMA_TABLES.keys() if s and s != 'dbo'))\n"
        "    if _all_schemas:\n"
        '        print(f"\\n--- Pre-creating {len(_all_schemas)} non-default schema(s) ---")\n'
        "        for _sn in _all_schemas:\n"
        "            try:\n"
        "                spark.sql(f'CREATE SCHEMA IF NOT EXISTS `{_sn}`')\n"
        '                print(f"  Schema `{_sn}`: OK")\n'
        "            except Exception as _se:\n"
        '                print(f"  Schema `{_sn}`: WARNING - {_se}")\n'
        '                _sync_status["errors"].append(f"Schema {_sn}: {_se}")\n'
        "    # Verify all schemas\n"
        "    try:\n"
        "        _existing = [r[0] for r in spark.sql('SHOW SCHEMAS').collect()]\n"
        '        print(f"  Schemas in lakehouse: {_existing}")\n'
        "        for _sn in _all_schemas:\n"
        "            if _sn not in _existing:\n"
        '                print(f"  WARNING: Schema `{_sn}` still missing after CREATE!")\n'
        "    except Exception as _ve:\n"
        '        print(f"  SHOW SCHEMAS failed: {_ve}")\n'
        '    print("")\n\n'

        # ── Build sync pairs ──
        "    _sync_pairs = []\n"
        "    for _sn, _tl in sorted(SCHEMA_TABLES.items()):\n"
        "        for _t in _tl:\n"
        "            _sync_pairs.append((_sn, _t))\n\n"
        '    print("=" * 72)\n'
        '    print(f"STARTING SYNC: {total_table_count} tables across {len(SCHEMA_TABLES)} schema(s)")\n'
        "    for _sn, _tl in sorted(SCHEMA_TABLES.items()):\n"
        '        print(f"  Schema {_sn!r}: {_tl}")\n'
        '    print("=" * 72)\n\n'

        "    synced, failed, skipped_empty, skipped_timeout = [], [], [], []\n"
        "    total_rows_copied = 0\n"
        "    total_cols_added = 0\n\n"

        # ── Main sync loop ──
        "    for idx, (schema_name, table) in enumerate(_sync_pairs, 1):\n"
        "        tbl_prefix = f'{schema_name}.' if schema_name else ''\n"
        "        source_path = f'{dev_base_path}/{schema_name}' if schema_name else dev_base_path\n"
        '        t_start = _time.time()\n'
        '        print("")\n'
        '        print("-" * 72)\n'
        '        print(f"[{idx}/{total_table_count}] TABLE: {tbl_prefix}{table}")\n'
        '        print("-" * 72)\n'
        "        try:\n"
        '            src = f"{source_path}/{table}"\n'
        '            full_name = f"{tbl_prefix}{table}"\n\n'

        # Size detection (O(1))
        '            print(f"  Reading source: {src}")\n'
        "            size_bytes, num_files = _estimate_size(src)\n"
        "            size_tier = 'LARGE' if size_bytes > LARGE_THRESHOLD else ('MEDIUM' if size_bytes > SMALL_THRESHOLD else 'SMALL')\n"
        "            if size_bytes >= 0:\n"
        '                print(f"  Size: {_fmt_bytes(size_bytes)} ({num_files} files) -> {size_tier}")\n'
        "            else:\n"
        '                print(f"  Size: unknown ({num_files} log entries) -> treating as SMALL")\n'
        "                size_tier = 'SMALL'\n\n"

        "            src_df = spark.read.format('delta').load(src)\n"
        "            src_cols = set(src_df.columns)\n"
        '            print(f"  Source columns: {len(src_cols)}")\n\n'

        # Count: only for small tables
        "            if size_tier == 'SMALL':\n"
        "                src_count = src_df.count()\n"
        '                print(f"  Source rows: {src_count:,}")\n'
        "                _print_schema('SRC', src_df)\n"
        "                _print_sample('SRC', src_df)\n"
        "            else:\n"
        '                src_count = -1  # skip expensive count for large tables\n'
        '                print(f"  Source rows: (skipped count for {size_tier} table)")\n'
        "                _print_schema('SRC', src_df)\n\n"

        # Check target
        '            print(f"  Checking target: {full_name}")\n'
        "            table_exists = False\n"
        "            try:\n"
        "                tgt_df = spark.read.table(full_name)\n"
        "                table_exists = True\n"
        "                if size_tier == 'SMALL':\n"
        "                    tgt_count = tgt_df.count()\n"
        '                    print(f"  Target EXISTS: {tgt_count} rows, {len(tgt_df.columns)} columns")\n'
        "                else:\n"
        "                    tgt_count = -1\n"
        '                    print(f"  Target EXISTS: {len(tgt_df.columns)} columns (skipped count for {size_tier})")\n'
        "            except Exception:\n"
        "                tgt_count = 0\n"
        '                print(f"  Target MISSING -- will create")\n\n'

        # ── TIERED SYNC LOGIC ──
        "            # ── LARGE/MEDIUM: direct overwrite (safest, fastest for big data) ──\n"
        "            if size_tier in ('LARGE', 'MEDIUM'):\n"
        '                print(f"  ACTION: {size_tier} table -> overwrite mode (no diff)")\n'
        "                write_builder = src_df.write.format('delta').mode('overwrite').option('overwriteSchema', 'true')\n"
        "                if size_tier == 'LARGE' and num_files > 4:\n"
        "                    partitions = max(4, num_files // 4)\n"
        '                    print(f"  Coalescing to {partitions} partitions for large write")\n'
        "                    write_builder = src_df.coalesce(partitions).write.format('delta').mode('overwrite').option('overwriteSchema', 'true')\n"
        "                write_builder.saveAsTable(full_name)\n"
        '                elapsed = _time.time() - t_start\n'
        '                print(f"  DONE: OVERWRITE {full_name} [{elapsed:.1f}s]")\n'
        "                synced.append((full_name, -1, f'overwrite-{size_tier.lower()}'))\n"
        "                continue\n\n"

        # ── SMALL: original incremental logic ──
        "            if not table_exists:\n"
        "                if src_count == 0:\n"
        '                    print(f"  SKIP: source empty")\n'
        "                    skipped_empty.append(full_name)\n"
        "                    continue\n"
        '                print(f"  ACTION: Creating {full_name} with {src_count} rows...")\n'
        "                src_df.write.format('delta').mode('overwrite').saveAsTable(full_name)\n"
        "                total_rows_copied += src_count\n"
        '                elapsed = _time.time() - t_start\n'
        '                print(f"  DONE: NEW {full_name} -> {src_count} rows [{elapsed:.1f}s]")\n'
        "                synced.append((full_name, src_count, 'created'))\n"
        "                continue\n\n"

        "            # Schema diff\n"
        "            tgt_cols = set(tgt_df.columns)\n"
        "            new_cols = src_cols - tgt_cols\n"
        "            if new_cols:\n"
        '                print(f"  Adding {len(new_cols)} new column(s): {new_cols}")\n'
        "                for cn in sorted(new_cols):\n"
        "                    ct = str(dict(src_df.dtypes).get(cn, 'string'))\n"
        '                    spark.sql(f"ALTER TABLE {full_name} ADD COLUMN `{cn}` {ct}")\n'
        "                total_cols_added += len(new_cols)\n"
        "                tgt_df = spark.read.table(full_name)\n"
        "                tgt_count = tgt_df.count()\n\n"

        "            if src_count == 0:\n"
        '                print(f"  SKIP: source empty")\n'
        "                skipped_empty.append(full_name)\n"
        "                continue\n\n"

        "            if tgt_count == 0:\n"
        '                print(f"  ACTION: Target empty, inserting all {src_count} rows...")\n'
        "                src_df.write.format('delta').mode('append').option('mergeSchema','true').saveAsTable(full_name)\n"
        "                total_rows_copied += src_count\n"
        '                elapsed = _time.time() - t_start\n'
        '                print(f"  DONE: FILL {full_name} -> {src_count} rows [{elapsed:.1f}s]")\n'
        "                synced.append((full_name, src_count, 'filled'))\n"
        "                continue\n\n"

        "            # Incremental diff (small tables only)\n"
        "            common_cols = sorted(list(src_cols & tgt_cols))\n"
        '            print(f"  Incremental diff on {len(common_cols)} common columns...")\n'
        "            new_rows = src_df.select(common_cols).subtract(tgt_df.select(common_cols))\n"
        "            new_count = new_rows.count()\n"
        '            print(f"  Diff: {new_count} new/changed rows")\n'
        "            if new_count == 0:\n"
        '                elapsed = _time.time() - t_start\n'
        '                print(f"  DONE: IN SYNC {full_name} ({src_count} rows) [{elapsed:.1f}s]")\n'
        "                synced.append((full_name, 0, 'unchanged'))\n"
        "            else:\n"
        "                if src_cols == set(common_cols):\n"
        "                    delta_df = new_rows\n"
        "                else:\n"
        "                    delta_df = src_df.join(new_rows, on=common_cols, how='inner').dropDuplicates()\n"
        '                print(f"  ACTION: Appending {new_count} rows...")\n'
        "                delta_df.write.format('delta').mode('append').option('mergeSchema','true').saveAsTable(full_name)\n"
        "                total_rows_copied += new_count\n"
        '                elapsed = _time.time() - t_start\n'
        '                print(f"  DONE: UPD {full_name} +{new_count} rows [{elapsed:.1f}s]")\n'
        "                synced.append((full_name, new_count, 'incremental'))\n\n"

        "            # Verify\n"
        '            print(f"  Verifying {full_name}...")\n'
        "            vdf = spark.read.table(full_name)\n"
        '            print(f"  Verified: {vdf.count()} rows, {len(vdf.columns)} columns")\n\n'

        # Per-table timeout check
        "            elapsed = _time.time() - t_start\n"
        "            if elapsed > TABLE_TIMEOUT:\n"
        '                print(f"  WARNING: table took {elapsed:.0f}s (>{TABLE_TIMEOUT}s timeout)")\n\n'

        "        except Exception as e:\n"
        '            elapsed = _time.time() - t_start\n'
        '            print(f"  FAILED: {full_name} [{elapsed:.1f}s]")\n'
        '            print(f"  Error: {type(e).__name__}: {e}")\n'
        "            _tb.print_exc()\n"
        "            failed.append(full_name)\n"
        "            _sync_status['errors'].append(f'{full_name}: {type(e).__name__}: {e}')\n\n"

        # ── Summary ──
        '    total_elapsed = _time.time() - _t0\n'
        '    print("")\n'
        '    print("=" * 72)\n'
        '    print("SYNC SUMMARY")\n'
        '    print("=" * 72)\n'
        '    print(f"Tables synced      : {len(synced)}/{total_table_count}")\n'
        '    print(f"Tables failed      : {len(failed)}")\n'
        '    print(f"Tables skipped     : {len(skipped_empty)} (empty source)")\n'
        '    print(f"Total rows copied  : {total_rows_copied:,}")\n'
        '    print(f"Total cols added   : {total_cols_added}")\n'
        '    print(f"Total elapsed      : {total_elapsed:.1f}s")\n'
        '    print("")\n'
        '    print("Detail:")\n'
        "    for t, r, mode in synced:\n"
        '        r_str = f"{r:>8,} rows" if r >= 0 else "   (full)"\n'
        '        print(f"  OK  {t:40s} {r_str}  ({mode})")\n'
        "    for t in failed:\n"
        '        print(f"  ERR {t:40s} FAILED")\n'
        "    for t in skipped_empty:\n"
        '        print(f"  --- {t:40s} skipped (empty)")\n'
        '    print("=" * 72)\n\n'

        # Write status marker
        "    _sync_status['status'] = 'completed' if not failed else 'partial'\n"
        "    _sync_status['tables_synced'] = [t for t, _, _ in synced]\n"
        "    _sync_status['tables_failed'] = failed\n"
        "    _sync_status['tables_skipped'] = skipped_empty\n"
        "    _write_status()\n\n"

        "    if failed:\n"
        '        print(f"WARNING: {len(failed)} table(s) failed: {failed}")\n'
        "        if not synced:\n"
        "            raise Exception(f\"All {len(failed)} tables failed: {failed}\")\n"
    )
else:
    # Fallback DDL-only when source IDs are unknown
    _all_tables = []
    for _st in SCHEMA_TABLES.values():
        _all_tables.extend(_st)
    inner_code = (
        "# Auto-generated — Digital Realty Schema Enforcement (DDL only)\n"
        "# WARNING: SOURCE_WORKSPACE_ID or SOURCE_LAKEHOUSE_ID not provided\n"
        f"# Schema version: {SCHEMA_VERSION}\n\n"
        f"SCHEMA_TABLES = {repr(SCHEMA_TABLES)}\n\n"
        "created, skipped = [], []\n"
        "for schema_name, tables in SCHEMA_TABLES.items():\n"
        "    prefix = f'{schema_name}.' if schema_name else ''\n"
        "    for table in tables:\n"
        "        full = f'{prefix}{table}'\n"
        "        try:\n"
        "            spark.sql(f'CREATE TABLE IF NOT EXISTS {full} USING DELTA')\n"
        "            created.append(full)\n"
        '            print(f"OK: {full}")\n'
        "        except Exception as e:\n"
        '            print(f"SKIP: {full}: {e}")\n'
        "            skipped.append(full)\n\n"
        "print(f'DDL enforcement complete: {len(created)} tables')\n"
        "if skipped:\n"
        "    print(f'Skipped: {skipped}')\n"
    )

# ── Notebook metadata — attach lakehouse so spark.sql() works ─────────────────

# Wrap inner_code in a top-level try/except so notebook ALWAYS prints diagnostics
inner_code_wrapped = "import traceback as _tb\ntry:\n"
for line in inner_code.split("\n"):
    inner_code_wrapped += "    " + line + "\n"
inner_code_wrapped += (
    "except Exception as _fatal:\n"
    "    print('\\n' + '!' * 72)\n"
    "    print('FATAL UNHANDLED ERROR')\n"
    "    print('!' * 72)\n"
    "    print(f'Error type : {type(_fatal).__name__}')\n"
    "    print(f'Error msg  : {_fatal}')\n"
    "    print('Full traceback:')\n"
    "    _tb.print_exc()\n"
    "    print('!' * 72)\n"
    "    raise\n"
)
inner_code = inner_code_wrapped
nb_metadata = {
    "kernelspec": {
        "display_name": "Synapse PySpark",
        "language": "Python",
        "name": "synapse_pyspark",
    },
    "language_info": {"name": "python"},
}

if LAKEHOUSE_ID and WORKSPACE_ID:
    nb_metadata["trident"] = {
        "lakehouse": {
            "default_lakehouse":              LAKEHOUSE_ID,
            "default_lakehouse_workspace_id": WORKSPACE_ID,
            "known_lakehouses": [{"id": LAKEHOUSE_ID}],
        }
    }
    print(f"Lakehouse attached: {LAKEHOUSE_ID}")
else:
    print("WARNING: No LAKEHOUSE_ID/WORKSPACE_ID — saveAsTable() may fail")

notebook = {
    "nbformat": 4,
    "nbformat_minor": 4,
    "metadata": nb_metadata,
    "cells": [
        {
            "cell_type": "code",
            "metadata": {},
            "source": inner_code.splitlines(keepends=True),
            "outputs": [],
            "execution_count": None,
        }
    ],
}

# ── Write payload ──────────────────────────────────────────────────────────────
payload = {
    "displayName": NOTEBOOK_DISPLAY_NAME,
    "type": "Notebook",
    "definition": {
        "format": "ipynb",
        "parts": [
            {
                "path": "artifact.content.ipynb",
                "payload": base64.b64encode(json.dumps(notebook).encode()).decode(),
                "payloadType": "InlineBase64",
            }
        ],
    },
}

with open(OUT_PATH, "w") as f:
    json.dump(payload, f)

print(f"Notebook payload -> {OUT_PATH}")
total_tables = sum(len(v) for v in SCHEMA_TABLES.values())
print(f"Tables: {total_tables} across {len(SCHEMA_TABLES)} schema(s)")
for schema, tbls in sorted(SCHEMA_TABLES.items()):
    for t in tbls:
        prefix = f"{schema}." if schema else ""
        print(f"  {prefix}{t}")
