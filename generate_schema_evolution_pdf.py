#!/usr/bin/env python3
"""
Generate Digital Realty — Lakehouse Schema Evolution CI/CD Solution Approach PDF
Uses fpdf2 DemoPDF pattern from the workspace skill template.
"""

from fpdf import FPDF
import textwrap
import os


class SolutionPDF(FPDF):
    """PDF class for technical solution approach documents."""

    NAVY = (27, 42, 74)
    BLUE = (0, 120, 212)
    TEAL = (0, 130, 130)
    DARK = (40, 40, 40)
    MED_GRAY = (100, 100, 100)
    LIGHT_GRAY = (245, 245, 245)
    WHITE = (255, 255, 255)
    GREEN = (16, 124, 16)
    ORANGE = (200, 100, 0)
    RED = (180, 0, 0)
    LIGHT_BLUE = (232, 244, 253)
    LIGHT_GREEN = (232, 248, 232)
    LIGHT_ORANGE = (255, 243, 224)
    LIGHT_RED = (255, 232, 232)

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)
        # Load Unicode-capable fonts from Windows
        font_dir = "C:/Windows/Fonts"
        self.add_font("DejaVu", "", f"{font_dir}/arial.ttf", uni=True)
        self.add_font("DejaVu", "B", f"{font_dir}/arialbd.ttf", uni=True)
        self.add_font("DejaVu", "I", f"{font_dir}/ariali.ttf", uni=True)
        self.add_font("DejaVu", "BI", f"{font_dir}/arialbi.ttf", uni=True)
        self.add_font("Mono", "", f"{font_dir}/consola.ttf", uni=True)
        self.add_font("Mono", "B", f"{font_dir}/consolab.ttf", uni=True)

    def header(self):
        if self.page_no() <= 1:
            return
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, "Digital Realty | Lakehouse Schema Evolution - Solution Approach | Confidential", align="C")
        self.ln(4)
        self.set_draw_color(*self.BLUE)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    # ── Title Page ────────────────────────────────────────────────────

    def title_page(self):
        self.add_page()
        # Navy background
        self.set_fill_color(*self.NAVY)
        self.rect(0, 0, 210, 297, "F")
        # Blue accent bar
        self.set_fill_color(*self.BLUE)
        self.rect(0, 110, 210, 4, "F")

        self.ln(45)
        self.set_font("DejaVu", "B", 30)
        self.set_text_color(*self.WHITE)
        self.cell(0, 15, "Lakehouse Schema Evolution", align="C")
        self.ln(16)
        self.set_font("DejaVu", "", 20)
        self.set_text_color(176, 196, 222)
        self.cell(0, 12, "in Fabric CI/CD Pipelines", align="C")
        self.ln(30)

        self.set_font("DejaVu", "I", 14)
        self.set_text_color(180, 180, 200)
        self.cell(0, 10, "Solution Approach & Recommended Architecture", align="C")
        self.ln(35)

        details = [
            ("Prepared for:", "Digital Realty Trust"),
            ("Prepared by:", "GitHub Solutions Engineering"),
            ("Focus:", "CI/CD for Lakehouse Schema Changes"),
            ("Status:", "Recommended Approach"),
        ]
        self.set_font("DejaVu", "", 11)
        for label, val in details:
            self.set_x(50)
            self.set_font("DejaVu", "B", 11)
            self.set_text_color(180, 196, 222)
            self.cell(35, 9, label)
            self.set_font("DejaVu", "", 11)
            self.set_text_color(220, 220, 235)
            self.cell(0, 9, val)
            self.ln(9)

        # Bottom accent bar
        self.set_fill_color(*self.BLUE)
        self.rect(0, 280, 210, 4, "F")

    # ── Section Helpers ───────────────────────────────────────────────

    def section_title(self, number, title):
        self.add_page()
        self.set_fill_color(*self.NAVY)
        self.rect(10, self.get_y() - 2, 190, 18, "F")
        self.set_font("DejaVu", "B", 16)
        self.set_text_color(*self.WHITE)
        self.cell(0, 14, f"  {number}. {title}", align="L")
        self.ln(22)

    def sub_header(self, text):
        self.ln(3)
        self.set_font("DejaVu", "B", 13)
        self.set_text_color(*self.BLUE)
        self.cell(0, 10, text)
        self.ln(10)

    def sub_header_colored(self, text, color):
        self.ln(3)
        self.set_font("DejaVu", "B", 13)
        self.set_text_color(*color)
        self.cell(0, 10, text)
        self.ln(10)

    def body(self, text):
        self.set_font("DejaVu", "", 10)
        self.set_text_color(*self.DARK)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def bold_body(self, text):
        self.set_font("DejaVu", "B", 10)
        self.set_text_color(*self.DARK)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def bullet(self, text, indent=0):
        x = 15 + indent
        self.set_x(x)
        self.set_font("DejaVu", "", 10)
        self.set_text_color(*self.DARK)
        self.cell(5, 6, "-")
        max_w = 180 - indent
        self.multi_cell(max_w, 6, text)

    def numbered_item(self, num, text):
        self.set_x(15)
        self.set_font("DejaVu", "B", 10)
        self.set_text_color(*self.BLUE)
        self.cell(8, 6, f"{num}.")
        self.set_font("DejaVu", "", 10)
        self.set_text_color(*self.DARK)
        self.multi_cell(170, 6, text)

    def code_block(self, text):
        self.set_font("Mono", "", 8.5)
        self.set_text_color(30, 30, 30)
        self.set_fill_color(*self.LIGHT_GRAY)
        self.ln(2)
        for line in text.strip().split("\n"):
            self.set_x(15)
            self.cell(180, 5.2, f"  {line}", fill=True)
            self.ln(5.2)
        self.ln(3)
        self.set_font("DejaVu", "", 10)
        self.set_text_color(*self.DARK)

    def callout(self, text, bg_color=None, border_color=None):
        if bg_color is None:
            bg_color = self.LIGHT_BLUE
        if border_color is None:
            border_color = self.BLUE
        self.ln(2)
        y_start = self.get_y()
        self.set_fill_color(*bg_color)
        # Save position, write text to measure height
        self.set_x(15)
        self.set_font("DejaVu", "I", 10)
        self.set_text_color(30, 50, 90)
        self.set_x(20)
        self.multi_cell(170, 6, text, fill=False)
        y_end = self.get_y()
        height = y_end - y_start + 6
        # Draw background
        self.set_fill_color(*bg_color)
        self.rect(15, y_start - 3, 180, height, "F")
        # Draw left border
        self.set_draw_color(*border_color)
        self.set_line_width(1)
        self.line(15, y_start - 3, 15, y_start + height - 3)
        # Re-draw text
        self.set_xy(20, y_start)
        self.set_font("DejaVu", "I", 10)
        self.set_text_color(30, 50, 90)
        self.multi_cell(170, 6, text)
        self.ln(4)
        self.set_text_color(*self.DARK)

    def table(self, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)
        # Header
        self.set_font("DejaVu", "B", 9)
        self.set_fill_color(*self.NAVY)
        self.set_text_color(*self.WHITE)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 8, f" {h}", border=1, fill=True)
        self.ln(8)
        # Rows
        self.set_font("DejaVu", "", 9)
        for ri, row in enumerate(rows):
            if ri % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(240, 245, 255)
            self.set_text_color(*self.DARK)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 8, f" {cell}", border=1, fill=True)
            self.ln(8)
        self.ln(3)

    def divider(self):
        self.ln(3)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def approach_banner(self, label, title, color):
        self.ln(4)
        self.set_fill_color(*color)
        self.rect(10, self.get_y(), 190, 14, "F")
        self.set_font("DejaVu", "B", 12)
        self.set_text_color(*self.WHITE)
        self.cell(0, 12, f"  {label}: {title}")
        self.ln(18)

    def pro_con(self, pros, cons):
        self.set_font("DejaVu", "B", 10)
        self.set_text_color(*self.GREEN)
        self.cell(0, 7, "Strengths:")
        self.ln(7)
        for p in pros:
            self.set_x(18)
            self.set_font("DejaVu", "", 9)
            self.set_text_color(*self.DARK)
            self.cell(5, 5.5, "+")
            self.set_text_color(16, 124, 16)
            self.cell(0, 5.5, p)
            self.ln(5.5)

        self.ln(2)
        self.set_font("DejaVu", "B", 10)
        self.set_text_color(*self.RED)
        self.cell(0, 7, "Trade-offs:")
        self.ln(7)
        for c in cons:
            self.set_x(18)
            self.set_font("DejaVu", "", 9)
            self.set_text_color(*self.DARK)
            self.cell(5, 5.5, "-")
            self.set_text_color(140, 40, 40)
            self.cell(0, 5.5, c)
            self.ln(5.5)
        self.ln(3)


# ── Build the Document ────────────────────────────────────────────────

pdf = SolutionPDF()
pdf.alias_nb_pages()

# ══════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ══════════════════════════════════════════════════════════════════════
pdf.title_page()

# ══════════════════════════════════════════════════════════════════════
# SECTION 1: THE PROBLEM
# ══════════════════════════════════════════════════════════════════════
pdf.section_title("1", "The Problem")

pdf.body(
    "Microsoft Fabric provides Git integration that serializes most workspace artifacts — "
    "pipelines, semantic models, notebooks, Dataflow Gen2, reports — into version-controlled files. "
    "This enables standard CI/CD: branch, commit, PR, merge, promote across Dev / UAT / Prod."
)

pdf.body(
    "However, there is one critical gap: Lakehouse table schemas are NOT tracked by Git integration. "
    "When someone creates a table, adds a column, changes a data type, or modifies a schema through "
    "the Fabric UI or SQL Analytics Endpoint, those structural changes exist only in the Lakehouse — "
    "they are not serialized to Git."
)

pdf.callout(
    "The core issue: Fabric Git integration serializes the Lakehouse container metadata and the "
    "default dbo schema, but does NOT track tables, columns, or schema modifications. This means "
    "your CI/CD pipeline has no mechanism to propagate schema changes from Dev to UAT to Prod."
)

pdf.sub_header("What This Breaks")

pdf.bullet("Schema changes made in Dev never reach UAT or Prod through the deployment pipeline")
pdf.bullet("No audit trail for who changed what schema and when")
pdf.bullet("Manual schema recreation required in each environment — error-prone and unscalable")
pdf.bullet("Deployment pipelines succeed but target environments have stale or missing table structures")
pdf.bullet("Data quality checks fail silently because expected columns don't exist in the target")
pdf.ln(3)

pdf.sub_header("What Already Works")

pdf.body("It is important to note that most Fabric artifacts work correctly with Git integration:")

pdf.table(
    ["Artifact Type", "Git Tracked?", "Deployment Pipeline?", "CI/CD Status"],
    [
        ["Notebooks", "Yes", "Yes", "Working"],
        ["Pipelines (Data Factory)", "Yes", "Yes", "Working"],
        ["Semantic Models (TMDL)", "Yes", "Yes", "Working"],
        ["Dataflow Gen2", "Yes", "Yes (rules in preview)", "Working"],
        ["Reports (PBIR/PBIP)", "Yes", "Yes", "Working"],
        ["Lakehouse (container)", "Yes (metadata only)", "Yes", "Partial"],
        ["Lakehouse (table schemas)", "NO", "NO", "BROKEN"],
        ["Warehouse (T-SQL objects)", "Yes", "Yes", "Working"],
    ],
    [45, 35, 45, 65],
)

pdf.callout(
    "Key insight: Fabric Warehouse objects (tables, views, stored procedures) ARE tracked in Git "
    "because they are defined as T-SQL scripts. This is an important distinction that informs "
    "our solution approach.",
    bg_color=(232, 248, 232),
    border_color=(16, 124, 16),
)

# ══════════════════════════════════════════════════════════════════════
# SECTION 2: SOLUTION APPROACHES
# ══════════════════════════════════════════════════════════════════════
pdf.section_title("2", "Solution Approaches")

pdf.body(
    "We evaluated four approaches to bridge the Lakehouse schema gap. Each has different trade-offs "
    "for complexity, maintainability, and production-readiness. Our recommendation is Approach C "
    "(Hybrid), but we present all options so Digital Realty can choose what fits their team's maturity."
)

pdf.table(
    ["Approach", "Summary", "Complexity", "Recommended For"],
    [
        ["A: Schema-as-Code", "Notebooks define schemas via writes", "Low", "Quick wins, demos"],
        ["B: DDL Migration Scripts", "Explicit CREATE/ALTER T-SQL or Spark", "Medium", "Controlled evolution"],
        ["C: Hybrid (Recommended)", "Notebooks + Migration + Validation", "Medium", "Production CI/CD"],
        ["D: Warehouse-First", "Move schema-sensitive tables to Warehouse", "High", "Long-term architecture"],
    ],
    [35, 60, 30, 65],
)

# ── APPROACH A ────────────────────────────────────────────────────────
pdf.approach_banner("Approach A", "Schema-as-Code via Notebooks", (0, 120, 212))

pdf.body(
    "In this approach, PySpark notebooks are the source of truth for table schemas. Instead of "
    "creating tables through the Fabric UI, every table structure is defined as an explicit "
    "StructType schema in a notebook. When the notebook runs, it creates or recreates the table "
    "with the defined schema."
)

pdf.sub_header("How It Works")

pdf.numbered_item("1", "Define explicit schemas as StructType objects in the ingestion/transformation notebooks")
pdf.numbered_item("2", "Use .saveAsTable() with mode='overwrite' and overwriteSchema='true' to enforce the schema")
pdf.numbered_item("3", "Schema changes are code changes — edit the StructType, commit, PR, merge")
pdf.numbered_item("4", "When CI/CD promotes notebooks to UAT/Prod, the next notebook run applies the new schema")
pdf.ln(2)

pdf.sub_header("Example: Bronze Ingestion with Explicit Schema")

pdf.code_block("""# Schema is defined in code — this IS the version-controlled schema
FIXED_ASSETS_SCHEMA = StructType([
    StructField("asset_id", StringType(), False),
    StructField("asset_name", StringType(), False),
    StructField("category", StringType(), True),
    StructField("region", StringType(), True),
    StructField("acquisition_cost", DoubleType(), True),
    StructField("current_value", DoubleType(), True),
    StructField("status", StringType(), True),
])

df = (spark.read.option("header", "true")
    .schema(FIXED_ASSETS_SCHEMA)
    .csv("Files/sample-data/fixed_assets.csv"))

# This CREATE-or-REPLACE ensures schema matches code
df.write.format("delta").mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("bronze_fixed_assets")""")

pdf.sub_header("Why This Works for Schema Promotion")

pdf.body(
    "The schema definition lives in the notebook code, which IS tracked in Git. When the notebook "
    "is promoted from Dev to UAT via the deployment pipeline, the schema definition travels with it. "
    "The next scheduled or triggered run of the notebook in UAT applies the schema. No manual "
    "intervention needed."
)

pdf.pro_con(
    [
        "Lowest complexity — uses existing notebook patterns",
        "Schema definitions are version-controlled in Git automatically",
        "Works with current Fabric deployment pipelines — no API workarounds",
        "Schema and data transformation logic live together",
    ],
    [
        "Requires notebook execution to apply schema changes (not instant on deploy)",
        "overwriteSchema with overwrite mode causes brief data unavailability during refresh",
        "Does not handle additive-only changes (e.g., add column without full rewrite)",
        "Schema is scattered across multiple notebooks if many tables exist",
    ],
)

# ── APPROACH B ────────────────────────────────────────────────────────
pdf.approach_banner("Approach B", "DDL Migration Scripts", (0, 130, 130))

pdf.body(
    "This approach borrows from traditional database migration patterns (like Flyway or Liquibase). "
    "Schema changes are expressed as explicit DDL statements — CREATE TABLE, ALTER TABLE ADD COLUMN, "
    "ALTER TABLE ALTER COLUMN — in numbered migration scripts that run in sequence."
)

pdf.sub_header("How It Works")

pdf.numbered_item("1", "Maintain a /migrations folder with numbered Spark SQL or T-SQL scripts")
pdf.numbered_item("2", "Each migration has a unique version number and is idempotent (safe to re-run)")
pdf.numbered_item("3", "A migration runner notebook tracks which migrations have been applied (migration_history table)")
pdf.numbered_item("4", "On deployment, the runner executes only unapplied migrations in order")
pdf.ln(2)

pdf.sub_header("Example: Migration Scripts")

pdf.code_block("""# migrations/V001__create_bronze_fixed_assets.py
spark.sql(\"\"\"
    CREATE TABLE IF NOT EXISTS bronze_fixed_assets (
        asset_id STRING NOT NULL,
        asset_name STRING NOT NULL,
        category STRING,
        region STRING,
        acquisition_cost DOUBLE,
        status STRING,
        _ingested_at TIMESTAMP,
        _source_file STRING
    ) USING DELTA
\"\"\")""")

pdf.code_block("""# migrations/V002__add_current_value_column.py
spark.sql(\"\"\"
    ALTER TABLE bronze_fixed_assets
    ADD COLUMNS (current_value DOUBLE)
\"\"\")""")

pdf.code_block("""# migrations/V003__create_silver_regional_budgets.py
spark.sql(\"\"\"
    CREATE TABLE IF NOT EXISTS silver_regional_budgets (
        budget_id STRING NOT NULL,
        region STRING NOT NULL,
        variance DOUBLE,
        variance_pct DOUBLE,
        status STRING,
        _transformed_at TIMESTAMP
    ) USING DELTA
\"\"\")""")

pdf.sub_header("Migration Runner Pattern")

pdf.code_block("""# notebooks/00_run_migrations.py
import os

# Track applied migrations
spark.sql(\"\"\"
    CREATE TABLE IF NOT EXISTS _migration_history (
        version STRING, applied_at TIMESTAMP, checksum STRING
    ) USING DELTA
\"\"\")

applied = {r.version for r in spark.table("_migration_history").collect()}

for migration_file in sorted(os.listdir("/migrations")):
    version = migration_file.split("__")[0]  # e.g., "V001"
    if version not in applied:
        exec(open(f"/migrations/{migration_file}").read())
        spark.sql(f"INSERT INTO _migration_history VALUES ('{version}', current_timestamp(), '')")
        print(f"Applied {migration_file}")""")

pdf.pro_con(
    [
        "Fine-grained control — additive changes without full table rewrite",
        "Audit trail of every schema change with timestamps",
        "Familiar pattern for teams with SQL Server / database migration experience",
        "Supports rollback by writing reverse migration scripts",
    ],
    [
        "More files to manage — each schema change is a separate script",
        "Requires a migration runner notebook and tracking table",
        "Must ensure migrations are idempotent (re-runnable without error)",
        "Team discipline required — all schema changes must go through migration scripts",
    ],
)

# ── APPROACH C ────────────────────────────────────────────────────────
pdf.approach_banner("Approach C", "Hybrid: Notebooks + Migration + Validation (Recommended)", (16, 124, 16))

pdf.callout(
    "THIS IS OUR RECOMMENDED APPROACH. It combines the simplicity of Schema-as-Code with the "
    "rigor of migration tracking and the safety of automated validation. It works within Fabric's "
    "current capabilities and scales to production.",
    bg_color=(232, 248, 232),
    border_color=(16, 124, 16),
)

pdf.body(
    "The hybrid approach uses three layers working together. Each layer is a notebook, "
    "version-controlled in Git, and promoted through the standard Fabric deployment pipeline."
)

pdf.sub_header("Layer 1: Schema Registry Notebook")

pdf.body(
    "A single notebook (00_schema_registry.py) contains ALL table schemas as a Python dictionary. "
    "This is the canonical schema definition — the single source of truth. Any schema change "
    "starts here."
)

pdf.code_block("""# notebooks/00_schema_registry.py
# ============================================================
# SCHEMA REGISTRY — Single source of truth for all table schemas
# Version-controlled in Git, promoted via deployment pipeline
# ============================================================

SCHEMA_VERSION = "2.3.0"  # Semantic versioning for schema changes

SCHEMAS = {
    "bronze_fixed_assets": {
        "columns": [
            ("asset_id", "STRING", False),
            ("asset_name", "STRING", False),
            ("category", "STRING", True),
            ("region", "STRING", True),
            ("acquisition_cost", "DOUBLE", True),
            ("current_value", "DOUBLE", True),  # Added in v2.1.0
            ("status", "STRING", True),
            ("_ingested_at", "TIMESTAMP", True),
            ("_source_file", "STRING", True),
        ],
        "partition_by": ["region"],
        "primary_key": ["asset_id"],
    },
    "silver_fixed_assets": {
        "columns": [
            ("asset_id", "STRING", False),
            ("asset_name", "STRING", False),
            ("region", "STRING", True),
            ("acquisition_cost", "DOUBLE", True),
            ("net_book_value", "DOUBLE", True),
            ("annual_depreciation", "DOUBLE", True),
            ("age_years", "DOUBLE", True),
            ("_transformed_at", "TIMESTAMP", True),
        ],
        "partition_by": ["region"],
        "primary_key": ["asset_id"],
    },
    # ... all other tables defined here
}""")

pdf.sub_header("Layer 2: Schema Enforcer (Migration Logic)")

pdf.body(
    "A schema enforcer notebook reads the registry and applies changes. It compares the registry "
    "definition against the actual table in the Lakehouse and applies only the needed changes "
    "(additive columns, type widening). Destructive changes require explicit flags."
)

pdf.code_block("""# notebooks/00_apply_schema.py
from pyspark.sql.types import *

def enforce_schema(table_name, expected_schema):
    if not spark.catalog.tableExists(table_name):
        # Create table from scratch
        cols = ", ".join(
            f"{c[0]} {c[1]}" + (" NOT NULL" if not c[2] else "")
            for c in expected_schema["columns"]
        )
        spark.sql(f"CREATE TABLE {table_name} ({cols}) USING DELTA")
        print(f"  Created {table_name}")
        return

    # Compare existing vs expected
    existing = {f.name: f.dataType.simpleString()
                for f in spark.table(table_name).schema.fields}
    for col_name, col_type, nullable in expected_schema["columns"]:
        if col_name not in existing:
            spark.sql(f"ALTER TABLE {table_name} ADD COLUMNS ({col_name} {col_type})")
            print(f"  Added column {col_name} to {table_name}")

for table_name, schema_def in SCHEMAS.items():
    enforce_schema(table_name, schema_def)""")

pdf.sub_header("Layer 3: Schema Validation (Quality Gate)")

pdf.body(
    "The data quality notebook validates that actual table schemas match the registry. "
    "This runs after every deployment and after every data pipeline run. If schemas drift, "
    "the pipeline fails loudly."
)

pdf.code_block("""# In 03_data_quality_checks.py — add schema validation
def validate_schema(table_name, expected_schema):
    actual_fields = {f.name for f in spark.table(table_name).schema.fields}
    expected_fields = {c[0] for c in expected_schema["columns"]}

    missing = expected_fields - actual_fields
    if missing:
        raise Exception(
            f"SCHEMA DRIFT: {table_name} is missing columns: {missing}"
        )
    print(f"  Schema OK: {table_name} ({len(actual_fields)} columns)")""")

pdf.sub_header("CI/CD Flow with Hybrid Approach")

pdf.body("Here is how the three layers work together in the deployment pipeline:")

pdf.ln(2)
pdf.numbered_item("1", "Developer modifies 00_schema_registry.py (adds column, new table, etc.)")
pdf.numbered_item("2", "Developer updates the transformation notebook to use the new column")
pdf.numbered_item("3", "Developer updates 03_data_quality_checks.py to validate the new schema")
pdf.numbered_item("4", "Commit, PR, code review, merge to main")
pdf.numbered_item("5", "Fabric Git Sync pulls the updated notebooks into the Dev workspace")
pdf.numbered_item("6", "Dev pipeline runs: 00_apply_schema -> 01_ingest -> 02_transform -> 03_quality")
pdf.numbered_item("7", "Deployment pipeline promotes notebooks to UAT (schema travels with the code)")
pdf.numbered_item("8", "UAT pipeline runs: 00_apply_schema detects new column, runs ALTER TABLE")
pdf.numbered_item("9", "03_quality validates schema matches registry — pipeline passes")
pdf.numbered_item("10", "Same flow for Prod after UAT approval")
pdf.ln(2)

pdf.pro_con(
    [
        "Single source of truth for all schemas (00_schema_registry.py)",
        "Additive changes without full table rewrite (ALTER TABLE for new columns)",
        "Automated drift detection catches manual UI changes",
        "Works entirely within existing Fabric deployment pipeline — no external tools",
        "Schema versioning provides audit trail and rollback reference",
        "Validation layer prevents broken schemas from reaching production",
    ],
    [
        "Requires notebook execution after deployment (not instant schema apply)",
        "Team must adopt the discipline of 'schema changes start in the registry'",
        "Breaking changes (type narrowing, column removal) need careful handling",
    ],
)

# ── APPROACH D ────────────────────────────────────────────────────────
pdf.approach_banner("Approach D", "Warehouse-First for Schema-Sensitive Tables", (100, 100, 100))

pdf.body(
    "This approach acknowledges that Fabric Warehouses DO track their schemas in Git (as T-SQL "
    "scripts). For tables where schema evolution is frequent and must be tightly controlled, move "
    "those tables from Lakehouse to Warehouse. Keep the Lakehouse for raw/bronze data where schema "
    "flexibility matters more than strict versioning."
)

pdf.sub_header("When to Consider This")

pdf.bullet("Tables with frequent schema changes driven by business requirements")
pdf.bullet("Regulatory or compliance requirements for schema audit trails")
pdf.bullet("Teams with strong T-SQL skills who prefer DDL-based schema management")
pdf.bullet("Long-term architecture planning (Fabric Warehouse Git support will improve over time)")
pdf.ln(3)

pdf.sub_header("Architecture Split")

pdf.table(
    ["Data Layer", "Storage", "Why"],
    [
        ["Bronze (raw ingestion)", "Lakehouse", "Schema flexibility, Delta format, Spark-native"],
        ["Silver (curated)", "Warehouse", "Schema versioning via Git, T-SQL DDL, strict typing"],
        ["Gold (aggregates)", "Warehouse", "Report-facing, TMDL integration, full Git tracking"],
    ],
    [40, 40, 110],
)

pdf.pro_con(
    [
        "Native Git tracking for Warehouse schemas — the gap disappears entirely",
        "T-SQL DDL is the industry standard for schema management",
        "Deployment pipelines handle Warehouse schemas natively",
        "Clear separation: Lakehouse for flexibility, Warehouse for governance",
    ],
    [
        "Significant architecture change — moving tables between engines",
        "Cross-engine queries (Lakehouse to Warehouse) add complexity",
        "DirectLake semantic models require Lakehouse — Warehouse uses Import or DirectQuery",
        "Higher initial effort; only justified if schema evolution is a persistent pain point",
    ],
)

# ══════════════════════════════════════════════════════════════════════
# SECTION 3: WHY WE RECOMMEND APPROACH C
# ══════════════════════════════════════════════════════════════════════
pdf.section_title("3", "Why We Recommend Approach C (Hybrid)")

pdf.body(
    "After evaluating all four approaches against Digital Realty's requirements — automated CI/CD "
    "across three environments, minimal manual intervention, audit trail, and compatibility with "
    "existing Fabric deployment pipelines — we recommend Approach C for the following reasons:"
)

pdf.sub_header("1. It Works Within Fabric's Current Capabilities")

pdf.body(
    "Approach C does not require any Fabric features that don't exist yet. It uses notebooks "
    "(which are fully Git-tracked), Delta table DDL (ALTER TABLE, CREATE TABLE), and standard "
    "deployment pipelines. There is no dependency on a future Fabric update or preview feature."
)

pdf.sub_header("2. It Solves the Actual Problem: Schema Promotion")

pdf.body(
    "The customer's core ask is: 'How do we ensure schema consistency across Dev, UAT, and Prod?' "
    "The hybrid approach answers this directly — schemas are defined in code, travel through Git, "
    "and are applied automatically in each environment. The schema enforcer handles the gap between "
    "'notebook promoted' and 'schema applied' by running ALTER TABLE for any missing columns."
)

pdf.sub_header("3. It Prevents Schema Drift")

pdf.body(
    "The validation layer (Layer 3) is the safety net. If someone bypasses the process and makes a "
    "schema change directly in the Fabric UI, the next pipeline run will detect the drift and "
    "either correct it (if additive) or fail loudly (if incompatible). This is critical for "
    "production environments where untracked changes can break downstream reports and models."
)

pdf.sub_header("4. It Scales Incrementally")

pdf.body(
    "Digital Realty can adopt this approach incrementally. Start with the schema registry for "
    "the most critical tables, add the enforcer, then add validation. It does not require a "
    "big-bang migration or architecture overhaul. Existing notebooks continue to work — you're "
    "adding a layer on top, not replacing what's already working."
)

pdf.sub_header("5. It Provides an Audit Trail")

pdf.body(
    "Every schema change is a Git commit with a PR, a reviewer, and a timestamp. The "
    "SCHEMA_VERSION field in the registry makes it easy to correlate schema states with "
    "deployments. This satisfies governance and compliance requirements without additional tooling."
)

# ══════════════════════════════════════════════════════════════════════
# SECTION 4: IMPLEMENTATION ROADMAP
# ══════════════════════════════════════════════════════════════════════
pdf.section_title("4", "Implementation Roadmap")

pdf.body("We recommend a phased rollout to minimize risk and build team confidence:")

pdf.sub_header("Phase 1: Schema Registry + Enforcer")

pdf.bullet("Create 00_schema_registry.py with definitions for all existing Lakehouse tables")
pdf.bullet("Create 00_apply_schema.py with the enforce_schema() function")
pdf.bullet("Run against Dev to verify it correctly identifies the current state (no-op on first run)")
pdf.bullet("Add to the notebook execution pipeline: 00_apply_schema runs BEFORE 01_ingestion")
pdf.ln(2)

pdf.sub_header("Phase 2: Validation Integration")

pdf.bullet("Add schema validation checks to 03_data_quality_checks.py")
pdf.bullet("Configure the pipeline to fail on schema drift detection")
pdf.bullet("Test by making a manual UI change in Dev and observing the validation failure")
pdf.ln(2)

pdf.sub_header("Phase 3: CI/CD Pipeline Integration")

pdf.bullet("Add a GitHub Actions workflow that triggers schema enforcement post-deployment")
pdf.bullet("Integrate with the existing promote-with-change-detection workflow")
pdf.bullet("Add schema version to the deployment change report for reviewer visibility")
pdf.ln(2)

pdf.sub_header("Phase 4: Governance Hardening")

pdf.bullet("Lock down Lakehouse UI write access in UAT and Prod (viewer-only for most users)")
pdf.bullet("Require PR approval for any change to 00_schema_registry.py")
pdf.bullet("Add automated schema diff comments to PRs when the registry changes")
pdf.bullet("Evaluate Approach D (Warehouse-First) for tables with the most frequent schema changes")
pdf.ln(2)

# ══════════════════════════════════════════════════════════════════════
# SECTION 5: NOTEBOOK EXECUTION ORDER
# ══════════════════════════════════════════════════════════════════════
pdf.section_title("5", "Updated Notebook Execution Order")

pdf.body("With the hybrid approach, the notebook execution order becomes:")

pdf.table(
    ["Order", "Notebook", "Purpose", "Layer"],
    [
        ["0", "00_schema_registry.py", "Schema definitions (imported, not run directly)", "Config"],
        ["1", "00_apply_schema.py", "Compare registry vs actual, apply ALTER/CREATE", "Schema"],
        ["2", "01_data_ingestion.py", "Load source data into bronze_* Delta tables", "Bronze"],
        ["3", "02_data_transformation.py", "Transform bronze to silver_* with business logic", "Silver"],
        ["4", "03_data_quality_checks.py", "Validate data AND schema, fail on drift", "Quality"],
    ],
    [15, 50, 75, 50],
)

pdf.callout(
    "The schema enforcer (step 1) runs BEFORE data ingestion so that new columns exist before "
    "data tries to write to them. The quality checker (step 4) runs AFTER transformation to "
    "validate that everything is consistent end-to-end."
)

# ══════════════════════════════════════════════════════════════════════
# SECTION 6: COMPARISON MATRIX
# ══════════════════════════════════════════════════════════════════════
pdf.section_title("6", "Approach Comparison Matrix")

pdf.table(
    ["Criteria", "A: Schema-Code", "B: DDL Migration", "C: Hybrid", "D: Warehouse"],
    [
        ["Implementation effort", "Low", "Medium", "Medium", "High"],
        ["Schema version control", "Implicit", "Explicit", "Explicit", "Native"],
        ["Additive changes", "Full rewrite", "ALTER TABLE", "ALTER TABLE", "ALTER TABLE"],
        ["Breaking changes", "Full rewrite", "Migration script", "Flagged + review", "T-SQL DDL"],
        ["Drift detection", "None", "None", "Automated", "Git-native"],
        ["Audit trail", "Git commits", "Migration history", "Git + versioning", "Git-native"],
        ["Fabric compatibility", "Full", "Full", "Full", "Requires arch change"],
        ["DirectLake support", "Yes", "Yes", "Yes", "No (Import/DQ)"],
        ["Production readiness", "Demo/POC", "Good", "Production", "Production"],
    ],
    [35, 35, 35, 35, 40],
)

# ══════════════════════════════════════════════════════════════════════
# SECTION 7: NEXT STEPS
# ══════════════════════════════════════════════════════════════════════
pdf.section_title("7", "Recommended Next Steps")

pdf.numbered_item("1",
    "Technical deep-dive session: Walk through the hybrid approach with Digital Realty's "
    "data engineering team. Review their current notebook structure and identify which tables "
    "need schema governance first."
)
pdf.ln(2)
pdf.numbered_item("2",
    "GitHub + SDLC demo with Fabric product group: Coordinate the session mentioned in "
    "Digital Realty's request. This would cover Git integration roadmap, upcoming schema "
    "tracking improvements, and best-practice CI/CD patterns."
)
pdf.ln(2)
pdf.numbered_item("3",
    "Proof of concept: Implement Approach C for 2-3 representative tables in the Dev "
    "workspace. Validate the full cycle: schema change in registry -> PR -> merge -> "
    "Git sync -> schema enforcement -> data pipeline -> quality validation."
)
pdf.ln(2)
pdf.numbered_item("4",
    "CI/CD pipeline update: Extend the existing promote-with-change-detection workflow "
    "to include schema version tracking and post-deployment schema enforcement."
)
pdf.ln(2)
pdf.numbered_item("5",
    "Production rollout: After POC validation, roll out to all Lakehouse tables across "
    "Dev, UAT, and Prod workspaces."
)

pdf.ln(8)
pdf.divider()
pdf.set_font("DejaVu", "I", 10)
pdf.set_text_color(*pdf.MED_GRAY)
pdf.multi_cell(0, 6,
    "This document was prepared by GitHub Solutions Engineering for Digital Realty Trust. "
    "The approaches described here are based on current Microsoft Fabric capabilities as of "
    "April 2026 and proven patterns from similar enterprise Fabric deployments."
)

# ── Output ────────────────────────────────────────────────────────────
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "DigitalRealty_Lakehouse_Schema_Evolution.pdf")
pdf.output(output_path)
print(f"PDF generated: {output_path}")
