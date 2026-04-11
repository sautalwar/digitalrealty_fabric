"""
Generate DigitalRealty_Project_Explanation.pdf
Comprehensive color-coded explanation of the entire Digital Realty Fabric project.
"""
from fpdf import FPDF, XPos, YPos
import os, datetime

# ── Color palette ──────────────────────────────────────────────────────────────
MSFT_BLUE   = (0, 120, 212)
DARK_GRAY   = (50, 50, 50)
MED_GRAY    = (100, 100, 100)
LIGHT_GRAY  = (180, 180, 180)
WHITE       = (255, 255, 255)
GREEN       = (16, 124, 16)
ORANGE      = (202, 80, 16)
RED         = (196, 43, 28)
PURPLE      = (107, 36, 178)
TEAL        = (0, 128, 128)
GOLD        = (180, 140, 20)
NAVY        = (0, 50, 100)
CODE_BG     = (240, 240, 245)
SECTION_BG  = (230, 240, 255)
WARN_BG     = (255, 245, 230)
ERR_BG      = (255, 235, 235)
OK_BG       = (235, 250, 235)
GOLD_BG     = (255, 248, 220)
PURPLE_BG   = (245, 235, 255)
TEAL_BG     = (230, 248, 248)

class ProjectPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*MED_GRAY)
        self.cell(0, 8, "Digital Realty Trust - Fabric CI/CD Project Guide",
                  new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.set_draw_color(*MSFT_BLUE)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*MED_GRAY)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}  |  CONFIDENTIAL  |  Digital Realty Trust",
                  align="C")

    def title_page_line(self, text, size=14, color=DARK_GRAY, bold=False):
        self.set_font("Helvetica", "B" if bold else "", size)
        self.set_text_color(*color)
        self.cell(0, size * 0.7, text, align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.ln(2)

    def section_title(self, text, color=MSFT_BLUE):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*color)
        self.cell(0, 10, text, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.set_draw_color(*color)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def subsection(self, text, color=DARK_GRAY):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*color)
        self.cell(0, 7, text, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.ln(2)

    def body(self, text, bold=False, size=10):
        self.set_font("Helvetica", "B" if bold else "", size)
        self.set_text_color(*DARK_GRAY)
        self.set_x(10)
        self.multi_cell(190, 5.5, text, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.ln(2)

    def bullet(self, text, indent=15, color=DARK_GRAY):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*color)
        self.set_x(indent)
        self.cell(5, 5.5, chr(149), new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.multi_cell(190 - indent, 5.5, text, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.ln(1)

    def numbered(self, num, text, indent=15, color=DARK_GRAY, num_color=MSFT_BLUE):
        self.set_x(indent)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*num_color)
        self.cell(8, 5.5, f"{num}.", new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*color)
        self.multi_cell(190 - indent - 8, 5.5, text, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.ln(1)

    def code_block(self, code, bg=CODE_BG):
        self.set_fill_color(*bg)
        self.set_font("Courier", "", 8.5)
        self.set_text_color(*DARK_GRAY)
        lines = code.strip().split("\n")
        block_h = len(lines) * 4.5 + 6
        if self.get_y() + block_h > 270:
            self.add_page()
        y_start = self.get_y()
        self.rect(12, y_start, 186, block_h, "F")
        self.ln(3)
        for line in lines:
            self.set_x(15)
            self.cell(180, 4.5, line, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.ln(4)

    def colored_box(self, title, text, bg, title_color=DARK_GRAY):
        self.set_fill_color(*bg)
        lines = text.strip().split("\n")
        block_h = len(lines) * 5 + 16
        if self.get_y() + block_h > 270:
            self.add_page()
        y_start = self.get_y()
        self.rect(12, y_start, 186, block_h, "F")
        self.set_xy(15, y_start + 3)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*title_color)
        self.cell(180, 6, title, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*DARK_GRAY)
        for line in lines:
            self.set_x(15)
            self.multi_cell(178, 5, line, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.set_y(y_start + block_h + 3)

    def table_row(self, cells, widths, bold=False, bg=None, header=False):
        if bg:
            self.set_fill_color(*bg)
        h = 7
        x_start = self.get_x()
        max_y = self.get_y()
        for i, (cell, w) in enumerate(zip(cells, widths)):
            self.set_x(x_start + sum(widths[:i]))
            if header:
                self.set_font("Helvetica", "B", 9)
                self.set_text_color(*WHITE)
            elif bold:
                self.set_font("Helvetica", "B", 9)
                self.set_text_color(*DARK_GRAY)
            else:
                self.set_font("Helvetica", "", 9)
                self.set_text_color(*DARK_GRAY)
            fill = bg is not None or header
            if header:
                self.set_fill_color(*MSFT_BLUE)
            self.cell(w, h, cell, border=1, fill=fill, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.ln(h)

    def draw_box(self, x, y, w, h, title, subtitle, bg, border_color):
        self.set_fill_color(*bg)
        self.rect(x, y, w, h, "F")
        self.set_draw_color(*border_color)
        self.set_line_width(0.8)
        self.rect(x, y, w, h, "D")
        self.set_xy(x + 2, y + 2)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*border_color)
        self.multi_cell(w - 4, 4.5, title, align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.set_x(x + 2)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(*DARK_GRAY)
        self.multi_cell(w - 4, 3.5, subtitle, align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)

    def draw_arrow_h(self, x1, y, x2, color=MED_GRAY):
        self.set_draw_color(*color)
        self.set_line_width(0.6)
        self.line(x1, y, x2, y)
        self.set_fill_color(*color)
        self.polygon([(x2, y), (x2 - 3, y - 2), (x2 - 3, y + 2)], style="F")

    def draw_arrow_v(self, x, y1, y2, color=MED_GRAY):
        self.set_draw_color(*color)
        self.set_line_width(0.6)
        self.line(x, y1, x, y2)
        self.set_fill_color(*color)
        self.polygon([(x, y2), (x - 2, y2 - 3), (x + 2, y2 - 3)], style="F")

    def check_space(self, h=30):
        if self.get_y() + h > 270:
            self.add_page()


# ── Build PDF ──────────────────────────────────────────────────────────────────
pdf = ProjectPDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)

# ══════════════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.ln(30)
pdf.set_font("Helvetica", "B", 32)
pdf.set_text_color(*MSFT_BLUE)
pdf.cell(0, 16, "Digital Realty Trust", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.set_font("Helvetica", "", 18)
pdf.set_text_color(*MED_GRAY)
pdf.cell(0, 10, "Microsoft Fabric CI/CD Platform", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.ln(4)
pdf.set_draw_color(*MSFT_BLUE)
pdf.set_line_width(1.2)
pdf.line(50, pdf.get_y(), 160, pdf.get_y())
pdf.ln(10)
pdf.set_font("Helvetica", "B", 14)
pdf.set_text_color(*TEAL)
pdf.cell(0, 8, "Complete Project Explanation", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(*DARK_GRAY)
pdf.cell(0, 7, "Architecture, Components, Workflows & How Everything Connects", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.ln(25)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(*MED_GRAY)
pdf.cell(0, 6, f"Generated: {datetime.datetime.now().strftime('%B %d, %Y')}", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.cell(0, 6, "Schema Evolution | Multi-Lakehouse Sync | Performance Analysis", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)

# ══════════════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("Table of Contents")
toc = [
    ("1", "Project Overview - What and Why"),
    ("2", "Architecture Diagram - The Big Picture"),
    ("3", "Repository Structure - Every File Explained"),
    ("4", "Environment Configuration - Dev, UAT, Prod"),
    ("5", "Data Pipeline - Bronze, Silver, Gold Notebooks"),
    ("6", "Schema-as-Code Strategy - The Core Innovation"),
    ("7", "CI/CD Workflows - All GitHub Actions Explained"),
    ("8", "Dynamic Discovery Pipeline - How Tables Are Found"),
    ("9", "Deployment Pipeline - How Promotion Works"),
    ("10", "Security Model - 4-Layer Protection"),
    ("11", "Semantic Model - TMDL, DirectLake, RLS"),
    ("12", "Performance Analysis - BPA, Memory, Compression"),
    ("13", "Fabric Workspace Artifacts"),
    ("14", "Migration Scripts - Schema Versioning"),
    ("15", "Sample Data"),
    ("16", "Key API Patterns - Fabric REST API"),
    ("17", "How Everything Connects - End-to-End Flow"),
]
for num, title in toc:
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*MSFT_BLUE)
    pdf.cell(12, 7, f"{num}.", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*DARK_GRAY)
    pdf.cell(0, 7, title, new_x=XPos.LEFT, new_y=YPos.NEXT)

# ══════════════════════════════════════════════════════════════════════════════
# 1. PROJECT OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("1. Project Overview - What and Why")

pdf.body("This project implements a CI/CD-enabled Microsoft Fabric data platform for Digital Realty Trust, a global data center REIT. The platform manages power capacity, asset tracking, and sustainability data across multiple data centers worldwide.")

pdf.ln(2)
pdf.subsection("The Core Problem", RED)
pdf.body("Microsoft Fabric's Git integration works well for most artifacts (pipelines, semantic models, notebooks). However, Lakehouse structural changes -- creating tables, modifying schemas, adding columns -- are NOT captured in Git. This breaks CI/CD for schema promotion across environments.")

pdf.check_space(30)
pdf.colored_box(
    "WHAT FABRIC GIT INTEGRATION DOES AND DOESN'T DO",
    "DOES sync to Git: Notebooks, Pipelines, Semantic Models, Dataflows, Reports\n"
    "DOES NOT sync: Lakehouse table schemas, column definitions, table data\n"
    "\n"
    "This means if you add a column in Dev, the UAT Lakehouse won't know about it.\n"
    "This project solves that gap with schema-as-code + dynamic discovery.",
    WARN_BG, ORANGE
)

pdf.ln(2)
pdf.subsection("The Solution: 3 Use Cases", MSFT_BLUE)

pdf.check_space(50)
pdf.colored_box("UC1: Schema Evolution & CI/CD",
    "Version and promote Lakehouse table schemas across Dev -> UAT -> Prod.\n"
    "Notebooks define schemas. CI/CD discovers and syncs them automatically.",
    SECTION_BG, MSFT_BLUE)
pdf.ln(2)
pdf.colored_box("UC2: Performance Optimization",
    "Analyze semantic model efficiency using Best Practice Analyzer,\n"
    "VertiPaq memory analysis, and Delta compression diagnostics.",
    PURPLE_BG, PURPLE)
pdf.ln(2)
pdf.colored_box("UC3: Data Quality Governance",
    "Automated quality gates that validate row counts, null checks,\n"
    "duplicates, range validation, and allowed values before data is consumed.",
    TEAL_BG, TEAL)

# ══════════════════════════════════════════════════════════════════════════════
# 2. ARCHITECTURE DIAGRAM
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("2. Architecture Diagram - The Big Picture")

pdf.body("The architecture follows a medallion pattern (Bronze -> Silver -> Gold) with three workspace environments and automated promotion via GitHub Actions.")

pdf.ln(4)
y = pdf.get_y()

# GitHub row
pdf.draw_box(15, y, 40, 20, "GitHub", "main branch\nPR workflow", SECTION_BG, MSFT_BLUE)
pdf.draw_arrow_h(55, y + 10, 65, MSFT_BLUE)
pdf.draw_box(65, y, 40, 20, "GitHub Actions", "9 workflows\nCI/CD engine", OK_BG, GREEN)
pdf.draw_arrow_h(105, y + 10, 115, GREEN)
pdf.draw_box(115, y, 35, 20, "Fabric API", "REST + OneLake\nDFS endpoints", WARN_BG, ORANGE)
pdf.draw_arrow_h(150, y + 10, 160, ORANGE)
pdf.draw_box(160, y, 35, 20, "Fabric", "Workspaces\nLakehouses", PURPLE_BG, PURPLE)

pdf.set_y(y + 28)
y2 = pdf.get_y()

# Workspace row
pdf.draw_box(15, y2, 55, 28, "Dev Workspace", "DigitalRealty-Dev\n2 Lakehouses\nActive development", OK_BG, GREEN)
pdf.draw_arrow_h(70, y2 + 14, 80, GREEN)
pdf.draw_box(80, y2, 55, 28, "UAT Workspace", "DigitalRealty-UAT\nValidation\nEMEA filter", WARN_BG, ORANGE)
pdf.draw_arrow_h(135, y2 + 14, 145, ORANGE)
pdf.draw_box(145, y2, 55, 28, "Prod Workspace", "DigitalRealty-Prod\nProduction\nALL regions", SECTION_BG, MSFT_BLUE)

pdf.set_y(y2 + 36)
y3 = pdf.get_y()

# Lakehouse row
pdf.draw_box(15, y3, 90, 25, "DigitalRealty_Capacity", "Schemas: dbo\nTables: bronze_assets, bronze_budgets,\nsilver_asset_summary, silver_regional_summary", TEAL_BG, TEAL)
pdf.draw_box(110, y3, 90, 25, "DataCenterLakehouse", "Schemas: year_2017-year_2022 (6 schemas)\n7 tables with yearly datacenter metrics\nNon-standard schema names", GOLD_BG, GOLD)

pdf.set_y(y3 + 33)
y4 = pdf.get_y()

# Data pipeline row
pdf.draw_box(15, y4, 55, 22, "Bronze Layer", "01_data_ingestion.py\nRaw CSV -> Delta tables\nbronze_* prefix", (255, 205, 150), ORANGE)
pdf.draw_arrow_h(70, y4 + 11, 80, ORANGE)
pdf.draw_box(80, y4, 55, 22, "Silver Layer", "02_data_transformation.py\nCleansed + business logic\nsilver_* prefix", (200, 200, 230), PURPLE)
pdf.draw_arrow_h(135, y4 + 11, 145, PURPLE)
pdf.draw_box(145, y4, 55, 22, "Gold / Quality", "03_data_quality_checks.py\nValidation gates\nRow counts, nulls, ranges", (200, 235, 200), GREEN)

pdf.set_y(y4 + 30)

# ══════════════════════════════════════════════════════════════════════════════
# 3. REPOSITORY STRUCTURE
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("3. Repository Structure - Every File Explained")

pdf.body("The repository has a clear structure. Here is every directory and file with its purpose:")

pdf.ln(2)
# ── .github/workflows/ ────────────────────────────────────────────────────────
pdf.subsection(".github/workflows/ - CI/CD Automation (9 workflows)", MSFT_BLUE)

widths = [75, 115]
pdf.table_row(["Workflow File", "Purpose"], widths, header=True)
pdf.table_row(["promote-with-schema-validation.yml", "Core: Discover schemas, deploy, sync tables Dev->UAT"], widths, bg=SECTION_BG)
pdf.table_row(["fabric-git-sync-on-merge.yml", "Auto-sync Fabric workspace from Git on PR merge"], widths)
pdf.table_row(["performance-analysis.yml", "Run BPA + memory + compression analysis notebooks"], widths, bg=SECTION_BG)
pdf.table_row(["performance-gate.yml", "Gate: block promotion if perf metrics below threshold"], widths)
pdf.table_row(["schema-enforcement-post-deploy.yml", "Post-deploy: validate schemas match after promotion"], widths, bg=SECTION_BG)
pdf.table_row(["squad-heartbeat.yml", "Health check: monitor workflow health + alert Teams"], widths)
pdf.table_row(["squad-issue-assign.yml", "Auto-assign issues to squad members"], widths, bg=SECTION_BG)
pdf.table_row(["squad-triage.yml", "Auto-label and triage incoming issues"], widths)
pdf.table_row(["sync-squad-labels.yml", "Sync GitHub labels for the squad workflow"], widths, bg=SECTION_BG)

pdf.check_space(60)
pdf.ln(4)
# ── scripts/ ──────────────────────────────────────────────────────────────────
pdf.subsection("scripts/ - Automation Scripts (4 files)", TEAL)

widths = [75, 115]
pdf.table_row(["Script File", "Purpose"], widths, header=True)
pdf.table_row(["discover_fabric_schema.py", "Scan ALL lakehouses via Fabric API + OneLake DFS"], widths, bg=TEAL_BG)
pdf.table_row(["gen_nb_payload.py", "Generate self-contained Fabric notebook for table sync"], widths)
pdf.table_row(["Check-GitSyncStatus.ps1", "Check Git sync health across all workspaces"], widths, bg=TEAL_BG)
pdf.table_row(["Validate-SchemaConsistency.ps1", "Compare live Lakehouse schema vs Git schema registry"], widths)

pdf.check_space(70)
pdf.ln(4)
# ── notebooks/ ────────────────────────────────────────────────────────────────
pdf.subsection("notebooks/ - PySpark Notebooks (8 files)", PURPLE)

widths = [70, 120]
pdf.table_row(["Notebook File", "Purpose"], widths, header=True)
pdf.table_row(["00_schema_registry.py", "Schema source of truth - defines table structures"], widths, bg=PURPLE_BG)
pdf.table_row(["00_apply_schema.py", "Enforce registry schemas onto Lakehouse tables"], widths)
pdf.table_row(["01_data_ingestion.py", "Bronze: Load CSVs into bronze_* Delta tables"], widths, bg=PURPLE_BG)
pdf.table_row(["02_data_transformation.py", "Silver: Business logic, cleansing -> silver_* tables"], widths)
pdf.table_row(["03_data_quality_checks.py", "Gold: Row counts, nulls, duplicates, range validation"], widths, bg=PURPLE_BG)
pdf.table_row(["04_bpa_analyzer.py", "Performance: Semantic model Best Practice Analyzer"], widths)
pdf.table_row(["05_memory_analyzer.py", "Performance: VertiPaq/memory bloat analysis"], widths, bg=PURPLE_BG)
pdf.table_row(["06_compression_analyzer.py", "Performance: Delta storage compression diagnostics"], widths)

# ── environments/ ─────────────────────────────────────────────────────────────
pdf.add_page()
pdf.subsection("environments/ - Workspace Configs (3 JSON files)", GREEN)

widths = [40, 55, 50, 45]
pdf.table_row(["File", "Workspace Name", "Region Filter", "Schedule"], widths, header=True)
pdf.table_row(["dev.json", "DigitalRealty-Dev", "ALL", "Manual"], widths, bg=OK_BG)
pdf.table_row(["uat.json", "DigitalRealty-UAT", "EMEA", "Daily 0600 UTC"], widths)
pdf.table_row(["prod.json", "DigitalRealty-Prod", "ALL", "Daily 0400 UTC"], widths, bg=OK_BG)

pdf.ln(4)
# ── deployment-pipeline/ ─────────────────────────────────────────────────────
pdf.subsection("deployment-pipeline/ - Promotion Config (2 files)", ORANGE)

widths = [70, 120]
pdf.table_row(["File", "Purpose"], widths, header=True)
pdf.table_row(["deployment-rules.json", "Lakehouse name mapping + notebook promotion rules"], widths, bg=WARN_BG)
pdf.table_row(["pipeline-config.json", "Deployment pipeline ID, stage names, ordering"], widths)

pdf.ln(4)
# ── security/ ─────────────────────────────────────────────────────────────────
pdf.subsection("security/ - Access Control (2 files)", RED)

widths = [70, 120]
pdf.table_row(["File", "Purpose"], widths, header=True)
pdf.table_row(["onelake-roles.json", "Region-based OneLake RBAC: NA, EMEA, APAC, Global"], widths, bg=ERR_BG)
pdf.table_row(["rls-rules.dax", "DAX row-level security by USERPRINCIPALNAME()"], widths)

pdf.ln(4)
# ── semantic-model/ ───────────────────────────────────────────────────────────
pdf.subsection("semantic-model/ - TMDL Model (2 files)", NAVY)

widths = [85, 105]
pdf.table_row(["File", "Purpose"], widths, header=True)
pdf.table_row(["digitalrealty-capacity.tmdl", "DirectLake semantic model with measures + RLS"], widths, bg=SECTION_BG)
pdf.table_row(["digitalrealty-capacity-BEFORE.tmdl", "Pre-optimization baseline for comparison"], widths)

pdf.ln(4)
# ── remaining dirs ────────────────────────────────────────────────────────────
pdf.subsection("Other Directories", MED_GRAY)

widths = [50, 70, 70]
pdf.table_row(["Directory", "Contents", "Purpose"], widths, header=True)
pdf.table_row(["migrations/", "V001-V004 .py files", "Versioned schema DDL scripts"], widths, bg=CODE_BG)
pdf.table_row(["sample-data/", "5 CSV files", "Test data for ingestion notebooks"], widths)
pdf.table_row(["fabric-workspace/", "Lakehouse + Notebook", "Git-exported Fabric artifacts"], widths, bg=CODE_BG)
pdf.table_row(["docs/", "schema-evolution-guide.md", "Schema-as-code documentation"], widths)
pdf.table_row(["diagrams/", "(empty)", "Reserved for architecture diagrams"], widths, bg=CODE_BG)

# ══════════════════════════════════════════════════════════════════════════════
# 4. ENVIRONMENT CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("4. Environment Configuration - Dev, UAT, Prod")

pdf.body("Each environment has a JSON config file that the CI/CD workflows read at runtime. These files contain workspace IDs, lakehouse names, SQL endpoints, and scheduling info.")

pdf.ln(2)
pdf.subsection("Environment Flow:")

y = pdf.get_y()
pdf.draw_box(15, y, 55, 30, "Dev", "Active development\nAll regions\nFeature branches", OK_BG, GREEN)
pdf.draw_arrow_h(70, y + 15, 80, GREEN)
pdf.draw_box(80, y + 3, 55, 24, "UAT", "Validation\nEMEA region subset\nApproval required", WARN_BG, ORANGE)
pdf.draw_arrow_h(135, y + 15, 145, ORANGE)
pdf.draw_box(145, y + 3, 55, 24, "Prod", "Production\nAll regions\nFull data", SECTION_BG, MSFT_BLUE)
pdf.set_y(y + 38)

pdf.code_block(
    '// environments/dev.json\n'
    '{\n'
    '  "workspace_id": "ffb373f3-c810-453a-b598-badb52dfd152",\n'
    '  "workspace_name": "DigitalRealty-Dev",\n'
    '  "lakehouse_name": "DigitalRealty_Capacity",\n'
    '  "filter_region": "ALL"\n'
    '}\n\n'
    '// environments/uat.json\n'
    '{\n'
    '  "workspace_id": "a27b49db-255b-499e-a2ac-e00f8b812d1a",\n'
    '  "workspace_name": "DigitalRealty-UAT",\n'
    '  "lakehouse_name": "DigitalRealty_Capacity",\n'
    '  "filter_region": "EMEA"\n'
    '}\n\n'
    '// environments/prod.json\n'
    '{\n'
    '  "workspace_id": "...",\n'
    '  "workspace_name": "DigitalRealty-Prod",\n'
    '  "filter_region": "ALL"\n'
    '}'
)

pdf.colored_box(
    "WHY REGION FILTERS?",
    "Dev and Prod use ALL regions for full testing/production.\n"
    "UAT uses EMEA subset to speed up validation with smaller data volume.\n"
    "Dataflow Gen2 parameters (pFilterRegion) are swapped per environment\n"
    "using deployment rules.",
    SECTION_BG, MSFT_BLUE
)

# ══════════════════════════════════════════════════════════════════════════════
# 5. DATA PIPELINE - NOTEBOOKS
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("5. Data Pipeline - Bronze, Silver, Gold Notebooks")

pdf.body("The data pipeline follows the Medallion Architecture pattern. Notebooks are numbered for execution order and each layer builds on the previous one.")

pdf.ln(2)

# Visual pipeline
y = pdf.get_y()
pdf.draw_box(15, y, 58, 35, "BRONZE (01)", "01_data_ingestion.py\n\nCSV files -> Delta tables\nbronze_assets\nbronze_budgets", (255, 220, 180), ORANGE)
pdf.draw_arrow_h(73, y + 17, 83, ORANGE)
pdf.draw_box(83, y, 58, 35, "SILVER (02)", "02_data_transformation.py\n\nBusiness logic + cleansing\nsilver_asset_summary\nsilver_regional_summary", (220, 210, 245), PURPLE)
pdf.draw_arrow_h(141, y + 17, 151, PURPLE)
pdf.draw_box(151, y, 50, 35, "GOLD (03)", "03_data_quality.py\n\nValidation gates\nRow counts\nNull checks", (210, 240, 210), GREEN)
pdf.set_y(y + 43)

pdf.subsection("01_data_ingestion.py (Bronze Layer)", ORANGE)
pdf.body("Reads raw CSV files from the Files/ section of the Lakehouse and writes them as Delta tables with the bronze_ prefix. Uses explicit StructType schemas (not inferred). Write mode is 'overwrite' for full refresh.")
pdf.code_block(
    "# Pattern:\n"
    "schema = StructType([StructField('asset_id', StringType()), ...])\n"
    "df = spark.read.csv('Files/datacenters.csv', header=True, schema=schema)\n"
    "df.write.format('delta').mode('overwrite').saveAsTable('dbo.bronze_assets')"
)

pdf.check_space(40)
pdf.subsection("02_data_transformation.py (Silver Layer)", PURPLE)
pdf.body("Reads bronze tables, applies business logic (depreciation calculations, variance analysis, regional summaries), and writes silver_ tables. Includes incremental merge patterns for large datasets.")
pdf.code_block(
    "# Pattern:\n"
    "bronze_df = spark.table('dbo.bronze_assets')\n"
    "silver_df = bronze_df.withColumn('depreciation',\n"
    "    col('original_cost') * (1 - col('years_in_service') / col('useful_life')))\n"
    "silver_df.write.format('delta').mode('overwrite').saveAsTable('dbo.silver_asset_summary')"
)

pdf.check_space(40)
pdf.subsection("03_data_quality_checks.py (Gold / Validation Layer)", GREEN)
pdf.body("Validates silver tables against quality rules: minimum row counts, null percentage thresholds, duplicate detection, numeric range validation, and allowed categorical values. Raises exceptions if quality gates fail -- blocking downstream consumption.")
pdf.code_block(
    "# Pattern:\n"
    "row_count = spark.table('dbo.silver_asset_summary').count()\n"
    "assert row_count >= 100, f'Row count {row_count} below minimum 100'\n"
    "null_pct = df.where(col('asset_id').isNull()).count() / row_count\n"
    "assert null_pct < 0.01, f'Null rate {null_pct:.2%} exceeds 1% threshold'"
)

# ══════════════════════════════════════════════════════════════════════════════
# 6. SCHEMA-AS-CODE
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("6. Schema-as-Code Strategy - The Core Innovation")

pdf.body("Since Fabric doesn't version Lakehouse schemas in Git, this project treats notebooks as the schema source of truth. Schema changes go through code, not through the Fabric UI.")

pdf.ln(2)
pdf.subsection("The Schema Registry (00_schema_registry.py)", TEAL)
pdf.body("This notebook is the single source of truth for table schemas. It defines every table's structure using Python dictionaries with column names, types, and nullability.")

pdf.code_block(
    "# notebooks/00_schema_registry.py\n"
    'SCHEMA_VERSION = "2.3"\n\n'
    "SCHEMAS = {\n"
    '    "bronze_assets": {\n'
    '        "columns": [\n'
    '            ("asset_id",        "STRING",  False),\n'
    '            ("asset_name",      "STRING",  True),\n'
    '            ("datacenter_id",   "STRING",  False),\n'
    '            ("original_cost",   "DECIMAL", True),\n'
    '            ("install_date",    "DATE",    True),\n'
    "        ]\n"
    "    },\n"
    '    "bronze_budgets": { ... },\n'
    '    "silver_asset_summary": { ... },\n'
    "}"
)

pdf.check_space(40)
pdf.subsection("The Schema Enforcer (00_apply_schema.py)")
pdf.body("This notebook reads the registry and compares it against actual Lakehouse tables. It applies additive changes (new columns) idempotently and reports any drift.")

pdf.check_space(40)
pdf.subsection("The Schema Change Workflow:")

pdf.numbered(1, "Developer modifies the schema definition in the appropriate notebook (registry or ingestion).")
pdf.numbered(2, "For additive changes (new columns, new tables): update the write schema in the notebook.")
pdf.numbered(3, "For breaking changes (type changes, renames): create a migration step that handles both old and new states.")
pdf.numbered(4, "The quality notebook (03_) must be updated to validate new schema expectations.")
pdf.numbered(5, "Commit, PR, merge -- the CI/CD pipeline handles promotion automatically.")

pdf.check_space(30)
pdf.colored_box(
    "GOLDEN RULE",
    "NEVER modify schemas directly in the Fabric UI for tracked environments.\n"
    "All schema changes go through code -> Git -> CI/CD.\n"
    "The UI is for exploration only.",
    ERR_BG, RED
)

# ══════════════════════════════════════════════════════════════════════════════
# 7. CI/CD WORKFLOWS
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("7. CI/CD Workflows - All GitHub Actions Explained")

pdf.body("There are 9 GitHub Actions workflows. Here is what each one does and when it triggers:")

pdf.ln(2)
pdf.subsection("Core Workflows (UC1: Schema Evolution)", MSFT_BLUE)

pdf.colored_box(
    "promote-with-schema-validation.yml  [THE MAIN WORKFLOW]",
    "Trigger: Push to main (schema-related files) OR manual dispatch\n"
    "Jobs: preflight -> deploy -> enforce-schemas -> verify\n\n"
    "1. PREFLIGHT: Discover ALL lakehouses + tables via Fabric API\n"
    "2. DEPLOY: Trigger Fabric deployment pipeline (artifact definitions)\n"
    "3. ENFORCE: For EACH lakehouse, generate + upload + run sync notebook\n"
    "4. VERIFY: Scan ALL UAT lakehouses to confirm tables arrived\n\n"
    "This is the 920-line orchestrator that does the actual promotion.",
    SECTION_BG, MSFT_BLUE
)

pdf.ln(2)
pdf.colored_box(
    "fabric-git-sync-on-merge.yml",
    "Trigger: PR merge to main\n"
    "Action: Calls Fabric API 'updateFromGit' to sync workspace from Git\n"
    "Purpose: Keeps Fabric workspace artifacts in sync with Git (notebooks, etc.)",
    OK_BG, GREEN
)

pdf.ln(2)
pdf.colored_box(
    "schema-enforcement-post-deploy.yml",
    "Trigger: After deployment completes\n"
    "Action: Runs Validate-SchemaConsistency.ps1 against target workspace\n"
    "Purpose: Double-check that schemas match after promotion",
    TEAL_BG, TEAL
)

pdf.check_space(50)
pdf.ln(2)
pdf.subsection("Performance Workflows (UC2)", PURPLE)

pdf.colored_box(
    "performance-analysis.yml",
    "Trigger: Manual dispatch or scheduled\n"
    "Action: Runs notebooks 04, 05, 06 (BPA, memory, compression)\n"
    "Purpose: Generate performance reports for semantic model optimization",
    PURPLE_BG, PURPLE
)
pdf.ln(2)
pdf.colored_box(
    "performance-gate.yml",
    "Trigger: Before promotion (optional gate)\n"
    "Action: Checks if performance metrics meet thresholds\n"
    "Purpose: Block promotion if model is too bloated or slow",
    PURPLE_BG, PURPLE
)

pdf.check_space(55)
pdf.ln(2)
pdf.subsection("Operational Workflows (Squad)", ORANGE)

pdf.colored_box(
    "Squad Workflows (4 files)",
    "squad-heartbeat.yml    - Health check every 2 hours, alerts Teams on drift\n"
    "squad-issue-assign.yml - Auto-assign issues to squad members by label\n"
    "squad-triage.yml       - Auto-label and prioritize incoming issues\n"
    "sync-squad-labels.yml  - Keep GitHub labels in sync with squad config",
    WARN_BG, ORANGE
)

# ══════════════════════════════════════════════════════════════════════════════
# 8. DYNAMIC DISCOVERY PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("8. Dynamic Discovery Pipeline - How Tables Are Found")

pdf.body("Nothing is hardcoded. The pipeline dynamically discovers all lakehouses, schemas, and tables at runtime using 3 chained scripts.")

pdf.ln(2)
# Diagram
y = pdf.get_y()
pdf.draw_box(15, y, 55, 22, "Fabric REST API", "GET /lakehouses\n+ OneLake DFS", SECTION_BG, TEAL)
pdf.draw_arrow_h(70, y + 11, 78, TEAL)
pdf.draw_box(78, y, 55, 22, "discover_fabric_\nschema.py", "Step 1: Scan\nall lakehouses", OK_BG, GREEN)
pdf.draw_arrow_h(133, y + 11, 141, GREEN)
pdf.draw_box(141, y, 55, 22, "schema_discovery\n.json", "All LHs, schemas\ntables, columns", WARN_BG, ORANGE)

pdf.set_y(y + 28)
y2 = pdf.get_y()
pdf.draw_box(15, y2, 55, 22, "schema_discovery\n.json", "Input from Step 1", WARN_BG, ORANGE)
pdf.draw_arrow_h(70, y2 + 11, 78, ORANGE)
pdf.draw_box(78, y2, 55, 22, "gen_nb_payload.py", "Step 2: Generate\nnotebook per LH", OK_BG, PURPLE)
pdf.draw_arrow_h(133, y2 + 11, 141, PURPLE)
pdf.draw_box(141, y2, 55, 22, "nb_payload.json", "Self-contained\nFabric notebook", SECTION_BG, MSFT_BLUE)

pdf.set_y(y2 + 28)
y3 = pdf.get_y()
pdf.draw_box(15, y3, 55, 22, "Fabric Notebook", "Uploaded via\nREST API", SECTION_BG, MSFT_BLUE)
pdf.draw_arrow_h(70, y3 + 11, 78, MSFT_BLUE)
pdf.draw_box(78, y3, 55, 22, "5 Discovery\nStrategies", "Runtime re-scan\ninside Spark", OK_BG, GREEN)
pdf.draw_arrow_h(133, y3 + 11, 141, GREEN)
pdf.draw_box(141, y3, 55, 22, "UAT Tables", "Synced with data\n+ schema", OK_BG, TEAL)
pdf.set_y(y3 + 30)

pdf.ln(2)
pdf.subsection("Step 1: discover_fabric_schema.py", TEAL)
pdf.numbered(1, "Calls Fabric REST API to list ALL lakehouses in the workspace.")
pdf.numbered(2, "For each lakehouse, does recursive DFS on OneLake Tables/ directory.")
pdf.numbered(3, "Discovers ALL schemas (dbo, year_2017, year_2018, etc.) dynamically.")
pdf.numbered(4, "Reads Delta transaction logs for column-level metadata.")
pdf.numbered(5, "Writes schema_discovery.json with complete inventory.")

pdf.check_space(30)
pdf.subsection("Step 2: gen_nb_payload.py", PURPLE)
pdf.numbered(1, "Reads schema_discovery.json and selects one lakehouse (by LAKEHOUSE_INDEX).")
pdf.numbered(2, "Generates PySpark code with 5 runtime discovery strategies embedded.")
pdf.numbered(3, "Strategies: CI hints -> dbo -> enumerate all -> flat Tables/ -> CI fallback.")
pdf.numbered(4, "The generated notebook re-discovers tables at runtime (doesn't blindly trust the JSON).")
pdf.numbered(5, "Includes verbose logging so every discovery step is visible in the output.")

pdf.check_space(30)
pdf.subsection("Step 3: Workflow loops all lakehouses", ORANGE)
pdf.numbered(1, "Matches each Dev lakehouse to its UAT equivalent by displayName.")
pdf.numbered(2, "Generates a separate notebook for each (e.g., 00_sync_DataCenterLakehouse).")
pdf.numbered(3, "Uploads, executes, and polls each notebook via Fabric REST API.")
pdf.numbered(4, "Final verification scan confirms tables arrived in UAT.")

# ══════════════════════════════════════════════════════════════════════════════
# 9. DEPLOYMENT PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("9. Deployment Pipeline - How Promotion Works")

pdf.body("Promotion from Dev to UAT uses two mechanisms: the Fabric Deployment Pipeline for artifact definitions, and the custom sync notebooks for table data/schemas.")

pdf.ln(2)
pdf.subsection("What the Fabric Deployment Pipeline copies:")
pdf.bullet("Notebook definitions (code)")
pdf.bullet("Semantic model definitions (TMDL)")
pdf.bullet("Dataflow Gen2 definitions (M code)")
pdf.bullet("Pipeline definitions")
pdf.bullet("Report definitions (PBIR/PBIP)")

pdf.ln(2)
pdf.subsection("What the Fabric Deployment Pipeline does NOT copy:", RED)
pdf.bullet("Lakehouse table schemas", color=RED)
pdf.bullet("Lakehouse table data", color=RED)
pdf.bullet("Column definitions", color=RED)
pdf.bullet("OneLake file contents", color=RED)

pdf.ln(2)
pdf.colored_box(
    "THIS IS THE GAP WE FILL",
    "The custom sync notebooks (generated by gen_nb_payload.py) read data\n"
    "from Dev OneLake via abfss:// paths and write it to UAT using\n"
    "incremental sync (only new/changed rows + schema evolution).\n\n"
    "Deployment Pipeline: artifact DEFINITIONS only\n"
    "Custom Notebooks:    table DATA + SCHEMAS",
    WARN_BG, ORANGE
)

pdf.check_space(40)
pdf.ln(2)
pdf.subsection("deployment-pipeline/deployment-rules.json:")
pdf.body("Maps lakehouse names across environments and specifies which artifacts get promoted as-is vs. which need parameter overrides.")

pdf.code_block(
    '{\n'
    '  "rules": [\n'
    '    {\n'
    '      "sourceItemName": "DigitalRealty_Capacity",\n'
    '      "targetItemName": "DigitalRealty_Capacity",\n'
    '      "type": "Lakehouse"\n'
    '    },\n'
    '    {\n'
    '      "sourceItemName": "DataCenterLakehouse",\n'
    '      "targetItemName": "DataCenterLakehouse",\n'
    '      "type": "Lakehouse"\n'
    '    }\n'
    '  ]\n'
    '}'
)

# ══════════════════════════════════════════════════════════════════════════════
# 10. SECURITY MODEL
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("10. Security Model - 4-Layer Protection", RED)

pdf.body("Security is implemented in 4 layers. ALL FOUR must be configured correctly -- they are independent and complementary.")

pdf.ln(4)
# Security layers diagram
y = pdf.get_y()
layers = [
    ("Layer 1: Workspace Permissions", "Role-based access per environment\nAdmin/Member/Contributor/Viewer", (255, 230, 230), RED),
    ("Layer 2: OneLake RBAC", "Region-based data access roles\nNA, EMEA, APAC, Global_Admin", (255, 240, 220), ORANGE),
    ("Layer 3: Semantic Model RLS", "DAX row-level security\nFilter by USERPRINCIPALNAME()", (255, 248, 220), GOLD),
    ("Layer 4: OLS / Hidden Tables", "Security bridge tables hidden\nfrom end users in the model", (240, 240, 250), PURPLE),
]
for i, (title, desc, bg, color) in enumerate(layers):
    ly = y + i * 28
    pdf.draw_box(25, ly, 160, 24, title, desc, bg, color)
    if i < 3:
        pdf.draw_arrow_v(105, ly + 24, ly + 28, color)

pdf.set_y(y + 4 * 28 + 4)

pdf.check_space(40)
pdf.subsection("security/onelake-roles.json:")
pdf.code_block(
    '{\n'
    '  "roles": [\n'
    '    {\n'
    '      "name": "NorthAmerica",\n'
    '      "members": ["na-team@digitalrealty.com"],\n'
    '      "permissions": {\n'
    '        "tables": ["bronze_*", "silver_*"],\n'
    '        "filter": "region = \'NA\'"\n'
    '      }\n'
    '    },\n'
    '    { "name": "EMEA", ... },\n'
    '    { "name": "APAC", ... },\n'
    '    { "name": "Global_Admin", "permissions": { "tables": ["*"] } }\n'
    '  ]\n'
    '}'
)

pdf.check_space(30)
pdf.subsection("security/rls-rules.dax:")
pdf.code_block(
    '// Row-Level Security - filters data by user identity\n'
    'DEFINE ROLE "NorthAmerica"\n'
    '  TABLE bronze_assets\n'
    '    FILTER [region] = "NA"\n'
    '\n'
    'DEFINE ROLE "EMEA"\n'
    '  TABLE bronze_assets\n'
    '    FILTER [region] = "EMEA"\n'
    '\n'
    '// Dynamic RLS using USERPRINCIPALNAME()\n'
    'FILTER [assigned_to] = USERPRINCIPALNAME()'
)

# ══════════════════════════════════════════════════════════════════════════════
# 11. SEMANTIC MODEL
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("11. Semantic Model - TMDL, DirectLake, RLS", NAVY)

pdf.body("The semantic model is defined in TMDL format (Tabular Model Definition Language) and uses DirectLake mode for optimal performance. It connects directly to Delta tables in the Lakehouse without importing data.")

pdf.ln(2)
pdf.subsection("Key Characteristics:")
pdf.bullet("TMDL format: Text-based, Git-friendly model definition")
pdf.bullet("DirectLake mode: Reads directly from OneLake Delta tables (no import copy)")
pdf.bullet("RLS roles: Defined inline in the model for region-based filtering")
pdf.bullet("Measures: Financial KPIs (assets, budgets, variance, growth)")

pdf.ln(2)
pdf.subsection("Before/After Optimization:")
pdf.body("The repository includes two TMDL files for comparison:")

pdf.colored_box(
    "digitalrealty-capacity-BEFORE.tmdl",
    "Baseline model before optimization.\n"
    "May have redundant columns, suboptimal relationships,\n"
    "or missing measures. Used for performance comparison.",
    WARN_BG, ORANGE
)
pdf.ln(2)
pdf.colored_box(
    "digitalrealty-capacity.tmdl (CURRENT)",
    "Optimized model with:\n"
    "- Pruned unused columns to reduce VertiPaq memory\n"
    "- Proper relationship cardinality\n"
    "- Efficient DAX measures\n"
    "- RLS roles configured\n"
    "- Hidden security bridge tables (OLS)",
    OK_BG, GREEN
)

pdf.check_space(30)
pdf.ln(2)
pdf.subsection("DirectLake Connection Pattern:")
pdf.code_block(
    "// TMDL partition definition (simplified)\n"
    "partition 'bronze_assets' = lakehouse\n"
    "  source\n"
    "    schemaName: dbo\n"
    "    tableName: bronze_assets\n"
    "    expressionSource: DatabaseQuery\n"
    "\n"
    "// DirectLake reads DIRECTLY from Delta tables in OneLake\n"
    "// No data copy, no import refresh needed\n"
    "// Changes to Lakehouse tables are reflected immediately"
)

# ══════════════════════════════════════════════════════════════════════════════
# 12. PERFORMANCE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("12. Performance Analysis - BPA, Memory, Compression", PURPLE)

pdf.body("Three specialized notebooks analyze different aspects of semantic model and Lakehouse performance:")

pdf.ln(2)
pdf.colored_box(
    "04_bpa_analyzer.py - Best Practice Analyzer",
    "Purpose: Scans semantic model for anti-patterns\n"
    "Checks: Unused columns, bi-directional relationships, complex DAX,\n"
    "         missing descriptions, non-optimal data types\n"
    "Output: Severity-ranked list of recommendations\n"
    "Trigger: performance-analysis.yml workflow",
    PURPLE_BG, PURPLE
)
pdf.ln(2)
pdf.colored_box(
    "05_memory_analyzer.py - VertiPaq Memory Analysis",
    "Purpose: Analyze in-memory column storage efficiency\n"
    "Checks: Column cardinality, dictionary size, data encoding,\n"
    "         memory per column, total model memory footprint\n"
    "Output: Top memory consumers + optimization recommendations\n"
    "Trigger: performance-analysis.yml workflow",
    SECTION_BG, MSFT_BLUE
)
pdf.ln(2)
pdf.colored_box(
    "06_compression_analyzer.py - Delta Compression Diagnostics",
    "Purpose: Analyze Delta table storage efficiency on disk\n"
    "Checks: Parquet file sizes, row group counts, compression ratios,\n"
    "         small file proliferation, Z-order opportunities\n"
    "Output: Storage optimization recommendations (OPTIMIZE, VACUUM)\n"
    "Trigger: performance-analysis.yml workflow",
    TEAL_BG, TEAL
)

pdf.check_space(35)
pdf.ln(2)
pdf.subsection("Performance Gate:")
pdf.body("The performance-gate.yml workflow can optionally block promotion if performance metrics fall below thresholds. This prevents deploying a bloated or inefficient model to production.")

# ══════════════════════════════════════════════════════════════════════════════
# 13. FABRIC WORKSPACE ARTIFACTS
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("13. Fabric Workspace Artifacts")

pdf.body("The fabric-workspace/ directory contains Git-exported Fabric artifacts. These are automatically synced to Git when Fabric Git integration is enabled.")

pdf.ln(2)
pdf.subsection("DataCenterLakehouse.Lakehouse/")
pdf.bullet("lakehouse.metadata.json: Lakehouse configuration (schemas enabled, properties)")
pdf.bullet("shortcuts.metadata.json: OneLake shortcut definitions (cross-lakehouse links)")
pdf.bullet("alm.settings.json: Application lifecycle management settings")
pdf.bullet(".platform: Fabric platform metadata (item type, GUID)")

pdf.ln(2)
pdf.subsection("Notebook_extra_column.Notebook/")
pdf.bullet("notebook-content.sql: SQL notebook for ad-hoc schema modifications")
pdf.bullet(".platform: Fabric platform metadata")

pdf.ln(2)
pdf.colored_box(
    "IMPORTANT: What Git captures vs. what it doesn't",
    "Git CAPTURES: Lakehouse metadata, notebook code, shortcuts, ALM settings\n"
    "Git DOES NOT CAPTURE: Table schemas, table data, Delta files\n\n"
    "This is exactly why the dynamic discovery pipeline exists --\n"
    "to bridge the gap between what Git syncs and what actually\n"
    "needs to be promoted.",
    WARN_BG, ORANGE
)

# ══════════════════════════════════════════════════════════════════════════════
# 14. MIGRATION SCRIPTS
# ══════════════════════════════════════════════════════════════════════════════
pdf.check_space(80)
pdf.ln(4)
pdf.section_title("14. Migration Scripts - Schema Versioning", TEAL)

pdf.body("The migrations/ directory contains versioned schema DDL scripts following a Flyway-like naming convention (V001, V002, etc.). Each migration is idempotent and can be re-run safely.")

pdf.ln(2)
widths = [65, 125]
pdf.table_row(["Migration File", "What It Does"], widths, header=True)
pdf.table_row(["V001__create_bronze_tables.py", "Create initial bronze_assets and bronze_budgets tables"], widths, bg=TEAL_BG)
pdf.table_row(["V002__create_silver_tables.py", "Create silver_asset_summary and silver_regional_summary"], widths)
pdf.table_row(["V003__add_sustainability_cols.py", "Add carbon_footprint, pue_rating columns to tables"], widths, bg=TEAL_BG)
pdf.table_row(["V004__remove_bloat_columns.py", "Remove deprecated/unused columns to reduce model size"], widths)

pdf.ln(2)
pdf.body("Migrations are executed in order during schema enforcement. Each migration checks if the change has already been applied before running, making them safe to re-execute.")

# ══════════════════════════════════════════════════════════════════════════════
# 15. SAMPLE DATA
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("15. Sample Data")

pdf.body("The sample-data/ directory contains CSV files used by the ingestion notebook (01_data_ingestion.py). There are both clean and dirty variants for demonstrating data quality scenarios.")

pdf.ln(2)
widths = [75, 115]
pdf.table_row(["CSV File", "Contents"], widths, header=True)
pdf.table_row(["datacenters.csv", "Clean data center records (location, capacity, region)"], widths, bg=OK_BG)
pdf.table_row(["datacenters_dirty.csv", "Intentionally dirty data (nulls, duplicates, bad types)"], widths)
pdf.table_row(["customer_deployments.csv", "Clean customer deployment records"], widths, bg=OK_BG)
pdf.table_row(["customer_deployments_dirty.csv", "Dirty variant for quality check demos"], widths)
pdf.table_row(["power_capacity.csv", "Power capacity metrics across data centers"], widths, bg=OK_BG)

pdf.ln(2)
pdf.colored_box(
    "DEMO TIP",
    "Use clean CSVs first to show the happy path (ingestion -> quality pass).\n"
    "Then swap to dirty CSVs to demonstrate quality gates catching bad data.\n"
    "The 03_data_quality_checks.py notebook will raise exceptions on dirty data.",
    SECTION_BG, MSFT_BLUE
)

# ══════════════════════════════════════════════════════════════════════════════
# 16. KEY API PATTERNS
# ══════════════════════════════════════════════════════════════════════════════
pdf.check_space(50)
pdf.ln(4)
pdf.section_title("16. Key API Patterns - Fabric REST API", ORANGE)

pdf.body("All automation uses the Fabric REST API (https://api.fabric.microsoft.com/v1). Here are the key patterns:")

pdf.ln(2)
pdf.subsection("Authentication (TWO tokens required):", RED)

pdf.colored_box(
    "CRITICAL: Two separate authentication scopes",
    "Fabric API token:  scope https://api.fabric.microsoft.com/.default\n"
    "  Used for: workspace ops, item management, notebook execution\n\n"
    "Storage API token: scope https://storage.azure.com/.default\n"
    "  Used for: OneLake DFS listing, Delta log reading\n\n"
    "If the Storage token is missing, ALL DFS calls silently return empty,\n"
    "resulting in 0 tables discovered. This was a major debugging issue.",
    ERR_BG, RED
)

pdf.check_space(60)
pdf.ln(2)
pdf.subsection("Key API Endpoints:")
pdf.code_block(
    "# List lakehouses in a workspace\n"
    "GET /v1/workspaces/{workspace_id}/lakehouses\n\n"
    "# Git sync status\n"
    "GET /v1/workspaces/{workspace_id}/git/status\n\n"
    "# Force sync from Git\n"
    "POST /v1/workspaces/{workspace_id}/git/updateFromGit\n\n"
    "# Deploy via deployment pipeline\n"
    "POST /v1/deploymentPipelines/{pipeline_id}/deploy\n\n"
    "# Upload/update item definition (notebook)\n"
    "POST /v1/workspaces/{workspace_id}/items/{item_id}/updateDefinition\n\n"
    "# Run notebook\n"
    "POST /v1/workspaces/{ws_id}/items/{nb_id}/jobs/instances?jobType=RunNotebook\n"
    "  Returns: 202 with Location header for polling\n\n"
    "# OneLake DFS (file system listing)\n"
    "GET https://onelake.dfs.fabric.microsoft.com/{ws_id}/{lh_id}\n"
    "    ?resource=filesystem&directory=Tables&recursive=true"
)

# ══════════════════════════════════════════════════════════════════════════════
# 17. END-TO-END FLOW
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("17. How Everything Connects - End-to-End Flow")

pdf.body("Here is the complete flow from a developer making a change to data appearing in UAT/Prod:")

pdf.ln(4)

pdf.numbered(1, "DEVELOPER makes a change: Modifies a notebook (schema change, new table, business logic update). Commits to a feature branch and opens a PR.", num_color=MSFT_BLUE)
pdf.ln(1)

pdf.numbered(2, "PR REVIEW + MERGE: Team reviews the change. On merge to main, the fabric-git-sync-on-merge.yml workflow triggers, calling Fabric's updateFromGit API to sync notebook definitions.", num_color=GREEN)
pdf.ln(1)

pdf.numbered(3, "SCHEMA VALIDATION TRIGGERS: The promote-with-schema-validation.yml workflow auto-triggers (or is manually dispatched). It starts the preflight job.", num_color=TEAL)
pdf.ln(1)

pdf.numbered(4, "DISCOVERY (Preflight): discover_fabric_schema.py calls Fabric API to list ALL lakehouses, then scans each one via OneLake DFS to find every schema and table. Outputs schema_discovery.json.", num_color=PURPLE)
pdf.ln(1)

pdf.numbered(5, "DEPLOYMENT PIPELINE: The workflow triggers the Fabric Deployment Pipeline to copy artifact DEFINITIONS (notebooks, semantic model, reports) from Dev stage to UAT stage.", num_color=ORANGE)
pdf.ln(1)

pdf.numbered(6, "SCHEMA ENFORCEMENT: For EACH lakehouse found in discovery, the workflow generates a sync notebook (gen_nb_payload.py), uploads it to UAT workspace via REST API, and executes it. The notebook reads data from Dev OneLake and writes to UAT with incremental sync.", num_color=RED)
pdf.ln(1)

pdf.numbered(7, "VERIFICATION: After all notebooks complete, a final scan verifies that ALL tables across ALL lakehouses exist in UAT with correct schemas.", num_color=NAVY)
pdf.ln(1)

pdf.numbered(8, "NOTIFICATION: The workflow posts results to the GitHub Actions summary -- showing exactly which tables, schemas, and lakehouses were synced, with row counts and column details for each.", num_color=MSFT_BLUE)

pdf.check_space(35)
pdf.ln(4)

pdf.colored_box(
    "THE COMPLETE FLOW",
    "Code change -> PR -> Merge -> Git Sync -> Discovery -> Deploy artifacts\n"
    "-> Generate notebooks -> Upload -> Execute -> Sync tables -> Verify\n\n"
    "Total automation: Zero manual steps after the PR is merged.\n"
    "Total visibility: Every table, schema, and row count printed in the logs.",
    OK_BG, GREEN
)

# ══════════════════════════════════════════════════════════════════════════════
# FINAL PAGE: Key Takeaways
# ══════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("Key Takeaways")

pdf.ln(2)
takeaways = [
    ("Dynamic Discovery", "Nothing hardcoded. All lakehouses, schemas, and tables found at runtime via Fabric API.", TEAL),
    ("Schema-as-Code", "Notebooks are the schema source of truth. Changes go through Git, not the Fabric UI.", PURPLE),
    ("Multi-Lakehouse", "ALL lakehouses synced automatically. Standard (dbo) and non-standard (year_2017) schemas.", MSFT_BLUE),
    ("Incremental Sync", "Only new/changed rows and schema additions are applied. Existing data preserved.", GREEN),
    ("4-Layer Security", "Workspace permissions + OneLake RBAC + Semantic RLS + OLS -- all independently configured.", RED),
    ("Full Observability", "Every step logged. Tables, schemas, columns, row counts visible in GitHub Actions output.", ORANGE),
    ("Performance Analysis", "3 notebooks analyze model efficiency: BPA, memory, compression.", NAVY),
    ("Versioned Migrations", "V001-V004 migration scripts for controlled schema evolution.", TEAL),
]

for title, desc, color in takeaways:
    pdf.check_space(20)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*color)
    pdf.cell(0, 7, title, new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*DARK_GRAY)
    pdf.set_x(10)
    pdf.multi_cell(190, 5.5, desc, new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.ln(3)

pdf.ln(8)
pdf.set_draw_color(*MSFT_BLUE)
pdf.set_line_width(1)
pdf.line(50, pdf.get_y(), 160, pdf.get_y())
pdf.ln(6)
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(*MED_GRAY)
pdf.cell(0, 7, "This document was auto-generated from the project codebase.", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.cell(0, 7, "For questions, refer to docs/schema-evolution-guide.md or the README.", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)

# ── Save ───────────────────────────────────────────────────────────────────────
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "DigitalRealty_Project_Explanation.pdf")
pdf.output(out_path)
print(f"PDF generated: {out_path}")
print(f"Pages: {pdf.page_no()}")
