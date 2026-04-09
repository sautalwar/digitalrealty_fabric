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

    # Write as Delta table (overwrite for demo; use merge/append in production)
    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(f"bronze_{table_name}")
    )

    row_count = spark.table(f"bronze_{table_name}").count()
    print(f"   bronze_{table_name}: {row_count} rows loaded")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Tables

# COMMAND ----------

for table_name in DATASETS:
    df = spark.table(f"bronze_{table_name}")
    print(f"\nbronze_{table_name} ({df.count()} rows):")
    df.show(3, truncate=False)
