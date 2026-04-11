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
        "# Auto-generated — Digital Realty Full Data Sync (Multi-Schema)\n"
        "# Reads from Dev OneLake -> writes to this workspace lakehouse\n"
        f"# Schema version: {SCHEMA_VERSION}\n"
        "import time as _time\n\n"
        f'DEV_WS_ID = "{SOURCE_WORKSPACE_ID}"\n'
        f'DEV_LH_ID = "{SOURCE_LAKEHOUSE_ID}"\n'
        f"CI_SCHEMA_TABLES = {ci_schema_tables_repr}  # from CI discovery\n"
        f"SCHEMAS_ENABLED = {schemas_enabled_repr}\n\n"
        "# ── Helper: readable size ──\n"
        "def _fmt_bytes(n):\n"
        "    for unit in ['B','KB','MB','GB']:\n"
        "        if abs(n) < 1024: return f'{n:.1f} {unit}'\n"
        "        n /= 1024\n"
        "    return f'{n:.1f} TB'\n\n"
        "# ── Helper: print column detail for a dataframe ──\n"
        "def _print_schema(label, df):\n"
        "    print(f'  {label} schema ({len(df.columns)} columns):')\n"
        "    for col_name, col_type in df.dtypes:\n"
        "        print(f'    | {col_name:30s} | {col_type:15s} |')\n\n"
        "# ── Helper: print sample rows ──\n"
        "def _print_sample(label, df, n=3):\n"
        "    rows = df.limit(n).collect()\n"
        "    if rows:\n"
        "        print(f'  {label} sample ({n} rows):')\n"
        "        for r in rows:\n"
        "            vals = ', '.join(f'{k}={v!r}' for k, v in r.asDict().items())\n"
        "            print(f'    {vals}')\n"
        "    else:\n"
        "        print(f'  {label}: (empty)')\n\n"
        "# ── Environment diagnostics ──\n"
        '_t0 = _time.time()\n'
        'print("=" * 72)\n'
        'print("DIGITAL REALTY DATA SYNC — VERBOSE DIAGNOSTICS")\n'
        'print("=" * 72)\n'
        'print(f"Timestamp        : {_time.strftime(\'%Y-%m-%d %H:%M:%S UTC\', _time.gmtime())}")\n'
        'print(f"Source workspace : {DEV_WS_ID}")\n'
        'print(f"Source lakehouse : {DEV_LH_ID}")\n'
        'print(f"Schemas enabled  : {SCHEMAS_ENABLED}")\n'
        'print(f"CI schemas/tables: {len(CI_SCHEMA_TABLES)} schema(s) -> {CI_SCHEMA_TABLES}")\n'
        'try:\n'
        '    print(f"Spark version    : {spark.version}")\n'
        'except Exception:\n'
        '    print("Spark version    : (unavailable)")\n'
        'try:\n'
        '    print(f"mssparkutils     : available ({type(mssparkutils).__name__})")\n'
        'except NameError:\n'
        '    print("mssparkutils     : NOT available")\n'
        'print("")\n\n'
        "# Runtime discovery builds SCHEMA_TABLES dict: {schema: [tables]}\n"
        'dev_base_path = f"abfss://{DEV_WS_ID}@onelake.dfs.fabric.microsoft.com/{DEV_LH_ID}/Tables"\n'
        'print(f"OneLake base path: {dev_base_path}")\n\n'
        "_SKIP_DIRS = {'_delta_log', '_schemas', '_temporary', '__checkpoint', 'Files', 'TableMaintenance', 'Tables'}\n\n"
        "def _try_list(path):\n"
        "    '''List directories at path, filtering out non-table entries.'''\n"
        "    try:\n"
        '        print(f"  -> Listing: {path}")\n'
        "        entries = mssparkutils.fs.ls(path)\n"
        "        all_dirs = [e.name.rstrip('/') for e in entries if e.isDir]\n"
        '        print(f"     Raw dirs: {all_dirs}")\n'
        "        filtered = [d for d in all_dirs if d not in _SKIP_DIRS and not d.startswith('_')]\n"
        '        print(f"     After filter: {filtered}  (skipped: {set(all_dirs) - set(filtered)})")\n'
        "        return filtered\n"
        "    except Exception as ex:\n"
        '        print(f"     FAILED: {ex}")\n'
        "        return []\n\n"
        "SCHEMA_TABLES = {}  # {schema_name: [table_names]}\n\n"
        "# Strategy 1: try schemas known from CI discovery\n"
        'print(f"\\n--- Discovery Strategy 1: CI-known schemas ---")\n'
        "for ci_schema in sorted(CI_SCHEMA_TABLES.keys()):\n"
        "    if ci_schema:  # non-empty schema name\n"
        '        path = f"{dev_base_path}/{ci_schema}"\n'
        "        found = _try_list(path)\n"
        "        if found:\n"
        "            SCHEMA_TABLES[ci_schema] = found\n"
        '            print(f"  [FOUND] {len(found)} tables via Tables/{ci_schema}/")\n'
        "    else:  # empty schema = no schema prefix\n"
        "        found = _try_list(dev_base_path)\n"
        "        if found:\n"
        '            SCHEMA_TABLES[""] = found\n'
        '            print(f"  [FOUND] {len(found)} tables in Tables/ (no schema)")\n\n'
        "# Strategy 2: try dbo if not already found\n"
        "if 'dbo' not in SCHEMA_TABLES:\n"
        '    print(f"\\n--- Discovery Strategy 2: dbo schema ---")\n'
        '    path = f"{dev_base_path}/dbo"\n'
        "    found = _try_list(path)\n"
        "    if found:\n"
        "        SCHEMA_TABLES['dbo'] = found\n"
        '        print(f"  [FOUND] {len(found)} tables in Tables/dbo/")\n\n'
        "# Strategy 3: enumerate ALL schema dirs (NO BREAK — collect all)\n"
        "if not SCHEMA_TABLES:\n"
        '    print(f"\\n--- Discovery Strategy 3: enumerate ALL schema folders ---")\n'
        "    try:\n"
        "        schema_entries = mssparkutils.fs.ls(dev_base_path)\n"
        "        schema_dirs = [e.name.rstrip('/') for e in schema_entries if e.isDir]\n"
        '        print(f"  Schema dirs found: {schema_dirs}")\n'
        "        for sd in schema_dirs:\n"
        "            if sd in _SKIP_DIRS or sd.startswith('_'):\n"
        '                print(f"  Skipping system dir: {sd}")\n'
        "                continue\n"
        '            path = f"{dev_base_path}/{sd}"\n'
        "            found = _try_list(path)\n"
        "            if found:\n"
        "                SCHEMA_TABLES[sd] = found\n"
        '                print(f"  [FOUND] {len(found)} tables in Tables/{sd}/")\n'
        "    except Exception as ex:\n"
        '        print(f"  Strategy 3 failed: {ex}")\n\n'
        "# Strategy 4: direct Tables/ (no schema prefix)\n"
        "if not SCHEMA_TABLES:\n"
        '    print(f"\\n--- Discovery Strategy 4: direct Tables/ ---")\n'
        "    found = _try_list(dev_base_path)\n"
        "    if found:\n"
        '        SCHEMA_TABLES[""] = found\n'
        '        print(f"  [FOUND] {len(found)} tables in Tables/ (no schema)")\n\n'
        "# Strategy 5: CI table list fallback\n"
        "if not SCHEMA_TABLES and CI_SCHEMA_TABLES:\n"
        '    print(f"\\n--- Discovery Strategy 5: CI table list fallback ---")\n'
        "    SCHEMA_TABLES = dict(CI_SCHEMA_TABLES)\n"
        '    print(f"  Using CI table list: {SCHEMA_TABLES}")\n\n'
        "total_table_count = sum(len(v) for v in SCHEMA_TABLES.values())\n"
        "if total_table_count == 0:\n"
        '    print("\\n" + "!" * 72)\n'
        '    print("NO TABLES FOUND -- nothing to sync.")\n'
        '    print("All 5 discovery strategies returned 0 tables.")\n'
        '    print("Check: Does the source lakehouse have tables?")\n'
        '    print("Check: Does the service principal have OneLake read access?")\n'
        '    print("!" * 72)\n'
        '    print("RESULT: 0 tables synced")\n'
        "    # Do NOT call mssparkutils.notebook.exit() — Fabric treats it as failure\n\n"
        "if total_table_count > 0:\n"
        "    _sync_pairs = []\n"
        "    for _sn, _tl in sorted(SCHEMA_TABLES.items()):\n"
        "        for _t in _tl:\n"
        "            _sync_pairs.append((_sn, _t))\n\n"
        '    print("")\n'
        '    print("=" * 72)\n'
        '    print(f"STARTING SYNC: {total_table_count} tables across {len(SCHEMA_TABLES)} schema(s)")\n'
        "    for _sn, _tl in sorted(SCHEMA_TABLES.items()):\n"
        '        print(f"  Schema {_sn!r}: {_tl}")\n'
        '    print("=" * 72)\n\n'
        "    synced, failed, skipped_empty = [], [], []\n"
        "    total_rows_copied = 0\n"
        "    total_cols_added = 0\n\n"
        "    for idx, (schema_name, table) in enumerate(_sync_pairs, 1):\n"
        "        tbl_prefix = f'{schema_name}.' if schema_name else ''\n"
        "        source_path = f'{dev_base_path}/{schema_name}' if schema_name else dev_base_path\n"
        '        t_start = _time.time()\n'
        '        print("")\n'
        '        print("-" * 72)\n'
        '        print(f"[{idx}/{total_table_count}] TABLE: {tbl_prefix}{table} (schema={schema_name!r})")\n'
        '        print("-" * 72)\n'
        "        try:\n"
        '            src = f"{source_path}/{table}"\n'
        '            print(f"  Reading source: {src}")\n'
        "            src_df = spark.read.format('delta').load(src)\n"
        "            src_count = src_df.count()\n"
        "            src_cols = set(src_df.columns)\n"
        "            full_name = f'{tbl_prefix}{table}'\n"
        '            print(f"  Source: {src_count} rows, {len(src_cols)} columns")\n'
        "            _print_schema('SRC', src_df)\n"
        "            _print_sample('SRC', src_df)\n"
        "\n"
        "            # Check target\n"
        '            print(f"  Checking target: {full_name}")\n'
        "            table_exists = False\n"
        "            try:\n"
        "                tgt_df = spark.read.table(full_name)\n"
        "                table_exists = True\n"
        "                tgt_count = tgt_df.count()\n"
        "                tgt_cols = set(tgt_df.columns)\n"
        '                print(f"  Target EXISTS: {tgt_count} rows, {len(tgt_cols)} columns")\n'
        "                _print_schema('TGT', tgt_df)\n"
        "            except Exception as read_err:\n"
        "                tgt_count = 0\n"
        "                tgt_cols = set()\n"
        '                print(f"  Target MISSING: {read_err}")\n'
        "\n"
        "            if not table_exists:\n"
        '                print(f"  ACTION: Creating new table {full_name} with {src_count} rows...")\n'
        "                (src_df.write\n"
        "                   .format('delta')\n"
        "                   .mode('overwrite')\n"
        "                   .saveAsTable(full_name))\n"
        "                total_rows_copied += src_count\n"
        '                elapsed = _time.time() - t_start\n'
        '                print(f"  DONE: NEW {full_name} -> {src_count} rows, {len(src_cols)} cols [{elapsed:.1f}s]")\n'
        "                synced.append((full_name, src_count, 'created'))\n"
        "                continue\n"
        "\n"
        "            # Schema diff\n"
        "            new_cols = src_cols - tgt_cols\n"
        "            dropped_cols = tgt_cols - src_cols\n"
        '            print(f"  Schema diff: +{len(new_cols)} new cols, {len(dropped_cols)} only-in-target")\n'
        "            if new_cols:\n"
        '                print(f"  Adding columns to target: {new_cols}")\n'
        "                for col_name in sorted(new_cols):\n"
        "                    col_type = str(dict(src_df.dtypes).get(col_name, 'string'))\n"
        '                    print(f"    ALTER TABLE {full_name} ADD COLUMN `{col_name}` {col_type}")\n'
        '                    spark.sql(f"ALTER TABLE {full_name} ADD COLUMN `{col_name}` {col_type}")\n'
        "                total_cols_added += len(new_cols)\n"
        "                tgt_df = spark.read.table(full_name)\n"
        "                tgt_count = tgt_df.count()\n"
        '                print(f"  Re-read target after ALTER: {tgt_count} rows, {len(tgt_df.columns)} cols")\n'
        "            if dropped_cols:\n"
        '                print(f"  NOTE: columns only in target (not in source): {dropped_cols}")\n'
        "\n"
        "            if src_count == 0:\n"
        '                print(f"  SKIP: source is empty (0 rows)")\n'
        "                skipped_empty.append(full_name)\n"
        "                continue\n"
        "\n"
        "            if tgt_count == 0:\n"
        '                print(f"  ACTION: Target empty, inserting all {src_count} rows...")\n'
        "                (src_df.write\n"
        "                   .format('delta')\n"
        "                   .mode('append')\n"
        "                   .option('mergeSchema', 'true')\n"
        "                   .saveAsTable(full_name))\n"
        "                total_rows_copied += src_count\n"
        '                elapsed = _time.time() - t_start\n'
        '                print(f"  DONE: FILL {full_name} -> {src_count} rows [{elapsed:.1f}s]")\n'
        "                synced.append((full_name, src_count, 'filled'))\n"
        "                continue\n"
        "\n"
        "            # Incremental diff\n"
        "            common_cols = sorted(list(src_cols & tgt_cols))\n"
        '            print(f"  Comparing data: {len(common_cols)} common columns")\n'
        '            print(f"    Common columns: {common_cols}")\n'
        "            src_subset = src_df.select(common_cols)\n"
        "            tgt_subset = tgt_df.select(common_cols)\n"
        '            print(f"  Running subtract (src - tgt) to find new/changed rows...")\n'
        "            new_rows = src_subset.subtract(tgt_subset)\n"
        "            new_count = new_rows.count()\n"
        '            print(f"  Diff result: {new_count} new/changed rows (src={src_count}, tgt={tgt_count})")\n'
        "\n"
        "            if new_count == 0:\n"
        '                elapsed = _time.time() - t_start\n'
        '                print(f"  DONE: IN SYNC {full_name} ({src_count} rows, no changes) [{elapsed:.1f}s]")\n'
        "                synced.append((full_name, 0, 'unchanged'))\n"
        "            else:\n"
        "                _print_sample('NEW/CHANGED', new_rows)\n"
        "                if src_cols == set(common_cols):\n"
        "                    delta_df = new_rows\n"
        "                else:\n"
        '                    print(f"  Joining back to get full columns ({len(src_cols)} cols)...")\n'
        "                    delta_df = src_df.join(\n"
        "                        new_rows, on=common_cols, how='inner'\n"
        "                    ).dropDuplicates()\n"
        '                print(f"  ACTION: Appending {new_count} rows to {full_name}...")\n'
        "                (delta_df.write\n"
        "                   .format('delta')\n"
        "                   .mode('append')\n"
        "                   .option('mergeSchema', 'true')\n"
        "                   .saveAsTable(full_name))\n"
        "                total_rows_copied += new_count\n"
        '                elapsed = _time.time() - t_start\n'
        '                print(f"  DONE: UPD {full_name} -> +{new_count} rows (was {tgt_count}, now {tgt_count + new_count}) [{elapsed:.1f}s]")\n'
        "                synced.append((full_name, new_count, 'incremental'))\n"
        "\n"
        "            # Verify target after write\n"
        '            print(f"  Verifying {full_name} after write...")\n'
        "            verify_df = spark.read.table(full_name)\n"
        '            print(f"  Verified: {verify_df.count()} rows, {len(verify_df.columns)} columns")\n'
        "\n"
        "        except Exception as e:\n"
        '            import traceback\n'
        '            elapsed = _time.time() - t_start\n'
        '            print(f"  FAILED: {table} [{elapsed:.1f}s]")\n'
        '            print(f"  Error type : {type(e).__name__}")\n'
        '            print(f"  Error msg  : {e}")\n'
        '            print(f"  Traceback:")\n'
        '            traceback.print_exc()\n'
        "            failed.append(table)\n\n"
        "    # ── Final summary ──\n"
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
        '        print(f"  OK  {t:40s} {r:>8,} rows  ({mode})")\n'
        "    for t in failed:\n"
        '        print(f"  ERR {t:40s} FAILED")\n'
        "    for t in skipped_empty:\n"
        '        print(f"  --- {t:40s} skipped (empty)")\n'
        '    print("=" * 72)\n\n'
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
