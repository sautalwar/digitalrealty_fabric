"""
Generate DigitalRealty_Pipeline_Explanation.pdf
Color-coded explanation of the dynamic discovery pipeline and the line 483 bug.
"""
from fpdf import FPDF, XPos, YPos
import os, datetime

# ── Color palette ──────────────────────────────────────────────────────────────
MSFT_BLUE   = (0, 120, 212)
DARK_GRAY   = (50, 50, 50)
MED_GRAY    = (100, 100, 100)
LIGHT_BG    = (245, 245, 250)
WHITE       = (255, 255, 255)
GREEN       = (16, 124, 16)
ORANGE      = (202, 80, 16)
RED         = (196, 43, 28)
PURPLE      = (107, 36, 178)
TEAL        = (0, 128, 128)
CODE_BG     = (240, 240, 245)
SECTION_BG  = (230, 240, 255)
WARN_BG     = (255, 245, 230)
ERR_BG      = (255, 235, 235)
OK_BG       = (235, 250, 235)

class PipelinePDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*MED_GRAY)
        self.cell(0, 8, "Digital Realty - Dynamic Discovery Pipeline Explanation",
                  new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.set_draw_color(*MSFT_BLUE)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*MED_GRAY)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}  |  CONFIDENTIAL",
                  align="C")

    def section_title(self, text, color=MSFT_BLUE):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*color)
        self.cell(0, 10, text, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.set_draw_color(*color)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def subsection(self, text, color=DARK_GRAY):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*color)
        self.cell(0, 8, text, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.ln(2)

    def body(self, text, bold=False):
        self.set_font("Helvetica", "B" if bold else "", 10)
        self.set_text_color(*DARK_GRAY)
        self.set_x(10)
        self.multi_cell(190, 5.5, text, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.ln(2)

    def bullet(self, text, indent=15, color=DARK_GRAY):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*color)
        x = self.get_x()
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
        self.set_font("Courier", "", 9)
        self.set_text_color(*DARK_GRAY)
        lines = code.strip().split("\n")
        block_h = len(lines) * 5 + 6
        if self.get_y() + block_h > 270:
            self.add_page()
        y_start = self.get_y()
        self.rect(12, y_start, 186, block_h, "F")
        self.ln(3)
        for line in lines:
            self.set_x(15)
            self.cell(180, 5, line, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.ln(4)

    def colored_box(self, title, text, bg, title_color=DARK_GRAY):
        self.set_fill_color(*bg)
        lines = text.strip().split("\n")
        block_h = len(lines) * 5.5 + 16
        if self.get_y() + block_h > 270:
            self.add_page()
        y_start = self.get_y()
        self.rect(12, y_start, 186, block_h, "F")
        self.set_xy(15, y_start + 3)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*title_color)
        self.cell(180, 6, title, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*DARK_GRAY)
        for line in lines:
            self.set_x(15)
            self.multi_cell(178, 5.5, line, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.set_y(y_start + block_h + 3)

    def tag(self, label, color):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*WHITE)
        self.set_fill_color(*color)
        w = self.get_string_width(label) + 6
        self.cell(w, 6, label, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(3, 6, "", new_x=XPos.RIGHT, new_y=YPos.TOP)

    def check_space(self, h=30):
        if self.get_y() + h > 270:
            self.add_page()


# ── Build PDF ──────────────────────────────────────────────────────────────────
pdf = PipelinePDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)

# ── Title page ─────────────────────────────────────────────────────────────────
pdf.add_page()
pdf.ln(40)
pdf.set_font("Helvetica", "B", 28)
pdf.set_text_color(*MSFT_BLUE)
pdf.cell(0, 14, "Dynamic Discovery Pipeline", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.set_font("Helvetica", "", 16)
pdf.set_text_color(*MED_GRAY)
pdf.cell(0, 10, "How Tables & Schemas Are Found On-the-Fly", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.ln(8)
pdf.set_draw_color(*MSFT_BLUE)
pdf.set_line_width(1)
pdf.line(60, pdf.get_y(), 150, pdf.get_y())
pdf.ln(12)
pdf.set_font("Helvetica", "", 12)
pdf.set_text_color(*DARK_GRAY)
pdf.cell(0, 8, "Digital Realty Trust - Microsoft Fabric CI/CD", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.cell(0, 8, f"Generated: {datetime.datetime.now().strftime('%B %d, %Y')}", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.ln(30)

pdf.set_font("Helvetica", "B", 11)
pdf.set_text_color(*GREEN)
pdf.cell(0, 8, "KEY TAKEAWAY: Nothing is hardcoded.", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(*MED_GRAY)
pdf.cell(0, 7, "The entire pipeline discovers lakehouses, schemas, and tables dynamically", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.cell(0, 7, "using Fabric REST API and OneLake DFS at runtime.", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)

# ── Page 2: Pipeline Overview ──────────────────────────────────────────────────
pdf.add_page()
pdf.section_title("Pipeline Overview: 3 Dynamic Scripts")

pdf.body("The promotion pipeline has 3 scripts that chain together. Each discovers data dynamically from the Fabric workspace -- there are zero hardcoded table names, schema names, or lakehouse IDs in the logic.")

pdf.ln(2)
pdf.colored_box(
    "Pipeline Flow (GitHub Actions Workflow)",
    "Step 1: discover_fabric_schema.py  -->  schema_discovery.json  (live API scan)\n"
    "Step 2: gen_nb_payload.py          -->  nb_payload.json        (notebook generator)\n"
    "Step 3: Fabric Notebook Execution  -->  Tables synced in UAT   (runtime re-discovery)",
    SECTION_BG, MSFT_BLUE
)

pdf.ln(2)
pdf.body("Each step feeds into the next, but every step also validates independently. Even if step 1 missed something, steps 2 and 3 have fallback discovery strategies.")

# ── Page 3: Script 1 ──────────────────────────────────────────────────────────
pdf.add_page()
pdf.section_title("Step 1: discover_fabric_schema.py", TEAL)
pdf.subsection("Purpose: Scan the Dev workspace and find EVERYTHING", TEAL)

pdf.body("This script runs first in the GitHub Actions workflow. It calls real Fabric APIs to discover all lakehouses and their contents dynamically.")

pdf.ln(2)
pdf.subsection("What it does (in order):")

pdf.numbered(1, "Calls GET /v1/workspaces/{id}/lakehouses to list ALL lakehouses in the Dev workspace. This is a Fabric REST API call -- it returns whatever lakehouses exist right now, not a hardcoded list.")
pdf.numbered(2, "For EACH lakehouse found, does a recursive DFS scan on OneLake (the Tables/ directory) to find every schema folder -- dbo, year_2017, year_2018, year_2019, year_2020, year_2021, year_2022, or any other schema that exists.")
pdf.numbered(3, "For each table found under each schema, reads the Delta transaction log (_delta_log/00000...json) to extract the actual column names, data types, and nullability.")
pdf.numbered(4, "Writes everything to schema_discovery.json -- this file is the output, and it contains zero hardcoded values. Everything came from live API calls.")

pdf.check_space(40)
pdf.ln(2)
pdf.subsection("Output format (schema_discovery.json):")
pdf.code_block(
    '{\n'
    '  "workspace_id": "ffb373f3-...",\n'
    '  "total_table_count": 11,\n'
    '  "lakehouses": [\n'
    '    {\n'
    '      "lakehouse_id": "2ba784e1-...",\n'
    '      "lakehouse_name": "DigitalRealty_Capacity",\n'
    '      "schemas_enabled": true,\n'
    '      "table_count": 4,\n'
    '      "schemas": {\n'
    '        "dbo": { "tables": { "bronze_assets": {...}, ... } }\n'
    '      }\n'
    '    },\n'
    '    {\n'
    '      "lakehouse_id": "11fedcf0-...",\n'
    '      "lakehouse_name": "DataCenterLakehouse",\n'
    '      "schemas_enabled": true,\n'
    '      "table_count": 7,\n'
    '      "schemas": {\n'
    '        "year_2017": { "tables": {...} },\n'
    '        "year_2018": { "tables": {...} },\n'
    '        ... (all discovered dynamically)\n'
    '      }\n'
    '    }\n'
    '  ]\n'
    '}'
)

pdf.colored_box(
    "KEY POINT",
    "If you add a new lakehouse or new tables tomorrow, this script\n"
    "will automatically find them on the next workflow run.\n"
    "No code changes needed.",
    OK_BG, GREEN
)

# ── Page: Script 2 ─────────────────────────────────────────────────────────────
pdf.add_page()
pdf.section_title("Step 2: gen_nb_payload.py", PURPLE)
pdf.subsection("Purpose: Generate a Fabric notebook from the discovery JSON", PURPLE)

pdf.body("This script reads schema_discovery.json and builds a self-contained PySpark notebook. But critically, the generated notebook ALSO contains its own runtime discovery code.")

pdf.ln(2)
pdf.subsection("Two layers of discovery:")

pdf.check_space(25)
pdf.colored_box(
    "Layer A: CI Discovery (from schema_discovery.json)",
    "Reads the JSON from step 1 and embeds the table list as CI_SCHEMA_TABLES.\n"
    "This is used as a HINT -- not the final truth.",
    SECTION_BG, MSFT_BLUE
)
pdf.ln(2)
pdf.colored_box(
    "Layer B: Runtime Discovery (5 strategies inside the notebook)",
    "The generated notebook re-discovers tables at runtime inside Fabric Spark.\n"
    "Even if the JSON was stale, the notebook finds current tables.\n"
    "CI_SCHEMA_TABLES is only used as a last-resort fallback (Strategy 5).",
    SECTION_BG, PURPLE
)

pdf.ln(4)
pdf.subsection("The 5 Runtime Discovery Strategies:")

pdf.numbered(1, "CI-known schemas: Try listing tables under each schema that CI found (e.g., Tables/dbo/, Tables/year_2017/). Uses mssparkutils.fs.ls() which runs inside Fabric Spark.", num_color=GREEN)
pdf.numbered(2, "dbo schema: If strategy 1 didn't find a 'dbo' schema, explicitly try Tables/dbo/ as it's the most common schema name.", num_color=MSFT_BLUE)
pdf.numbered(3, "Enumerate ALL schema folders: List everything under Tables/ and try each subdirectory as a potential schema. This catches schemas that CI might have missed -- completely dynamic.", num_color=TEAL)
pdf.numbered(4, "Direct Tables/: For lakehouses without schema prefixes, try listing tables directly under Tables/ (flat structure).", num_color=ORANGE)
pdf.numbered(5, "CI fallback: Only if strategies 1-4 all returned nothing, fall back to the CI_SCHEMA_TABLES list. This is the safety net.", num_color=RED)

pdf.check_space(30)
pdf.ln(2)
pdf.colored_box(
    "WHY 5 STRATEGIES?",
    "Fabric lakehouses have different internal structures:\n"
    "- Some have schemas (dbo/, year_2017/) under Tables/\n"
    "- Some have tables directly under Tables/ (no schema prefix)\n"
    "- Some have non-standard schemas that only appear with recursive listing\n"
    "The 5 strategies ensure we find tables regardless of structure.",
    WARN_BG, ORANGE
)

# ── Page: Script 3 (workflow) ─────────────────────────────────────────────────
pdf.add_page()
pdf.section_title("Step 3: Workflow Loops All Lakehouses", ORANGE)
pdf.subsection("Purpose: Run the notebook for EACH lakehouse", ORANGE)

pdf.body("The GitHub Actions workflow (promote-with-schema-validation.yml) orchestrates everything:")

pdf.numbered(1, "Runs discover_fabric_schema.py to get the JSON with all lakehouses and tables.")
pdf.numbered(2, "Reads the JSON and counts how many lakehouses were found.")
pdf.numbered(3, "For EACH lakehouse: matches it by displayName to the UAT workspace equivalent, generates a unique notebook (e.g., 00_sync_DataCenterLakehouse), uploads it to Fabric via REST API, executes it, and polls until completion.")
pdf.numbered(4, "After all notebooks complete, does a final verification scan across ALL UAT lakehouses to confirm tables arrived.")

pdf.ln(4)
pdf.subsection("Lakehouse matching (Dev to UAT):")
pdf.body("The workflow matches lakehouses by displayName. If Dev has 'DataCenterLakehouse' and UAT also has 'DataCenterLakehouse', they're paired. This means you must use the same lakehouse names across workspaces.")

pdf.check_space(35)
pdf.ln(2)
pdf.code_block(
    "# Workflow pseudo-code (simplified)\n"
    "discovery = run(discover_fabric_schema.py)  # Step 1\n"
    "\n"
    "for i, lakehouse in enumerate(discovery['lakehouses']):\n"
    "    dev_name = lakehouse['lakehouse_name']\n"
    "    uat_id   = find_uat_lakehouse_by_name(dev_name)\n"
    "    \n"
    "    notebook = gen_nb_payload(            # Step 2\n"
    "        schema_file    = discovery.json,\n"
    "        lakehouse_index = i,              # which LH from JSON\n"
    "        source_ids      = dev_ids,\n"
    "        target_ids      = uat_ids\n"
    "    )\n"
    "    \n"
    "    upload_and_run(notebook)              # Step 3\n"
    "    poll_until_done()\n"
    "    verify_tables(uat_id)                 # Step 4"
)

# ── Page: The Bug Explanation ──────────────────────────────────────────────────
pdf.add_page()
pdf.section_title("The Line 483 Bug: What Happened", RED)

pdf.subsection("Before the refactoring (single-lakehouse era):")
pdf.body("The script had a simple flat list of table names:")

pdf.code_block(
    "TABLES = ['bronze_assets', 'bronze_budgets', ...]  # flat list\n"
    "# ... (all logic used TABLES)\n"
    "\n"
    "# At the end of the file (line 483):\n"
    'print(f"Tables: {len(TABLES)}")\n'
    "for t in TABLES:\n"
    '    print(f"  {t}")'
)

pdf.subsection("During the multi-lakehouse refactoring:")
pdf.body("I changed the data structure from a flat list to a dictionary so we could track which tables belong to which schema:")

pdf.code_block(
    "# OLD: flat list\n"
    "TABLES = ['bronze_assets', 'bronze_budgets', ...]\n"
    "\n"
    "# NEW: dict mapping schema -> table list\n"
    'SCHEMA_TABLES = {\n'
    '    "dbo":       ["bronze_assets", "bronze_budgets", ...],\n'
    '    "year_2017": ["datacenter_metrics"],\n'
    '    "year_2018": ["datacenter_metrics"],\n'
    '    ...\n'
    '}'
)

pdf.check_space(40)
pdf.subsection("The mistake:")
pdf.colored_box(
    "WHAT WENT WRONG",
    "I updated ALL the logic throughout the file to use SCHEMA_TABLES,\n"
    "but I MISSED the 3 diagnostic print lines at the very end (lines 483-485).\n"
    "\n"
    "These lines still referenced the OLD variable name 'TABLES' which\n"
    "no longer existed in the multi-lakehouse code path.",
    ERR_BG, RED
)

pdf.ln(3)
pdf.subsection("Why it only crashed on multi-lakehouse runs:")

pdf.body("The script has two code paths for loading the discovery JSON:")

pdf.check_space(30)
pdf.code_block(
    'if "lakehouses" in disc:     # <-- MULTI-LAKEHOUSE path\n'
    "    # Only creates SCHEMA_TABLES (dict)\n"
    "    # TABLES variable is NEVER created\n"
    "    SCHEMA_TABLES = {'dbo': [...], 'year_2017': [...]}\n"
    "\n"
    "else:                         # <-- LEGACY single-lakehouse path\n"
    "    # Creates TABLES first, then converts to SCHEMA_TABLES\n"
    "    TABLES = ['table1', 'table2', ...]\n"
    "    SCHEMA_TABLES = {'dbo': TABLES}"
)

pdf.body("In the legacy path, TABLES existed (line 66), so line 483 worked fine. In the multi-lakehouse path, only SCHEMA_TABLES was created (lines 48-52), so when Python reached line 483 and tried len(TABLES), the variable didn't exist.")

pdf.check_space(35)
pdf.ln(2)
pdf.colored_box(
    "THE FIX (commit 023b9be)",
    "Replaced the stale references with SCHEMA_TABLES:\n"
    "\n"
    "BEFORE (broken):\n"
    '  print(f"Tables: {len(TABLES)}")        # TABLES doesn\'t exist!\n'
    "  for t in TABLES:                        # NameError!\n"
    '      print(f"  {t}")\n'
    "\n"
    "AFTER (fixed):\n"
    "  total = sum(len(v) for v in SCHEMA_TABLES.values())\n"
    '  print(f"Tables: {total} across {len(SCHEMA_TABLES)} schema(s)")\n'
    "  for schema, tbls in sorted(SCHEMA_TABLES.items()):\n"
    "      for t in tbls:\n"
    '          print(f"  {schema}.{t}")',
    OK_BG, GREEN
)

# ── Page: Visual Flow ──────────────────────────────────────────────────────────
pdf.add_page()
pdf.section_title("Visual Summary: Data Flow", MSFT_BLUE)

pdf.ln(4)

# Draw flow diagram using boxes and arrows
def draw_box(pdf, x, y, w, h, title, subtitle, bg, title_color):
    pdf.set_fill_color(*bg)
    pdf.rect(x, y, w, h, "F")
    pdf.set_draw_color(*title_color)
    pdf.set_line_width(0.8)
    pdf.rect(x, y, w, h, "D")
    pdf.set_xy(x + 2, y + 3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*title_color)
    pdf.cell(w - 4, 5, title, align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.set_xy(x + 2, y + 10)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*DARK_GRAY)
    pdf.multi_cell(w - 4, 4, subtitle, align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)

def draw_arrow(pdf, x1, y1, x2, y2, color=MED_GRAY):
    pdf.set_draw_color(*color)
    pdf.set_line_width(0.6)
    pdf.line(x1, y1, x2, y2)
    # arrowhead
    pdf.set_fill_color(*color)
    pdf.set_xy(x2 - 2, y2 - 1)
    # simple triangle
    pdf.polygon([(x2, y2), (x2 - 3, y2 - 2), (x2 - 3, y2 + 2)], style="F")

y_base = pdf.get_y()

# Box 1: Fabric APIs
draw_box(pdf, 15, y_base, 55, 25,
         "Fabric REST API", "GET /lakehouses\nOneLake DFS recursive", SECTION_BG, TEAL)

# Arrow 1->2
draw_arrow(pdf, 70, y_base + 12, 80, y_base + 12, TEAL)

# Box 2: discover script
draw_box(pdf, 80, y_base, 55, 25,
         "discover_fabric_", "schema.py\n(Step 1)", OK_BG, GREEN)

# Arrow 2->3
draw_arrow(pdf, 135, y_base + 12, 145, y_base + 12, GREEN)

# Box 3: JSON output
draw_box(pdf, 145, y_base, 50, 25,
         "schema_discovery", ".json\n(all LHs + tables)", WARN_BG, ORANGE)

pdf.set_y(y_base + 35)

# Row 2
y2 = pdf.get_y()
draw_box(pdf, 15, y2, 55, 25,
         "schema_discovery", ".json (input)", WARN_BG, ORANGE)
draw_arrow(pdf, 70, y2 + 12, 80, y2 + 12, ORANGE)
draw_box(pdf, 80, y2, 55, 25,
         "gen_nb_payload.py", "(Step 2)\nPer-lakehouse loop", OK_BG, PURPLE)
draw_arrow(pdf, 135, y2 + 12, 145, y2 + 12, PURPLE)
draw_box(pdf, 145, y2, 50, 25,
         "nb_payload.json", "Fabric Notebook\n(self-contained)", SECTION_BG, MSFT_BLUE)

pdf.set_y(y2 + 35)

# Row 3
y3 = pdf.get_y()
draw_box(pdf, 15, y3, 55, 25,
         "Fabric Notebook", "Uploaded via REST API", SECTION_BG, MSFT_BLUE)
draw_arrow(pdf, 70, y3 + 12, 80, y3 + 12, MSFT_BLUE)
draw_box(pdf, 80, y3, 55, 25,
         "5 Discovery", "Strategies (runtime)\nRe-discovers tables", OK_BG, GREEN)
draw_arrow(pdf, 135, y3 + 12, 145, y3 + 12, GREEN)
draw_box(pdf, 145, y3, 50, 25,
         "UAT Tables", "Synced with data\n+ schema", OK_BG, TEAL)

pdf.set_y(y3 + 40)

pdf.colored_box(
    "ZERO HARDCODING GUARANTEE",
    "1. Lakehouse names: discovered via Fabric REST API (not in code)\n"
    "2. Schema names: discovered via OneLake DFS recursive listing (not in code)\n"
    "3. Table names: discovered via OneLake DFS + Delta log reading (not in code)\n"
    "4. Column definitions: read from Delta transaction logs (not in code)\n"
    "5. Lakehouse IDs: resolved dynamically by matching displayName across workspaces\n"
    "\n"
    "If you add new lakehouses, new schemas, or new tables in Dev,\n"
    "the next workflow run will automatically discover and promote them to UAT.",
    OK_BG, GREEN
)

# ── Page: Timeline of what happened ───────────────────────────────────────────
pdf.add_page()
pdf.section_title("Timeline: What the Workflow Run Showed", MSFT_BLUE)

pdf.subsection("What was WORKING (from the screenshots):")

pdf.bullet("Discovery found 2 lakehouses (DigitalRealty_Capacity + DataCenterLakehouse)", color=GREEN)
pdf.bullet("DataCenterLakehouse correctly identified with 7 tables across 6 schemas (year_2017 through year_2022)", color=GREEN)
pdf.bullet("Source/target lakehouse IDs resolved correctly via displayName matching", color=GREEN)
pdf.bullet("Notebook name generated correctly: 00_sync_DataCenterLakehouse", color=GREEN)
pdf.bullet("All multi-lakehouse logic worked as designed", color=GREEN)

pdf.ln(2)
pdf.subsection("Where it CRASHED:")

pdf.bullet("Line 483 of gen_nb_payload.py: print(f\"Tables: {len(TABLES)}\")", color=RED)
pdf.bullet("The variable TABLES did not exist -- it should have been SCHEMA_TABLES", color=RED)
pdf.bullet("This was a diagnostic print AFTER the notebook payload was already built", color=RED)
pdf.bullet("The crash prevented the workflow from proceeding to upload + execute the notebook", color=RED)

pdf.ln(2)
pdf.subsection("The irony:")
pdf.colored_box(
    "THE NOTEBOOK WAS ALREADY GENERATED CORRECTLY",
    "The crash happened at line 483 -- AFTER line 480 wrote the payload JSON.\n"
    "The notebook was already built with all the correct multi-lakehouse logic.\n"
    "The bug was in a diagnostic print statement that ran AFTER the real work was done.\n"
    "3 lines of leftover code from the old variable name caused the failure.",
    WARN_BG, ORANGE
)

pdf.ln(4)
pdf.subsection("Current status:")
pdf.colored_box(
    "FIX DEPLOYED - commit 023b9be",
    "The stale TABLES references have been replaced with SCHEMA_TABLES.\n"
    "The fix is pushed to main and should trigger a new workflow run.\n"
    "All 9 commits from this session are in GitHub.\n"
    "\n"
    "Expected result on next run:\n"
    "  - DigitalRealty_Capacity: 4 tables synced to UAT (already proven)\n"
    "  - DataCenterLakehouse: 7 tables across 6 schemas synced to UAT (first time!)",
    OK_BG, GREEN
)

# ── Save ───────────────────────────────────────────────────────────────────────
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "DigitalRealty_Pipeline_Explanation.pdf")
pdf.output(out_path)
print(f"PDF generated: {out_path}")
print(f"Pages: {pdf.page_no()}")
