"""
Layer 1 — Schema Registry: Dynamically discover Lakehouse table schemas
from a Microsoft Fabric workspace by reading Delta transaction logs.

This replaces the static schema registry (00_schema_registry.py) with
schemas pulled directly from the Dev workspace at promotion time.

Environment variables:
  FABRIC_TOKEN    Bearer token for Fabric REST API
  STORAGE_TOKEN   Bearer token for OneLake/Storage API (scope: storage.azure.com)
  WORKSPACE_ID    Source workspace GUID
  LAKEHOUSE_NAME  Lakehouse display name (optional — uses first lakehouse)
  OUT_FILE        Output JSON file path (default: schema_discovery.json)

Output (schema_discovery.json):
  {
    "workspace_id": "...",
    "lakehouse_id": "...",
    "lakehouse_name": "...",
    "table_count": N,
    "tables": {
      "year_2017": {
        "columns": [["Col1", "STRING", true], ["Col2", "BIGINT", false], ...]
      },
      ...
    }
  }
"""
import os
import json
import sys
import urllib.request
import urllib.error

FABRIC_TOKEN   = os.environ.get("FABRIC_TOKEN", "")
STORAGE_TOKEN  = os.environ.get("STORAGE_TOKEN", "")
WORKSPACE_ID   = os.environ.get("WORKSPACE_ID", "")
LAKEHOUSE_NAME = os.environ.get("LAKEHOUSE_NAME", "")
OUT_FILE       = os.environ.get("OUT_FILE", "schema_discovery.json")

# Spark type → SQL DDL type mapping
SPARK_TO_SQL = {
    "string":    "STRING",
    "long":      "BIGINT",
    "integer":   "INT",
    "int":       "INT",
    "short":     "SMALLINT",
    "byte":      "TINYINT",
    "double":    "DOUBLE",
    "float":     "FLOAT",
    "boolean":   "BOOLEAN",
    "binary":    "BINARY",
    "timestamp": "TIMESTAMP",
    "date":      "DATE",
    "decimal":   "DECIMAL(18,2)",
}


def fabric_get(path):
    url = f"https://api.fabric.microsoft.com/v1{path}"
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {FABRIC_TOKEN}"}
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        print(f"  ⚠️  HTTP {e.code} for {path}: {body}")
        return {}
    except Exception as e:
        print(f"  ⚠️  Request failed for {path}: {e}")
        return {}


def list_tables_via_dfs(ws_id, lh_id):
    """List table directories via OneLake DFS directory-listing API (ADLS Gen2)."""
    if not STORAGE_TOKEN:
        print("  ⚠️  STORAGE_TOKEN not set — DFS listing skipped")
        return []
    url = (
        f"https://onelake.dfs.fabric.microsoft.com"
        f"/{ws_id}/{lh_id}/Tables"
        f"?resource=directory&recursive=false"
    )
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {STORAGE_TOKEN}",
            "x-ms-version": "2023-01-03",
        },
    )
    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
        paths = data.get("paths", [])
        tables = []
        for p in paths:
            if str(p.get("isDirectory", "false")).lower() == "true":
                # name is "Tables/year_2017" or just "year_2017"
                name = p["name"].split("/")[-1]
                if name:
                    tables.append({"name": name})
        print(f"  DFS listing: {len(tables)} table folder(s) found")
        return tables
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:400]
        print(f"  ⚠️  DFS listing HTTP {e.code}: {body}")
        return []
    except Exception as e:
        print(f"  ⚠️  DFS listing failed: {e}")
        return []


def onelake_read(ws_id, lh_id, relative_path):
    """Read a file from OneLake DFS API. Requires STORAGE_TOKEN scope."""
    if not STORAGE_TOKEN:
        return None
    url = (
        f"https://onelake.dfs.fabric.microsoft.com"
        f"/{ws_id}/{lh_id}/{relative_path}"
    )
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {STORAGE_TOKEN}",
            "x-ms-version": "2023-01-03",
        },
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.read().decode()
    except urllib.error.HTTPError:
        return None
    except Exception:
        return None


def delta_schema_to_columns(schema_string):
    """Parse Delta schemaString JSON → list of [name, sql_type, nullable] triples."""
    schema = json.loads(schema_string)
    cols = []
    for field in schema.get("fields", []):
        name     = field["name"]
        raw_type = field["type"]
        nullable = field.get("nullable", True)

        if isinstance(raw_type, dict):
            # Complex type (struct, array, map) — represent as STRING
            sql_type = "STRING"
        else:
            base = str(raw_type).lower().split("(")[0]
            sql_type = SPARK_TO_SQL.get(base, "STRING")

        cols.append([name, sql_type, nullable])
    return cols


# ── Entry point ────────────────────────────────────────────────────────────────
if not FABRIC_TOKEN or not WORKSPACE_ID:
    print("ERROR: FABRIC_TOKEN and WORKSPACE_ID are required")
    sys.exit(1)

if not STORAGE_TOKEN:
    print("⚠️  STORAGE_TOKEN not set — Delta log reading will be skipped")
    print("   Schema discovery may be incomplete (table names only)")

print(f"🔍 Layer 1 — Schema Registry: discovering from workspace {WORKSPACE_ID}")

# 1. Find the lakehouse in the workspace
items_resp = fabric_get(f"/workspaces/{WORKSPACE_ID}/items?type=Lakehouse")
lakehouses = items_resp.get("value", [])

if not lakehouses:
    print("ERROR: No lakehouses found in workspace")
    sys.exit(1)

if LAKEHOUSE_NAME:
    lh = next((x for x in lakehouses if x["displayName"] == LAKEHOUSE_NAME), None)
    if not lh:
        names = ", ".join(x["displayName"] for x in lakehouses)
        print(f"ERROR: Lakehouse '{LAKEHOUSE_NAME}' not found. Available: {names}")
        sys.exit(1)
    candidates = [lh]
else:
    # Try all lakehouses — pick the first one that has tables
    candidates = list(lakehouses)
    print(f"ℹ️  No LAKEHOUSE_NAME specified — will try {len(candidates)} lakehouse(s)")

# Find the first lakehouse with tables
lh = None
LH_ID = ""
LH_NAME = ""
for candidate in candidates:
    cid = candidate["id"]
    cname = candidate["displayName"]
    print(f"  Trying lakehouse: {cname} ({cid})")
    tables_check = fabric_get(f"/workspaces/{WORKSPACE_ID}/lakehouses/{cid}/tables")
    tbl_list = tables_check.get("data", []) or tables_check.get("value", [])
    if not tbl_list:
        tbl_list = list_tables_via_dfs(WORKSPACE_ID, cid)
    if tbl_list:
        lh = candidate
        LH_ID = cid
        LH_NAME = cname
        print(f"  ✅ Found {len(tbl_list)} table(s) in {cname}")
        break
    else:
        print(f"  ⚠️  {cname}: 0 tables — skipping")

if not lh:
    # Fall back to the first lakehouse even if 0 tables
    lh = candidates[0]
    LH_ID = lh["id"]
    LH_NAME = lh["displayName"]
    print(f"⚠️  No lakehouse had tables — defaulting to {LH_NAME}")

print(f"✅ Lakehouse: {LH_NAME} ({LH_ID})")

# 2. List tables — try Lakehouse Tables API first, fall back to DFS listing
tables_resp = fabric_get(f"/workspaces/{WORKSPACE_ID}/lakehouses/{LH_ID}/tables")
# Debug: show raw keys so we can diagnose API shape issues
if tables_resp:
    print(f"   Lakehouse Tables API response keys: {list(tables_resp.keys())}")
# Accept either "data" or "value" key (Fabric API can differ by version)
tables = tables_resp.get("data", []) or tables_resp.get("value", [])
print(f"📋 Lakehouse Tables API: {len(tables)} table(s)")

if not tables:
    print("ℹ️  Lakehouse Tables API returned 0 — trying OneLake DFS directory listing...")
    tables = list_tables_via_dfs(WORKSPACE_ID, LH_ID)

if not tables:
    print("⚠️  No tables found via any method — nothing to promote")
    output = {
        "workspace_id":   WORKSPACE_ID,
        "lakehouse_id":   LH_ID,
        "lakehouse_name": LH_NAME,
        "table_count":    0,
        "tables":         {},
    }
    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print(f"✅ Written → {OUT_FILE} (no tables)")
    sys.exit(0)

# 3. Read Delta transaction logs to discover actual schemas
discovered = {}
skipped    = []

for t in tables:
    tname = t["name"]

    # The first transaction log always contains the metaData with the schema.
    # OneLake DFS path: /Tables/{name}/_delta_log/00000000000000000000.json
    content = onelake_read(
        WORKSPACE_ID, LH_ID,
        f"Tables/{tname}/_delta_log/00000000000000000000.json"
    )

    if content is None:
        print(f"  ⚠️  {tname}: cannot read Delta log — skipping")
        skipped.append(tname)
        continue

    # Delta log is NDJSON — scan lines for the metaData entry
    cols = []
    for line in content.strip().split("\n"):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        if "metaData" in entry:
            schema_str = entry["metaData"].get("schemaString", "")
            if schema_str:
                cols = delta_schema_to_columns(schema_str)
            break

    if cols:
        discovered[tname] = {"columns": cols}
        print(f"  ✅ {tname}: {len(cols)} columns")
    else:
        print(f"  ⚠️  {tname}: no schema in Delta log — skipping")
        skipped.append(tname)

print(f"\n📊 Discovered: {len(discovered)} tables, skipped: {len(skipped)}")
if skipped:
    print(f"   Skipped: {', '.join(skipped)}")

# 4. Write output
output = {
    "workspace_id":   WORKSPACE_ID,
    "lakehouse_id":   LH_ID,
    "lakehouse_name": LH_NAME,
    "table_count":    len(discovered),
    "tables":         discovered,
}

with open(OUT_FILE, "w") as f:
    json.dump(output, f, indent=2)

print(f"✅ Schema Registry written → {OUT_FILE}")
