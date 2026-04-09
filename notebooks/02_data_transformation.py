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

silver_dc.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("silver_datacenters")
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

silver_cap.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("silver_capacity_trends")
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

silver_dep.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("silver_customer_deployments")
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

regional.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("silver_regional_summary")
print("silver_regional_summary:")
regional.show(truncate=False)
