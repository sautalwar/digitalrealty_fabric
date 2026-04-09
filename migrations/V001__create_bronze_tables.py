# Migration V001: Create all Bronze tables
# Applied by: 00_apply_schema.py (SchemaEnforcer)
# This migration exists as documentation of the initial schema.
# The SchemaEnforcer handles CREATE TABLE automatically from the registry.

# Bronze: Datacenters
spark.sql("""
    CREATE TABLE IF NOT EXISTS bronze_datacenters (
        datacenter_id STRING NOT NULL,
        datacenter_name STRING NOT NULL,
        market STRING,
        region STRING,
        country STRING,
        facility_type STRING,
        total_power_mw DOUBLE,
        it_power_mw DOUBLE,
        pue DOUBLE,
        status STRING,
        opened_date STRING,
        tier_level STRING,
        _ingested_at TIMESTAMP,
        _source_file STRING
    ) USING DELTA
""")

# Bronze: Power Capacity
spark.sql("""
    CREATE TABLE IF NOT EXISTS bronze_power_capacity (
        capacity_id STRING NOT NULL,
        datacenter_id STRING NOT NULL,
        measurement_date STRING,
        total_power_mw DOUBLE,
        contracted_power_mw DOUBLE,
        available_power_mw DOUBLE,
        utilization_pct DOUBLE,
        cooling_capacity_mw DOUBLE,
        ups_capacity_mw DOUBLE,
        generator_capacity_mw DOUBLE,
        fiber_connections INT,
        cross_connects INT,
        _ingested_at TIMESTAMP,
        _source_file STRING
    ) USING DELTA
""")

# Bronze: Customer Deployments
spark.sql("""
    CREATE TABLE IF NOT EXISTS bronze_customer_deployments (
        deployment_id STRING NOT NULL,
        customer_name STRING NOT NULL,
        datacenter_id STRING NOT NULL,
        contract_type STRING,
        power_kw DOUBLE,
        cabinets INT,
        contract_start STRING,
        contract_end STRING,
        monthly_revenue_usd DOUBLE,
        status STRING,
        connectivity_type STRING,
        compliance_requirements STRING,
        _ingested_at TIMESTAMP,
        _source_file STRING
    ) USING DELTA
""")
