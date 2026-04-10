# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Data Ingestion (Bronze Layer)
# MAGIC **Digital Realty - Lakehouse Schema Evolution Demo**
# MAGIC
# MAGIC Loads CSV files from the lakehouse Files section into Bronze Delta tables.
# MAGIC Run this notebook after uploading the sample-data CSVs to your lakehouse.

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import current_timestamp, lit

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

LAKEHOUSE_PATH = "Files/sample-data"

DATASETS = {
    "datacenters": {
        "file": "datacenters.csv",
        "schema": StructType([
            StructField("datacenter_id", StringType(), False),
            StructField("datacenter_name", StringType(), False),
            StructField("market", StringType(), True),
            StructField("region", StringType(), True),
            StructField("country", StringType(), True),
            StructField("facility_type", StringType(), True),
            StructField("total_power_mw", DoubleType(), True),
            StructField("it_power_mw", DoubleType(), True),
            StructField("pue", DoubleType(), True),
            StructField("status", StringType(), True),
            StructField("opened_date", StringType(), True),
            StructField("tier_level", StringType(), True),
        ]),
    },
    "power_capacity": {
        "file": "power_capacity.csv",
        "schema": StructType([
            StructField("capacity_id", StringType(), False),
            StructField("datacenter_id", StringType(), False),
            StructField("measurement_date", StringType(), True),
            StructField("total_power_mw", DoubleType(), True),
            StructField("contracted_power_mw", DoubleType(), True),
            StructField("available_power_mw", DoubleType(), True),
            StructField("utilization_pct", DoubleType(), True),
            StructField("cooling_capacity_mw", DoubleType(), True),
            StructField("ups_capacity_mw", DoubleType(), True),
            StructField("generator_capacity_mw", DoubleType(), True),
            StructField("fiber_connections", IntegerType(), True),
            StructField("cross_connects", IntegerType(), True),
        ]),
    },
    "customer_deployments": {
        "file": "customer_deployments.csv",
        "schema": StructType([
            StructField("deployment_id", StringType(), False),
            StructField("customer_name", StringType(), False),
            StructField("datacenter_id", StringType(), False),
            StructField("contract_type", StringType(), True),
            StructField("power_kw", DoubleType(), True),
            StructField("cabinets", IntegerType(), True),
            StructField("contract_start", StringType(), True),
            StructField("contract_end", StringType(), True),
            StructField("monthly_revenue_usd", DoubleType(), True),
            StructField("status", StringType(), True),
            StructField("connectivity_type", StringType(), True),
            StructField("compliance_requirements", StringType(), True),
        ]),
    },
}

# COMMAND ----------

# MAGIC %md
# MAGIC ## Ingest CSVs into Bronze Delta Tables

# COMMAND ----------

for table_name, config in DATASETS.items():
    target_table = f"bronze_{table_name}"
    print(f"Ingesting {table_name}...")

    df = (
        spark.read
        .option("header", "true")
        .schema(config["schema"])
        .csv(f"{LAKEHOUSE_PATH}/{config['file']}")
    )

    # Add ingestion metadata
    df = (
        df
        .withColumn("_ingested_at", current_timestamp())
        .withColumn("_source_file", lit(config["file"]))
    )

    # Check if table exists — incremental sync (new/changed rows only)
    table_exists = False
    try:
        existing = spark.table(target_table)
        table_exists = True
    except Exception:
        pass

    if not table_exists:
        # First run — create table
        (
            df.write
            .format("delta")
            .mode("overwrite")
            .saveAsTable(target_table)
        )
        row_count = spark.table(target_table).count()
        print(f"   {target_table}: CREATED with {row_count} rows")
    else:
        # Incremental: add new columns if schema evolved
        new_cols = set(df.columns) - set(existing.columns)
        if new_cols:
            for c in new_cols:
                col_type = str(dict(df.dtypes).get(c, "string"))
                spark.sql(f"ALTER TABLE {target_table} ADD COLUMN `{c}` {col_type}")
            print(f"   {target_table}: added {len(new_cols)} new column(s): {new_cols}")
            existing = spark.table(target_table)

        # Only append rows not already in target (compare on all non-metadata cols)
        compare_cols = sorted([c for c in df.columns if not c.startswith("_")])
        src_subset = df.select(compare_cols)
        tgt_subset = existing.select(compare_cols)
        new_rows = src_subset.subtract(tgt_subset)
        new_count = new_rows.count()

        if new_count > 0:
            # Get full rows (with metadata) for the new data
            full_new = df.join(new_rows, on=compare_cols, how="inner").dropDuplicates()
            (
                full_new.write
                .format("delta")
                .mode("append")
                .option("mergeSchema", "true")
                .saveAsTable(target_table)
            )
            print(f"   {target_table}: appended {new_count} new rows")
        else:
            print(f"   {target_table}: no new rows (already in sync)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Tables

# COMMAND ----------

for table_name in DATASETS:
    df = spark.table(f"bronze_{table_name}")
    print(f"\nbronze_{table_name} ({df.count()} rows):")
    df.show(3, truncate=False)
