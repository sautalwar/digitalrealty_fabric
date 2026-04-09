# Migration V002: Create all Silver tables
# The SchemaEnforcer handles this automatically from the registry.
# This file documents the expected Silver schema for reference.

spark.sql("""
    CREATE TABLE IF NOT EXISTS silver_datacenters (
        datacenter_id STRING NOT NULL,
        datacenter_name STRING NOT NULL,
        market STRING,
        region STRING,
        country STRING,
        facility_type STRING,
        total_power_mw DOUBLE,
        it_power_mw DOUBLE,
        pue DOUBLE,
        efficiency_rating STRING,
        status STRING,
        opened_date DATE,
        age_years DOUBLE,
        tier_level STRING,
        _transformed_at TIMESTAMP
    ) USING DELTA PARTITIONED BY (region)
""")

spark.sql("""
    CREATE TABLE IF NOT EXISTS silver_capacity_trends (
        capacity_id STRING NOT NULL,
        datacenter_id STRING NOT NULL,
        measurement_date DATE,
        total_power_mw DOUBLE,
        contracted_power_mw DOUBLE,
        available_power_mw DOUBLE,
        utilization_pct DOUBLE,
        utilization_band STRING,
        mom_utilization_change DOUBLE,
        cooling_capacity_mw DOUBLE,
        power_headroom_mw DOUBLE,
        fiber_connections INT,
        cross_connects INT,
        _transformed_at TIMESTAMP
    ) USING DELTA
""")

spark.sql("""
    CREATE TABLE IF NOT EXISTS silver_customer_deployments (
        deployment_id STRING NOT NULL,
        customer_name STRING NOT NULL,
        datacenter_id STRING NOT NULL,
        contract_type STRING,
        power_kw DOUBLE,
        power_mw DOUBLE,
        cabinets INT,
        kw_per_cabinet DOUBLE,
        contract_start DATE,
        contract_end DATE,
        contract_months_remaining INT,
        monthly_revenue_usd DOUBLE,
        annual_revenue_usd DOUBLE,
        revenue_per_kw DOUBLE,
        status STRING,
        renewal_risk STRING,
        connectivity_type STRING,
        compliance_requirements STRING,
        _transformed_at TIMESTAMP
    ) USING DELTA
""")

spark.sql("""
    CREATE TABLE IF NOT EXISTS silver_regional_summary (
        region STRING NOT NULL,
        total_datacenters INT,
        total_power_mw DOUBLE,
        total_contracted_mw DOUBLE,
        avg_utilization_pct DOUBLE,
        total_customers INT,
        total_monthly_revenue DOUBLE,
        avg_pue DOUBLE,
        _transformed_at TIMESTAMP
    ) USING DELTA
""")
