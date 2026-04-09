#!/usr/bin/env python3
"""
Digital Realty - 3 Use Case Demo Guide PDF Generator
Click-by-click instructions for all 3 demo use cases using the StoryDemo HTML.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.github', 'skills', 'demo-workflow-pdf', 'references'))

from fpdf import FPDF
import textwrap


class DemoGuidePDF(FPDF):
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
        self.cell(0, 8, "Digital Realty | 3 Use Case Demo Guide | Confidential", align="C")
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

    # ---- Title Page ----
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
        self.cell(0, 12, "3 Use Case Demo Guide", align="C")
        self.ln(14)
        self.set_font("Helvetica", "I", 14)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, "Click-by-Click Instructions with Talk Tracks", align="C")
        self.ln(30)
        details = [
            ("Demo File:", "DigitalRealty_StoryDemo.html"),
            ("Duration:", "45-60 minutes (20 screens, 5 acts)"),
            ("Format:", "Offline HTML -- works without internet"),
            ("Audience:", "Data Platform Team, Analytics Leads, IT Director"),
            ("Presenter:", "GitHub Solutions Engineering"),
        ]
        self.set_font("Helvetica", "", 11)
        self.set_text_color(60, 60, 60)
        for label, val in details:
            self.set_x(35)
            self.set_font("Helvetica", "B", 11)
            self.cell(35, 8, label)
            self.set_font("Helvetica", "", 11)
            self.cell(0, 8, val)
            self.ln(8)
        self.ln(16)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*self.BLUE)
        self.cell(0, 10, "The 3 Use Cases", align="C")
        self.ln(12)
        cases = [
            ("1. Power BI Performance Optimization", "Diagnose and fix DAX anti-patterns, memory bloat, and compression issues"),
            ("2. Lakehouse Schema Evolution (CI/CD)", "Version-control table schemas, promote changes across Dev/UAT/Prod"),
            ("3. Automated Quality & Governance", "CI gates, drift detection, and continuous compliance enforcement"),
        ]
        for title, desc in cases:
            self.set_x(25)
            self.set_font("Helvetica", "B", 11)
            self.set_text_color(*self.BLUE)
            self.cell(0, 7, title)
            self.ln(7)
            self.set_x(30)
            self.set_font("Helvetica", "", 10)
            self.set_text_color(80, 80, 80)
            self.cell(0, 6, desc)
            self.ln(9)
        self.set_fill_color(*self.BLUE)
        self.rect(0, 280, 210, 8, "F")

    # ---- Helpers ----
    def _safe(self, text):
        return (text
            .replace("\u2014", "--")
            .replace("\u2013", "-")
            .replace("\u2018", "'").replace("\u2019", "'")
            .replace("\u201c", '"').replace("\u201d", '"')
            .replace("\u2192", "->")
            .replace("\u2022", "-")
            .replace("\u2713", "[OK]")
            .replace("\u2717", "[X]")
            .replace("\u27a1", "->")
            .replace("\u2728", "*")
            .replace("\u26a0", "[!]")
            .replace("\u2b50", "*")
            .replace("\u2705", "[OK]")
            .replace("\u274c", "[X]")
            .replace("\u25ba", ">")
            .replace("\u25b6", ">")
            .replace("\u21e8", "=>")
            .replace("\u00d7", "x")
            .replace("\u2026", "...")
            .replace("\u2265", ">=")
            .replace("\u2264", "<="))

    def _wrap(self, text, max_w_mm):
        chars = int(max_w_mm / 2.1)
        return textwrap.wrap(self._safe(text), width=chars)

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

    def screen_header(self, screen_num, title, act, use_case, timing):
        self.ln(2)
        if self.get_y() > 220:
            self.add_page()
        self.set_fill_color(240, 248, 255)
        self.rect(10, self.get_y(), 190, 18, "F")
        self.set_draw_color(*self.BLUE)
        self.rect(10, self.get_y(), 190, 18, "D")
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*self.BLUE)
        self.cell(0, 9, f"  Screen {screen_num}: {self._safe(title)}")
        self.ln(9)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 9, f"  {act}  |  {use_case}  |  {timing}")
        self.ln(12)

    def action(self, tag, text):
        if self.get_y() > 265:
            self.add_page()
        r, g, b = self.ACTION_COLORS.get(tag, (0, 0, 0))
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(r, g, b)
        self.cell(18, 7, f"[{tag}]")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)
        lines = self._wrap(text, 165)
        for i, line in enumerate(lines):
            if i > 0:
                self.cell(18, 6, "")
            self.cell(165, 7 if i == 0 else 6, line)
            self.ln(7 if i == 0 else 6)

    def value_prop(self, text):
        if self.get_y() > 265:
            self.add_page()
        self.set_font("Helvetica", "BI", 10)
        self.set_text_color(0, 100, 0)
        lines = self._wrap(f"VALUE: {text}", 180)
        for i, line in enumerate(lines):
            self.set_x(15)
            self.cell(175, 6, line)
            self.ln(6)
        self.set_text_color(*self.DARK)
        self.ln(2)

    def talk_track(self, text):
        if self.get_y() > 260:
            self.add_page()
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(60, 60, 120)
        lines = self._wrap(text, 175)
        for line in lines:
            self.set_x(15)
            self.cell(0, 6, line)
            self.ln(6)
        self.ln(2)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)

    def divider(self):
        self.ln(3)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def bullet(self, text, indent=0):
        if self.get_y() > 268:
            self.add_page()
        x = 15 + indent
        self.set_x(x)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)
        self.cell(5, 6, "-")
        max_w = 180 - indent
        for i, line in enumerate(self._wrap(text, max_w)):
            if i > 0:
                self.set_x(x + 5)
            self.cell(max_w, 6, line)
            self.ln(6)

    def check_item(self, text, checked=False):
        if self.get_y() > 268:
            self.add_page()
        mark = "[x]" if checked else "[ ]"
        self.set_x(15)
        self.set_font("Courier", "B", 10)
        self.set_text_color(0, 150, 0) if checked else self.set_text_color(*self.BLUE)
        self.cell(10, 6, mark)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)
        self.cell(0, 6, self._safe(text))
        self.ln(7)

    def sub_header(self, text):
        if self.get_y() > 255:
            self.add_page()
        self.ln(4)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(0, 100, 180)
        self.cell(0, 10, self._safe(text))
        self.ln(10)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)
        self.set_x(10)
        self.multi_cell(190, 6, self._safe(text))
        self.ln(2)

    def code_block(self, text):
        if self.get_y() > 250:
            self.add_page()
        self.set_font("Courier", "", 9)
        self.set_text_color(0, 80, 0)
        self.set_fill_color(*self.LIGHT_GRAY)
        for line in self._safe(text).strip().split("\n"):
            self.cell(0, 5.5, f"  {line}", fill=True)
            self.ln(5.5)
        self.ln(3)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)

    def component_box(self, title, description, tech_detail):
        """Render a boxed component card with title, description, and technical detail."""
        if self.get_y() > 230:
            self.add_page()
        y_start = self.get_y()
        self.set_fill_color(240, 248, 255)
        self.set_draw_color(*self.BLUE)
        self.rect(12, y_start, 186, 6, "F")
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*self.BLUE)
        self.set_x(14)
        self.cell(0, 6, self._safe(title))
        self.ln(8)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)
        self.set_x(14)
        self.multi_cell(182, 5.5, self._safe(description))
        self.ln(1)
        self.set_font("Courier", "", 8.5)
        self.set_text_color(80, 80, 80)
        for line in self._safe(tech_detail).strip().split("\n"):
            self.set_x(16)
            self.cell(0, 5, line)
            self.ln(5)
        self.ln(4)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)

    def flow_arrow(self, steps):
        """Render a horizontal flow: step1 -> step2 -> step3."""
        if self.get_y() > 260:
            self.add_page()
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*self.BLUE)
        self.set_x(12)
        line = "  ->  ".join(self._safe(s) for s in steps)
        self.cell(0, 8, line)
        self.ln(10)
        self.set_text_color(*self.DARK)

    def qa_pair(self, question, answer):
        if self.get_y() > 240:
            self.add_page()
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(0, 80, 160)
        self.cell(0, 8, f"Q: {self._safe(question)}")
        self.ln(9)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)
        self.set_x(10)
        self.multi_cell(190, 6, f"A: {self._safe(answer)}")
        self.ln(5)

    def table_row(self, cells, header=False, widths=None):
        if widths is None:
            widths = [190 / len(cells)] * len(cells)
        if self.get_y() > 268:
            self.add_page()
        if header:
            self.set_font("Helvetica", "B", 9)
            self.set_fill_color(*self.BLUE)
            self.set_text_color(*self.WHITE)
        else:
            self.set_font("Helvetica", "", 9)
            self.set_fill_color(250, 250, 250)
            self.set_text_color(*self.DARK)
        for i, cell in enumerate(cells):
            self.cell(widths[i], 8, f" {self._safe(cell)}", border=1, fill=True)
        self.ln(8)


def build_pdf():
    pdf = DemoGuidePDF()
    pdf.alias_nb_pages()

    # ================================================================
    # TITLE PAGE
    # ================================================================
    pdf.title_page()

    # ================================================================
    # TABLE OF CONTENTS / AGENDA
    # ================================================================
    pdf.section_banner("Demo Agenda", "20 screens across 5 acts -- a story-driven approach")

    pdf.body_text("This demo follows a narrative arc: a real Monday morning crisis at Digital Realty. "
                  "Three problems hit simultaneously -- slow dashboards, schema drift in production, "
                  "and a CFO demanding sustainability data. The demo shows how all three are solved "
                  "with one integrated approach.")
    pdf.ln(4)

    widths = [20, 60, 50, 30, 30]
    pdf.table_row(["#", "Screen", "Use Case", "Act", "Timing"], header=True, widths=widths)
    screens = [
        ("1", "Monday Morning Crisis", "All 3 -- Setup", "Act 1", "2 min"),
        ("2", "Slow Dashboard (45s)", "UC1: Performance", "Act 1", "2 min"),
        ("3", "Capacity Metrics (89% CU)", "UC1: Performance", "Act 1", "2 min"),
        ("4", "Teams Alerts + Schema Drift", "UC2: Schema / UC3: Gov", "Act 1", "2 min"),
        ("5", "BPA Notebook -- 12 Violations", "UC1: Performance", "Act 2", "3 min"),
        ("6", "DAX Anti-Pattern Details", "UC1: Performance", "Act 2", "3 min"),
        ("7", "Memory Analyzer -- 890 MB", "UC1: Performance", "Act 2", "3 min"),
        ("8", "Compression Analyzer", "UC1: Performance", "Act 2", "2 min"),
        ("9", "Schema Enforcer -- Drift", "UC2: Schema", "Act 2", "3 min"),
        ("10", "TMDL Diff: Before vs After", "UC1: Performance", "Act 3", "3 min"),
        ("11", "Schema Registry Update", "UC2: Schema", "Act 3", "2 min"),
        ("12", "Git Commit + PR Summary", "UC3: Governance", "Act 3", "2 min"),
        ("13", "Pipeline Running", "UC3: Governance", "Act 3", "2 min"),
        ("14", "All Gates Pass", "UC3: Governance", "Act 3", "2 min"),
        ("15", "Before/After: Load Time", "UC1: Performance", "Act 4", "2 min"),
        ("16", "Before/After: Memory", "UC1: Performance", "Act 4", "2 min"),
        ("17", "Sustainability Cols Live", "UC2: Schema", "Act 4", "2 min"),
        ("18", "Next Drift Caught", "UC3: Governance", "Act 4", "2 min"),
        ("19", "ROI Summary", "All 3 -- Close", "Act 5", "2 min"),
        ("20", "Next Steps + POC Timeline", "All 3 -- Close", "Act 5", "3 min"),
    ]
    for s in screens:
        pdf.table_row(list(s), widths=widths)

    # ================================================================
    # PRE-DEMO SETUP
    # ================================================================
    pdf.section_banner("Pre-Demo Setup Checklist", "Complete these before the customer arrives")

    pdf.sub_header("Files to Have Ready")
    pdf.check_item("DigitalRealty_StoryDemo.html open in Chrome/Edge (fullscreen: F11)")
    pdf.check_item("Backup: DigitalRealty_Realistic_Demo.html (18-screen version)")
    pdf.check_item("Backup: DigitalRealty_Visual_Demo.html (17-screen version)")
    pdf.check_item("This PDF printed or on a second screen")

    pdf.sub_header("Browser Setup")
    pdf.check_item("Close all other tabs (no notifications)")
    pdf.check_item("Bookmark bar hidden (Ctrl+Shift+B)")
    pdf.check_item("Zoom set to 100% (Ctrl+0)")
    pdf.check_item("Dark mode preferred (matches demo styling)")

    pdf.sub_header("Presentation Setup")
    pdf.check_item("Screen sharing on (single screen, not desktop)")
    pdf.check_item("Teams/Slack/Outlook notifications OFF")
    pdf.check_item("Font size: 100% browser zoom")
    pdf.check_item("Arrow keys tested -- left/right navigate screens")
    pdf.check_item("Press F in demo for fullscreen toggle")

    pdf.sub_header("Key Numbers to Memorize")
    pdf.bullet("45s -> 2.8s dashboard load time (16x improvement)")
    pdf.bullet("890 MB -> 340 MB memory (62% reduction, 550 MB saved)")
    pdf.bullet("12 -> 0 BPA violations")
    pdf.bullet("2m 47s pipeline runtime (commit to production)")
    pdf.bullet("40 hours/month saved in manual schema work")
    pdf.bullet("$180K/year deferred capacity cost")

    # ================================================================
    # TECHNICAL ARCHITECTURE — USE CASE 1
    # ================================================================
    pdf.section_banner("Technical Deep Dive: UC1 -- Power BI Performance Optimization",
                       "How the diagnostic pipeline works under the hood")

    pdf.body_text(
        "This use case deploys three Fabric notebooks that diagnose semantic model performance "
        "from different angles, plus a GitHub Actions CI gate that catches issues statically "
        "before code is merged. Together they form a layered performance safety net."
    )
    pdf.ln(2)

    pdf.sub_header("Architecture Flow")
    pdf.flow_arrow(["PR Opened", "CI Gate (static TMDL scan)", "Merge to main",
                    "Deploy to Dev", "Runtime Notebooks (BPA + Memory + Compression)", "Results"])

    # -- Component 1: BPA Analyzer --
    pdf.sub_header("Component 1: Best Practice Analyzer (04_bpa_analyzer.py)")
    pdf.body_text(
        "A PySpark notebook that runs inside a Fabric Spark session. It uses two analysis layers:"
    )

    pdf.component_box(
        "Layer A: semantic-link-labs BPA (50+ built-in rules)",
        "Calls labs.run_model_bpa(dataset, workspace) which connects to the semantic model over "
        "the XMLA endpoint. This is Microsoft's own BPA rule engine, ported to Python. It returns "
        "a Pandas DataFrame with columns: Severity, Category, Rule, Object, Object Type, Description. "
        "Rules cover DAX anti-patterns, unused objects, relationship issues, and formatting gaps.",
        "import sempy_labs as labs\n"
        "bpa_results = labs.run_model_bpa(\n"
        "    dataset=\"DigitalRealty_Capacity\",\n"
        "    workspace=\"DigitalRealty_Dev\"\n"
        ")"
    )

    pdf.component_box(
        "Layer B: Custom DMV Queries (Digital Realty-specific checks)",
        "In addition to the library rules, the notebook executes DAX queries against Analysis Services "
        "Dynamic Management Views (DMVs) to find issues specific to this model. It queries "
        "$SYSTEM.MDSCHEMA_COLUMNS with COLUMN_TYPE=2 to find calculated columns, checks "
        "$SYSTEM.MDSCHEMA_DIMENSIONS for orphan tables, and uses INFO.COLUMNS() for encoding hints.",
        "calc_cols = fabric.evaluate_dax(\n"
        "    dataset=DATASET_NAME,\n"
        "    dax_string=\"\"\"\n"
        "      SELECT [DIMENSION_UNIQUE_NAME], [COLUMN_NAME]\n"
        "      FROM $SYSTEM.MDSCHEMA_COLUMNS\n"
        "      WHERE [COLUMN_TYPE] = 2\n"
        "    \"\"\"\n"
        ")"
    )

    pdf.body_text(
        "Anti-patterns detected: SUMX on large tables (should be SUM), FILTER(ALL()) instead of "
        "CALCULATE with simple filters, AVERAGEX instead of AVERAGE, calculated columns that should "
        "be measures, missing formatString on measures, and high-cardinality STRING columns."
    )
    pdf.body_text(
        "Output: A JSON report with status (PASS/WARN/FAIL), violation count, and details. "
        "This report is consumed by the CI/CD pipeline to gate promotions."
    )

    # -- Component 2: Memory Analyzer --
    pdf.sub_header("Component 2: VertiPaq Memory Analyzer (05_memory_analyzer.py)")
    pdf.body_text(
        "This notebook queries the Analysis Services VertiPaq storage engine directly via DMVs "
        "to produce a column-level and table-level memory consumption report."
    )

    pdf.component_box(
        "DMV: $SYSTEM.DISCOVER_STORAGE_TABLE_COLUMNS",
        "Returns per-column storage statistics: dictionary_size (how much memory the dictionary "
        "encoding uses), column_data_size (actual data storage), and column_cardinality (unique "
        "value count). The notebook sums dictionary_size + column_data_size to get total memory "
        "per column, then aggregates to table level.",
        "df_columns = fabric.evaluate_dax(\n"
        "    dataset=DATASET_NAME,\n"
        "    dax_string=\"SELECT * FROM\n"
        "       $SYSTEM.DISCOVER_STORAGE_TABLE_COLUMNS\"\n"
        ")"
    )

    pdf.component_box(
        "DMV: $SYSTEM.DISCOVER_STORAGE_TABLES",
        "Returns table-level aggregates: row count, total size, and table type. Used to cross-reference "
        "with the column-level data for validation and to identify calculated tables vs. regular tables.",
        "df_tables = fabric.evaluate_dax(\n"
        "    dataset=DATASET_NAME,\n"
        "    dax_string=\"SELECT * FROM\n"
        "       $SYSTEM.DISCOVER_STORAGE_TABLES\"\n"
        ")"
    )

    pdf.body_text(
        "Analysis logic: Each column is compared against configurable thresholds -- TABLE_ALERT_MB=100, "
        "COLUMN_ALERT_MB=50, MEMORY_BUDGET_MB=500. The notebook flags columns where cardinality exceeds "
        "100K (high-cardinality STRING problem), computes compression ratios (estimated uncompressed / actual), "
        "and identifies calculated columns consuming memory that could be zero-memory measures."
    )

    pdf.body_text(
        "Key insight for Digital Realty: contract_notes (210 MB, 92% unique), raw_api_response (140 MB, "
        "100% unique), and datacenter_description (95 MB, 98% unique) are high-cardinality text columns "
        "that no report visual references. Removing them recovers 445 MB. The three calculated columns "
        "(Revenue per MW, Annual Revenue Calc, Is High Value) add another 125 MB -- converting them to "
        "measures makes that cost zero because measures are computed at query time, not stored."
    )

    # -- Component 3: Compression Analyzer --
    pdf.sub_header("Component 3: Delta Compression Analyzer (06_compression_analyzer.py)")
    pdf.body_text(
        "This notebook analyzes the physical storage layer -- the Delta Lake files that underpin "
        "every Lakehouse table. It identifies the 'small file problem' and compression inefficiencies."
    )

    pdf.component_box(
        "PySpark DESCRIBE DETAIL + DESCRIBE HISTORY",
        "For each table in the TABLES list, the notebook runs spark.sql('DESCRIBE DETAIL table_name') "
        "to get file count, total size, and partition info. It also reads the Delta log to compute file "
        "size distribution (how many files are <1 MB, 1-32 MB, 32-128 MB, >128 MB). "
        "Files under 32 MB are flagged as 'small files' -- each one is a separate read/open operation "
        "that degrades Spark and DirectLake query performance.",
        "for table in TABLES:\n"
        "    detail = spark.sql(f'DESCRIBE DETAIL {table}')\n"
        "    history = spark.sql(f'DESCRIBE HISTORY {table}')\n"
        "    file_list = spark.read.format('delta') \\\n"
        "        .load(f'Tables/{table}').inputFiles()"
    )

    pdf.body_text(
        "Compression analysis: The notebook estimates the raw (uncompressed) size based on row count "
        "and column types, then compares against the actual Delta file size. A healthy Delta table "
        "should achieve 3x+ compression. Tables below 2x indicate high-cardinality columns or "
        "suboptimal data types that hurt Parquet/Delta encoding."
    )
    pdf.body_text(
        "Recommendations generated: OPTIMIZE commands to consolidate small files, ZORDER BY suggestions "
        "based on common filter columns (e.g., datacenter_id, measurement_date), and V-ORDER hints "
        "for DirectLake-optimized read patterns."
    )

    # -- Component 4: CI Gate --
    pdf.sub_header("Component 4: CI Performance Gate (performance-gate.yml)")
    pdf.body_text(
        "A GitHub Actions workflow that runs on every PR touching semantic-model/, notebooks/, or "
        "migrations/ paths. It performs static analysis of TMDL files -- NO Fabric connection needed. "
        "This catches the most common issues before code is even merged."
    )

    pdf.component_box(
        "Job 1: TMDL Anti-Pattern Scan",
        "Uses grep to search TMDL files for known anti-patterns. Each check outputs GitHub Actions "
        "annotations (::warning:: or ::error::) that appear inline on the PR diff.",
        "# Checks performed (bash grep on .tmdl files):\n"
        "grep -c 'calculatedColumn' *.tmdl   # 0 allowed\n"
        "grep -c 'SUMX(' *.tmdl              # flag for review\n"
        "grep -c 'FILTER(ALL(' *.tmdl        # 0 allowed\n"
        "grep -c 'AVERAGEX(' *.tmdl          # flag for review\n"
        "# Also checks: formatString count vs measure count\n"
        "# Also checks: bloat column patterns (description,\n"
        "#   notes, raw_, _hash, _etl_, response)"
    )

    pdf.component_box(
        "Job 2: Schema Registry Validation",
        "Parses notebooks/00_schema_registry.py as a Python AST to verify syntax is valid and "
        "SCHEMA_VERSION is present. Also validates migration file naming matches V###__description.py.",
        "python -c \"\n"
        "  import ast\n"
        "  tree = ast.parse(open('00_schema_registry.py').read())\n"
        "  # Walks AST for SCHEMA_VERSION assignment\n"
        "  # Verifies SCHEMAS dict is parseable\n"
        "\""
    )

    pdf.component_box(
        "Job 3: Gate Decision",
        "Depends on both Job 1 and Job 2. If either fails, the PR cannot be merged. "
        "The threshold is configurable: currently >5 total DAX issues = hard fail. "
        "This prevents anti-patterns from reaching main branch.",
        "gate-decision:\n"
        "  needs: [tmdl-lint, schema-check]\n"
        "  # Fails if either upstream job failed\n"
        "  # Outputs combined pass/fail status"
    )

    pdf.body_text(
        "The layered approach: CI gate catches ~80% of issues statically on the PR (fast, no Fabric "
        "needed). The remaining 20% -- runtime memory consumption, actual query timing, live "
        "cardinality stats -- are caught by the post-deploy notebooks in the Fabric session."
    )

    # ================================================================
    # TECHNICAL ARCHITECTURE — USE CASE 2
    # ================================================================
    pdf.section_banner("Technical Deep Dive: UC2 -- Lakehouse Schema Evolution",
                       "How schema-as-code bridges the Fabric Git integration gap")

    pdf.body_text(
        "The core problem: Fabric Git integration serializes artifact metadata (notebook code, "
        "pipeline JSON, semantic model TMDL) but does NOT serialize Lakehouse table structures. "
        "A Lakehouse .platform file in Git contains workspace/item IDs -- not CREATE TABLE statements. "
        "So when a developer adds a column via the Fabric UI or SQL endpoint, that change is invisible "
        "to Git and cannot be promoted through a deployment pipeline."
    )
    pdf.ln(2)

    pdf.sub_header("Architecture Flow")
    pdf.flow_arrow(["Edit 00_schema_registry.py", "Commit + PR", "CI Validates Syntax",
                    "Merge to main", "00_apply_schema runs", "Lakehouse Updated"])

    # -- Component 1: Schema Registry --
    pdf.sub_header("Component 1: Schema Registry (00_schema_registry.py)")
    pdf.body_text(
        "A single Python file that defines every table's structure as a Python dictionary. "
        "This is the SINGLE SOURCE OF TRUTH for all Lakehouse schemas across all environments. "
        "The file is version-controlled in Git and never modified outside of a pull request."
    )

    pdf.component_box(
        "Data Structure",
        "The SCHEMAS dictionary maps table names to their column definitions. Each column is a "
        "tuple of (name, type, nullable). The file also defines primary_key and partition_by per table. "
        "SCHEMA_VERSION is a semver string (e.g., '1.1.0') that is bumped on every schema change.",
        "SCHEMA_VERSION = \"1.1.0\"\n"
        "\n"
        "SCHEMAS = {\n"
        "  \"bronze_datacenters\": {\n"
        "    \"columns\": [\n"
        "      (\"datacenter_id\", \"STRING\", False),\n"
        "      (\"datacenter_name\", \"STRING\", False),\n"
        "      (\"market\", \"STRING\", True),\n"
        "      ...\n"
        "    ],\n"
        "    \"primary_key\": [\"datacenter_id\"],\n"
        "    \"partition_by\": None,\n"
        "  },\n"
        "  # 7 tables total (3 bronze, 4 silver)\n"
        "}"
    )

    pdf.body_text(
        "Why Python and not SQL DDL files? Because the same dictionary is consumed by the Schema "
        "Enforcer (to generate CREATE/ALTER statements), the Data Quality notebook (to validate "
        "expected columns), and the CI gate (to parse and validate syntax). One definition, three consumers."
    )

    # -- Component 2: Schema Enforcer --
    pdf.sub_header("Component 2: Schema Enforcer (00_apply_schema.py)")
    pdf.body_text(
        "A PySpark notebook that reads the registry and compares it against the actual Lakehouse. "
        "It runs BEFORE data ingestion notebooks and performs three operations:"
    )

    pdf.component_box(
        "Operation 1: CREATE -- Missing Tables",
        "If a table in the registry doesn't exist in the Spark catalog, the enforcer generates "
        "a CREATE TABLE statement from the column definitions and executes it via spark.sql(). "
        "This handles first-time setup and new table additions.",
        "if not spark.catalog.tableExists(table_name):\n"
        "    columns_sql = \", \".join(\n"
        "        f\"{c[0]} {c[1]}\" for c in schema_def[\"columns\"]\n"
        "    )\n"
        "    spark.sql(f\"CREATE TABLE {table_name} ({columns_sql})\n"
        "              USING DELTA\")"
    )

    pdf.component_box(
        "Operation 2: ALTER -- Missing Columns",
        "If a table exists but is missing columns defined in the registry, the enforcer generates "
        "ALTER TABLE ADD COLUMN statements. This handles schema evolution -- adding new columns "
        "(like the sustainability columns in v1.1.0) without recreating the table.",
        "for col_name, col_type in missing_columns:\n"
        "    spark.sql(\n"
        "        f\"ALTER TABLE {table_name}\n"
        "          ADD COLUMN {col_name} {col_type}\"\n"
        "    )"
    )

    pdf.component_box(
        "Operation 3: DRIFT DETECTION -- Extra Columns",
        "If the Lakehouse table has columns NOT in the registry, the enforcer flags them as drift. "
        "It compares the set of actual column names against the set of expected names. Extra columns "
        "mean someone modified the table outside the Git workflow (e.g., via Fabric UI or SQL endpoint). "
        "Drift causes the pipeline to BLOCK until resolved.",
        "expected_names = {c[0] for c in expected_columns}\n"
        "actual_names = set(existing_fields.keys())\n"
        "extra = actual_names - expected_names\n"
        "if extra:\n"
        "    print(f\"DRIFT: {table_name} has {extra}\")\n"
        "    actions.append((\"DRIFT\", table_name, extra))"
    )

    # -- Component 3: Migrations --
    pdf.sub_header("Component 3: Versioned Migrations (migrations/V001-V004)")
    pdf.body_text(
        "For changes that go beyond simple ADD COLUMN (type changes, column removals, data backfills), "
        "the project uses numbered migration scripts. Each migration is idempotent -- it checks "
        "the current state before acting, so running it twice is safe."
    )

    widths_mig = [30, 70, 90]
    pdf.table_row(["Version", "Name", "What It Does"], header=True, widths=widths_mig)
    pdf.table_row(["V001", "create_bronze_tables", "Initial CREATE TABLE for 3 bronze tables"], widths=widths_mig)
    pdf.table_row(["V002", "create_silver_tables", "Initial CREATE TABLE for 4 silver tables"], widths=widths_mig)
    pdf.table_row(["V003", "add_sustainability", "ALTER TABLE ADD COLUMN x3 on bronze_power_capacity"], widths=widths_mig)
    pdf.table_row(["V004", "remove_bloat_columns", "ALTER TABLE DROP COLUMN x6 (550 MB savings)"], widths=widths_mig)

    pdf.body_text(
        "Migration V004 example: Before dropping columns, it takes a pre-migration snapshot (current column "
        "count, row count, cardinality of each column being removed). After the DROP, it takes a post-migration "
        "snapshot and reports the memory savings. This audit trail is critical for compliance."
    )

    # -- How promotion works --
    pdf.sub_header("How Schema Changes Promote Across Environments")
    pdf.body_text(
        "The promotion flow leverages the fact that the schema registry is a CODE file, not a Lakehouse artifact:"
    )
    pdf.bullet("Developer edits 00_schema_registry.py (bumps SCHEMA_VERSION, adds/removes columns)")
    pdf.bullet("Developer creates a migration script if needed (V00N__description.py)")
    pdf.bullet("PR is opened -- CI gate validates registry syntax and migration naming")
    pdf.bullet("PR is merged to main -- Fabric Git Sync pushes notebooks to Dev workspace")
    pdf.bullet("00_apply_schema runs in Dev -- creates/alters tables to match registry")
    pdf.bullet("Deployment pipeline promotes Dev -> UAT -- same notebooks run, same result")
    pdf.bullet("Deployment pipeline promotes UAT -> Prod -- schema is now consistent everywhere")
    pdf.body_text(
        "The key insight: because the notebooks contain the logic to CREATE and ALTER tables, "
        "promoting the notebook IS promoting the schema. Fabric Git Sync handles the notebook files; "
        "the notebooks handle the table structures. No manual steps."
    )

    # ================================================================
    # TECHNICAL ARCHITECTURE — USE CASE 3
    # ================================================================
    pdf.section_banner("Technical Deep Dive: UC3 -- Automated Quality & Governance",
                       "CI gates, drift detection, and continuous compliance enforcement")

    pdf.body_text(
        "This use case combines the schema enforcement from UC2 with the performance gates from UC1 "
        "into a continuous governance system that runs automatically. It has three layers: "
        "pre-merge CI checks, post-deploy validation, and scheduled health monitoring."
    )
    pdf.ln(2)

    pdf.sub_header("Architecture Flow")
    pdf.flow_arrow(["PR Created", "CI Gate (static)", "Merge", "Deploy + Enforce",
                    "Quality Check", "Scheduled Health (every 2h)"])

    # -- Layer 1: Pre-Merge CI --
    pdf.sub_header("Layer 1: Pre-Merge CI Checks (GitHub Actions)")
    pdf.body_text(
        "Two GitHub Actions workflows run on every PR targeting main:"
    )

    pdf.component_box(
        "performance-gate.yml (triggered on PR)",
        "Runs 3 parallel jobs: (1) TMDL Anti-Pattern Scan -- grep-based static analysis of .tmdl files "
        "for calculated columns, SUMX, FILTER(ALL()), AVERAGEX, missing formatString, and bloat column "
        "name patterns. (2) Schema Registry Validation -- AST-parses 00_schema_registry.py, verifies "
        "SCHEMA_VERSION exists, checks migration naming convention. (3) Gate Decision -- aggregates "
        "results, blocks PR if thresholds exceeded.",
        "on:\n"
        "  pull_request:\n"
        "    branches: [main]\n"
        "    paths:\n"
        "      - 'semantic-model/**'\n"
        "      - 'notebooks/**'\n"
        "      - 'migrations/**'"
    )

    pdf.component_box(
        "promote-with-schema-validation.yml (triggered on merge)",
        "After merge to main, this workflow: (1) Snapshots source and target workspace states via "
        "Fabric REST API. (2) Diffs reports, datasets, tables, and TMDL definitions between environments. "
        "(3) Generates a change report. (4) Requires GitHub Environment approval before deploying. "
        "(5) Calls POST /deploymentPipelines/{id}/deploy to promote.",
        "# Fabric REST API calls:\n"
        "GET /workspaces/{id}/git/status\n"
        "POST /workspaces/{id}/git/updateFromGit\n"
        "POST /deploymentPipelines/{id}/deploy"
    )

    # -- Layer 2: Post-Deploy Validation --
    pdf.sub_header("Layer 2: Post-Deploy Validation (Fabric Notebooks)")
    pdf.body_text(
        "After deployment, the notebook pipeline runs in order:"
    )

    widths_pipe = [35, 60, 95]
    pdf.table_row(["Step", "Notebook", "What It Validates"], header=True, widths=widths_pipe)
    pdf.table_row(["1", "00_apply_schema.py", "Tables match registry. Missing cols added. Drift flagged."], widths=widths_pipe)
    pdf.table_row(["2", "01_data_ingestion.py", "Bronze tables populated from source CSVs."], widths=widths_pipe)
    pdf.table_row(["3", "02_data_transformation.py", "Silver tables computed with business logic."], widths=widths_pipe)
    pdf.table_row(["4", "03_data_quality_checks.py", "Row counts, nulls, duplicates, range checks, schema match."], widths=widths_pipe)
    pdf.table_row(["5", "04_bpa_analyzer.py", "Runtime BPA -- 12 violation categories checked."], widths=widths_pipe)
    pdf.table_row(["6", "05_memory_analyzer.py", "Column-level memory vs budget (500 MB threshold)."], widths=widths_pipe)
    pdf.table_row(["7", "06_compression_analyzer.py", "File distribution, compression ratios, OPTIMIZE recs."], widths=widths_pipe)

    pdf.body_text(
        "The Data Quality notebook (03) is the governance backbone. It validates:"
    )
    pdf.bullet("Row count thresholds -- tables must have a minimum expected row count")
    pdf.bullet("Null checks -- critical columns (IDs, names) must not be null")
    pdf.bullet("Duplicate detection -- primary key uniqueness enforced")
    pdf.bullet("Range validation -- numeric columns checked against business ranges (e.g., PUE 1.0-3.0)")
    pdf.bullet("Allowed values -- status fields checked against enum lists")
    pdf.bullet("Schema consistency -- actual columns compared against registry (same as enforcer)")

    # -- Layer 3: Scheduled Health --
    pdf.sub_header("Layer 3: Scheduled Health Monitoring")
    pdf.body_text(
        "Two scheduled processes run independently of deployments:"
    )

    pdf.component_box(
        "health-check.yml (GitHub Actions, every 2 hours)",
        "Calls Fabric REST API GET /workspaces/{id}/git/status for each environment (Dev, UAT, Prod). "
        "Reports whether the workspace is in sync with the Git branch. If drift is detected (workspace "
        "state differs from Git), sends an alert to the Microsoft Teams channel via webhook.",
        "# Runs every 2 hours:\n"
        "on:\n"
        "  schedule:\n"
        "    - cron: '0 */2 * * *'\n"
        "# Checks 3 workspaces:\n"
        "for env in dev uat prod; do\n"
        "  curl GET /workspaces/$ID/git/status\n"
        "done"
    )

    pdf.component_box(
        "Schema Enforcer Scheduled Run (Fabric Pipeline)",
        "00_apply_schema.py is also triggered on a schedule (e.g., every 2 hours) independent of "
        "deployments. This catches drift that happens BETWEEN deployments -- someone using the SQL "
        "endpoint to ALTER TABLE, or using the Fabric UI to add a column. When drift is detected, "
        "the pipeline blocks and Teams alerts fire.",
        "# Scheduled via Fabric Pipeline:\n"
        "# Activity: Run notebook 00_apply_schema\n"
        "# Trigger: Schedule (every 2 hours)\n"
        "# On DRIFT: Pipeline status = BLOCKED\n"
        "#           Teams webhook alert sent"
    )

    pdf.sub_header("Security Layer Integration")
    pdf.body_text(
        "Governance extends beyond schemas into the security model. Four layers must be consistent:"
    )
    pdf.bullet("Workspace permissions -- role-based access per environment (security/onelake-roles.json)")
    pdf.bullet("OneLake RBAC -- region-based data access roles (NorthAmerica, EMEA, APAC, LATAM)")
    pdf.bullet("Semantic model RLS -- DAX row-level security filtering by USERPRINCIPALNAME()")
    pdf.bullet("OLS / hidden tables -- security bridge tables hidden from end users via IsAvailableInMDX=false")
    pdf.body_text(
        "The RLS rules are defined in security/rls-rules.dax and tracked in Git alongside the "
        "schema registry. Changes to security rules follow the same PR -> CI -> deploy workflow."
    )

    # ================================================================
    # ACT 1: THE CRISIS (Screens 1-4)
    # ================================================================
    pdf.section_banner("ACT 1: THE CRISIS (Screens 1-4)",
                       "Set the scene -- three simultaneous problems land on Monday morning")

    # Screen 1
    pdf.screen_header(1, "Monday Morning Crisis", "ACT 1: The Crisis",
                      "All 3 Use Cases -- Setup", "~2 min")
    pdf.action("DO", "Open DigitalRealty_StoryDemo.html in browser. Press F11 for fullscreen.")
    pdf.action("EXPECT", "Title screen: 'Monday Morning at Digital Realty' with three red metric cards showing 45s load time, 89% CU saturation, 1 schema drift.")
    pdf.action("SAY", "It's Monday morning. Your phone is blowing up. The CFO can't get her sustainability numbers. Capacity is maxed. Someone made unauthorized changes to production. Sound familiar? This is what happens without automated governance. Let me show you what we're going to fix today.")
    pdf.value_prop("Immediately frames the demo around THEIR pain -- not feature lists. Gets heads nodding.")
    pdf.action("NOTE", "Pause 3-5 seconds. Let the numbers sink in. Then press right arrow.")
    pdf.divider()

    # Screen 2
    pdf.screen_header(2, "Slow Dashboard (45 seconds)", "ACT 1: The Crisis",
                      "UC1: Performance Optimization", "~2 min")
    pdf.action("CLICK", "Press RIGHT ARROW to advance to Screen 2")
    pdf.action("EXPECT", "Power BI dashboard mockup with a spinning loader, '45 seconds' in red, faded KPI cards behind it.")
    pdf.action("SAY", "This is what your executives see every morning. 45 seconds staring at a spinner. The data is there, but the model is so bloated that every query crawls. Let's find out why.")
    pdf.value_prop("Every second of dashboard load time costs user trust and executive patience.")
    pdf.action("NOTE", "Point to the spinner animation and the faded cards. The SLA target (3 seconds) is shown below.")
    pdf.divider()

    # Screen 3
    pdf.screen_header(3, "Capacity Metrics App -- 89% CU", "ACT 1: The Crisis",
                      "UC1: Performance Optimization", "~2 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 3")
    pdf.action("EXPECT", "Fabric Admin Portal Capacity Metrics App: 89% CU (red), 890 MB memory (yellow), 12.4s avg query (yellow). Table shows DigitalRealty_Capacity semantic model as top consumer.")
    pdf.action("SAY", "Here's the Capacity Metrics App. 89% CU utilization -- you're about to get throttled. The semantic model is using 890 MB -- 78% over budget. And the transformation notebook is competing for the same capacity. Spark and Power BI are fighting each other.")
    pdf.value_prop("Without visibility into what's consuming capacity, you're flying blind -- and about to crash.")
    pdf.action("NOTE", "Point to the CRITICAL badge on the semantic model row. Mention the memory budget of 500 MB.")
    pdf.divider()

    # Screen 4
    pdf.screen_header(4, "Teams Alerts + Schema Drift", "ACT 1: The Crisis",
                      "UC2: Schema / UC3: Governance", "~2 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 4")
    pdf.action("EXPECT", "Three notifications: (1) CFO email asking about sustainability columns, (2) Teams alert showing schema drift in Prod -- 'unauthorized_field' added, (3) Slack from junior dev admitting they added a column to Prod.")
    pdf.action("SAY", "Three messages. The CFO wants sustainability data stuck in Dev. There's unauthorized schema drift in Prod. And the junior dev who caused it didn't know there was a process. This is what happens without automated governance. Now let me show you how we fix ALL of this with one solution.")
    pdf.value_prop("This isn't hypothetical. Every Fabric customer with multiple environments faces this exact scenario.")
    pdf.action("NOTE", "This is the emotional peak of Act 1. Three problems, one root cause: no automation. Transition to Act 2 with confidence.")

    # ================================================================
    # ACT 2: THE DIAGNOSIS (Screens 5-9)
    # ================================================================
    pdf.section_banner("ACT 2: THE DIAGNOSIS (Screens 5-9)",
                       "Show the diagnostic tools that identify root causes automatically")

    # Screen 5
    pdf.screen_header(5, "BPA Notebook -- 12 Violations Found", "ACT 2: Diagnosis",
                      "UC1: Performance Optimization", "~3 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 5")
    pdf.action("EXPECT", "Fabric notebook '04_bpa_analyzer' with Run All button, output showing '12 violations found': 4 Errors, 6 Warnings, 2 Info. Violations by category: Performance (5), DAX Expressions (4), Maintenance (2), Error Prevention (1).")
    pdf.action("SAY", "Step one: diagnosis. We run the Best Practice Analyzer notebook. 12 violations. 4 errors, 6 warnings. 5 performance issues. This is why the dashboard takes 45 seconds. Let's drill into the details.")
    pdf.value_prop("Automated diagnostics replace hours of manual DAX Studio analysis with one notebook run.")
    pdf.action("NOTE", "Point to the 'Run All' green button -- emphasize this is one click. Point to the Error count in red.")
    pdf.divider()

    # Screen 6
    pdf.screen_header(6, "DAX Anti-Pattern Details", "ACT 2: Diagnosis",
                      "UC1: Performance Optimization", "~3 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 6")
    pdf.action("EXPECT", "Detailed violation list with 4 red Error cards and 4 yellow Warning cards. Key violations: SUMX iterating 2.1M rows, FILTER(ALL()) anti-pattern (x2), AVERAGEX instead of AVERAGE, 3 calculated columns that should be measures.")
    pdf.action("SAY", "There it is. SUMX iterating 2.1 million rows on every single query -- that's your 45 seconds. Three calculated columns stored in memory that should be measures. FILTER wrapping ALL, preventing the engine from optimizing. Every one of these has a one-line fix.")
    pdf.value_prop("Root cause analysis in seconds, not hours. Every violation has a specific fix.")
    pdf.action("NOTE", "Walk through the top 3 violations slowly. Explain: SUMX scans every row. FILTER(ALL()) prevents the storage engine from optimizing. Calculated columns eat RAM 24/7.")
    pdf.action("NOTE", "RED HIGHLIGHT: 'ROOT CAUSE FOUND' banner at the bottom of the screen.")
    pdf.divider()

    # Screen 7
    pdf.screen_header(7, "Memory Analyzer -- 890 MB Breakdown", "ACT 2: Diagnosis",
                      "UC1: Performance Optimization", "~3 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 7")
    pdf.action("EXPECT", "Two output tables: (1) Table-level memory showing customer_deployments at 428 MB, datacenters at 245 MB, calc columns at 125 MB. (2) Column-level top 6: contract_notes 210 MB, raw_api_response 140 MB, datacenter_description 95 MB, then 3 calc columns (45+42+38 MB).")
    pdf.action("SAY", "Now the Memory Analyzer. 890 MB total. Look at the top consumers: contract_notes -- 210 MB of free-text that nobody uses in a report. raw_api_response -- raw JSON sitting in your semantic model. Three calculated columns eating 125 MB combined. We can recover 550 MB -- that's 62% of your model.")
    pdf.value_prop("Know exactly WHERE memory is being wasted and HOW MUCH you'll save by fixing each one.")
    pdf.action("NOTE", "Point to each #1-#6 entry. Emphasize: 'These columns are not used in any visual or measure -- they're dead weight.'")
    pdf.divider()

    # Screen 8
    pdf.screen_header(8, "Compression Analyzer -- Small Files", "ACT 2: Diagnosis",
                      "UC1: Performance Optimization", "~2 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 8")
    pdf.action("EXPECT", "Delta table storage report: 47 small files in bronze_datacenters, 312 in power_capacity. Compression ratios shown -- customer_deployments at 1.8x (should be 3x+). Summary: 4 of 7 tables have small file issues.")
    pdf.action("SAY", "Storage diagnostics. 847 small files across your Bronze tables -- each one is a separate read. Customer deployments has 1.8x compression, far below the 3x target, because of those high-cardinality text columns. One OPTIMIZE command plus removing bloat fixes both problems.")
    pdf.value_prop("Small files = slow reads. Poor compression = wasted capacity. Both are fixable.")
    pdf.action("NOTE", "This is the final diagnostic. Transition: 'Now you've seen all three root causes. Let me show you the fix.'")
    pdf.divider()

    # Screen 9
    pdf.screen_header(9, "Schema Enforcer -- Drift Detected", "ACT 2: Diagnosis",
                      "UC2: Schema Evolution", "~3 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 9")
    pdf.action("EXPECT", "Fabric notebook '00_apply_schema' output: Schema Enforcement Report showing most tables OK, but bronze_datacenters has DRIFT -- 'unauthorized_field' (STRING) not in registry. Pipeline shows BLOCKED status.")
    pdf.action("SAY", "Now the schema enforcer. It reads the registry and compares it to every table in the Lakehouse. 6 tables are clean. But look -- bronze_datacenters has a column that's not in the registry: 'unauthorized_field'. That's Marcus's Monday mistake. The pipeline is now BLOCKED. Nothing deploys until this is resolved.")
    pdf.value_prop("Unauthorized changes are caught automatically. No manual auditing. No surprises in production.")
    pdf.action("NOTE", "Point to the DRIFT! red alert. Emphasize: 'The pipeline BLOCKED itself. No human had to notice this.'")

    # ================================================================
    # ACT 3: THE FIX (Screens 10-14)
    # ================================================================
    pdf.section_banner("ACT 3: THE FIX (Screens 10-14)",
                       "Show the solution: code changes, Git workflow, and automated deployment")

    # Screen 10
    pdf.screen_header(10, "TMDL Diff: Before vs After", "ACT 3: The Fix",
                      "UC1: Performance Optimization", "~3 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 10")
    pdf.action("EXPECT", "VS Code diff view. Red (deleted): 3 calculated columns, 6 bloat columns, 4 bad DAX measures. Green (added): optimized measures using SUM, CALCULATE, AVERAGE.")
    pdf.action("SAY", "Here's the fix. Red is what we're removing. Green is what replaces it. Calculated columns become measures -- zero memory. Bloat columns removed -- 550 MB saved. SUMX becomes SUM. FILTER(ALL()) becomes CALCULATE. Each one is a one-line change. Together, they transform the model.")
    pdf.value_prop("Every fix is visible, reviewable, and reversible through Git history.")
    pdf.action("NOTE", "Walk through each diff pair slowly. 'SUMX -> SUM: 40x speedup. FILTER(ALL()) -> CALCULATE: lets the engine optimize. Calc column -> measure: 45 MB saved per column.'")
    pdf.divider()

    # Screen 11
    pdf.screen_header(11, "Schema Registry Update (v1.0 -> v1.1)", "ACT 3: The Fix",
                      "UC2: Schema Evolution", "~2 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 11")
    pdf.action("EXPECT", "VS Code editor showing 00_schema_registry.py. SCHEMA_VERSION bumped from 1.0.0 to 1.1.0. Three new sustainability columns highlighted in green (carbon_emissions_tons, renewable_energy_pct, sustainability_rating). Three bloat columns shown as removed with strikethrough.")
    pdf.action("SAY", "Here's the schema change. Version bumped from 1.0.0 to 1.1.0. Three sustainability columns added -- carbon emissions, renewable energy, sustainability rating. Three bloat columns removed. When this code reaches production, the enforcer reads it and makes the Lakehouse match. One file is the truth.")
    pdf.value_prop("The CFO gets her sustainability data. The model gets 550 MB lighter. One commit.")
    pdf.action("NOTE", "Emphasize: 'This is the ONLY file you edit to change table schemas. No Fabric UI. No SQL endpoint. Just this Python dictionary.'")
    pdf.divider()

    # Screen 12
    pdf.screen_header(12, "Git Commit + PR Summary", "ACT 3: The Fix",
                      "UC3: Governance", "~2 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 12")
    pdf.action("EXPECT", "VS Code Source Control panel: 4 staged files (TMDL, schema registry, V004 migration, quality checks). Commit message: 'fix: optimize model + add sustainability schema v1.1'. PR summary sidebar showing: 4 files, +47/-23 lines, fixes 12 BPA violations, saves 550 MB, adds sustainability columns, removes drift.")
    pdf.action("SAY", "One pull request. Four files changed. 47 lines of code. This single PR fixes 12 BPA violations, saves 550 MB of memory, adds sustainability columns for the CFO, and removes the schema drift. Everything is reviewable, auditable, and reversible. That's the power of treating infrastructure as code.")
    pdf.value_prop("One PR = one atomic change. Reviewable by the team. Reversible if anything goes wrong.")
    pdf.action("NOTE", "Point to each of the 4 files. Explain what each one does. Then point to the PR Summary box.")
    pdf.divider()

    # Screen 13
    pdf.screen_header(13, "Pipeline Running", "ACT 3: The Fix",
                      "UC3: Governance", "~2 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 13")
    pdf.action("EXPECT", "GitHub Actions workflow view. Three steps completed (green checkmarks): TMDL Anti-Pattern Scan (0 calc cols, 0 SUMX, 0 FILTER(ALL)), Schema Registry Validation (v1.1.0), Deploy to Dev (running). Two steps pending: Promote to UAT, Promote to Prod.")
    pdf.action("SAY", "Push to main. The pipeline takes over. First: static analysis of the TMDL -- zero calculated columns, zero anti-patterns, all format strings present. Second: schema registry syntax validated. Now it's deploying to Dev -- running the enforcer, executing migration V004, and doing a runtime BPA check.")
    pdf.value_prop("Automated quality gates -- no human can forget to check. Every deploy is validated.")
    pdf.action("NOTE", "Point to each green checkmark. Then point to the spinning 'Deploy to Dev' step. Then the grayed-out UAT/Prod steps: 'These require approval.'")
    pdf.divider()

    # Screen 14
    pdf.screen_header(14, "All Gates Pass -- Full Green", "ACT 3: The Fix",
                      "UC3: Governance", "~2 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 14")
    pdf.action("EXPECT", "All pipeline steps green: TMDL scan, schema validation, Dev deploy, UAT promotion, Prod promotion. Total runtime: 2m 47s. All checkmarks green.")
    pdf.action("SAY", "All green. From commit to production in 2 minutes 47 seconds. Every gate passed. TMDL lint, schema validation, runtime BPA, deployment to all three environments. This is what CI/CD should look like for a data platform.")
    pdf.value_prop("2m 47s from code to production, fully validated. Compare to manual deployments that take hours and miss issues.")
    pdf.action("NOTE", "This is the 'aha moment' for the CI/CD story. Let it breathe. Pause 3 seconds.")

    # ================================================================
    # ACT 4: THE PROOF (Screens 15-18)
    # ================================================================
    pdf.section_banner("ACT 4: THE PROOF (Screens 15-18)",
                       "Show the measurable results -- before vs after")

    # Screen 15
    pdf.screen_header(15, "Before/After: Dashboard Load Time", "ACT 4: The Proof",
                      "UC1: Performance Optimization", "~2 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 15")
    pdf.action("EXPECT", "Side-by-side comparison: LEFT (red) 45s with list of anti-patterns. RIGHT (green) 2.8s with list of fixes. Large '16x faster' in green text at bottom.")
    pdf.action("SAY", "Same dashboard. Same data. Same Fabric capacity. 45 seconds became 2.8 seconds. 16x faster. No hardware changes. No SKU upgrade. Just code optimization deployed through a pipeline.")
    pdf.value_prop("Performance optimization without buying more capacity = direct cost savings.")
    pdf.action("NOTE", "Let the numbers speak. Point to '16x faster'. Then: 'Same data. Same dashboard. Same capacity. Just optimized code.'")
    pdf.divider()

    # Screen 16
    pdf.screen_header(16, "Before/After: Memory Reduction", "ACT 4: The Proof",
                      "UC1: Performance Optimization", "~2 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 16")
    pdf.action("EXPECT", "Bar chart: tall red bar (890 MB BEFORE) with labeled memory consumers, short green bar (340 MB AFTER). Large '62% reduction' and '$180K/year in deferred costs' below.")
    pdf.action("SAY", "890 MB down to 340 MB. 62% reduction. That's 550 MB of capacity headroom you just got back. At F64 pricing, deferring that SKU upgrade saves roughly $180K per year. And we didn't lose any analytical capability -- we removed columns no report ever used.")
    pdf.value_prop("Memory optimization = capacity savings = real dollars. No capabilities lost.")
    pdf.action("NOTE", "Point to the specific column labels on the red bar: contract_notes (210 MB), raw_api_response (140 MB), etc.")
    pdf.divider()

    # Screen 17
    pdf.screen_header(17, "Sustainability Columns -- Live in Prod", "ACT 4: The Proof",
                      "UC2: Schema Evolution", "~2 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 17")
    pdf.action("EXPECT", "Fabric Portal showing bronze_power_capacity table in Prod. 13 columns (was 10). Three new columns highlighted in green: carbon_emissions_tons, renewable_energy_pct, sustainability_rating. Tabs showing Dev/UAT/Prod all at 13 columns. 'CONSISTENT ACROSS ALL ENVIRONMENTS' banner.")
    pdf.action("SAY", "And here's the answer to the CFO's email. Sustainability columns -- carbon emissions, renewable energy percentage, sustainability rating -- live in all three environments. Dev, UAT, Prod. All matching. No one logged into Fabric. The pipeline read the registry and made it happen. Board presentation: ready.")
    pdf.value_prop("Schema changes flow from Git to every environment automatically. No drift. No surprises.")
    pdf.action("NOTE", "THIS IS THE SCHEMA EVOLUTION AHA MOMENT. Point to the three green NEW rows. Then point to the Dev/UAT/Prod tabs all showing 13 columns.")
    pdf.divider()

    # Screen 18
    pdf.screen_header(18, "Next Drift Caught Automatically", "ACT 4: The Proof",
                      "UC3: Governance", "~2 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 18")
    pdf.action("EXPECT", "Schema enforcer scheduled run output: 6 tables OK, 1 DRIFT detected on silver_customer_analytics (extra column: test_margin_calc). Pipeline BLOCKED. Alert sent. Blue banner: 'THE SAFETY NET WORKS'.")
    pdf.action("SAY", "Thursday afternoon. Someone else adds a test column. The scheduled health check catches it within 2 hours. Teams alert fires. Pipeline blocked. This isn't a one-time fix -- it's continuous governance. Every unauthorized change is caught and documented.")
    pdf.value_prop("Continuous compliance, not point-in-time audits. The system watches 24/7.")
    pdf.action("NOTE", "Emphasize: 'This happened without anyone asking for it. The system runs on a schedule.'")

    # ================================================================
    # ACT 5: THE CLOSE (Screens 19-20)
    # ================================================================
    pdf.section_banner("ACT 5: THE CLOSE (Screens 19-20)",
                       "Summarize ROI and propose next steps")

    # Screen 19
    pdf.screen_header(19, "ROI Summary -- All 3 Use Cases", "ACT 5: The Close",
                      "All 3 Use Cases", "~2 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 19")
    pdf.action("EXPECT", "Four metric cards: 16x Faster Dashboards, 62% Memory Reduction, 40h Saved/Month, $180K Deferred Costs. Two columns: 'What We Solved Today' (6 items with green checks) and 'What You Get Going Forward' (6 items with blue arrows).")
    pdf.action("SAY", "Let's recap. 16x faster dashboards. 62% less memory. 40 hours saved per month in manual schema work. $180K in deferred capacity costs. And going forward, every PR gets BPA-checked, memory-budgeted, and schema-validated before it touches production. This is the Monday morning you WANT to have.")
    pdf.value_prop("Quantified ROI across all three use cases. Real numbers, not estimates.")
    pdf.action("NOTE", "Walk through the 'What We Solved Today' list item by item. Then: 'And this is just day one.'")
    pdf.divider()

    # Screen 20
    pdf.screen_header(20, "Next Steps + POC Timeline", "ACT 5: The Close",
                      "All 3 Use Cases", "~3 min")
    pdf.action("CLICK", "Press RIGHT ARROW to Screen 20")
    pdf.action("EXPECT", "POC timeline with 4 phases. Phase 1: Foundation (Git + schemas). Phase 2: Diagnostics (BPA + memory). Phase 3: Report Mode (CI gates). Phase 4: Full Automation (continuous governance).")
    pdf.action("SAY", "Here's the roadmap. Four phases. Phase 1: reverse-engineer your existing schemas into the registry and connect Git. Phase 2: deploy the diagnostic notebooks and establish baselines. Phase 3: add CI gates in report mode -- flag but don't block. Phase 4: full automation -- block bad changes, continuous governance. Questions?")
    pdf.value_prop("Phased approach reduces risk. Start with diagnostics (immediate value), build to automation.")
    pdf.action("NOTE", "This is the 'ask' slide. Propose specific dates. 'Can we schedule Phase 1 for next week?'")

    # ================================================================
    # HARD QUESTIONS & PREPARED RESPONSES
    # ================================================================
    pdf.section_banner("Hard Questions & Prepared Responses",
                       "Anticipated tough questions grouped by category")

    pdf.sub_header("Technical Depth")

    pdf.qa_pair(
        "Does this work with existing Lakehouse tables we already have?",
        "Yes. Phase 1 is specifically about reverse-engineering your existing tables into the schema registry. "
        "We run a discovery script that reads your current table structures and generates the registry Python dictionary. "
        "No data migration required -- we're adding governance on top of what you already have."
    )

    pdf.qa_pair(
        "What if we use Dataflow Gen2 or SQL to create tables instead of notebooks?",
        "The schema enforcer works regardless of HOW tables were created. It compares the registry (source of truth) "
        "against the Spark catalog (actual state). Whether a table was created by notebook, DFG2, SQL endpoint, or "
        "the Fabric UI, drift is detected. The key rule: ALL schema changes go through the registry file first."
    )

    pdf.qa_pair(
        "Can the BPA run automatically on every PR, not just manually?",
        "Absolutely. The performance-gate.yml workflow already does static TMDL analysis on every PR. For runtime BPA "
        "(which requires a live Fabric session), we trigger it as a post-deploy step. The CI gate catches 80% of issues "
        "statically; the runtime check catches the rest."
    )

    pdf.qa_pair(
        "What about breaking schema changes -- renaming columns, changing types?",
        "Breaking changes use the migration pattern. See V003 (add columns) and V004 (remove columns) in the repo. "
        "Each migration is idempotent -- it checks before acting. For type changes, we create a new column, backfill, "
        "drop the old one. The quality gate validates the result."
    )

    pdf.sub_header("Fabric-Specific")

    pdf.qa_pair(
        "Why can't Fabric Git integration handle schema changes natively?",
        "Fabric Git tracks artifact METADATA (notebook code, pipeline JSON, semantic model TMDL) but not Lakehouse "
        "TABLE STRUCTURES. A Lakehouse .platform file in Git has workspace/item IDs -- not CREATE TABLE statements. "
        "This is by design: Lakehouse tables are data-layer objects, not metadata. Our Schema-as-Code approach bridges this gap."
    )

    pdf.qa_pair(
        "Does DirectLake mode still work after these optimizations?",
        "Yes, and it works BETTER. Removing bloat columns means fewer columns for DirectLake to frame. "
        "Converting calculated columns to measures means less memory pressure. The compression improvements "
        "also reduce the data DirectLake needs to read from OneLake."
    )

    pdf.sub_header("Pricing & ROI")

    pdf.qa_pair(
        "What does this cost to implement?",
        "The notebooks, workflows, and scripts are included in this engagement. No additional software licenses needed -- "
        "it runs on GitHub Actions (included in GitHub Enterprise) and Fabric Spark (your existing capacity). "
        "The $180K savings is from deferred F64 capacity upgrades alone."
    )

    pdf.qa_pair(
        "How long until we see results?",
        "Phase 1 (Foundation) delivers the schema registry and first drift detection within the first sprint. "
        "Phase 2 (Diagnostics) gives you the BPA/memory baselines immediately. The 16x dashboard improvement "
        "happens as soon as the optimized TMDL is deployed -- that can be day one of the POC."
    )

    pdf.sub_header("Migration & Risk")

    pdf.qa_pair(
        "What if we already have a deployment pipeline in Azure DevOps?",
        "The schema-as-code pattern is CI/CD-agnostic. The schema registry, enforcer, and migration notebooks "
        "work the same whether triggered by GitHub Actions, Azure DevOps Pipelines, or manual execution. "
        "We provide GitHub Actions workflows but the same logic ports to YAML pipelines."
    )

    pdf.qa_pair(
        "What's the risk if the enforcer blocks a deployment incorrectly?",
        "The enforcer has a DRY-RUN mode that reports drift without blocking. We recommend running in report mode "
        "(Phase 3) for 2 weeks before enabling blocking. Every block is logged with the exact drift details, "
        "so overrides are always possible via PR to the registry."
    )

    # ================================================================
    # FALLBACK PLANS
    # ================================================================
    pdf.section_banner("Fallback Plans",
                       "What to do if the live demo has issues")

    pdf.sub_header("If the HTML file doesn't load")
    pdf.bullet("Option A: Refresh the browser (Ctrl+F5). Check zoom is 100%.")
    pdf.bullet("Option B: Open DigitalRealty_Realistic_Demo.html (18-screen backup).")
    pdf.bullet("Option C: Open DigitalRealty_Visual_Demo.html (17-screen backup).")

    pdf.sub_header("If navigation stops working")
    pdf.bullet("Option A: Click directly on the navigation dots at the bottom.")
    pdf.bullet("Option B: Open browser console (F12) and type: showScreen(N) where N is the screen number.")
    pdf.bullet("Option C: Use the keyboard -- left/right arrows navigate between screens.")

    pdf.sub_header("If a screen doesn't render properly")
    pdf.bullet("Option A: Skip to the next screen (right arrow) and narrate what was supposed to show.")
    pdf.bullet("Option B: Refer to the PDF demo guide for the talk track and value props.")
    pdf.bullet("Option C: Use the DigitalRealty_Schema_Evolution_Demo_Guide.pdf for screenshots.")

    pdf.sub_header("If customers ask for a live demo instead")
    pdf.bullet("Option A: Explain this is the architecture/approach walkthrough. Live POC is Phase 1.")
    pdf.bullet("Option B: Show the actual notebooks in the repo (notebooks/ folder) to prove they're real code.")
    pdf.bullet("Option C: Show the TMDL files side-by-side in VS Code to demonstrate the before/after.")

    # ================================================================
    # SUCCESS CRITERIA
    # ================================================================
    pdf.section_banner("Success Criteria",
                       "How to know the demo landed well")

    pdf.sub_header("During the Demo")
    pdf.check_item("Customer asks clarifying questions (engagement signal)", False)
    pdf.check_item("Customer references their own pain points ('we have that problem')", False)
    pdf.check_item("Customer asks about timeline or POC scope (buying signal)", False)
    pdf.check_item("Customer mentions other teams who need to see this", False)

    pdf.sub_header("After the Demo")
    pdf.check_item("POC start date agreed", False)
    pdf.check_item("Technical point of contact identified", False)
    pdf.check_item("Access to at least one Fabric workspace granted", False)
    pdf.check_item("Follow-up meeting scheduled within 1 week", False)

    pdf.sub_header("Key Metrics to Reference")
    widths2 = [50, 40, 40, 60]
    pdf.table_row(["Metric", "Before", "After", "Impact"], header=True, widths=widths2)
    pdf.table_row(["Dashboard Load", "45s", "2.8s", "16x faster"], widths=widths2)
    pdf.table_row(["Model Memory", "890 MB", "340 MB", "62% reduction"], widths=widths2)
    pdf.table_row(["BPA Violations", "12", "0", "100% resolved"], widths=widths2)
    pdf.table_row(["Pipeline Time", "Manual", "2m 47s", "Fully automated"], widths=widths2)
    pdf.table_row(["Monthly Effort", "40+ hours", "~0", "40h saved/month"], widths=widths2)
    pdf.table_row(["Capacity Cost", "SKU upgrade", "Deferred", "$180K/year saved"], widths=widths2)

    # ---- Output ----
    output_path = os.path.join(os.path.dirname(__file__), "DigitalRealty_3UseCase_Demo_Guide.pdf")
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")
    print(f"Size: {os.path.getsize(output_path) / 1024:.0f} KB")


if __name__ == "__main__":
    build_pdf()
