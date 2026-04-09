# Databricks notebook source
# MAGIC %md
# MAGIC # 00 — Schema Registry
# MAGIC **Digital Realty — Lakehouse Schema Evolution Demo**
# MAGIC
# MAGIC This notebook is the SINGLE SOURCE OF TRUTH for all Lakehouse table schemas.
# MAGIC Every schema change starts here. This file is version-controlled in Git and
# MAGIC promoted through the Fabric deployment pipeline.
# MAGIC
# MAGIC **DO NOT create or modify tables through the Fabric UI.**
# MAGIC **All schema changes must be made in this file, committed via PR, and promoted via CI/CD.**

# COMMAND ----------

SCHEMA_VERSION = "1.0.0"

# ============================================================
# BRONZE LAYER SCHEMAS
# ============================================================

SCHEMAS = {

    # ── Bronze: Datacenters ──────────────────────────────────
    "bronze_datacenters": {
        "columns": [
            ("datacenter_id", "STRING", False),
            ("datacenter_name", "STRING", False),
            ("market", "STRING", True),
            ("region", "STRING", True),
            ("country", "STRING", True),
            ("facility_type", "STRING", True),
            ("total_power_mw", "DOUBLE", True),
            ("it_power_mw", "DOUBLE", True),
            ("pue", "DOUBLE", True),
            ("status", "STRING", True),
            ("opened_date", "STRING", True),
            ("tier_level", "STRING", True),
            ("_ingested_at", "TIMESTAMP", True),
            ("_source_file", "STRING", True),
        ],
        "primary_key": ["datacenter_id"],
        "partition_by": None,
    },

    # ── Bronze: Power Capacity ───────────────────────────────
    "bronze_power_capacity": {
        "columns": [
            ("capacity_id", "STRING", False),
            ("datacenter_id", "STRING", False),
            ("measurement_date", "STRING", True),
            ("total_power_mw", "DOUBLE", True),
            ("contracted_power_mw", "DOUBLE", True),
            ("available_power_mw", "DOUBLE", True),
            ("utilization_pct", "DOUBLE", True),
            ("cooling_capacity_mw", "DOUBLE", True),
            ("ups_capacity_mw", "DOUBLE", True),
            ("generator_capacity_mw", "DOUBLE", True),
            ("fiber_connections", "INT", True),
            ("cross_connects", "INT", True),
            ("_ingested_at", "TIMESTAMP", True),
            ("_source_file", "STRING", True),
        ],
        "primary_key": ["capacity_id"],
        "partition_by": None,
    },

    # ── Bronze: Customer Deployments ─────────────────────────
    "bronze_customer_deployments": {
        "columns": [
            ("deployment_id", "STRING", False),
            ("customer_name", "STRING", False),
            ("datacenter_id", "STRING", False),
            ("contract_type", "STRING", True),
            ("power_kw", "DOUBLE", True),
            ("cabinets", "INT", True),
            ("contract_start", "STRING", True),
            ("contract_end", "STRING", True),
            ("monthly_revenue_usd", "DOUBLE", True),
            ("status", "STRING", True),
            ("connectivity_type", "STRING", True),
            ("compliance_requirements", "STRING", True),
            ("_ingested_at", "TIMESTAMP", True),
            ("_source_file", "STRING", True),
        ],
        "primary_key": ["deployment_id"],
        "partition_by": None,
    },

    # ============================================================
    # SILVER LAYER SCHEMAS
    # ============================================================

    # ── Silver: Datacenters (enriched) ───────────────────────
    "silver_datacenters": {
        "columns": [
            ("datacenter_id", "STRING", False),
            ("datacenter_name", "STRING", False),
            ("market", "STRING", True),
            ("region", "STRING", True),
            ("country", "STRING", True),
            ("facility_type", "STRING", True),
            ("total_power_mw", "DOUBLE", True),
            ("it_power_mw", "DOUBLE", True),
            ("pue", "DOUBLE", True),
            ("efficiency_rating", "STRING", True),
            ("status", "STRING", True),
            ("opened_date", "DATE", True),
            ("age_years", "DOUBLE", True),
            ("tier_level", "STRING", True),
            ("_transformed_at", "TIMESTAMP", True),
        ],
        "primary_key": ["datacenter_id"],
        "partition_by": ["region"],
    },

    # ── Silver: Capacity Trends ──────────────────────────────
    "silver_capacity_trends": {
        "columns": [
            ("capacity_id", "STRING", False),
            ("datacenter_id", "STRING", False),
            ("measurement_date", "DATE", True),
            ("total_power_mw", "DOUBLE", True),
            ("contracted_power_mw", "DOUBLE", True),
            ("available_power_mw", "DOUBLE", True),
            ("utilization_pct", "DOUBLE", True),
            ("utilization_band", "STRING", True),
            ("mom_utilization_change", "DOUBLE", True),
            ("cooling_capacity_mw", "DOUBLE", True),
            ("power_headroom_mw", "DOUBLE", True),
            ("fiber_connections", "INT", True),
            ("cross_connects", "INT", True),
            ("_transformed_at", "TIMESTAMP", True),
        ],
        "primary_key": ["capacity_id"],
        "partition_by": None,
    },

    # ── Silver: Customer Deployments (enriched) ──────────────
    "silver_customer_deployments": {
        "columns": [
            ("deployment_id", "STRING", False),
            ("customer_name", "STRING", False),
            ("datacenter_id", "STRING", False),
            ("contract_type", "STRING", True),
            ("power_kw", "DOUBLE", True),
            ("power_mw", "DOUBLE", True),
            ("cabinets", "INT", True),
            ("kw_per_cabinet", "DOUBLE", True),
            ("contract_start", "DATE", True),
            ("contract_end", "DATE", True),
            ("contract_months_remaining", "INT", True),
            ("monthly_revenue_usd", "DOUBLE", True),
            ("annual_revenue_usd", "DOUBLE", True),
            ("revenue_per_kw", "DOUBLE", True),
            ("status", "STRING", True),
            ("renewal_risk", "STRING", True),
            ("connectivity_type", "STRING", True),
            ("compliance_requirements", "STRING", True),
            ("_transformed_at", "TIMESTAMP", True),
        ],
        "primary_key": ["deployment_id"],
        "partition_by": None,
    },

    # ── Silver: Regional Summary ─────────────────────────────
    "silver_regional_summary": {
        "columns": [
            ("region", "STRING", False),
            ("total_datacenters", "INT", True),
            ("total_power_mw", "DOUBLE", True),
            ("total_contracted_mw", "DOUBLE", True),
            ("avg_utilization_pct", "DOUBLE", True),
            ("total_customers", "INT", True),
            ("total_monthly_revenue", "DOUBLE", True),
            ("avg_pue", "DOUBLE", True),
            ("_transformed_at", "TIMESTAMP", True),
        ],
        "primary_key": ["region"],
        "partition_by": None,
    },
}

# ============================================================
# SCHEMA CHANGELOG
# ============================================================
# v1.0.0 — Initial schema: 3 bronze tables, 4 silver tables
#           Bronze: datacenters, power_capacity, customer_deployments
#           Silver: datacenters, capacity_trends, customer_deployments, regional_summary
#
# When making changes:
# 1. Increment SCHEMA_VERSION (use semver: major.minor.patch)
# 2. Add new/modified columns to the appropriate table definition above
# 3. Add a changelog entry here
# 4. Update 03_data_quality_checks.py to validate the new schema
# 5. Commit via PR — code review required for schema changes
