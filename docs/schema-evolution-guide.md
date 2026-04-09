# Schema Evolution Guide

## The Problem

Fabric Git integration tracks Lakehouse container metadata but **does NOT track table schemas**.
When someone creates a table, adds a column, or modifies a schema through the Fabric UI or SQL endpoint,
those changes are not serialized to Git and cannot be promoted via CI/CD.

## Our Solution: Schema-as-Code (Hybrid Approach)

Three layers working together:

### Layer 1: Schema Registry (`notebooks/00_schema_registry.py`)

Single source of truth for all table schemas. Every table's columns, types, and constraints
are defined as a Python dictionary. Schema changes start here.

**To make a schema change:**
1. Edit `SCHEMAS` dictionary in `00_schema_registry.py`
2. Bump `SCHEMA_VERSION` (use semver)
3. Add a changelog entry at the bottom of the file
4. Update transformation notebooks if needed
5. Update quality checks to validate the new columns
6. Commit via PR

### Layer 2: Schema Enforcer (`notebooks/00_apply_schema.py`)

Reads the registry and compares against actual Lakehouse tables:
- **Missing table?** CREATE TABLE with all columns
- **Missing column?** ALTER TABLE ADD COLUMNS
- **Extra column not in registry?** Reports as DRIFT (warning)

Runs BEFORE data ingestion in the pipeline.

### Layer 3: Quality Gate (`notebooks/03_data_quality_checks.py`)

Validates both data quality AND schema consistency:
- Checks every table's actual columns against the registry
- Fails the pipeline on missing columns (schema drift)
- Warns on extra columns

### CI/CD Flow

```
Edit 00_schema_registry.py
    |
    v
Commit -> PR -> Review -> Merge to main
    |
    v
Fabric Git Sync (pulls updated notebooks into Dev workspace)
    |
    v
Run notebooks in order:
  00_apply_schema  (detects missing columns, runs ALTER TABLE)
  01_ingestion     (loads data into bronze tables)
  02_transformation (transforms to silver tables)
  03_quality       (validates data + schema)
    |
    v
Deployment Pipeline: Dev -> UAT
    |
    v
Run notebooks in UAT (00_apply_schema applies same changes)
    |
    v
Deployment Pipeline: UAT -> Prod (with approval gate)
    |
    v
Run notebooks in Prod
```

## Example: Adding a Column

Scenario: Digital Realty wants to track sustainability metrics (carbon intensity per datacenter).

**Step 1:** Edit `00_schema_registry.py`:
```python
SCHEMA_VERSION = "1.1.0"  # was 1.0.0

# In silver_datacenters columns, add:
("carbon_intensity_kg_mwh", "DOUBLE", True),
("renewable_energy_pct", "DOUBLE", True),
```

**Step 2:** Edit `02_data_transformation.py`:
```python
.withColumn("carbon_intensity_kg_mwh", lit(None).cast("double"))
.withColumn("renewable_energy_pct", lit(None).cast("double"))
```

**Step 3:** Edit `03_data_quality_checks.py`:
```python
dq.check_numeric_range("silver_datacenters", "renewable_energy_pct", min_val=0, max_val=100)
```

**Step 4:** Commit, PR, merge. The schema change flows through CI/CD automatically.

## Anti-Patterns to Avoid

1. **DO NOT** create tables through the Fabric UI in tracked environments
2. **DO NOT** add columns via SQL endpoint without updating the schema registry
3. **DO NOT** skip the quality check notebook in the pipeline
4. **DO NOT** deploy without running the schema enforcer first
