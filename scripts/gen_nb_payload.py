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
OUT_PATH            = os.environ.get("OUT_PATH", "/tmp/nb_payload.json")

# ── Load schema / table list ───────────────────────────────────────────────────
if SCHEMA_FILE and os.path.isfile(SCHEMA_FILE):
    disc = json.load(open(SCHEMA_FILE))
    SCHEMA_VERSION = f"live-{disc.get('workspace_id','')[:8]}"
    TABLES = list(disc.get("tables", {}).keys())
    SCHEMAS_ENABLED = disc.get("schemas_enabled", False)
    DEFAULT_SCHEMA = disc.get("default_schema", "dbo")
    # Sanitise: "Files" is a storage area, not a valid schema name
    if not DEFAULT_SCHEMA or DEFAULT_SCHEMA == "Files":
        DEFAULT_SCHEMA = "dbo"
    if not SOURCE_LAKEHOUSE_ID:
        SOURCE_LAKEHOUSE_ID = disc.get("lakehouse_id", "")
    if not SOURCE_WORKSPACE_ID:
        SOURCE_WORKSPACE_ID = disc.get("workspace_id", "")
    print(f"Schema source   : {SCHEMA_FILE} ({len(TABLES)} tables)")
    if SCHEMAS_ENABLED:
        print(f"Schemas enabled : yes (default schema: {DEFAULT_SCHEMA})")
else:
    repo_root = os.path.join(os.path.dirname(__file__), "..")
    registry_path = os.path.join(repo_root, "notebooks", "00_schema_registry.py")
    ns = {}
    exec(open(registry_path).read(), ns)
    SCHEMA_VERSION = ns["SCHEMA_VERSION"]
    TABLES = list(ns["SCHEMAS"].keys())
    SCHEMAS_ENABLED = False
    DEFAULT_SCHEMA = "dbo"
    print(f"Schema source   : 00_schema_registry.py (static fallback, {len(TABLES)} tables)")

print(f"Source workspace: {SOURCE_WORKSPACE_ID}")
print(f"Source lakehouse: {SOURCE_LAKEHOUSE_ID}")
print(f"Target workspace: {WORKSPACE_ID}")
print(f"Target lakehouse: {LAKEHOUSE_ID}")

# ── Build PySpark notebook code ────────────────────────────────────────────────
has_source = bool(SOURCE_WORKSPACE_ID and SOURCE_LAKEHOUSE_ID)

if has_source:
    ci_tables_repr = repr(TABLES)  # may be [] if CI discovery returned 0 tables
    schemas_enabled_repr = repr(SCHEMAS_ENABLED)
    default_schema_repr = repr(DEFAULT_SCHEMA)
    inner_code = (
        "# Auto-generated — Digital Realty Full Data Sync\n"
        "# Reads from Dev OneLake -> writes to this workspace lakehouse\n"
        f"# Schema version: {SCHEMA_VERSION}\n"
        "import time as _time\n\n"
        f'DEV_WS_ID = "{SOURCE_WORKSPACE_ID}"\n'
        f'DEV_LH_ID = "{SOURCE_LAKEHOUSE_ID}"\n'
        f"CI_TABLES = {ci_tables_repr}  # from CI schema discovery (may be empty)\n"
        f"SCHEMAS_ENABLED = {schemas_enabled_repr}\n"
        f"DEFAULT_SCHEMA = {default_schema_repr}\n\n"
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
        'print(f"Default schema   : {DEFAULT_SCHEMA}")\n'
        'print(f"CI tables        : {len(CI_TABLES)} -> {CI_TABLES}")\n'
        'try:\n'
        '    print(f"Spark version    : {spark.version}")\n'
        'except Exception:\n'
        '    print("Spark version    : (unavailable)")\n'
        'try:\n'
        '    print(f"mssparkutils     : available ({type(mssparkutils).__name__})")\n'
        'except NameError:\n'
        '    print("mssparkutils     : NOT available")\n'
        'print("")\n\n'
        "# Runtime discovery\n"
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
        "TABLES = []\n"
        "SCHEMAS_TO_TRY = ['dbo']\n"
        "if DEFAULT_SCHEMA and DEFAULT_SCHEMA != 'dbo':\n"
        "    SCHEMAS_TO_TRY.append(DEFAULT_SCHEMA)\n\n"
        'print(f"\\n--- Discovery Strategy 1: schema-prefixed paths ---")\n'
        "for schema in SCHEMAS_TO_TRY:\n"
        '    path = f"{dev_base_path}/{schema}"\n'
        "    found = _try_list(path)\n"
        "    if found:\n"
        "        TABLES = found\n"
        "        dev_tables_path = path\n"
        "        SCHEMAS_ENABLED = True\n"
        "        DEFAULT_SCHEMA = schema\n"
        '        print(f"  [FOUND] {len(TABLES)} tables via Tables/{schema}/")\n'
        "        break\n\n"
        "if not TABLES:\n"
        '    print(f"\\n--- Discovery Strategy 2: direct Tables/ ---")\n'
        "    found = _try_list(dev_base_path)\n"
        "    if found:\n"
        "        TABLES = found\n"
        "        dev_tables_path = dev_base_path\n"
        "        SCHEMAS_ENABLED = False\n"
        '        print(f"  [FOUND] {len(TABLES)} tables in Tables/ (no schema)")\n\n'
        "if not TABLES:\n"
        '    print(f"\\n--- Discovery Strategy 3: enumerate schema folders ---")\n'
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
        "                TABLES = found\n"
        "                dev_tables_path = path\n"
        "                SCHEMAS_ENABLED = True\n"
        "                DEFAULT_SCHEMA = sd\n"
        '                print(f"  [FOUND] {len(TABLES)} tables in Tables/{sd}/")\n'
        "                break\n"
        "    except Exception as ex:\n"
        '        print(f"  Strategy 3 failed: {ex}")\n\n'
        "if not TABLES and CI_TABLES:\n"
        '    print(f"\\n--- Discovery Strategy 4: CI table list ---")\n'
        "    TABLES = CI_TABLES\n"
        "    if SCHEMAS_ENABLED:\n"
        '        dev_tables_path = f"{dev_base_path}/{DEFAULT_SCHEMA}"\n'
        "    else:\n"
        "        dev_tables_path = dev_base_path\n"
        '    print(f"  Using CI table list: {TABLES}")\n\n'
        "if not TABLES:\n"
        '    print("\\n" + "!" * 72)\n'
        '    print("NO TABLES FOUND — nothing to sync.")\n'
        '    print("All 4 discovery strategies returned 0 tables.")\n'
        '    print("Check: Does the source lakehouse have tables?")\n'
        '    print("Check: Does the service principal have OneLake read access?")\n'
        '    print("!" * 72)\n'
        '    print("RESULT: 0 tables synced")\n'
        "    # Do NOT call mssparkutils.notebook.exit() — Fabric treats it as failure\n\n"
        "if TABLES:\n"
        "    tbl_prefix = f'{DEFAULT_SCHEMA}.' if SCHEMAS_ENABLED else ''\n\n"
        '    print("")\n'
        '    print("=" * 72)\n'
        '    print(f"STARTING SYNC: {len(TABLES)} tables")\n'
        '    print(f"Source path    : {dev_tables_path}")\n'
        '    print(f"Table prefix   : {tbl_prefix!r} (schemas_enabled={SCHEMAS_ENABLED})")\n'
        '    print(f"Tables to sync : {TABLES}")\n'
        '    print("=" * 72)\n\n'
        "    synced, failed, skipped_empty = [], [], []\n"
        "    total_rows_copied = 0\n"
        "    total_cols_added = 0\n\n"
        "    for idx, table in enumerate(TABLES, 1):\n"
        '        t_start = _time.time()\n'
        '        print("")\n'
        '        print("-" * 72)\n'
        '        print(f"[{idx}/{len(TABLES)}] TABLE: {table}")\n'
        '        print("-" * 72)\n'
        "        try:\n"
        '            src = f"{dev_tables_path}/{table}"\n'
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
        '    print(f"Tables synced      : {len(synced)}/{len(TABLES)}")\n'
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
    inner_code = (
        "# Auto-generated — Digital Realty Schema Enforcement (DDL only)\n"
        "# WARNING: SOURCE_WORKSPACE_ID or SOURCE_LAKEHOUSE_ID not provided\n"
        f"# Schema version: {SCHEMA_VERSION}\n\n"
        f"TABLES = {repr(TABLES)}\n\n"
        "created, skipped = [], []\n"
        "for table in TABLES:\n"
        "    try:\n"
        "        spark.sql(f'CREATE TABLE IF NOT EXISTS {table} USING DELTA')\n"
        "        created.append(table)\n"
        '        print(f"OK: {table}")\n'
        "    except Exception as e:\n"
        '        print(f"SKIP: {table}: {e}")\n'
        "        skipped.append(table)\n\n"
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
    "displayName": "00_sync_to_uat",
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
print(f"Tables: {len(TABLES)}")
for t in TABLES:
    print(f"  {t}")
