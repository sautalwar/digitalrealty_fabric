# Databricks notebook source

# MAGIC %md
# MAGIC # 05 — Semantic Model Memory Analyzer
# MAGIC
# MAGIC Analyzes VertiPaq memory consumption for the Digital Realty capacity semantic model.
# MAGIC Queries DMVs for column-level and table-level storage statistics, flags bloat,
# MAGIC and produces a pass/fail assessment against a configurable memory budget.
# MAGIC
# MAGIC **Medallion layer:** Post-Gold (operational diagnostics)
# MAGIC
# MAGIC | Parameter | Default | Description |
# MAGIC |---|---|---|
# MAGIC | WORKSPACE_NAME | DigitalRealty_Dev | Target Fabric workspace |
# MAGIC | DATASET_NAME | DigitalRealty_Capacity | Semantic model to analyze |
# MAGIC | MEMORY_BUDGET_MB | 500 | Alert threshold in megabytes |

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1 — Configuration

# COMMAND ----------

WORKSPACE_NAME = "DigitalRealty_Dev"
DATASET_NAME = "DigitalRealty_Capacity"
MEMORY_BUDGET_MB = 500

TABLE_ALERT_MB = 100  # flag individual tables above this size
COLUMN_ALERT_MB = 50  # flag individual columns above this size
HIGH_CARDINALITY_THRESHOLD = 100_000
MEDIUM_CARDINALITY_THRESHOLD = 50_000

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2 — Install & Import Dependencies

# COMMAND ----------

# MAGIC %pip install semantic-link-labs --quiet

# COMMAND ----------

import sempy_labs
import sempy.fabric as fabric
import pandas as pd
import json
from datetime import datetime, timezone

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3 — Query VertiPaq Storage via DMVs

# COMMAND ----------

def query_dmv(dataset: str, dmv: str, workspace: str | None = None) -> pd.DataFrame:
    """Execute a DMV query against a semantic model and return a DataFrame."""
    dax = f"SELECT * FROM {dmv}"
    return fabric.evaluate_dax(dataset=dataset, dax_string=dax, workspace=workspace)


print("╔══════════════════════════════════════════════════════════════╗")
print("║  Querying VertiPaq DMVs — DISCOVER_STORAGE_TABLE_COLUMNS   ║")
print("╚══════════════════════════════════════════════════════════════╝")

df_columns = query_dmv(
    dataset=DATASET_NAME,
    dmv="$SYSTEM.DISCOVER_STORAGE_TABLE_COLUMNS",
    workspace=WORKSPACE_NAME,
)

print(f"  → Retrieved {len(df_columns)} column storage records\n")

print("╔══════════════════════════════════════════════════════════════╗")
print("║  Querying VertiPaq DMVs — DISCOVER_STORAGE_TABLES          ║")
print("╚══════════════════════════════════════════════════════════════╝")

df_tables = query_dmv(
    dataset=DATASET_NAME,
    dmv="$SYSTEM.DISCOVER_STORAGE_TABLES",
    workspace=WORKSPACE_NAME,
)

print(f"  → Retrieved {len(df_tables)} table storage records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4 — Table-Level Memory Report

# COMMAND ----------

def bytes_to_mb(b: float) -> float:
    return round(b / (1024 * 1024), 2)


# Normalise column names to lowercase for resilience across API versions
df_columns.columns = [c.strip().lower() for c in df_columns.columns]
df_tables.columns = [c.strip().lower() for c in df_tables.columns]

# Build table-level summary from the column-level data
dict_size_col = "dictionary_size" if "dictionary_size" in df_columns.columns else "DICTIONARY_SIZE"
data_size_col = "column_data_size" if "column_data_size" in df_columns.columns else "COLUMN_DATA_SIZE"

df_columns["total_bytes"] = df_columns.get("dictionary_size", 0) + df_columns.get("column_data_size", 0)
df_columns["total_mb"] = df_columns["total_bytes"].apply(bytes_to_mb)

table_summary = (
    df_columns.groupby("table_name")
    .agg(
        total_memory_bytes=("total_bytes", "sum"),
        column_count=("column_name", "nunique"),
        max_row_count=("column_cardinality", "max"),
    )
    .reset_index()
)
table_summary["total_memory_mb"] = table_summary["total_memory_bytes"].apply(bytes_to_mb)
table_summary = table_summary.sort_values("total_memory_mb", ascending=False).reset_index(drop=True)

print("╔══════════════════════════════════════════════════════════════════════════╗")
print("║                     TABLE-LEVEL MEMORY REPORT                          ║")
print("╠══════════════════════════════════════════════════════════════════════════╣")
print(f"║  {'Table':<35} {'Memory (MB)':>12} {'Rows':>12} {'Cols':>6} {'Flag':>6} ║")
print("╠══════════════════════════════════════════════════════════════════════════╣")

for _, row in table_summary.iterrows():
    flag = "🔴" if row["total_memory_mb"] > TABLE_ALERT_MB else "  "
    name = row["table_name"][:35]
    print(
        f"║  {name:<35} {row['total_memory_mb']:>10.2f}   "
        f"{int(row['max_row_count']):>10,}   {int(row['column_count']):>4}   {flag:<4} ║"
    )

print("╠══════════════════════════════════════════════════════════════════════════╣")
grand_total_mb = table_summary["total_memory_mb"].sum()
print(f"║  {'TOTAL':<35} {grand_total_mb:>10.2f}{'':>30} ║")
print("╚══════════════════════════════════════════════════════════════════════════╝")
print(f"\n  🔴 = table exceeds {TABLE_ALERT_MB} MB threshold")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5 — Column-Level Memory Report

# COMMAND ----------

df_columns["dictionary_mb"] = df_columns.get("dictionary_size", pd.Series(0)).apply(bytes_to_mb)
df_columns["data_mb"] = df_columns.get("column_data_size", pd.Series(0)).apply(bytes_to_mb)
df_columns["cardinality"] = df_columns.get("column_cardinality", pd.Series(0)).astype(int)

# Estimate uncompressed size: cardinality * avg_width or row_count * type_width
# Use a simple heuristic: 8 bytes per numeric value, cardinality * 50 for strings
df_columns["est_uncompressed"] = df_columns.apply(
    lambda r: r["cardinality"] * 50 if "str" in str(r.get("column_type", "")).lower() else r["cardinality"] * 8,
    axis=1,
)
df_columns["compression_ratio"] = df_columns.apply(
    lambda r: round(r["est_uncompressed"] / r["total_bytes"], 1) if r["total_bytes"] > 0 else 0.0,
    axis=1,
)

print("╔══════════════════════════════════════════════════════════════════════════════════════╗")
print("║                          COLUMN-LEVEL MEMORY REPORT                                ║")
print("╚══════════════════════════════════════════════════════════════════════════════════════╝\n")

for table_name in table_summary["table_name"]:
    subset = df_columns[df_columns["table_name"] == table_name].sort_values("total_mb", ascending=False)
    tbl_mem = subset["total_mb"].sum()
    print(f"  ┌──────────────────────────────────────────────────────────────────────────────┐")
    print(f"  │  📊 {table_name:<40} Total: {tbl_mem:>8.2f} MB            │")
    print(f"  ├───────────────────────────┬──────────┬──────────┬──────────┬───────┬─────────┤")
    print(f"  │ {'Column':<25} │ {'Dict MB':>8} │ {'Data MB':>8} │ {'Total MB':>8} │ {'Card.':>5} │ {'Ratio':>7} │")
    print(f"  ├───────────────────────────┼──────────┼──────────┼──────────┼───────┼─────────┤")

    for _, col in subset.iterrows():
        col_name = str(col.get("column_name", ""))[:25]
        card = int(col["cardinality"])
        col_type = str(col.get("column_type", "")).lower()

        flag = ""
        if "str" in col_type and card > HIGH_CARDINALITY_THRESHOLD:
            flag = " 🔴"
        elif col["total_mb"] > COLUMN_ALERT_MB:
            flag = " 🟡"

        print(
            f"  │ {col_name:<25} │ {col['dictionary_mb']:>8.2f} │ {col['data_mb']:>8.2f} │ "
            f"{col['total_mb']:>8.2f} │ {card:>5} │ {col['compression_ratio']:>6.1f}x │{flag}"
        )

    print(f"  └───────────────────────────┴──────────┴──────────┴──────────┴───────┴─────────┘\n")

print("  Legend:  🔴 High-cardinality STRING (>{:,} distinct)   🟡 Column >{} MB".format(
    HIGH_CARDINALITY_THRESHOLD, COLUMN_ALERT_MB
))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6 — Top 10 Memory Consumers with Recommendations

# COMMAND ----------

def recommend(row: pd.Series) -> str:
    """Return an optimisation recommendation based on column characteristics."""
    col_type = str(row.get("column_type", "")).lower()
    card = int(row["cardinality"])

    if "str" in col_type and card > HIGH_CARDINALITY_THRESHOLD:
        return "Consider removing or hashing — high-cardinality text kills compression"
    if "str" in col_type and card > MEDIUM_CARDINALITY_THRESHOLD:
        return "Review necessity — may benefit from categorization"
    if row["total_mb"] > COLUMN_ALERT_MB:
        return "Large footprint — verify column is used in measures/relationships"
    return "Candidate for removal — not referenced in model"


top10 = df_columns.nlargest(10, "total_mb").copy()
top10["recommendation"] = top10.apply(recommend, axis=1)

print("╔══════════════════════════════════════════════════════════════════════════════════════╗")
print("║                    TOP 10 MEMORY CONSUMERS — RECOMMENDATIONS                       ║")
print("╚══════════════════════════════════════════════════════════════════════════════════════╝\n")

for rank, (_, r) in enumerate(top10.iterrows(), 1):
    print(f"  ┌─ #{rank} ─────────────────────────────────────────────────────────────────────┐")
    print(f"  │  Table:       {str(r['table_name']):<60}  │")
    print(f"  │  Column:      {str(r.get('column_name', '')):<60}  │")
    print(f"  │  Type:        {str(r.get('column_type', 'N/A')):<60}  │")
    print(f"  │  Cardinality: {int(r['cardinality']):>10,}{'':<50}  │")
    print(f"  │  Dict Size:   {r['dictionary_mb']:>8.2f} MB{'':<52}  │")
    print(f"  │  Data Size:   {r['data_mb']:>8.2f} MB{'':<52}  │")
    print(f"  │  TOTAL:       {r['total_mb']:>8.2f} MB{'':<52}  │")
    print(f"  │{'':─<77}│")
    print(f"  │  💡 {r['recommendation']:<72} │")
    print(f"  └{'':─<77}┘\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7 — Before / After Optimization Comparison (Simulated)

# COMMAND ----------

# Simulated baseline and projected values for the Digital Realty model.
# In a live run, replace with actual pre/post measurements.

before = {
    "silver_datacenters":     {"mb": 245, "note": "includes description, notes, raw_api columns"},
    "silver_customer_deploy": {"mb": 428, "note": "includes contract_notes, etl_id, hash columns"},
    "silver_capacity_trends": {"mb":  92, "note": ""},
    "_Measures (calc cols)":  {"mb": 125, "note": ""},
}

after = {
    "silver_datacenters":     {"mb":  98, "note": "bloat columns removed"},
    "silver_customer_deploy": {"mb": 156, "note": "bloat columns + calc cols removed"},
    "silver_capacity_trends": {"mb":  82, "note": "no changes needed"},
    "_Measures":              {"mb":   4, "note": "measures only, no materialization"},
}

before_total = sum(v["mb"] for v in before.values())
after_total = sum(v["mb"] for v in after.values())
savings = before_total - after_total
pct = round(savings / before_total * 100)

print("╔══════════════════════════════════════════════════════════════════════════════════════╗")
print("║               BEFORE / AFTER OPTIMIZATION COMPARISON                               ║")
print("╚══════════════════════════════════════════════════════════════════════════════════════╝\n")

print("  BEFORE optimization:")
for name, v in before.items():
    note = f"  ({v['note']})" if v["note"] else ""
    print(f"    {name + ':':<30} {v['mb']:>5} MB{note}")
print(f"    {'TOTAL:':<30} {before_total:>5} MB")

print()
print("  AFTER optimization (projected):")
for name, v in after.items():
    note = f"  ({v['note']})" if v["note"] else ""
    print(f"    {name + ':':<30} {v['mb']:>5} MB{note}")
print(f"    {'TOTAL:':<30} {after_total:>5} MB")

print()
print(f"  ┌──────────────────────────────────────────────────────────────┐")
print(f"  │  💰 SAVINGS: {savings} MB  ({pct}% reduction)                          │")
print(f"  └──────────────────────────────────────────────────────────────┘")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8 — Summary & JSON Report

# COMMAND ----------

budget_pass = grand_total_mb <= MEMORY_BUDGET_MB
status = "✅ PASS" if budget_pass else "❌ FAIL"
timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

print("╔══════════════════════════════════════════════════════════════╗")
print("║                   MEMORY BUDGET ASSESSMENT                 ║")
print("╠══════════════════════════════════════════════════════════════╣")
print(f"║  Semantic Model:   {DATASET_NAME:<39}║")
print(f"║  Workspace:        {WORKSPACE_NAME:<39}║")
print(f"║  Timestamp:        {timestamp:<39}║")
print(f"║  Total Memory:     {grand_total_mb:>8.2f} MB{'':<29}║")
print(f"║  Budget Threshold: {MEMORY_BUDGET_MB:>8} MB{'':<29}║")
print(f"║  Status:           {status:<39}║")
print("╚══════════════════════════════════════════════════════════════╝")

if not budget_pass:
    over = grand_total_mb - MEMORY_BUDGET_MB
    print(f"\n  ⚠️  Model exceeds budget by {over:.2f} MB — review Top 10 recommendations above.")

# Build JSON report for downstream pipeline consumption
report = {
    "notebook": "05_memory_analyzer",
    "timestamp": timestamp,
    "workspace": WORKSPACE_NAME,
    "dataset": DATASET_NAME,
    "memory_budget_mb": MEMORY_BUDGET_MB,
    "total_memory_mb": round(grand_total_mb, 2),
    "budget_pass": budget_pass,
    "table_count": len(table_summary),
    "column_count": len(df_columns),
    "tables_over_threshold": table_summary[table_summary["total_memory_mb"] > TABLE_ALERT_MB]["table_name"].tolist(),
    "top_consumers": [
        {
            "table": r["table_name"],
            "column": r.get("column_name", ""),
            "total_mb": round(r["total_mb"], 2),
            "cardinality": int(r["cardinality"]),
            "recommendation": r["recommendation"],
        }
        for _, r in top10.iterrows()
    ],
    "before_after": {
        "before_total_mb": before_total,
        "after_total_mb": after_total,
        "savings_mb": savings,
        "savings_pct": pct,
    },
}

print("\n── JSON Report (for pipeline consumption) " + "─" * 38)
print(json.dumps(report, indent=2))
