# Databricks notebook source
# MAGIC %md
# MAGIC # Migration V004 — Remove Bloat Columns
# MAGIC **Digital Realty — Performance Optimization**
# MAGIC
# MAGIC Removes high-cardinality STRING columns identified by the Memory Analyzer
# MAGIC as consuming excessive memory with minimal analytical value.
# MAGIC
# MAGIC **Columns removed:**
# MAGIC - `silver_datacenters.datacenter_description` (avg 340 chars, 98% unique → ~145 MB)
# MAGIC - `silver_datacenters.facility_notes` (avg 280 chars, 85% unique → ~95 MB)
# MAGIC - `silver_datacenters.raw_api_response` (avg 2.1 KB, 100% unique → ~140 MB)
# MAGIC - `silver_customer_deployments.contract_notes` (avg 450 chars, 92% unique → ~210 MB)
# MAGIC - `silver_customer_deployments.internal_etl_id` (UUID, 100% unique → ~12 MB)
# MAGIC - `silver_customer_deployments.source_hash` (SHA256, 100% unique → ~18 MB)
# MAGIC
# MAGIC **Expected memory savings:** ~550 MB (62% reduction)

# COMMAND ----------

MIGRATION_VERSION = "V004"
MIGRATION_NAME = "remove_bloat_columns"

# Columns to remove per table
BLOAT_COLUMNS = {
    "silver_datacenters": [
        "datacenter_description",
        "facility_notes", 
        "raw_api_response"
    ],
    "silver_customer_deployments": [
        "contract_notes",
        "internal_etl_id",
        "source_hash"
    ]
}

print(f"Migration {MIGRATION_VERSION}: {MIGRATION_NAME}")
print(f"Tables affected: {len(BLOAT_COLUMNS)}")
total_cols = sum(len(v) for v in BLOAT_COLUMNS.values())
print(f"Columns to remove: {total_cols}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Pre-Migration Snapshot

# COMMAND ----------

print("=" * 60)
print("PRE-MIGRATION SNAPSHOT")
print("=" * 60)

for table, columns in BLOAT_COLUMNS.items():
    try:
        df = spark.table(table)
        current_cols = df.columns
        print(f"\n{table}:")
        print(f"  Current columns: {len(current_cols)}")
        
        for col in columns:
            if col in current_cols:
                # Sample cardinality
                distinct_count = df.select(col).distinct().count()
                row_count = df.count()
                cardinality_pct = (distinct_count / row_count * 100) if row_count > 0 else 0
                print(f"  - {col}: {distinct_count:,} distinct values ({cardinality_pct:.0f}% cardinality)")
            else:
                print(f"  - {col}: NOT FOUND (already removed or never existed)")
    except Exception as e:
        print(f"  {table}: Error — {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Remove Bloat Columns

# COMMAND ----------

print("=" * 60)
print("REMOVING BLOAT COLUMNS")
print("=" * 60)

removed = 0
skipped = 0

for table, columns in BLOAT_COLUMNS.items():
    print(f"\n--- {table} ---")
    try:
        df = spark.table(table)
        current_cols = df.columns
        
        for col in columns:
            if col in current_cols:
                spark.sql(f"ALTER TABLE {table} DROP COLUMN {col}")
                print(f"  ✓ Dropped: {col}")
                removed += 1
            else:
                print(f"  - Skipped: {col} (not present)")
                skipped += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")

print(f"\nRemoved: {removed} | Skipped: {skipped}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Post-Migration Validation

# COMMAND ----------

print("=" * 60)
print("POST-MIGRATION VALIDATION")
print("=" * 60)

all_clean = True
for table, columns in BLOAT_COLUMNS.items():
    df = spark.table(table)
    remaining = [c for c in columns if c in df.columns]
    if remaining:
        print(f"  ✗ {table}: Still has bloat columns: {remaining}")
        all_clean = False
    else:
        print(f"  ✓ {table}: Clean ({len(df.columns)} columns)")

print(f"\n{'=' * 60}")
if all_clean:
    print(f"Migration {MIGRATION_VERSION} complete: All bloat columns removed")
    print(f"Expected memory savings: ~550 MB")
    print(f"STATUS: SUCCESS")
else:
    print(f"Migration {MIGRATION_VERSION}: PARTIAL — some columns remain")
    print(f"STATUS: NEEDS REVIEW")
