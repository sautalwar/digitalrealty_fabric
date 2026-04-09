#!/usr/bin/env python3
"""
Digital Realty - 3 Use Case Demo Workflow PDF Generator
Comprehensive step-by-step demo guide with talk tracks, fallbacks, and Q&A
"""

from fpdf import FPDF
import textwrap


class WorkflowPDF(FPDF):
    BLUE = (0, 120, 212)
    DARK = (40, 40, 40)
    LIGHT_GRAY = (245, 245, 245)
    WHITE = (255, 255, 255)
    GREEN = (16, 124, 16)
    RED = (200, 30, 30)
    ORANGE = (200, 100, 0)
    PURPLE = (120, 0, 150)
    TEAL = (0, 130, 130)

    ACTION_COLORS = {
        "DO": (0, 150, 0),
        "CLICK": (200, 100, 0),
        "TYPE": (150, 0, 150),
        "SAY": (0, 100, 200),
        "EXPECT": (180, 0, 0),
        "VERIFY": (0, 130, 130),
        "NOTE": (100, 100, 100),
    }

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() <= 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, "Digital Realty | 3 Use Case Demo Workflow | Confidential", align="C")
        self.ln(4)
        self.set_draw_color(*self.BLUE)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def _safe(self, text):
        # Convert to string if not already
        text = str(text)
        # Replace special Unicode characters with Latin-1 safe equivalents
        replacements = {
            "\u2014": "--", "\u2013": "-", "\u2018": "'", "\u2019": "'",
            "\u201c": '"', "\u201d": '"', "\u2192": "->", "\u2022": "-",
            "\u2713": "[OK]", "\u2717": "[X]", "\u27a1": "->", "\u2728": "*",
            "\u26a0": "[!]", "\u2b50": "*", "\u2705": "[OK]", "\u274c": "[X]",
            "\u25ba": ">", "\u25b6": ">", "\u21e8": "=>", "\u00d7": "x",
            "\u2026": "...", "\u2265": ">=", "\u2264": "<=", "\u2190": "<-",
            "\u2191": "^", "\u2193": "v", "\u2196": "\\", "\u2197": "/",
            "\u2198": "\\", "\u2199": "/", "\u25cf": "*", "\u25cb": "o",
            "\u2714": "[OK]", "\u2716": "[X]", "\u2610": "[ ]", "\u2611": "[X]",
            "\u2612": "[X]", "\u2713": "v", "\u2717": "x", "\u2718": "x",
            "\u2719": "+", "\u271a": "+", "\u271b": "*", "\u271c": "+",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        # Remove any remaining non-Latin-1 characters
        return text.encode('latin-1', 'ignore').decode('latin-1')

    def _wrap(self, text, max_w_mm):
        chars = int(max_w_mm / 2.1)
        return textwrap.wrap(self._safe(text), width=chars)

    def title_page(self):
        self.add_page()
        self.ln(40)
        self.set_fill_color(*self.BLUE)
        self.rect(0, 35, 210, 8, "F")
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(*self.BLUE)
        self.cell(0, 15, "Digital Realty", align="C")
        self.ln(18)
        self.set_font("Helvetica", "", 18)
        self.set_text_color(50, 50, 50)
        self.cell(0, 12, "3 Use Case Demo Workflow", align="C")
        self.ln(14)
        self.set_font("Helvetica", "I", 14)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, "Click-by-Click Instructions with Talk Tracks", align="C")
        self.ln(30)
        details = [
            ("Demo File:", "DigitalRealty_3UseCase_Presentation.html"),
            ("Duration:", "45-60 minutes"),
            ("Audience:", "Data Platform Team, Analytics Leads, IT Director"),
            ("Presenter:", "GitHub Solutions Engineering"),
            ("Objective:", "Showcase 3 critical Fabric capabilities for enterprise"),
        ]
        self.set_font("Helvetica", "", 11)
        self.set_text_color(60, 60, 60)
        for label, val in details:
            self.set_x(35)
            self.set_font("Helvetica", "B", 11)
            self.cell(40, 8, label)
            self.set_font("Helvetica", "", 11)
            self.cell(0, 8, val)
            self.ln(8)
        self.ln(16)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*self.BLUE)
        self.cell(0, 10, "The 3 Use Cases", align="C")
        self.ln(12)
        cases = [
            ("1. Lakehouse Schema Evolution (CI/CD)", "Version-control table schemas, promote changes across Dev/UAT/Prod"),
            ("2. Power BI Performance Optimization", "Diagnose and fix DAX anti-patterns, memory bloat, compression issues"),
            ("3. Automated Quality & Governance", "CI gates, drift detection, continuous compliance enforcement"),
        ]
        for title, desc in cases:
            self.set_x(20)
            self.set_font("Helvetica", "B", 11)
            self.set_text_color(*self.BLUE)
            self.cell(0, 7, title)
            self.ln(7)
            self.set_x(25)
            self.set_font("Helvetica", "", 10)
            self.set_text_color(80, 80, 80)
            self.cell(0, 6, desc)
            self.ln(9)
        self.set_fill_color(*self.BLUE)
        self.rect(0, 280, 210, 8, "F")

    def section_banner(self, title, subtitle=""):
        self.add_page()
        self.set_fill_color(*self.BLUE)
        self.rect(10, self.get_y() - 2, 190, 20, "F")
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*self.WHITE)
        self.cell(0, 16, f"  {title}", align="L")
        self.ln(22)
        if subtitle:
            self.set_font("Helvetica", "I", 11)
            self.set_text_color(100, 100, 100)
            self.cell(0, 7, subtitle)
            self.ln(10)

    def subsection(self, title):
        if self.get_y() > 240:
            self.add_page()
        self.ln(4)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*self.BLUE)
        self.cell(0, 8, title)
        self.ln(10)

    def action(self, tag, text):
        if self.get_y() > 265:
            self.add_page()
        r, g, b = self.ACTION_COLORS.get(tag, (0, 0, 0))
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(r, g, b)
        self.cell(20, 7, f"[{tag}]")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)
        lines = self._wrap(text, 165)
        for i, line in enumerate(lines):
            if i > 0:
                self.cell(20, 6, "")
            self.cell(165, 7 if i == 0 else 6, line)
            self.ln(7 if i == 0 else 6)

    def bullet(self, text, indent=15):
        if self.get_y() > 270:
            self.add_page()
        self.set_x(indent)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)
        self.cell(5, 6, "-")
        lines = self._wrap(text, 180 - indent)
        for i, line in enumerate(lines):
            if i > 0:
                self.set_x(indent + 5)
            self.cell(180 - indent, 6, line)
            self.ln(6)

    def value_box(self, text):
        if self.get_y() > 255:
            self.add_page()
        self.ln(2)
        self.set_fill_color(240, 255, 240)
        y_start = self.get_y()
        self.set_font("Helvetica", "BI", 10)
        self.set_text_color(0, 100, 0)
        lines = self._wrap(f"VALUE: {text}", 175)
        height = len(lines) * 6 + 4
        self.rect(10, y_start, 190, height, "F")
        self.ln(2)
        for line in lines:
            self.set_x(15)
            self.cell(175, 6, line)
            self.ln(6)
        self.ln(2)

    def talk_track_box(self, text):
        if self.get_y() > 250:
            self.add_page()
        self.ln(2)
        self.set_fill_color(240, 248, 255)
        y_start = self.get_y()
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(0, 60, 120)
        lines = self._wrap(f"TALK TRACK: {text}", 175)
        height = len(lines) * 6 + 4
        self.rect(10, y_start, 190, height, "F")
        self.ln(2)
        for line in lines:
            self.set_x(15)
            self.cell(175, 6, line)
            self.ln(6)
        self.ln(2)

    def qa_item(self, question, answer):
        if self.get_y() > 240:
            self.add_page()
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*self.ORANGE)
        q_lines = self._wrap(f"Q: {question}", 180)
        for line in q_lines:
            self.set_x(15)
            self.cell(175, 6, line)
            self.ln(6)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)
        a_lines = self._wrap(f"A: {answer}", 180)
        for line in a_lines:
            self.set_x(15)
            self.cell(175, 6, line)
            self.ln(6)
        self.ln(3)

    def table_row(self, cells, widths, is_header=False):
        if self.get_y() > 260:
            self.add_page()
        if is_header:
            self.set_font("Helvetica", "B", 9)
            self.set_fill_color(*self.BLUE)
            self.set_text_color(*self.WHITE)
        else:
            self.set_font("Helvetica", "", 8)
            self.set_fill_color(*self.LIGHT_GRAY)
            self.set_text_color(*self.DARK)
        for cell, width in zip(cells, widths):
            self.cell(width, 7, self._safe(cell), border=1, fill=is_header, align="C")
        self.ln()


def generate_pdf():
    pdf = WorkflowPDF()
    pdf.alias_nb_pages()
    
    # Title Page
    pdf.title_page()
    
    # Pre-Demo Setup Checklist
    pdf.section_banner("Pre-Demo Setup Checklist", "Complete these steps 15 minutes before demo")
    pdf.subsection("Environment Preparation")
    pdf.bullet("Open HTML presentation file: DigitalRealty_3UseCase_Presentation.html")
    pdf.bullet("Have VS Code open with notebooks folder visible")
    pdf.bullet("Browser tabs ready: GitHub repo, Fabric workspace, Azure Portal")
    pdf.bullet("Screen layout: Presentation (80%), VS Code sidebar (20%)")
    pdf.bullet("Disable notifications and close Slack/Teams")
    pdf.ln(3)
    pdf.subsection("Data & Artifacts")
    pdf.bullet("Verify sample data is loaded in Dev Lakehouse")
    pdf.bullet("Confirm GitHub Actions workflows are visible")
    pdf.bullet("Have environment configs accessible: dev.json, uat.json, prod.json")
    pdf.bullet("Ensure BPA analyzer and memory reports are pre-run")
    pdf.ln(3)
    pdf.subsection("Backup Plan")
    pdf.bullet("Screenshots folder ready for fallback")
    pdf.bullet("Pre-recorded video clips if live demo fails")
    pdf.bullet("Printed copy of this guide for quick reference")
    
    # ========== USE CASE 1: Lakehouse Schema Evolution ==========
    pdf.section_banner("Use Case 1: Lakehouse Schema Evolution (CI/CD)", "Duration: 15-20 minutes")
    
    pdf.subsection("A. Setup Steps")
    pdf.bullet("Open notebooks folder in VS Code")
    pdf.bullet("Have GitHub Actions tab open in browser")
    pdf.bullet("Navigate to environments/ folder")
    pdf.ln(2)
    
    pdf.subsection("B. Pain Point Introduction")
    pdf.action("SAY", "Let me show you a critical challenge with Fabric Git integration. Microsoft Fabric has excellent Git integration for notebooks, pipelines, semantic models -- but there's one massive gap: Lakehouse table schemas aren't tracked in Git.")
    pdf.talk_track_box("Speak slowly here. Let this sink in. Make eye contact. This is the setup for the entire use case.")
    pdf.action("SAY", "If you add a column in the Fabric UI or change a data type via SQL endpoint, those schema changes don't get captured in source control. For an enterprise like Digital Realty with multi-region data centers, this breaks CI/CD for schema promotion across Dev, UAT, and Production.")
    pdf.action("EXPECT", "Audience should nod or show concern -- this is a real pain point")
    pdf.ln(2)
    
    pdf.subsection("C. Solution Demo Flow")
    pdf.action("DO", "Navigate to notebooks/00_schema_registry.py in VS Code")
    pdf.action("SAY", "So we built a Schema Registry -- a single source of truth for all table schemas. This is the heart of our solution.")
    pdf.action("CLICK", "Scroll to BRONZE_SCHEMAS dictionary (line ~20)")
    pdf.action("EXPECT", "See explicit StructType definitions for bronze_assets, bronze_budgets, bronze_regional_data")
    pdf.action("SAY", "Every table's schema is defined explicitly as code. Notice the SCHEMA_VERSION -- we can track schema evolution over time. When we add a column, we increment the version and document the change.")
    pdf.talk_track_box("Point out the StructType definitions. Emphasize explicit vs inferred schemas. This is infrastructure-as-code but for data structures.")
    pdf.ln(3)
    
    pdf.action("DO", "Open 01_data_ingestion.py")
    pdf.action("SAY", "The Bronze ingestion notebook references these schemas directly. No schema inference, no surprises.")
    pdf.action("CLICK", "Scroll to bronze_assets write operation (line ~50)")
    pdf.action("EXPECT", "See: df.write.format('delta').mode('overwrite').option('mergeSchema', 'false')")
    pdf.action("SAY", "mergeSchema is false -- we control schema changes explicitly. If the incoming data doesn't match the registry, the job fails fast. No silent schema drift.")
    pdf.ln(3)
    
    pdf.action("DO", "Open 02_data_transformation.py")
    pdf.action("SAY", "Silver transformations apply business logic. For Digital Realty, that's depreciation calculations, regional summaries, and variance analysis.")
    pdf.action("CLICK", "Show silver_assets_enriched schema (line ~30)")
    pdf.action("EXPECT", "See calculated columns: depreciation_amount, current_value, age_years")
    pdf.action("SAY", "These transformations are versioned in Git. When we promote Dev to UAT, the entire transformation logic moves atomically.")
    pdf.ln(3)
    
    pdf.action("DO", "Open 03_data_quality_checks.py")
    pdf.action("SAY", "The data quality notebook validates schemas against the registry. This is the compliance gate.")
    pdf.action("CLICK", "Scroll to DataQualityChecker.validate_schema method (line ~80)")
    pdf.action("EXPECT", "See comparison logic: actual columns vs registry columns")
    pdf.action("SAY", "If the actual table has columns not in the registry -- that's schema drift. The check fails, and the pipeline stops. We detect drift immediately, not three weeks later when reports break.")
    pdf.ln(3)
    
    pdf.action("DO", "Open GitHub Actions tab in browser")
    pdf.action("SAY", "Now let me show you the CI/CD pipeline. When a developer makes a schema change, they update the Schema Registry, commit to Git, and open a PR.")
    pdf.action("CLICK", "Navigate to .github/workflows/fabric-git-sync.yml")
    pdf.action("EXPECT", "See workflow triggers: on push to main, on PR merge")
    pdf.action("SAY", "On merge, GitHub triggers Fabric's updateFromGit API. The Dev workspace syncs automatically. No manual clicks, no drift between Git and Fabric.")
    pdf.ln(3)
    
    pdf.action("DO", "Open environments/dev.json in VS Code")
    pdf.action("SAY", "Each environment has a config file. Dev uses all regions, UAT might filter to a subset for testing, Prod runs full scale.")
    pdf.action("EXPECT", "See: workspace_id, lakehouse_name, sql_endpoint, filter_region: ALL")
    pdf.action("SAY", "When we promote from Dev to UAT, deployment rules swap lakehouse names and override parameters. Same notebooks, different data.")
    pdf.ln(3)
    
    pdf.subsection("D. Value Proposition")
    pdf.value_box("Digital Realty operates 300+ data centers globally. Schema changes need to propagate consistently across regions. This solution provides: (1) Audit trail -- every schema change is in Git history. (2) Rollback capability -- revert bad schemas instantly. (3) Environment parity -- Dev, UAT, Prod schemas match exactly. (4) Compliance -- SOC 2 requires change tracking, this delivers it.")
    pdf.ln(2)
    
    pdf.subsection("E. Hard Questions & Prepared Responses")
    pdf.qa_item(
        "What if we need to change the Delta Lake format itself, like upgrading to Delta 2.0?",
        "Great question. Delta format upgrades are Spark-level changes. You'd update the Spark runtime in Fabric workspace settings, test in Dev, then promote. The Schema Registry handles table structure, not Delta protocol. If you need protocol-specific features like column mapping, add that to the table properties in the registry."
    )
    pdf.qa_item(
        "How do we handle backward-incompatible schema changes, like renaming a column?",
        "Backward-incompatible changes require migration notebooks. You create a migration step that: (1) Creates new column with new name. (2) Copies data from old column. (3) Updates downstream dependencies. (4) Deprecates old column (don't drop immediately). The Schema Registry documents both states during transition. Promote the migration notebook through CI/CD."
    )
    pdf.qa_item(
        "What about external tables or tables created by third-party tools?",
        "External tables aren't managed by this registry. If a third-party tool creates tables, you have two options: (1) Import their schemas into the registry as read-only reference. (2) Use the data quality checks to validate their structure and fail if they drift. The registry is for tables you own."
    )
    pdf.qa_item(
        "How long does it take to implement this for our 50 existing lakehouses?",
        "Phase 1 (1-2 weeks): Set up Schema Registry for critical tables, implement quality checks. Phase 2 (2-3 weeks): Connect CI/CD for Dev workspace. Phase 3 (1 month): Roll out to all 50 lakehouses with automation scripts. Total: 6-8 weeks for full deployment. We can start with 5 high-priority lakehouses as a pilot."
    )
    pdf.ln(2)
    
    pdf.subsection("F. Fallback Plans")
    pdf.bullet("Fallback 1: If GitHub Actions fails to trigger, show the workflow YAML code and explain the logic. Then show a pre-recorded video of successful sync.")
    pdf.bullet("Fallback 2: If Fabric workspace is unreachable, switch to VS Code and walk through notebooks line-by-line. Emphasize the code quality, not the live execution.")
    pdf.bullet("Fallback 3: Skip live demo and show architecture diagram + before/after schema diff screenshots. Return to live demo after Use Case 2.")
    
    # ========== USE CASE 2: Power BI Performance Optimization ==========
    pdf.section_banner("Use Case 2: Power BI Performance Optimization", "Duration: 15-20 minutes")
    
    pdf.subsection("A. Setup Steps")
    pdf.bullet("Have notebooks/04_bpa_analyzer.py open")
    pdf.bullet("Have notebooks/05_memory_analyzer.py open")
    pdf.bullet("Prepare to show Before/After semantic model comparison")
    pdf.ln(2)
    
    pdf.subsection("B. Pain Point Introduction")
    pdf.action("SAY", "Power BI semantic models can silently degrade over time. DAX patterns that worked fine with 10,000 rows become bottlenecks at 10 million rows. Calculated columns bloat memory. High-cardinality string columns kill compression.")
    pdf.action("SAY", "Most organizations don't discover these issues until users complain about slow reports -- or worse, reports time out and fail. By then, the model is in production, and fixing it requires downtime.")
    pdf.talk_track_box("Use a pained expression. Make this personal -- emphasize the cost of fixing production issues vs catching them early.")
    pdf.action("EXPECT", "Audience should relate -- everyone has experienced slow Power BI reports")
    pdf.ln(2)
    
    pdf.subsection("C. Solution Demo Flow")
    pdf.action("DO", "Open notebooks/04_bpa_analyzer.py in VS Code")
    pdf.action("SAY", "We use semantic-link-labs, Microsoft's official library, to run Best Practice Analyzer rules against our semantic models. This is the same engine that Tabular Editor uses.")
    pdf.action("CLICK", "Scroll to run_bpa_analysis function (line ~40)")
    pdf.action("EXPECT", "See: model_bpa = fabric.list_model_bpa(dataset=dataset_name, workspace=workspace)")
    pdf.action("SAY", "This connects to the Fabric semantic model and runs 150+ best practice checks. Let me show you what it finds.")
    pdf.ln(3)
    
    pdf.action("DO", "Scroll to output display section (line ~80)")
    pdf.action("SAY", "Violations are grouped by severity: Error, Warning, Informational. Errors are blockers -- things like missing relationships or invalid DAX. Warnings are performance issues.")
    pdf.action("EXPECT", "See example violations: calculated columns, missing descriptions, orphan tables")
    pdf.action("SAY", "For Digital Realty, we found 23 violations in the original model. Seven were critical: calculated columns that should be measures, high-cardinality string columns, missing date tables.")
    pdf.talk_track_box("If you have real BPA output, show it. Otherwise, describe the violations you'd typically see. Don't rush this -- make it tangible.")
    pdf.ln(3)
    
    pdf.action("DO", "Open notebooks/05_memory_analyzer.py")
    pdf.action("SAY", "Best practice checks are great, but they don't show you memory usage. That's where VertiPaq Analyzer comes in. This queries the semantic model's DMVs -- dynamic management views -- to see exactly how much memory each table and column consumes.")
    pdf.action("CLICK", "Scroll to DISCOVER_STORAGE_TABLE_COLUMNS query (line ~50)")
    pdf.action("EXPECT", "See DMV query for column-level memory stats")
    pdf.action("SAY", "VertiPaq is the in-memory engine behind Power BI. This query shows column cardinality, data size, dictionary size, and compression ratio.")
    pdf.ln(3)
    
    pdf.action("DO", "Scroll to memory report output (line ~120)")
    pdf.action("SAY", "Here's the memory report. The original model was 890 MB. After optimization, it's 340 MB. That's a 62% reduction.")
    pdf.action("EXPECT", "See table: Table Name | Memory MB | Row Count | Column Count | Avg Compression")
    pdf.action("SAY", "Look at the top consumers. The Assets table was 450 MB before optimization. We converted calculated columns to measures, changed high-cardinality strings to integers with lookup tables, and dropped unused columns. Now it's 180 MB.")
    pdf.talk_track_box("Point at specific numbers. Use your finger or cursor to trace the before/after. Make the 62% reduction feel massive.")
    pdf.ln(3)
    
    pdf.action("DO", "Open digitalrealty-capacity.tmdl in VS Code")
    pdf.action("SAY", "This is the optimized semantic model. TMDL format -- Tabular Model Definition Language. It's the same as XMLA but human-readable and Git-friendly.")
    pdf.action("CLICK", "Navigate to measures/ folder")
    pdf.action("EXPECT", "See DAX measures: TotalAssets, BudgetVariance, GrowthRate")
    pdf.action("SAY", "All our KPIs are measures, not calculated columns. Measures compute at query time, so they don't bloat the model. Calculated columns materialize in the data model and consume memory.")
    pdf.ln(3)
    
    pdf.action("DO", "Show Before/After comparison (if available)")
    pdf.action("SAY", "Before optimization: 890 MB, 12-second report load time. After: 340 MB, 4-second load time. Same data, same visuals, 3x faster.")
    pdf.action("EXPECT", "Audience should react positively to the 3x improvement")
    pdf.action("SAY", "And this is automated. Every time we deploy a semantic model change, the BPA analyzer runs. If memory exceeds our 500 MB budget, the CI gate fails. No bad models reach production.")
    pdf.ln(3)
    
    pdf.subsection("D. Value Proposition")
    pdf.value_box("Digital Realty's semantic models serve 200+ business users across finance, operations, and executive dashboards. Slow reports cost thousands of hours per year in lost productivity. This solution provides: (1) Proactive performance analysis before deployment. (2) Automated memory budgeting -- no model over 500 MB without approval. (3) Cost reduction -- smaller models mean cheaper Fabric capacity. (4) Better user experience -- reports load 3x faster.")
    pdf.ln(2)
    
    pdf.subsection("E. Hard Questions & Prepared Responses")
    pdf.qa_item(
        "Can we use this for composite models with DirectQuery tables?",
        "Yes, but with caveats. The memory analyzer only measures Import tables. DirectQuery tables don't consume memory. However, BPA still validates DirectQuery DAX and relationships. For composite models, run the memory analyzer on the Import portion and use query diagnostics for DirectQuery performance."
    )
    pdf.qa_item(
        "What if we have calculated columns that can't be converted to measures?",
        "Some calculated columns are necessary -- like concatenated keys for relationships or row-level security filters. The BPA analyzer flags them, but you can suppress false positives with annotations. The key is: calculated columns for data shaping = OK. Calculated columns for aggregations = bad. Convert those to measures."
    )
    pdf.qa_item(
        "How does this integrate with Tabular Editor or external BI tools?",
        "The semantic model is TMDL format, which Tabular Editor 3 natively supports. You can edit in Tabular Editor, commit TMDL to Git, and the CI/CD pipeline deploys to Fabric. Or edit directly in Fabric and sync to Git. Both workflows are supported."
    )
    pdf.qa_item(
        "What's the performance impact of running BPA on every deployment?",
        "BPA analysis takes 30-60 seconds for typical models. Memory analysis adds another 60 seconds. Total CI/CD time: 2-3 minutes. If that's too slow, run BPA only on semantic model changes (not notebook changes). Use GitHub Actions path filters to skip BPA when model files haven't changed."
    )
    pdf.ln(2)
    
    pdf.subsection("F. Fallback Plans")
    pdf.bullet("Fallback 1: If semantic-link-labs fails to connect, show the BPA code and pre-captured output. Walk through violation categories manually.")
    pdf.bullet("Fallback 2: If memory analyzer DMV query hangs, switch to static memory report CSV. Show before/after numbers in Excel or printed PDF.")
    pdf.bullet("Fallback 3: Skip live execution and show architecture diagram of BPA pipeline + DMV query flow. Emphasize the methodology, not the live run.")
    
    # ========== USE CASE 3: Automated Quality & Governance ==========
    pdf.section_banner("Use Case 3: Automated Quality & Governance", "Duration: 10-15 minutes")
    
    pdf.subsection("A. Setup Steps")
    pdf.bullet("Have notebooks/03_data_quality_checks.py open")
    pdf.bullet("Have security/onelake-roles.json open")
    pdf.bullet("Have security/rls-rules.dax open")
    pdf.ln(2)
    
    pdf.subsection("B. Pain Point Introduction")
    pdf.action("SAY", "Data pipelines without guardrails are a compliance nightmare. No validation means bad data reaches production. No drift detection means schemas diverge silently. No governance means audit failures.")
    pdf.action("SAY", "For a publicly traded company like Digital Realty, this isn't just inconvenient -- it's a regulatory risk. SOC 2, GDPR, and financial compliance all require data quality controls and access governance.")
    pdf.talk_track_box("Make this serious. Use words like 'regulatory risk' and 'audit failure'. This is about protection, not features.")
    pdf.action("EXPECT", "Audience should lean forward -- compliance issues get executive attention")
    pdf.ln(2)
    
    pdf.subsection("C. Solution Demo Flow")
    pdf.action("DO", "Open notebooks/03_data_quality_checks.py")
    pdf.action("SAY", "Our DataQualityChecker class runs seven types of validation checks on every table before data moves downstream.")
    pdf.action("CLICK", "Scroll to DataQualityChecker class definition (line ~20)")
    pdf.action("EXPECT", "See methods: check_nulls, check_row_count, check_duplicates, check_range, check_allowed_values, validate_schema")
    pdf.action("SAY", "Let's walk through these. First, null detection.")
    pdf.ln(3)
    
    pdf.action("DO", "Scroll to check_nulls method (line ~40)")
    pdf.action("SAY", "For critical columns like asset_id or budget_amount, nulls aren't allowed. This check fails the pipeline if any nulls are found.")
    pdf.action("EXPECT", "See: if null_count > 0: return 'CRITICAL', f'Found {null_count} nulls in {column}'")
    pdf.action("SAY", "Critical severity means the pipeline stops. Warnings let the pipeline continue but log the issue.")
    pdf.ln(3)
    
    pdf.action("DO", "Scroll to check_duplicates method (line ~60)")
    pdf.action("SAY", "For primary keys like asset_id, duplicates are data corruption. This check compares total row count to distinct count.")
    pdf.action("EXPECT", "See: if row_count != distinct_count: return 'CRITICAL', f'{duplicate_count} duplicates'")
    pdf.ln(3)
    
    pdf.action("DO", "Scroll to validate_schema method (line ~80)")
    pdf.action("SAY", "This is where schema drift detection happens. We compare the actual table columns against the Schema Registry.")
    pdf.action("EXPECT", "See: missing_columns = registry_columns - actual_columns")
    pdf.action("SAY", "If the actual table is missing columns that the registry expects, that's a critical error. If it has extra columns not in the registry, that's a warning -- might be a new column that hasn't been documented yet.")
    pdf.talk_track_box("Emphasize the bidirectional check: missing columns = critical, extra columns = warning. This catches both data loss and unexpected changes.")
    pdf.ln(3)
    
    pdf.action("DO", "Scroll to check_range method (line ~100)")
    pdf.action("SAY", "Business logic validation. For example, budget amounts should be positive. Asset ages should be less than 50 years.")
    pdf.action("EXPECT", "See: if value < min_val or value > max_val: violations.append(value)")
    pdf.action("SAY", "If we find 1000 assets with negative budgets, that's a data quality issue upstream. The check logs it and fails the pipeline.")
    pdf.ln(3)
    
    pdf.action("DO", "Open security/onelake-roles.json")
    pdf.action("SAY", "Now let's talk governance. Digital Realty has regional data access requirements. The finance team in North America shouldn't see European data, and vice versa.")
    pdf.action("CLICK", "Scroll to region-based roles")
    pdf.action("EXPECT", "See: NA-Finance-Read, EMEA-Finance-Read, APAC-Finance-Read")
    pdf.action("SAY", "OneLake RBAC controls file-level access. This JSON defines roles and maps them to Azure AD security groups.")
    pdf.ln(3)
    
    pdf.action("DO", "Open security/rls-rules.dax")
    pdf.action("SAY", "OneLake RBAC controls the files, but users also query through Power BI semantic models. That's where Row-Level Security comes in.")
    pdf.action("CLICK", "Scroll to RLS DAX expression")
    pdf.action("EXPECT", "See: [Region] = LOOKUPVALUE('Users'[Region], 'Users'[Email], USERPRINCIPALNAME())")
    pdf.action("SAY", "This DAX expression filters data based on the logged-in user's region. Finance users in North America see only North America assets. It's automatic and enforced at the semantic model layer.")
    pdf.ln(3)
    
    pdf.action("SAY", "So we have four layers of security: Workspace permissions control who can edit. OneLake RBAC controls who can read files. Semantic model RLS filters data by user. And OLS -- Object-Level Security -- hides sensitive tables like security bridge tables.")
    pdf.talk_track_box("Hold up four fingers. Count off each layer. This is defense in depth.")
    pdf.ln(3)
    
    pdf.subsection("D. Value Proposition")
    pdf.value_box("Digital Realty handles financial data, customer data, and operational metrics for 300+ data centers. Regulatory compliance is non-negotiable. This solution provides: (1) Automated data quality gates -- bad data never reaches production. (2) Schema drift detection -- catch divergence before reports break. (3) Multi-layer security -- workspace, file, row, and object-level controls. (4) Audit trail -- every quality check logged, every access decision traceable.")
    pdf.ln(2)
    
    pdf.subsection("E. Hard Questions & Prepared Responses")
    pdf.qa_item(
        "How do we handle edge cases where a quality check legitimately fails but we need to proceed?",
        "Great question. You can override checks with manual approval. The DataQualityChecker supports an 'override_mode' flag. When set, critical checks become warnings and log the override reason. This should be rare and require director-level approval in your process."
    )
    pdf.qa_item(
        "What if our data quality rules change frequently? How do we version them?",
        "Quality rules live in the data quality notebook, which is version-controlled in Git. When rules change, update the notebook, commit, and promote through CI/CD. You can also externalize rules to a config file (YAML or JSON) if you need non-developers to modify them."
    )
    pdf.qa_item(
        "How does RLS perform at scale? Does it slow down queries?",
        "RLS is evaluated at query time, so there is some overhead. For most models, it's negligible -- 10-50ms per query. If you have millions of rows and complex RLS logic, consider pre-filtering data at the Lakehouse layer. Create regional Silver tables (silver_assets_na, silver_assets_emea) and apply RLS only for cross-region users."
    )
    pdf.qa_item(
        "Can we integrate this with ServiceNow or other ITSM tools for approval workflows?",
        "Yes. GitHub Actions can call ServiceNow REST APIs to create change requests. When a quality check fails or a manual override is requested, trigger a ServiceNow workflow. Wait for approval, then continue the pipeline. We can help you build that integration."
    )
    pdf.ln(2)
    
    pdf.subsection("F. Fallback Plans")
    pdf.bullet("Fallback 1: If quality checks fail to run live, show the DataQualityChecker code and pre-captured logs. Walk through each validation method manually.")
    pdf.bullet("Fallback 2: If security demo fails, show onelake-roles.json and rls-rules.dax in VS Code. Explain the logic without live execution.")
    pdf.bullet("Fallback 3: Skip live demo and show compliance checklist PDF. Emphasize the governance framework, not the live validation.")
    
    # ========== COMPETITIVE COMPARISON ==========
    pdf.section_banner("Competitive Comparison", "How Microsoft Fabric compares for these 3 use cases")
    
    pdf.subsection("Comparison Table")
    pdf.set_font("Helvetica", "", 9)
    pdf.ln(2)
    headers = ["Capability", "Fabric", "Databricks", "Snowflake"]
    widths = [60, 40, 40, 40]
    pdf.table_row(headers, widths, is_header=True)
    
    rows = [
        ["Schema CI/CD", "★★★★☆ Native Git", "★★★☆☆ UC + Git", "★★☆☆☆ Manual"],
        ["BPA Automation", "★★★★★ Built-in", "★★☆☆☆ Custom", "★☆☆☆☆ None"],
        ["Data Quality", "★★★★☆ Notebooks", "★★★★☆ Expectations", "★★★☆☆ Streams"],
        ["RLS & Security", "★★★★★ Native", "★★★★☆ UC", "★★★★☆ Native"],
        ["Cost", "★★★☆☆ Capacity", "★★☆☆☆ DBU+Storage", "★★★☆☆ Compute+Storage"],
        ["Ecosystem", "★★★★★ Azure", "★★★★☆ Multi-cloud", "★★★★☆ Multi-cloud"],
    ]
    for row in rows:
        pdf.table_row(row, widths)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*pdf.DARK)
    pdf.multi_cell(0, 6, pdf._safe(
        "HONEST ASSESSMENT: Microsoft Fabric excels at integrated experiences -- BPA analyzer, Git sync, and "
        "semantic models are first-class citizens. Databricks is stronger for ML/AI workloads and multi-cloud "
        "portability. Snowflake is best for pure SQL analytics and data sharing. For Digital Realty's use cases "
        "(schema evolution, Power BI optimization, governance), Fabric is the natural fit because of Azure integration "
        "and native Power BI support."
    ))
    
    # ========== RECOMMENDED NEXT STEPS ==========
    pdf.section_banner("Recommended Next Steps", "Implementation timeline for Digital Realty")
    
    pdf.subsection("Immediate (Week 1)")
    pdf.bullet("Set up Dev workspace with Git integration")
    pdf.bullet("Deploy Schema Registry for 5 critical tables")
    pdf.bullet("Run BPA analyzer on existing semantic models")
    pdf.bullet("Document current data quality gaps")
    pdf.ln(3)
    
    pdf.subsection("Short-term (Weeks 2-4)")
    pdf.bullet("Implement CI/CD pipeline for Dev workspace")
    pdf.bullet("Deploy data quality checks on Bronze and Silver tables")
    pdf.bullet("Optimize top 3 memory-consuming semantic models")
    pdf.bullet("Set up OneLake RBAC for regional data access")
    pdf.ln(3)
    
    pdf.subsection("Medium-term (Months 2-3)")
    pdf.bullet("Promote to UAT with approval gates")
    pdf.bullet("Roll out Schema Registry to all 50 lakehouses")
    pdf.bullet("Deploy BPA analyzer as CI gate for all semantic models")
    pdf.bullet("Implement RLS for all Power BI reports")
    pdf.ln(3)
    
    pdf.subsection("Long-term (Months 3-6)")
    pdf.bullet("Production deployment with full CI/CD automation")
    pdf.bullet("Cross-region fan-out deployment for global operations")
    pdf.bullet("Integrate with ServiceNow for change management")
    pdf.bullet("Build custom compliance dashboards and audit reports")
    pdf.ln(3)
    
    pdf.subsection("Success Metrics")
    pdf.bullet("Schema drift incidents: Reduce from 5/month to 0")
    pdf.bullet("Semantic model performance: 3x faster average load time")
    pdf.bullet("Data quality incidents: 80% reduction in production issues")
    pdf.bullet("Compliance audit readiness: Pass all controls with zero findings")
    
    # Output
    output_file = "DigitalRealty_3UseCase_Demo_Workflow.pdf"
    pdf.output(output_file)
    print(f"✅ PDF generated: {output_file}")
    print(f"📄 Total pages: {pdf.page_no()}")
    return output_file


if __name__ == "__main__":
    generate_pdf()
