# Migration V003: Add sustainability tracking columns
# This migration demonstrates schema evolution -- adding new columns
# to existing tables without breaking the pipeline.
#
# SCENARIO: Digital Realty wants to track sustainability metrics.
# We add carbon_intensity and renewable_pct to the datacenter tables.
#
# STEPS TO APPLY:
# 1. Update SCHEMAS in 00_schema_registry.py with the new columns
# 2. Bump SCHEMA_VERSION to "1.1.0"
# 3. Run 00_apply_schema.py -- it will ALTER TABLE to add the columns
# 4. Update 02_data_transformation.py to populate the new columns
# 5. Update 03_data_quality_checks.py to validate them

spark.sql("""
    ALTER TABLE silver_datacenters
    ADD COLUMNS (
        carbon_intensity_kg_mwh DOUBLE,
        renewable_energy_pct DOUBLE
    )
""")

spark.sql("""
    ALTER TABLE silver_regional_summary
    ADD COLUMNS (
        avg_carbon_intensity DOUBLE,
        avg_renewable_pct DOUBLE
    )
""")
