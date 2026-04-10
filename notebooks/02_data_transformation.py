# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Data Transformation (Silver Layer)
# MAGIC **Digital Realty - Lakehouse Schema Evolution Demo**
# MAGIC
# MAGIC Transforms Bronze tables into Silver-layer curated datasets:
# MAGIC - Calculates efficiency ratings, utilization bands
# MAGIC - Computes contract metrics (renewal risk, revenue per kW)
# MAGIC - Creates regional aggregations

# COMMAND ----------

from pyspark.sql.functions import (
    col, to_date, year, month, datediff, current_date,
    round as spark_round, when, lit, sum as spark_sum,
    avg, count, current_timestamp, months_between, concat_ws
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Incremental Write Helper

# COMMAND ----------

def incremental_save(df, table_name, key_columns=None):
    """Write only new/changed rows to a Delta table. Add new columns if schema evolved.
    
    If key_columns is provided, uses them for comparison.
    Otherwise compares all non-metadata columns.
    """
    table_exists = False
    try:
        existing = spark.table(table_name)
        table_exists = True
    except Exception:
        pass

    if not table_exists:
        df.write.format("delta").mode("overwrite").saveAsTable(table_name)
        print(f"  {table_name}: CREATED with {df.count()} rows")
        return

    # Schema evolution: add new columns
    new_cols = set(df.columns) - set(existing.columns)
    if new_cols:
        for c in new_cols:
            col_type = str(dict(df.dtypes).get(c, "string"))
            spark.sql(f"ALTER TABLE {table_name} ADD COLUMN `{c}` {col_type}")
        print(f"  {table_name}: added {len(new_cols)} column(s): {new_cols}")
        existing = spark.table(table_name)

    # Determine comparison columns
    if key_columns:
        compare_cols = sorted(key_columns)
    else:
        compare_cols = sorted([c for c in df.columns if not c.startswith("_")])

    common_cols = sorted(list(set(compare_cols) & set(existing.columns) & set(df.columns)))
    src_subset = df.select(common_cols)
    tgt_subset = existing.select(common_cols)
    new_rows = src_subset.subtract(tgt_subset)
    new_count = new_rows.count()

    if new_count == 0:
        print(f"  {table_name}: no changes ({existing.count()} rows, in sync)")
        return

    # Append only the changed/new rows
    full_new = df.join(new_rows, on=common_cols, how="inner").dropDuplicates()
    full_new.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(table_name)
    print(f"  {table_name}: appended {new_count} new/changed rows (was {existing.count()})")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver: Datacenters with Efficiency Ratings

# COMMAND ----------

bronze_dc = spark.table("bronze_datacenters")

silver_dc = (
    bronze_dc
    .withColumn("opened_date", to_date(col("opened_date"), "yyyy-MM-dd"))
    .withColumn("age_years", spark_round(datediff(current_date(), col("opened_date")) / 365.25, 1))
    .withColumn(
        "efficiency_rating",
        when(col("pue") <= 1.2, "Excellent")
        .when(col("pue") <= 1.4, "Good")
        .when(col("pue") <= 1.6, "Average")
        .otherwise("Below Average")
    )
    .withColumn("_transformed_at", current_timestamp())
    .drop("_ingested_at", "_source_file")
)

incremental_save(silver_dc, "silver_datacenters", key_columns=["datacenter_id"])
print(f"silver_datacenters: {silver_dc.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver: Capacity Trends with Utilization Bands

# COMMAND ----------

bronze_cap = spark.table("bronze_power_capacity")

silver_cap = (
    bronze_cap
    .withColumn("measurement_date", to_date(col("measurement_date"), "yyyy-MM-dd"))
    .withColumn(
        "utilization_band",
        when(col("utilization_pct") >= 90, "Critical")
        .when(col("utilization_pct") >= 80, "High")
        .when(col("utilization_pct") >= 60, "Moderate")
        .otherwise("Low")
    )
    .withColumn(
        "power_headroom_mw",
        spark_round(col("cooling_capacity_mw") - col("contracted_power_mw"), 2)
    )
    .withColumn("mom_utilization_change", lit(None).cast("double"))
    .withColumn("_transformed_at", current_timestamp())
    .drop("_ingested_at", "_source_file")
)

incremental_save(silver_cap, "silver_capacity_trends", key_columns=["capacity_id"])
print(f"silver_capacity_trends: {silver_cap.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver: Customer Deployments with Contract Analytics

# COMMAND ----------

bronze_dep = spark.table("bronze_customer_deployments")

silver_dep = (
    bronze_dep
    .withColumn("contract_start", to_date(col("contract_start"), "yyyy-MM-dd"))
    .withColumn("contract_end", to_date(col("contract_end"), "yyyy-MM-dd"))
    .withColumn("power_mw", spark_round(col("power_kw") / 1000, 3))
    .withColumn(
        "kw_per_cabinet",
        spark_round(
            when(col("cabinets") > 0, col("power_kw") / col("cabinets")).otherwise(0), 2
        )
    )
    .withColumn(
        "contract_months_remaining",
        months_between(col("contract_end"), current_date()).cast("int")
    )
    .withColumn("annual_revenue_usd", spark_round(col("monthly_revenue_usd") * 12, 2))
    .withColumn(
        "revenue_per_kw",
        spark_round(
            when(col("power_kw") > 0, col("monthly_revenue_usd") / col("power_kw")).otherwise(0), 2
        )
    )
    .withColumn(
        "renewal_risk",
        when(col("contract_months_remaining") <= 6, "High")
        .when(col("contract_months_remaining") <= 12, "Medium")
        .otherwise("Low")
    )
    .withColumn("_transformed_at", current_timestamp())
    .drop("_ingested_at", "_source_file")
)

incremental_save(silver_dep, "silver_customer_deployments", key_columns=["deployment_id"])
print(f"silver_customer_deployments: {silver_dep.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver: Regional Summary Aggregation

# COMMAND ----------

dc_summary = (
    spark.table("silver_datacenters")
    .groupBy("region")
    .agg(
        count("*").alias("total_datacenters"),
        spark_round(spark_sum("total_power_mw"), 1).alias("total_power_mw"),
        spark_round(avg("pue"), 2).alias("avg_pue"),
    )
)

cap_summary = (
    spark.table("silver_capacity_trends")
    .join(spark.table("silver_datacenters").select("datacenter_id", "region"), "datacenter_id")
    .groupBy("region")
    .agg(
        spark_round(spark_sum("contracted_power_mw"), 1).alias("total_contracted_mw"),
        spark_round(avg("utilization_pct"), 1).alias("avg_utilization_pct"),
    )
)

rev_summary = (
    spark.table("silver_customer_deployments")
    .join(spark.table("silver_datacenters").select("datacenter_id", "region"), "datacenter_id")
    .groupBy("region")
    .agg(
        count("*").alias("total_customers"),
        spark_round(spark_sum("monthly_revenue_usd"), 0).alias("total_monthly_revenue"),
    )
)

regional = (
    dc_summary
    .join(cap_summary, "region", "left")
    .join(rev_summary, "region", "left")
    .withColumn("_transformed_at", current_timestamp())
    .orderBy("region")
)

incremental_save(regional, "silver_regional_summary", key_columns=["region"])
print("silver_regional_summary:")
regional.show(truncate=False)
