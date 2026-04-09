# Databricks notebook source

# MAGIC %md
# MAGIC # 06 — Compression & Storage Analyzer
# MAGIC **Digital Realty — Delta Table Storage Diagnostics**
# MAGIC
# MAGIC Analyzes file distribution, compression ratios, and identifies
# MAGIC storage optimization opportunities (small file consolidation, ZORDER).
# MAGIC
# MAGIC Part of the medallion pipeline diagnostics suite.
# MAGIC Run after ingestion/transformation notebooks to assess storage health.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

import json
from datetime import datetime
from pyspark.sql import functions as F
from pyspark.sql.types import StructType

LAKEHOUSE_NAME = "DL_Lakehouse"

TABLES = [
    "bronze_datacenters",
    "bronze_power_capacity",
    "bronze_customer_deployments",
    "silver_datacenter_capacity",
    "silver_customer_analytics",
    "silver_power_efficiency",
    "silver_regional_summary",
]

SMALL_FILE_THRESHOLD_MB = 32   # files smaller than this are "small"
TARGET_FILE_SIZE_MB = 128

BYTES_PER_MB = 1024 * 1024

report_data = {}

print(f"Lakehouse:              {LAKEHOUSE_NAME}")
print(f"Tables to analyze:      {len(TABLES)}")
print(f"Small file threshold:   {SMALL_FILE_THRESHOLD_MB} MB")
print(f"Target file size:       {TARGET_FILE_SIZE_MB} MB")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Analyze Each Table — Detail & History

# COMMAND ----------

table_details = {}
table_histories = {}

for table in TABLES:
    try:
        detail_df = spark.sql(f"DESCRIBE DETAIL {table}")
        detail_row = detail_df.collect()[0]

        table_details[table] = {
            "location": detail_row["location"],
            "numFiles": int(detail_row["numFiles"]),
            "sizeInBytes": int(detail_row["sizeInBytes"]),
            "sizeMB": round(int(detail_row["sizeInBytes"]) / BYTES_PER_MB, 2),
            "partitionColumns": list(detail_row["partitionColumns"]) if detail_row["partitionColumns"] else [],
            "format": detail_row["format"],
            "lastModified": str(detail_row["lastModified"]),
        }

        history_df = spark.sql(f"DESCRIBE HISTORY {table} LIMIT 5")
        history_rows = history_df.select(
            "version", "timestamp", "operation", "operationMetrics"
        ).collect()

        table_histories[table] = [
            {
                "version": row["version"],
                "timestamp": str(row["timestamp"]),
                "operation": row["operation"],
            }
            for row in history_rows
        ]

        print(f"✅ {table}: {table_details[table]['numFiles']} files, "
              f"{table_details[table]['sizeMB']} MB")

    except Exception as e:
        print(f"❌ {table}: {e}")
        table_details[table] = None
        table_histories[table] = None

# Read Delta logs to count files per partition where applicable
for table, detail in table_details.items():
    if detail is None:
        continue
    location = detail["location"]
    try:
        from delta.tables import DeltaTable
        dt = DeltaTable.forPath(spark, location)
        file_df = dt.detail().select("numFiles").collect()[0]
        detail["logFileCount"] = int(file_df["numFiles"])
    except Exception:
        detail["logFileCount"] = detail["numFiles"]

# COMMAND ----------

# MAGIC %md
# MAGIC ## File Distribution Report

# COMMAND ----------

def file_size_bucket(size_mb):
    if size_mb < 1:
        return "< 1 MB"
    elif size_mb < SMALL_FILE_THRESHOLD_MB:
        return f"1-{SMALL_FILE_THRESHOLD_MB} MB"
    elif size_mb <= TARGET_FILE_SIZE_MB:
        return f"{SMALL_FILE_THRESHOLD_MB}-{TARGET_FILE_SIZE_MB} MB"
    else:
        return f"> {TARGET_FILE_SIZE_MB} MB"


def classify_file_distribution(num_files, total_size_mb):
    """Estimate file size distribution from aggregate stats."""
    if num_files == 0:
        return {"< 1 MB": 0, f"1-{SMALL_FILE_THRESHOLD_MB} MB": 0,
                f"{SMALL_FILE_THRESHOLD_MB}-{TARGET_FILE_SIZE_MB} MB": 0,
                f"> {TARGET_FILE_SIZE_MB} MB": 0}

    avg_size = total_size_mb / num_files
    buckets = {
        "< 1 MB": 0,
        f"1-{SMALL_FILE_THRESHOLD_MB} MB": 0,
        f"{SMALL_FILE_THRESHOLD_MB}-{TARGET_FILE_SIZE_MB} MB": 0,
        f"> {TARGET_FILE_SIZE_MB} MB": 0,
    }

    try:
        location = table_details.get(table, {}).get("location", "")
        if location:
            files_df = (
                spark.read.format("delta")
                .load(location)
                .inputFiles()
            )
            # inputFiles returns a list of file paths — read sizes via Hadoop FS
            hadoop_conf = spark._jsc.hadoopConfiguration()
            fs_class = spark._jvm.org.apache.hadoop.fs.FileSystem
            for fpath in files_df:
                path_obj = spark._jvm.org.apache.hadoop.fs.Path(fpath)
                fs = path_obj.getFileSystem(hadoop_conf)
                file_status = fs.getFileStatus(path_obj)
                fsize_mb = file_status.getLen() / BYTES_PER_MB
                bucket = file_size_bucket(fsize_mb)
                buckets[bucket] = buckets.get(bucket, 0) + 1
            return buckets
    except Exception:
        pass

    # Fallback: estimate distribution from average file size
    bucket = file_size_bucket(avg_size)
    buckets[bucket] = num_files
    return buckets


SEVERITY_ICONS = {
    "< 1 MB": "🔴",
    f"1-{SMALL_FILE_THRESHOLD_MB} MB": "🟡",
    f"{SMALL_FILE_THRESHOLD_MB}-{TARGET_FILE_SIZE_MB} MB": "🟢",
    f"> {TARGET_FILE_SIZE_MB} MB": "🟢",
}

small_file_tables = []

for table in TABLES:
    detail = table_details.get(table)
    if detail is None:
        print(f"\nTABLE: {table}\n  ⚠️  Skipped — could not read detail\n")
        continue

    num_files = detail["numFiles"]
    size_mb = detail["sizeMB"]
    avg_file_mb = round(size_mb / num_files, 2) if num_files > 0 else 0
    partitions = detail["partitionColumns"] or "None"
    last_modified = detail["lastModified"]
    fmt = detail["format"]

    avg_flag = "  ⚠️ SMALL FILES" if avg_file_mb < SMALL_FILE_THRESHOLD_MB and num_files > 1 else ""
    if avg_flag:
        small_file_tables.append(table)

    buckets = classify_file_distribution(num_files, size_mb)
    target_files = max(1, int(size_mb / TARGET_FILE_SIZE_MB) + (1 if size_mb % TARGET_FILE_SIZE_MB > 0 else 0))

    print(f"\nTABLE: {table}")
    print(f"  Total Size:     {size_mb} MB")
    print(f"  Num Files:      {num_files}")
    print(f"  Avg File Size:  {avg_file_mb} MB{avg_flag}")
    print(f"  Partitions:     {partitions}")
    print(f"  Last Modified:  {last_modified}")
    print(f"  Format:         {fmt}")
    print()
    print(f"  File Size Distribution:")
    for bucket_name in ["< 1 MB", f"1-{SMALL_FILE_THRESHOLD_MB} MB",
                         f"{SMALL_FILE_THRESHOLD_MB}-{TARGET_FILE_SIZE_MB} MB",
                         f"> {TARGET_FILE_SIZE_MB} MB"]:
        count = buckets.get(bucket_name, 0)
        pct = round(count / num_files * 100) if num_files > 0 else 0
        icon = SEVERITY_ICONS.get(bucket_name, "")
        print(f"    {bucket_name:>12s}:  {count:>4d} files ({pct:>3d}%)  {icon if count > 0 else ''}")

    if num_files > target_files:
        print(f"\n  Recommendation: Run OPTIMIZE to consolidate "
              f"{num_files} files → ~{target_files} file(s)")
    else:
        print(f"\n  ✅ File count is healthy ({num_files} files)")

    report_data[table] = {
        "numFiles": num_files,
        "sizeMB": size_mb,
        "avgFileMB": avg_file_mb,
        "partitions": partitions if isinstance(partitions, list) else [],
        "smallFiles": bool(avg_flag),
        "distribution": buckets,
    }

# COMMAND ----------

# MAGIC %md
# MAGIC ## Compression Analysis

# COMMAND ----------

compression_results = {}

for table in TABLES:
    detail = table_details.get(table)
    if detail is None:
        continue

    try:
        df = spark.table(table)
        row_count = df.count()
        col_count = len(df.columns)

        # Estimate uncompressed size from schema:
        # STRING ~50 bytes avg, DOUBLE/FLOAT 8, INT/LONG 8, TIMESTAMP 8, BOOLEAN 1
        TYPE_SIZE_ESTIMATES = {
            "string": 50,
            "double": 8,
            "float": 4,
            "int": 4,
            "bigint": 8,
            "long": 8,
            "timestamp": 8,
            "date": 4,
            "boolean": 1,
            "decimal": 16,
            "short": 2,
        }

        avg_row_bytes = 0
        for field in df.schema.fields:
            type_name = field.dataType.simpleString().lower()
            # Handle parameterized types like decimal(10,2)
            base_type = type_name.split("(")[0]
            avg_row_bytes += TYPE_SIZE_ESTIMATES.get(base_type, 32)

        estimated_raw_bytes = row_count * avg_row_bytes
        estimated_raw_mb = round(estimated_raw_bytes / BYTES_PER_MB, 2)
        actual_mb = detail["sizeMB"]
        compression_ratio = round(estimated_raw_mb / actual_mb, 1) if actual_mb > 0 else 0

        poor = compression_ratio < 3.0 and actual_mb > 1
        flag = "  🔴 POOR COMPRESSION" if poor else "  🟢"

        print(f"\n{table}:")
        print(f"  Rows:                  {row_count:,}")
        print(f"  Columns:               {col_count}")
        print(f"  Est. Raw Size:         {estimated_raw_mb} MB")
        print(f"  Actual Delta Size:     {actual_mb} MB")
        print(f"  Compression Ratio:     {compression_ratio}x{flag}")

        compression_results[table] = {
            "rowCount": row_count,
            "colCount": col_count,
            "estimatedRawMB": estimated_raw_mb,
            "actualDeltaMB": actual_mb,
            "compressionRatio": compression_ratio,
            "poorCompression": poor,
        }

    except Exception as e:
        print(f"\n{table}: ❌ {e}")
        compression_results[table] = None

# COMMAND ----------

# MAGIC %md
# MAGIC ## Column-Type Storage Breakdown

# COMMAND ----------

for table in TABLES:
    detail = table_details.get(table)
    if detail is None:
        continue

    try:
        df = spark.table(table)
        schema = df.schema

        type_counts = {}
        for field in schema.fields:
            type_name = field.dataType.simpleString().upper().split("(")[0]
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        total_cols = len(schema.fields)

        TYPE_COMPRESSION_NOTES = {
            "STRING": "typically low compression for high-cardinality",
            "DOUBLE": "excellent compression (dictionary encoding)",
            "FLOAT": "excellent compression (dictionary encoding)",
            "INT": "excellent compression",
            "BIGINT": "excellent compression",
            "LONG": "excellent compression",
            "TIMESTAMP": "good compression",
            "DATE": "good compression",
            "BOOLEAN": "excellent compression (1 bit effective)",
            "DECIMAL": "good compression",
            "SHORT": "excellent compression",
        }

        print(f"\n{table} Column Type Distribution:")
        for type_name, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            pct = round(count / total_cols * 100)
            col_word = "column" if count == 1 else "columns"
            note = TYPE_COMPRESSION_NOTES.get(type_name, "")
            note_str = f" — {note}" if note else ""
            print(f"  {type_name:<12s} {count:>2d} {col_word:<8s} ({pct:>2d}%){note_str}")

        if table in report_data:
            report_data[table]["columnTypes"] = type_counts

    except Exception as e:
        print(f"\n{table}: ❌ {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## OPTIMIZE Recommendations

# COMMAND ----------

# Columns commonly used for filtering in Digital Realty workloads
ZORDER_CANDIDATES = {
    "bronze_datacenters": [],
    "bronze_power_capacity": ["datacenter_id", "measurement_date"],
    "bronze_customer_deployments": ["datacenter_id"],
    "silver_datacenter_capacity": ["datacenter_id", "region"],
    "silver_customer_analytics": ["datacenter_id", "customer_id"],
    "silver_power_efficiency": ["datacenter_id", "measurement_date"],
    "silver_regional_summary": ["region"],
}

print("-- ==============================================")
print("-- Recommended OPTIMIZE Commands")
print("-- ==============================================")
print()

optimize_commands = []
skip_count = 0

for table in TABLES:
    detail = table_details.get(table)
    if detail is None:
        continue

    num_files = detail["numFiles"]
    size_mb = detail["sizeMB"]
    avg_file_mb = round(size_mb / num_files, 2) if num_files > 0 else 0

    needs_optimize = (
        (avg_file_mb < SMALL_FILE_THRESHOLD_MB and num_files > 1)
        or num_files > max(1, int(size_mb / TARGET_FILE_SIZE_MB) + 1) * 2
    )

    zorder_cols = ZORDER_CANDIDATES.get(table, [])
    # Validate that ZORDER columns actually exist in the table
    try:
        actual_cols = [f.name for f in spark.table(table).schema.fields]
        zorder_cols = [c for c in zorder_cols if c in actual_cols]
    except Exception:
        zorder_cols = []

    if needs_optimize:
        if zorder_cols:
            cmd = f"OPTIMIZE {table} ZORDER BY ({', '.join(zorder_cols)});"
        else:
            cmd = f"OPTIMIZE {table};"
        optimize_commands.append(cmd)
        print(cmd)
    else:
        skip_count += 1
        print(f"-- {table}: OK ({num_files} files, good size distribution)")

print()
print(f"-- Total: {len(optimize_commands)} tables need OPTIMIZE, "
      f"{skip_count} tables are healthy")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary Report

# COMMAND ----------

total_tables = len(TABLES)
total_storage_mb = sum(
    d["sizeMB"] for d in table_details.values() if d is not None
)
small_file_count = len(small_file_tables)
poor_compression_count = sum(
    1 for r in compression_results.values()
    if r is not None and r.get("poorCompression")
)

# Estimate savings: small-file tables could reclaim ~25% overhead from file metadata
estimated_savings_mb = round(
    sum(
        table_details[t]["sizeMB"] * 0.25
        for t in small_file_tables
        if table_details.get(t) is not None
    ),
    1,
)

status = "✅ HEALTHY" if small_file_count == 0 and poor_compression_count == 0 else "⚠️ OPTIMIZATION RECOMMENDED"

print("=" * 50)
print("  COMPRESSION & STORAGE REPORT")
print("=" * 50)
print(f"  Tables Analyzed:     {total_tables}")
print(f"  Total Storage:       {total_storage_mb} MB")
print(f"  Small File Tables:   {small_file_count} of {total_tables} "
      f"({round(small_file_count / total_tables * 100)}%)  "
      f"{'⚠️' if small_file_count > 0 else '✅'}")
print(f"  Poor Compression:    {poor_compression_count} of {total_tables} "
      f"({round(poor_compression_count / total_tables * 100)}%)")
print(f"  Estimated Savings:   ~{estimated_savings_mb} MB after OPTIMIZE")
print()
print(f"  STATUS: {status}")
print()
print("  Action Items:")

action_items = []
if small_file_count > 0:
    item = f"Run OPTIMIZE on {small_file_count} tables with small file issues"
    action_items.append(item)
    print(f"    1. {item}")

action_items.append("Add ZORDER on frequently filtered columns")
print(f"    {len(action_items)}. Add ZORDER on frequently filtered columns")

if any(
    r is not None and r.get("poorCompression")
    for r in compression_results.values()
):
    poor_tables = [
        t for t, r in compression_results.items()
        if r is not None and r.get("poorCompression")
    ]
    item = f"Review STRING columns in {', '.join(poor_tables)} for encoding hints"
    action_items.append(item)
    print(f"    {len(action_items)}. {item}")

action_items.append("Schedule weekly OPTIMIZE via pipeline")
print(f"    {len(action_items)}. Schedule weekly OPTIMIZE via pipeline")
print("=" * 50)

# Save JSON report for pipeline consumption
summary_report = {
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "lakehouse": LAKEHOUSE_NAME,
    "tables_analyzed": total_tables,
    "total_storage_mb": total_storage_mb,
    "small_file_tables": small_file_count,
    "poor_compression_tables": poor_compression_count,
    "estimated_savings_mb": estimated_savings_mb,
    "status": "OPTIMIZATION_RECOMMENDED" if small_file_count > 0 or poor_compression_count > 0 else "HEALTHY",
    "action_items": action_items,
    "optimize_commands": optimize_commands,
    "tables": {},
}

for table in TABLES:
    entry = {}
    if table_details.get(table):
        entry["detail"] = table_details[table]
    if compression_results.get(table):
        entry["compression"] = compression_results[table]
    if table in report_data:
        entry["distribution"] = report_data[table]
    if table_histories.get(table):
        entry["recentHistory"] = table_histories[table]
    summary_report["tables"][table] = entry

report_json = json.dumps(summary_report, indent=2, default=str)

# Write to lakehouse Files area for downstream pipeline consumption
report_path = f"Files/diagnostics/compression_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
try:
    dbutils.fs.put(report_path, report_json, overwrite=True)
    print(f"\n📄 Report saved to: {report_path}")
except Exception:
    # Fallback: write via Spark
    report_rdd = spark.sparkContext.parallelize([report_json])
    report_rdd.saveAsTextFile(report_path + "_dir")
    print(f"\n📄 Report saved to: {report_path}_dir")

print("\n✅ Compression & Storage Analysis complete.")
