"""
Layer 1 — Schema Registry: Discover ALL Lakehouse table schemas
from a Microsoft Fabric workspace by reading Delta transaction logs.

Scans EVERY lakehouse in the workspace (not just the first one with tables).
For schema-enabled lakehouses, discovers ALL schemas including non-standard
ones like year_2017, year_2018 via recursive DFS.

Environment variables:
  FABRIC_TOKEN    Bearer token for Fabric REST API
  STORAGE_TOKEN   Bearer token for OneLake/Storage API (scope: storage.azure.com)
  WORKSPACE_ID    Source workspace GUID
  LAKEHOUSE_NAME  (optional) Limit to a single lakehouse by display name
  OUT_FILE        Output JSON file path (default: schema_discovery.json)

Output (schema_discovery.json):
  {
    "workspace_id": "...",
    "total_table_count": N,
    "lakehouses": [
      {
        "lakehouse_id": "...",
        "lakehouse_name": "...",
        "schemas_enabled": true,
        "table_count": N,
        "schemas": {
          "dbo": {
            "tables": {
              "table1": {"columns": [["Col1","STRING",true], ...]},
              ...
            }
          },
          "year_2017": { "tables": { ... } }
        }
      },
      ...
    ]
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


def fabric_get_detect_error(path):
    """Like fabric_get but returns (data_dict, error_code_string_or_None)."""
    url = f"https://api.fabric.microsoft.com/v1{path}"
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {FABRIC_TOKEN}"}
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        print(f"  ⚠️  HTTP {e.code} for {path}: {body}")
        try:
            err = json.loads(body)
            return {}, err.get("errorCode", f"HTTP_{e.code}")
        except (json.JSONDecodeError, ValueError):
            return {}, f"HTTP_{e.code}"
    except Exception as e:
        print(f"  ⚠️  Request failed for {path}: {e}")
        return {}, str(e)


def list_tables_via_dfs(ws_id, lh_id, directory="Tables"):
    """List subdirectories via OneLake DFS List Paths API (ADLS Gen2)."""
    if not STORAGE_TOKEN:
        print("  ⚠️  STORAGE_TOKEN not set — DFS listing skipped")
        return []
    url = (
        f"https://onelake.dfs.fabric.microsoft.com"
        f"/{ws_id}/{lh_id}"
        f"?resource=filesystem&directory={directory}&recursive=false"
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
        print(f"  DFS listing ({directory}): {len(tables)} folder(s) found")
        return tables
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:400]
        print(f"  ⚠️  DFS listing HTTP {e.code} ({directory}): {body}")
        return []
    except Exception as e:
        print(f"  ⚠️  DFS listing failed ({directory}): {e}")
        return []


def _is_delta_table_dir(ws_id, lh_id, directory):
    """Check whether a directory looks like a Delta table (has _delta_log/)."""
    content = onelake_read(ws_id, lh_id, f"{directory}/_delta_log/00000000000000000000.json")
    return content is not None


# Directories under Tables/ that are NOT schema names — skip during schema discovery
_NON_SCHEMA_DIRS = {"Files", "_delta_log", "_schemas", "__checkpoint", "_temporary", "TableMaintenance", "Tables"}


def _list_tables_recursive(ws_id, lh_id):
    """Recursive DFS listing to find ALL schemas and tables under Tables/.

    Falls back to this when flat (non-recursive) listing only returns system dirs.
    Returns list of (schema_name, table_name) tuples.
    """
    if not STORAGE_TOKEN:
        return []
    url = (
        f"https://onelake.dfs.fabric.microsoft.com"
        f"/{ws_id}/{lh_id}"
        f"?resource=filesystem&directory=Tables&recursive=true"
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
        # Find directories that contain _delta_log (these are tables)
        delta_dirs = set()
        all_dirs = set()
        for p in paths:
            name = p.get("name", "")
            is_dir = str(p.get("isDirectory", "false")).lower() == "true"
            if is_dir:
                all_dirs.add(name)
            if "/_delta_log" in name:
                # Parent of _delta_log is the table directory
                table_dir = name.rsplit("/_delta_log", 1)[0]
                delta_dirs.add(table_dir)

        results = []
        for td in sorted(delta_dirs):
            # Expected: Tables/{schema}/{table} or Tables/{table}
            parts = td.replace("Tables/", "").split("/")
            if len(parts) == 2:
                schema, table = parts
                if schema not in _NON_SCHEMA_DIRS and table not in _NON_SCHEMA_DIRS:
                    results.append((schema, table))
            elif len(parts) == 1 and parts[0] not in _NON_SCHEMA_DIRS:
                results.append(("", parts[0]))

        print(f"  Recursive DFS: {len(results)} table(s) found across {len(set(r[0] for r in results))} schema(s)")
        for schema, table in results:
            print(f"    {schema + '.' if schema else ''}{table}")
        return results
    except Exception as e:
        print(f"  ⚠️  Recursive DFS listing failed: {e}")
        return []


def list_all_schemas_and_tables(ws_id, lh_id):
    """Discover ALL schemas and their tables in a schema-enabled lakehouse.

    Returns dict: {schema_name: [table_name, ...]}
    Strategy: recursive DFS first (most reliable for non-standard schemas),
    then falls back to two-level flat DFS.
    """
    print(f"  Discovering all schemas and tables...")

    # Strategy 1: Recursive DFS (finds year_2017, year_2018, etc.)
    recursive_results = _list_tables_recursive(ws_id, lh_id)
    if recursive_results:
        schema_tables = {}
        for schema, table in recursive_results:
            s = schema if schema else "dbo"
            schema_tables.setdefault(s, []).append(table)
        total = sum(len(v) for v in schema_tables.values())
        print(f"  Recursive DFS: {total} table(s) in {len(schema_tables)} schema(s)")
        for s, tables in sorted(schema_tables.items()):
            print(f"    {s}: {tables}")
        return schema_tables

    # Strategy 2: Two-level flat DFS
    print(f"  Recursive DFS returned 0 -- trying two-level flat DFS...")
    schema_dirs = list_tables_via_dfs(ws_id, lh_id)
    schema_names = [
        sd["name"] for sd in schema_dirs
        if sd["name"] not in _NON_SCHEMA_DIRS and not sd["name"].startswith("_")
    ]
    if "dbo" not in schema_names:
        schema_names.append("dbo")

    schema_tables = {}
    for sname in sorted(schema_names):
        sub_tables = list_tables_via_dfs(ws_id, lh_id, f"Tables/{sname}")
        sub_tables = [
            t for t in sub_tables
            if t["name"] not in _NON_SCHEMA_DIRS and not t["name"].startswith("_")
        ]
        if sub_tables:
            schema_tables[sname] = [t["name"] for t in sub_tables]
            print(f"    {sname}: {[t['name'] for t in sub_tables]}")

    if schema_tables:
        total = sum(len(v) for v in schema_tables.values())
        print(f"  Flat DFS: {total} table(s) in {len(schema_tables)} schema(s)")
    else:
        print(f"  Flat DFS: 0 tables across {len(schema_names)} schemas")

    return schema_tables


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


def _parse_delta_log_schema(content):
    """Parse Delta transaction log NDJSON content and return column list."""
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
                return delta_schema_to_columns(schema_str)
    return []


# ── Entry point ────────────────────────────────────────────────────────────────
if not FABRIC_TOKEN or not WORKSPACE_ID:
    print("ERROR: FABRIC_TOKEN and WORKSPACE_ID are required")
    sys.exit(1)

if not STORAGE_TOKEN:
    print("WARNING: STORAGE_TOKEN not set -- Delta log reading will be skipped")
    print("   Schema discovery may be incomplete (table names only)")

print("=" * 72)
print(f"DISCOVERY: Scanning ALL lakehouses in workspace {WORKSPACE_ID}")
print("=" * 72)

# 1. List all lakehouses in the workspace
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
    candidates = list(lakehouses)

print(f"Found {len(candidates)} lakehouse(s): {[c['displayName'] for c in candidates]}")

# 2. Discover schemas and tables for EVERY lakehouse (no break)
all_lakehouses = []

for candidate in candidates:
    cid = candidate["id"]
    cname = candidate["displayName"]
    print(f"\n{'=' * 72}")
    print(f"  LAKEHOUSE: {cname}")
    print(f"  ID: {cid}")
    print(f"{'=' * 72}")

    lh_result = {
        "lakehouse_id": cid,
        "lakehouse_name": cname,
        "schemas_enabled": False,
        "schemas": {},
        "table_count": 0,
    }

    # Check if schema-enabled
    tables_check, err_code = fabric_get_detect_error(
        f"/workspaces/{WORKSPACE_ID}/lakehouses/{cid}/tables"
    )

    if err_code == "UnsupportedOperationForSchemasEnabledLakehouse":
        lh_result["schemas_enabled"] = True
        print(f"  Schema-enabled lakehouse -- discovering all schemas...")

        schema_tables = list_all_schemas_and_tables(WORKSPACE_ID, cid)

        for schema_name, table_names in sorted(schema_tables.items()):
            discovered = {}
            skipped = []
            for tname in table_names:
                delta_path = f"Tables/{schema_name}/{tname}/_delta_log/00000000000000000000.json"
                content = onelake_read(WORKSPACE_ID, cid, delta_path)
                if content is None:
                    print(f"    WARN {schema_name}.{tname}: cannot read Delta log")
                    discovered[tname] = {"columns": []}
                    skipped.append(tname)
                    continue
                cols = _parse_delta_log_schema(content)
                if cols:
                    discovered[tname] = {"columns": cols}
                    print(f"    OK   {schema_name}.{tname}: {len(cols)} columns")
                else:
                    print(f"    WARN {schema_name}.{tname}: no schema in Delta log")
                    discovered[tname] = {"columns": []}
                    skipped.append(tname)

            lh_result["schemas"][schema_name] = {"tables": discovered}
            lh_result["table_count"] += len(discovered)
            print(f"  Schema '{schema_name}': {len(discovered)} table(s), {len(skipped)} without column info")
    else:
        # Non-schema-enabled -- tables at top level
        tbl_list = tables_check.get("data", []) or tables_check.get("value", [])
        if not tbl_list:
            tbl_list = list_tables_via_dfs(WORKSPACE_ID, cid)

        discovered = {}
        skipped = []
        for t in tbl_list:
            tname = t.get("name", "")
            if not tname or tname in _NON_SCHEMA_DIRS or tname.startswith("_"):
                continue
            delta_path = f"Tables/{tname}/_delta_log/00000000000000000000.json"
            content = onelake_read(WORKSPACE_ID, cid, delta_path)
            if content is None:
                print(f"    WARN {tname}: cannot read Delta log")
                discovered[tname] = {"columns": []}
                skipped.append(tname)
                continue
            cols = _parse_delta_log_schema(content)
            if cols:
                discovered[tname] = {"columns": cols}
                print(f"    OK   {tname}: {len(cols)} columns")
            else:
                discovered[tname] = {"columns": []}
                skipped.append(tname)

        if discovered:
            lh_result["schemas"][""] = {"tables": discovered}
            lh_result["table_count"] = len(discovered)

    all_lakehouses.append(lh_result)
    print(f"\n  RESULT: {cname} -- {lh_result['table_count']} table(s) across {len(lh_result['schemas'])} schema(s)")

# 3. Summary
total_tables = sum(lh["table_count"] for lh in all_lakehouses)
total_schemas = sum(len(lh["schemas"]) for lh in all_lakehouses)
print(f"\n{'=' * 72}")
print(f"DISCOVERY COMPLETE")
print(f"  Lakehouses : {len(all_lakehouses)}")
print(f"  Schemas    : {total_schemas}")
print(f"  Tables     : {total_tables}")
for lh in all_lakehouses:
    schemas_str = ", ".join(lh["schemas"].keys()) if lh["schemas"] else "(none)"
    print(f"    {lh['lakehouse_name']}: {lh['table_count']} tables ({schemas_str})")
print(f"{'=' * 72}")

# 4. Write output
output = {
    "workspace_id": WORKSPACE_ID,
    "total_table_count": total_tables,
    "lakehouses": all_lakehouses,
}

with open(OUT_FILE, "w") as f:
    json.dump(output, f, indent=2)

print(f"Written -> {OUT_FILE}")
