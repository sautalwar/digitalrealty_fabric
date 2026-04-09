# Copilot Instructions — Digital Realty Fabric

## Project Overview

This project implements a CI/CD-enabled Microsoft Fabric data platform for Digital Realty, with a specific focus on **Lakehouse schema evolution** — versioning and promoting table schemas across Dev, UAT, and Prod workspaces. This is the core challenge: Fabric Git integration serializes Lakehouse container metadata but does NOT track table structures, schemas, or columns. This project provides the patterns and automation to bridge that gap.

## The Problem

Fabric Git integration works well for most artifacts (pipelines, semantic models, Dataflow Gen2, notebooks). However, Lakehouse structural changes — creating tables, modifying schemas, adding columns via the UI or SQL endpoint — are not captured in Git. This breaks CI/CD for schema promotion across environments.

## Architecture

### Medallion Lakehouse Pattern

Notebooks follow a Bronze → Silver → Gold medallion architecture:

- **Bronze** (`01_data_ingestion.py`) — raw ingestion from source files into `bronze_*` Delta tables
- **Silver** (`02_data_transformation.py`) — cleansed/transformed data into `silver_*` Delta tables with business logic (depreciation, variance, regional summaries)
- **Gold** (`03_data_quality_checks.py`) — validation layer that enforces row counts, null checks, duplicates, range validation, and allowed values before data is consumed
- Table naming: `bronze_` prefix for raw, `silver_` prefix for transformed

### Schema-as-Code Strategy

Since Fabric doesn't version Lakehouse schemas in Git, this project treats **notebooks as the schema source of truth**:

1. Notebooks define table structures via `CREATE TABLE` / `CREATE OR REPLACE TABLE` / Delta write operations with explicit schemas
2. Schema changes are made in notebook code (not through the Fabric UI), committed to Git, and promoted via CI/CD
3. A schema migration notebook applies structural changes (ALTER TABLE, new columns, type changes) idempotently
4. The data quality notebook validates schema expectations post-deployment

### Workspace Structure

Three environments following Fabric deployment pipeline conventions:

| Environment | Purpose | Git Branch |
|---|---|---|
| Dev | Active development, schema iteration | `main` (or feature branches) |
| UAT | Validation, user acceptance testing | Promoted from Dev |
| Prod | Production workload | Promoted from UAT |

### Environment Configuration

Each environment has a JSON config file (`environments/{dev,uat,prod}.json`) containing:
- `workspace_id` and `workspace_name`
- `lakehouse_name` and `warehouse_name`
- `sql_endpoint`
- `filter_region` (Dev = `ALL`, UAT = regional subset, Prod = `ALL`)

Deployment rules (`deployment-pipeline/deployment-rules.json`) handle lakehouse name swapping and DFG2 parameter overrides per environment.

### CI/CD Flow

```
Feature branch → PR → main → Fabric Git Sync → Health Check → Change Detection → Approval → Deploy → Fan-out (multi-region)
```

Key workflows:
- **Git sync on merge** — triggers Fabric `updateFromGit` when PRs merge to `main`
- **Health check** — scheduled every 2 hours, validates Git sync status across workspaces, alerts Teams on drift
- **Promote with change detection** — snapshots source/target, diffs reports/datasets/tables/TMDL, generates change report, requires GitHub Environment approval before deploying
- **Fan-out deploy** — matrix-based multi-region deployment (if applicable)
- **Cross-workspace report sync** — promotes PBIX/PBIP/PBIR reports across workspaces for app navigation
- **DFG2 parameter update** — patches Dataflow Gen2 parameters post-deployment via Fabric REST API

### Security Model

Layered security (all four must be configured):

1. **Workspace permissions** — role-based access per environment
2. **OneLake RBAC** — region-based data access roles (`security/onelake-roles.json`)
3. **Semantic model RLS** — DAX row-level security filtering by `USERPRINCIPALNAME()` (`security/rls-rules.dax`)
4. **OLS / hidden tables** — security bridge tables hidden from end users in the semantic model

## Key Conventions

### Notebook Patterns

- Notebooks are PySpark and run in Fabric Spark sessions
- Each notebook is numbered for execution order (`01_`, `02_`, `03_`)
- Use `spark.sql()` for DDL and `spark.read`/`spark.write` for data operations
- Delta format is mandatory — all tables are Delta tables
- Write mode is `overwrite` for full refresh, `merge` for incremental
- All schema definitions should be explicit (StructType) rather than inferred

### Dataflow Gen2

- Parameters are defined in `dataflow-gen2/parameters.json`
- Key parameters: `pLakehouseName`, `pSourceTable`, `pFilterRegion`
- Power Query M code lives in `.m` files
- Parameters must be marked as public for deployment rule overrides
- See `dataflow-gen2/WORKAROUND_GUIDE.md` for known DFG2 deployment quirks

### Deployment Scripts (PowerShell)

All scripts authenticate via Fabric REST API with Azure CLI or service principal tokens:

| Script | Purpose |
|---|---|
| `Check-GitSyncStatus.ps1` | Report Git sync health across workspaces |
| `Force-SyncFromGit.ps1` | Force workspace to match Git branch state |
| `Deploy-FanOut.ps1` | Parallel fan-out to regional deployment pipelines |
| `Rebind-Report.ps1` | Rebind a Power BI report to a different semantic model |

### Semantic Model

- TMDL format (`.tmdl` files) for the semantic model definition
- DirectLake mode preferred for performance
- RLS roles defined inline in the model
- Measures for financial KPIs (assets, budgets, variance, growth)

### Schema Migration Pattern

When making Lakehouse schema changes:

1. **Never** modify schemas directly in the Fabric UI for tracked environments
2. Add/modify the schema definition in the appropriate notebook
3. For additive changes (new columns, new tables): update the notebook's write schema
4. For breaking changes (type changes, renames): create a migration step in the notebook that handles both old and new states
5. The data quality notebook (`03_`) must be updated to validate new schema expectations
6. Commit, PR, merge — the CI/CD pipeline handles promotion

### Environment Variables and Secrets

GitHub Actions workflows expect these secrets:
- `FABRIC_CLIENT_ID` — Service principal app ID
- `FABRIC_CLIENT_SECRET` — Service principal secret
- `FABRIC_TENANT_ID` — Azure AD tenant ID
- Workspace IDs are stored in environment JSON configs, not as secrets

## Build / Run Commands

```bash
# Run notebooks in order (within Fabric Spark environment)
# 01 → 02 → 03 (Bronze → Silver → Quality)

# Setup workspaces and deployment pipeline (PowerShell)
.\setup-keller-fabric.ps1

# Check Git sync health
.\scripts\Check-GitSyncStatus.ps1

# Force sync workspace from Git
.\scripts\Force-SyncFromGit.ps1

# Fan-out deployment
.\scripts\Deploy-FanOut.ps1

# PDF generation (for analysis documents)
pip install reportlab
python generate_keller_pdf.py
```

## Fabric API Patterns

All automation uses the Fabric REST API (`https://api.fabric.microsoft.com/v1`):
- Authentication: `az account get-access-token --resource https://api.fabric.microsoft.com`
- Git sync: `POST /workspaces/{id}/git/updateFromGit`
- Git status: `GET /workspaces/{id}/git/status`
- Deployment: `POST /deploymentPipelines/{id}/deploy`
- Item definitions: `POST /workspaces/{id}/items/{id}/updateDefinition`
