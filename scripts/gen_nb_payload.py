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
        f"# Schema version: {SCHEMA_VERSION}\n\n"
        f'DEV_WS_ID = "{SOURCE_WORKSPACE_ID}"\n'
        f'DEV_LH_ID = "{SOURCE_LAKEHOUSE_ID}"\n'
        f"CI_TABLES = {ci_tables_repr}  # from CI schema discovery (may be empty)\n"
        f"SCHEMAS_ENABLED = {schemas_enabled_repr}\n"
        f"DEFAULT_SCHEMA = {default_schema_repr}\n\n"
        "# Runtime discovery: list the actual table directory in Dev OneLake\n"
        "# This runs inside Fabric with native permissions — bypasses SP API limits\n"
        'dev_base_path = f"abfss://{DEV_WS_ID}@onelake.dfs.fabric.microsoft.com/{DEV_LH_ID}/Tables"\n'
        "\n"
        "# Directories that are never table names — skip during runtime discovery\n"
        "_SKIP_DIRS = {'_delta_log', '_schemas', '_temporary', '__checkpoint', 'Files', 'TableMaintenance', 'Tables'}\n\n"
        "def _try_list(path):\n"
        "    '''List directories at path, filtering out non-table entries.'''\n"
        "    try:\n"
        "        entries = mssparkutils.fs.ls(path)\n"
        "        dirs = [e.name.rstrip('/') for e in entries if e.isDir]\n"
        "        return [d for d in dirs if d not in _SKIP_DIRS and not d.startswith('_')]\n"
        "    except Exception:\n"
        "        return []\n\n"
        "# Try multiple discovery strategies\n"
        "TABLES = []\n"
        "SCHEMAS_TO_TRY = ['dbo']\n"
        "if DEFAULT_SCHEMA and DEFAULT_SCHEMA != 'dbo':\n"
        "    SCHEMAS_TO_TRY.append(DEFAULT_SCHEMA)\n\n"
        "# Strategy 1: try schema-prefixed paths (Tables/{schema}/)\n"
        "for schema in SCHEMAS_TO_TRY:\n"
        '    path = f"{dev_base_path}/{schema}"\n'
        "    found = _try_list(path)\n"
        "    if found:\n"
        "        TABLES = found\n"
        "        dev_tables_path = path\n"
        "        SCHEMAS_ENABLED = True\n"
        "        DEFAULT_SCHEMA = schema\n"
        '        print(f"Runtime discovery: {len(TABLES)} tables in Tables/{schema}/")\n'
        "        break\n\n"
        "# Strategy 2: try direct Tables/ (non-schema-enabled)\n"
        "if not TABLES:\n"
        "    found = _try_list(dev_base_path)\n"
        "    if found:\n"
        "        TABLES = found\n"
        "        dev_tables_path = dev_base_path\n"
        "        SCHEMAS_ENABLED = False\n"
        '        print(f"Runtime discovery: {len(TABLES)} tables in Tables/ (no schema)")\n\n'
        "# Strategy 3: enumerate all schema folders dynamically\n"
        "if not TABLES:\n"
        "    try:\n"
        "        schema_entries = mssparkutils.fs.ls(dev_base_path)\n"
        "        schema_dirs = [e.name.rstrip('/') for e in schema_entries if e.isDir]\n"
        "        for sd in schema_dirs:\n"
        "            if sd in _SKIP_DIRS or sd.startswith('_'):\n"
        "                continue\n"
        '            path = f"{dev_base_path}/{sd}"\n'
        "            found = _try_list(path)\n"
        "            if found:\n"
        "                TABLES = found\n"
        "                dev_tables_path = path\n"
        "                SCHEMAS_ENABLED = True\n"
        "                DEFAULT_SCHEMA = sd\n"
        '                print(f"Runtime discovery: {len(TABLES)} tables in Tables/{sd}/")\n'
        "                break\n"
        "    except Exception:\n"
        "        pass\n\n"
        "# Strategy 4: fall back to CI-discovered list\n"
        "if not TABLES and CI_TABLES:\n"
        "    TABLES = CI_TABLES\n"
        "    if SCHEMAS_ENABLED:\n"
        '        dev_tables_path = f"{dev_base_path}/{DEFAULT_SCHEMA}"\n'
        "    else:\n"
        "        dev_tables_path = dev_base_path\n"
        '    print(f"Using CI table list: {len(TABLES)} tables")\n\n'
        "if not TABLES:\n"
        '    print("No tables found in Dev lakehouse — nothing to sync.")\n'
        '    print("This is OK if the lakehouse is empty or tables have not been created yet.")\n'
        '    print("RESULT: 0 tables synced")\n'
        "    # Do NOT call mssparkutils.notebook.exit() — Fabric treats it as failure\n\n"
        "if TABLES:\n"
        "    # For schema-enabled lakehouses, read.table/saveAsTable need schema prefix\n"
        "    tbl_prefix = f'{DEFAULT_SCHEMA}.' if SCHEMAS_ENABLED else ''\n\n"
        "    synced, failed, skipped_empty = [], [], []\n"
        '    print("=" * 60)\n'
        '    print(f"Starting incremental data sync: {len(TABLES)} tables")\n'
        '    print(f"Source: {dev_tables_path}")\n'
        '    print(f"Table prefix: {tbl_prefix!r} (schemas_enabled={SCHEMAS_ENABLED})")\n'
        '    print("Strategy: schema diff + new/changed rows only")\n'
        '    print("=" * 60)\n\n'
        "    for table in TABLES:\n"
        "        try:\n"
        '            src = f"{dev_tables_path}/{table}"\n'
        "            src_df = spark.read.format('delta').load(src)\n"
        "            src_count = src_df.count()\n"
        "            src_cols = set(src_df.columns)\n"
        "            full_name = f'{tbl_prefix}{table}'\n"
        "\n"
        "            # Check if table already exists in target\n"
        "            table_exists = False\n"
        "            try:\n"
        "                tgt_df = spark.read.table(full_name)\n"
        "                table_exists = True\n"
        "                tgt_count = tgt_df.count()\n"
        "                tgt_cols = set(tgt_df.columns)\n"
        "            except Exception:\n"
        "                tgt_count = 0\n"
        "                tgt_cols = set()\n"
        "\n"
        "            if not table_exists:\n"
        "                (src_df.write\n"
        "                   .format('delta')\n"
        "                   .mode('overwrite')\n"
        "                   .saveAsTable(full_name))\n"
        '                print(f"NEW {full_name}: created with {src_count} rows, {len(src_cols)} cols")\n'
        "                synced.append((full_name, src_count, 'created'))\n"
        "                continue\n"
        "\n"
        "            new_cols = src_cols - tgt_cols\n"
        "            if new_cols:\n"
        "                for col_name in new_cols:\n"
        "                    col_type = str(dict(src_df.dtypes).get(col_name, 'string'))\n"
        '                    spark.sql(f"ALTER TABLE {full_name} ADD COLUMN `{col_name}` {col_type}")\n'
        '                print(f"  + {full_name}: added {len(new_cols)} column(s): {new_cols}")\n'
        "                tgt_df = spark.read.table(full_name)\n"
        "                tgt_count = tgt_df.count()\n"
        "\n"
        "            if src_count == 0:\n"
        '                print(f"SKIP {full_name}: source is empty")\n'
        "                skipped_empty.append(full_name)\n"
        "                continue\n"
        "\n"
        "            if tgt_count == 0:\n"
        "                (src_df.write\n"
        "                   .format('delta')\n"
        "                   .mode('append')\n"
        "                   .option('mergeSchema', 'true')\n"
        "                   .saveAsTable(full_name))\n"
        '                print(f"FILL {full_name}: inserted {src_count} rows (target was empty)")\n'
        "                synced.append((full_name, src_count, 'filled'))\n"
        "                continue\n"
        "\n"
        "            common_cols = sorted(list(src_cols & tgt_cols))\n"
        "            src_subset = src_df.select(common_cols)\n"
        "            tgt_subset = tgt_df.select(common_cols)\n"
        "            new_rows = src_subset.subtract(tgt_subset)\n"
        "            new_count = new_rows.count()\n"
        "\n"
        "            if new_count == 0:\n"
        '                print(f"OK  {full_name}: in sync ({src_count} rows, no changes)")\n'
        "                synced.append((full_name, 0, 'unchanged'))\n"
        "            else:\n"
        "                if src_cols == set(common_cols):\n"
        "                    delta_df = new_rows\n"
        "                else:\n"
        "                    delta_df = src_df.join(\n"
        "                        new_rows, on=common_cols, how='inner'\n"
        "                    ).dropDuplicates()\n"
        "                (delta_df.write\n"
        "                   .format('delta')\n"
        "                   .mode('append')\n"
        "                   .option('mergeSchema', 'true')\n"
        "                   .saveAsTable(full_name))\n"
        '                print(f"UPD {full_name}: appended {new_count} new/changed rows '
        '(src={src_count}, tgt_before={tgt_count})")\n'
        "                synced.append((full_name, new_count, 'incremental'))\n"
        "        except Exception as e:\n"
        '            print(f"ERR {table}: {e}")\n'
        "            failed.append(table)\n\n"
        '    print("")\n'
        '    print("=" * 60)\n'
        '    print(f"Sync complete: {len(synced)} OK, {len(failed)} failed, {len(skipped_empty)} empty")\n'
        "    for t, r, mode in synced:\n"
        '        print(f"  {t}: {r} rows ({mode})")\n'
        "    if failed:\n"
        '        print(f"WARNING — failed tables: {failed}")\n'
        "        # Only raise if ALL tables failed (partial success is OK)\n"
        "        if not synced:\n"
        "            raise Exception(f\"All {len(failed)} tables failed: {failed}\")\n"
        '    print("=" * 60)\n'
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
