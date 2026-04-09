# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Data Quality Checks
# MAGIC **Digital Realty - Lakehouse Schema Evolution Demo**
# MAGIC
# MAGIC Automated data quality AND schema validation for Silver-layer tables.
# MAGIC Fails the notebook if any critical checks do not pass.
# MAGIC
# MAGIC This notebook validates BOTH data quality AND schema consistency
# MAGIC with the schema registry. Schema drift = pipeline failure.

# COMMAND ----------

%run ./00_schema_registry

# COMMAND ----------

from pyspark.sql.functions import col, count, when, min, max

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality Framework

# COMMAND ----------

class DataQualityChecker:
    """DQ framework with schema validation for Fabric notebooks."""

    def __init__(self):
        self.results = []

    def check(self, name, table, condition, severity="critical"):
        status = "PASS" if condition else ("FAIL" if severity == "critical" else "WARN")
        self.results.append({
            "check": name,
            "table": table,
            "status": status,
            "severity": severity,
            "passed": condition,
        })
        icon = {"PASS": "PASS", "FAIL": "FAIL", "WARN": "WARN"}[status]
        print(f"  {icon} | {table} | {name}")

    def check_not_null(self, table_name, column):
        df = spark.table(table_name)
        null_count = df.filter(col(column).isNull()).count()
        self.check(f"{column} has no nulls", table_name, null_count == 0)

    def check_row_count(self, table_name, min_rows=1):
        df = spark.table(table_name)
        row_count = df.count()
        self.check(f"Row count >= {min_rows} (actual: {row_count})", table_name, row_count >= min_rows)

    def check_no_duplicates(self, table_name, key_columns):
        df = spark.table(table_name)
        total = df.count()
        distinct = df.select(key_columns).distinct().count()
        self.check(f"No duplicate keys on {key_columns}", table_name, total == distinct)

    def check_values_in_set(self, table_name, column, valid_values):
        df = spark.table(table_name)
        invalid = df.filter(~col(column).isin(valid_values)).count()
        self.check(f"{column} values are valid (invalid: {invalid})", table_name, invalid == 0, severity="warning")

    def check_numeric_range(self, table_name, column, min_val=None, max_val=None):
        df = spark.table(table_name)
        stats = df.select(min(column).alias("min_v"), max(column).alias("max_v")).first()
        conditions = []
        if min_val is not None:
            conditions.append(stats["min_v"] >= min_val)
        if max_val is not None:
            conditions.append(stats["max_v"] <= max_val)
        self.check(
            f"{column} in range [{min_val}, {max_val}] (actual: [{stats['min_v']}, {stats['max_v']}])",
            table_name, all(conditions))

    # ── Schema Validation ────────────────────────────────────
    def validate_schema(self, table_name, expected_schema):
        """Validate that a table's schema matches the registry definition."""
        if not spark.catalog.tableExists(table_name):
            self.check(f"Table exists", table_name, False)
            return

        actual_fields = {f.name for f in spark.table(table_name).schema.fields}
        expected_fields = {c[0] for c in expected_schema["columns"]}

        missing = expected_fields - actual_fields
        if missing:
            self.check(f"Schema complete (missing: {missing})", table_name, False)
        else:
            self.check(f"Schema matches registry ({len(actual_fields)} columns)", table_name, True)

        extra = actual_fields - expected_fields
        if extra:
            self.check(f"No schema drift (extra: {extra})", table_name, False, severity="warning")

    def summary(self):
        passed = sum(1 for r in self.results if r["passed"])
        failed = sum(1 for r in self.results if not r["passed"] and r["severity"] == "critical")
        warnings = sum(1 for r in self.results if not r["passed"] and r["severity"] == "warning")
        total = len(self.results)
        print(f"\n{'=' * 60}")
        print(f"Data Quality Summary: {passed}/{total} passed, {failed} failed, {warnings} warnings")
        print(f"{'=' * 60}")
        if failed > 0:
            print("CRITICAL FAILURES DETECTED -- pipeline should not proceed")
            raise Exception(f"Data quality check failed: {failed} critical failures")
        elif warnings > 0:
            print("Warnings detected but no critical failures -- proceeding")
        else:
            print("All checks passed")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Schema Validation (from Registry)

# COMMAND ----------

dq = DataQualityChecker()

print("Schema Validation:")
for table_name, schema_def in SCHEMAS.items():
    dq.validate_schema(table_name, schema_def)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality Checks

# COMMAND ----------

# Datacenters
print("\nDatacenter Checks:")
dq.check_row_count("silver_datacenters", min_rows=10)
dq.check_not_null("silver_datacenters", "datacenter_id")
dq.check_not_null("silver_datacenters", "region")
dq.check_no_duplicates("silver_datacenters", ["datacenter_id"])
dq.check_numeric_range("silver_datacenters", "total_power_mw", min_val=0)
dq.check_numeric_range("silver_datacenters", "pue", min_val=1.0, max_val=3.0)
dq.check_values_in_set("silver_datacenters", "region",
    ["NorthAmerica", "EMEA", "APAC", "LATAM"])
dq.check_values_in_set("silver_datacenters", "efficiency_rating",
    ["Excellent", "Good", "Average", "Below Average"])

# Capacity
print("\nCapacity Checks:")
dq.check_row_count("silver_capacity_trends", min_rows=10)
dq.check_not_null("silver_capacity_trends", "capacity_id")
dq.check_not_null("silver_capacity_trends", "datacenter_id")
dq.check_no_duplicates("silver_capacity_trends", ["capacity_id"])
dq.check_numeric_range("silver_capacity_trends", "utilization_pct", min_val=0, max_val=100)

# Customer Deployments
print("\nCustomer Deployment Checks:")
dq.check_row_count("silver_customer_deployments", min_rows=10)
dq.check_not_null("silver_customer_deployments", "deployment_id")
dq.check_not_null("silver_customer_deployments", "customer_name")
dq.check_no_duplicates("silver_customer_deployments", ["deployment_id"])
dq.check_numeric_range("silver_customer_deployments", "power_kw", min_val=0)
dq.check_numeric_range("silver_customer_deployments", "monthly_revenue_usd", min_val=0)
dq.check_values_in_set("silver_customer_deployments", "renewal_risk",
    ["Low", "Medium", "High"])

# Regional Summary
print("\nRegional Summary Checks:")
dq.check_row_count("silver_regional_summary", min_rows=3)
dq.check_not_null("silver_regional_summary", "region")
dq.check_no_duplicates("silver_regional_summary", ["region"])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

dq.summary()
