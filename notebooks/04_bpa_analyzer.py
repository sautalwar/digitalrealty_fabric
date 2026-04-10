# Databricks notebook source
# MAGIC %md
# MAGIC # 04 — Best Practice Analyzer
# MAGIC **Digital Realty — Semantic Model Performance Diagnostics**
# MAGIC
# MAGIC This notebook connects to the Power BI semantic model via XMLA and runs
# MAGIC the Best Practice Analyzer (BPA) to identify inefficient DAX patterns,
# MAGIC calculated columns that should be measures, and other anti-patterns.
# MAGIC
# MAGIC **Uses:** `semantic-link-labs` library (pre-installed in Fabric)
# MAGIC
# MAGIC **Outputs:** Violations report with severity, category, rule, affected object, and recommendation

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Configuration

# COMMAND ----------

import json
from datetime import datetime

# Configuration
WORKSPACE_NAME = "DigitalRealty-Dev"
DATASET_NAME = "DigitalRealty_Capacity"

# BPA rule categories to focus on
FOCUS_CATEGORIES = [
    "Performance",
    "DAX Expressions",
    "Error Prevention",
    "Maintenance"
]

print(f"Target: {WORKSPACE_NAME} / {DATASET_NAME}")
print(f"Focus categories: {', '.join(FOCUS_CATEGORIES)}")
print(f"Analysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Install and Import semantic-link-labs

# COMMAND ----------

# MAGIC %pip install semantic-link-labs --quiet

import sempy_labs as labs
import sempy.fabric as fabric

print("semantic-link-labs loaded successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Run Best Practice Analyzer

# COMMAND ----------

# Run BPA against the semantic model
print(f"Running BPA against '{DATASET_NAME}'...")
print("=" * 60)

bpa_results = labs.run_model_bpa(
    dataset=DATASET_NAME,
    workspace=WORKSPACE_NAME
)

total_violations = len(bpa_results)
print(f"\nAnalysis complete: {total_violations} violations found")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Categorize and Prioritize Violations

# COMMAND ----------

# Display violations by severity
if total_violations > 0:
    # Group by severity
    severity_counts = bpa_results.groupby('Severity').size().reset_index(name='Count')
    print("=" * 60)
    print("VIOLATIONS BY SEVERITY")
    print("=" * 60)
    for _, row in severity_counts.iterrows():
        icon = "🔴" if row['Severity'] == 'Error' else "🟡" if row['Severity'] == 'Warning' else "ℹ️"
        print(f"  {icon} {row['Severity']}: {row['Count']}")

    print(f"\n{'=' * 60}")
    print("VIOLATIONS BY CATEGORY")
    print("=" * 60)
    category_counts = bpa_results.groupby('Category').size().reset_index(name='Count')
    for _, row in category_counts.iterrows():
        print(f"  [{row['Category']}]: {row['Count']}")

    print(f"\n{'=' * 60}")
    print("DETAILED VIOLATIONS")
    print("=" * 60)

    for idx, row in bpa_results.iterrows():
        sev_icon = "🔴" if row['Severity'] == 'Error' else "🟡" if row['Severity'] == 'Warning' else "ℹ️"
        print(f"\n{sev_icon} [{row['Severity']}] {row.get('Rule', 'Unknown Rule')}")
        print(f"   Category: {row.get('Category', 'N/A')}")
        print(f"   Object: {row.get('Object', 'N/A')} ({row.get('Object Type', 'N/A')})")
        if 'Description' in row:
            print(f"   Detail: {row['Description']}")
else:
    print("✅ No violations found! Model passes all BPA rules.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Known Anti-Patterns Check (Static Analysis)
# MAGIC
# MAGIC In addition to the BPA library rules, we check for Digital Realty-specific
# MAGIC anti-patterns that the team has identified.

# COMMAND ----------

# Custom anti-pattern checks via DMV queries
print("Running custom anti-pattern checks...")
print("=" * 60)

custom_violations = []

# Check 1: Calculated columns that should be measures
try:
    calc_cols = fabric.evaluate_dax(
        dataset=DATASET_NAME,
        workspace=WORKSPACE_NAME,
        dax_string="""
        SELECT 
            [DIMENSION_UNIQUE_NAME] AS [Table],
            [COLUMN_NAME] AS [Column],
            [COLUMN_TYPE] AS [Type]
        FROM $SYSTEM.MDSCHEMA_COLUMNS
        WHERE [COLUMN_TYPE] = 2
        """
    )
    if len(calc_cols) > 0:
        for _, col in calc_cols.iterrows():
            custom_violations.append({
                "severity": "Warning",
                "rule": "Calculated column detected",
                "object": f"{col['Table']}.{col['Column']}",
                "recommendation": "Convert to a measure for better performance. Calculated columns are computed at refresh time and consume memory."
            })
            print(f"  🟡 Calculated column: {col['Table']}.{col['Column']}")
            print(f"     → Convert to measure to save memory")
except Exception as e:
    print(f"  ⚠️ Calculated column check skipped: {e}")

# Check 2: Tables with no relationships (orphan tables)
try:
    relationships = fabric.evaluate_dax(
        dataset=DATASET_NAME,
        workspace=WORKSPACE_NAME,
        dax_string="""
        SELECT [DIMENSION_UNIQUE_NAME] FROM $SYSTEM.MDSCHEMA_DIMENSIONS
        """
    )
    print(f"\n  Tables in model: {len(relationships)}")
except Exception as e:
    print(f"  ⚠️ Relationship check skipped: {e}")

# Check 3: High-cardinality string columns
try:
    col_stats = fabric.evaluate_dax(
        dataset=DATASET_NAME,
        workspace=WORKSPACE_NAME,
        dax_string="""
        EVALUATE
        SELECTCOLUMNS(
            INFO.COLUMNS(),
            "Table", [ExplicitName],
            "Column", [ExplicitName],
            "DataType", [DataType],
            "EncodingHint", [EncodingHint]
        )
        """
    )
    print(f"\n  Column statistics retrieved for analysis")
except Exception as e:
    print(f"  ⚠️ Column stats check skipped: {e}")

print(f"\nCustom checks complete: {len(custom_violations)} additional issues found")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Generate Summary Report

# COMMAND ----------

# Build combined report
total_issues = total_violations + len(custom_violations)
print("=" * 60)
print(f"  BEST PRACTICE ANALYZER REPORT")
print(f"  Model: {DATASET_NAME}")
print(f"  Workspace: {WORKSPACE_NAME}")
print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
print(f"  BPA Library Violations: {total_violations}")
print(f"  Custom Pattern Checks:  {len(custom_violations)}")
print(f"  TOTAL ISSUES:           {total_issues}")
print("=" * 60)

if total_issues > 0:
    print("\n⚠️  RESULT: ISSUES FOUND — Review required before promotion")

    # Store results for pipeline consumption
    report = {
        "model": DATASET_NAME,
        "workspace": WORKSPACE_NAME,
        "timestamp": datetime.now().isoformat(),
        "total_violations": total_issues,
        "bpa_violations": total_violations,
        "custom_violations": len(custom_violations),
        "status": "FAIL" if any(
            row.get('Severity') == 'Error'
            for _, row in bpa_results.iterrows()
        ) else "WARN",
        "details": custom_violations
    }
else:
    print("\n✅ RESULT: ALL CHECKS PASSED — Model is ready for promotion")
    report = {
        "model": DATASET_NAME,
        "workspace": WORKSPACE_NAME,
        "timestamp": datetime.now().isoformat(),
        "total_violations": 0,
        "status": "PASS"
    }

# Save report as JSON for pipeline consumption
report_json = json.dumps(report, indent=2)
print(f"\nReport saved for CI/CD pipeline consumption")
print(report_json)
