"""
Generate a self-contained Fabric notebook payload (nb_payload.json).
Called by the promote-with-schema-validation workflow.

The generated notebook reads ALL data from Dev OneLake (abfss) and writes it
to the target workspace default lakehouse — full schema + data sync.

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
        "if SCHEMAS_ENABLED:\n"
        '    dev_tables_path = f"{dev_base_path}/{DEFAULT_SCHEMA}"\n'
        "else:\n"
        "    dev_tables_path = dev_base_path\n\n"
        "try:\n"
        "    entries = mssparkutils.fs.ls(dev_tables_path)\n"
        "    TABLES = [e.name.rstrip('/') for e in entries if e.isDir]\n"
        '    print(f"Runtime discovery: {len(TABLES)} tables found in Dev OneLake")\n'
        "    if not TABLES and not SCHEMAS_ENABLED:\n"
        "        # Maybe it is actually schema-enabled — try with dbo/\n"
        '        alt_path = f"{dev_base_path}/dbo"\n'
        "        try:\n"
        "            entries = mssparkutils.fs.ls(alt_path)\n"
        "            TABLES = [e.name.rstrip('/') for e in entries if e.isDir]\n"
        "            if TABLES:\n"
        "                dev_tables_path = alt_path\n"
        "                SCHEMAS_ENABLED = True\n"
        '                print(f"  Detected schema-enabled: {len(TABLES)} tables in dbo/")\n'
        "        except Exception:\n"
        "            pass\n"
        "except Exception as _e:\n"
        '    print(f"Runtime discovery failed ({_e}), trying fallback...")\n'
        "    try:\n"
        '        alt_path = f"{dev_base_path}/dbo" if not SCHEMAS_ENABLED else dev_base_path\n'
        "        entries = mssparkutils.fs.ls(alt_path)\n"
        "        TABLES = [e.name.rstrip('/') for e in entries if e.isDir]\n"
        "        if TABLES:\n"
        "            dev_tables_path = alt_path\n"
        '            print(f"  Fallback discovery: {len(TABLES)} tables")\n'
        "    except Exception as _e2:\n"
        '        print(f"  Fallback also failed ({_e2}), using CI list")\n'
        "        TABLES = CI_TABLES\n\n"
        "if not TABLES:\n"
        '    print("WARNING: No tables found to sync. Check Dev OneLake permissions.")\n\n'
        "synced, failed = [], []\n"
        'print("=" * 60)\n'
        'print(f"Starting full data sync: {len(TABLES)} tables")\n'
        'print(f"Source: {dev_tables_path}")\n'
        'print("=" * 60)\n\n'
        "for table in TABLES:\n"
        "    try:\n"
        '        src = f"{dev_tables_path}/{table}"\n'
        "        df = spark.read.format('delta').load(src)\n"
        "        row_count = df.count()\n"
        "        col_count = len(df.columns)\n"
        "        (df.write\n"
        "           .format('delta')\n"
        "           .mode('overwrite')\n"
        "           .option('overwriteSchema', 'true')\n"
        "           .saveAsTable(table))\n"
        '        print(f"OK  {table}: {row_count} rows, {col_count} columns")\n'
        "        synced.append((table, row_count))\n"
        "    except Exception as e:\n"
        '        print(f"ERR {table}: {e}")\n'
        "        failed.append(table)\n\n"
        'print("")\n'
        'print("=" * 60)\n'
        'print(f"Sync complete: {len(synced)} succeeded, {len(failed)} failed")\n'
        "for t, r in synced:\n"
        '    print(f"  {t} : {r} rows")\n'
        "if failed:\n"
        '    print(f"FAILED: {failed}")\n'
        "    raise Exception(f\"{len(failed)} tables failed: {failed}\")\n"
        'print("=" * 60)\n'
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
