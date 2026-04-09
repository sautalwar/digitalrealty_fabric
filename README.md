# Digital Realty — Fabric CI/CD: Schema Evolution + Performance Optimization

## The Problem

Microsoft Fabric has two gaps that break enterprise CI/CD:

1. **Lakehouse schemas aren't tracked in Git** — creating tables, modifying columns via the UI or SQL endpoint produces changes invisible to source control
2. **No automated performance gates** — inefficient DAX, bloated semantic models, and storage issues reach production unchecked

## The Solution

This repo solves both with a unified CI/CD pipeline:

| Layer | Notebook | Purpose |
|-------|----------|---------|
| Schema Registry | `00_schema_registry.py` | Single source of truth for all table schemas |
| Schema Enforcer | `00_apply_schema.py` | Compares registry vs actual tables, applies CREATE/ALTER |
| BPA Analyzer | `04_bpa_analyzer.py` | Detects inefficient DAX patterns via semantic-link-labs |
| Memory Analyzer | `05_memory_analyzer.py` | Identifies high-memory columns and compression issues |
| Compression Analyzer | `06_compression_analyzer.py` | Delta table storage diagnostics and OPTIMIZE recommendations |
| Quality Gate | `03_data_quality_checks.py` | Validates data AND schema consistency |
| Performance Gate | `performance-gate.yml` | CI workflow: BPA + memory + anti-pattern checks |

## Quick Start

### 1. Set Up Workspaces
`DigitalRealty_Dev`, `DigitalRealty_UAT`, `DigitalRealty_Prod`

### 2. Connect Git + Upload Sample Data
Connect Dev workspace to `main` branch. Upload CSVs from `sample-data/`.

### 3. Run Notebooks (in order)
```
00_apply_schema          # Creates/updates table schemas from registry
01_data_ingestion        # Bronze layer: CSVs → Delta tables
02_data_transformation   # Silver layer: business logic + aggregations
03_data_quality_checks   # Data + schema validation
04_bpa_analyzer          # Best Practice Analysis on semantic model
05_memory_analyzer       # Memory/VertiPaq analysis
06_compression_analyzer  # Delta storage optimization
```

### 4. Demo Performance Optimization
Compare `semantic-model/digitalrealty-capacity-BEFORE.tmdl` (bloated) vs `digitalrealty-capacity.tmdl` (optimized) to see: calculated columns → measures, SUMX → SUM, FILTER(ALL()) → CALCULATE, bloat columns removed.

## Repository Structure

```
notebooks/
  00_schema_registry.py      Schema definitions (source of truth)
  00_apply_schema.py         Schema enforcement engine
  01_data_ingestion.py       Bronze layer ingestion
  02_data_transformation.py  Silver layer transformations
  03_data_quality_checks.py  Data + schema validation
  04_bpa_analyzer.py         Best Practice Analyzer (DAX anti-patterns)
  05_memory_analyzer.py      Memory/VertiPaq column-level analysis
  06_compression_analyzer.py Delta storage diagnostics + OPTIMIZE

semantic-model/
  digitalrealty-capacity.tmdl         Optimized model (11 measures, 0 calc cols)
  digitalrealty-capacity-BEFORE.tmdl  Bloated model (for demo comparison)

migrations/                  V001-V004 schema migration scripts
sample-data/                 CSV files (datacenters, capacity, deployments)
environments/                Dev/UAT/Prod workspace configs
deployment-pipeline/         Pipeline and deployment rule configs
scripts/                     PowerShell automation
security/                    OneLake roles and RLS rules
.github/workflows/           CI/CD (git sync, schema validation, performance gate)
docs/                        Architecture and guides
```

## Demo Assets

| File | Description |
|------|-------------|
| `DigitalRealty_StoryDemo.html` | **Story-driven demo** (20 screens, 5-act narrative: Crisis → Diagnosis → Fix → Proof → Close) |
| `DigitalRealty_Realistic_Demo.html` | Pixel-perfect UI mockup demo (18 screens) |
| `DigitalRealty_Visual_Demo.html` | Visual demo with UI screenshots (17 screens) |
| `DigitalRealty_Schema_Evolution_Workshop.html` | Interactive workshop presentation (12 slides) |
| `DigitalRealty_Lakehouse_Schema_Evolution.pdf` | Solution approach document |
| `DigitalRealty_Schema_Evolution_Demo_Guide.pdf` | Click-by-click demo guide |

## GitHub Secrets Required

| Secret | Description |
|--------|-------------|
| `FABRIC_TENANT_ID` | Azure AD tenant ID |
| `FABRIC_CLIENT_ID` | Service principal app ID |
| `FABRIC_CLIENT_SECRET` | Service principal secret |

## Domain Context

Digital Realty Trust — data center REIT. Sample data:
- **15 datacenters** across NorthAmerica, EMEA, APAC, LATAM
- **Power capacity** with PUE metrics and sustainability tracking
- **Customer deployments** with revenue, renewal risk, and connectivity
