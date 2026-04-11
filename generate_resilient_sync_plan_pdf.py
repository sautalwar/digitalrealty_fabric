"""
Generate DigitalRealty_Resilient_Sync_Plan.pdf
Comprehensive plan for bulletproof lakehouse sync: error capture,
non-standard schemas, large table handling.
"""
from fpdf import FPDF, XPos, YPos
import os, datetime

MSFT_BLUE  = (0, 120, 212)
DARK_GRAY  = (50, 50, 50)
MED_GRAY   = (100, 100, 100)
WHITE      = (255, 255, 255)
GREEN      = (16, 124, 16)
ORANGE     = (202, 80, 16)
RED        = (196, 43, 28)
PURPLE     = (107, 36, 178)
TEAL       = (0, 128, 128)
CODE_BG    = (240, 240, 245)
SECTION_BG = (230, 240, 255)
WARN_BG    = (255, 245, 230)
ERR_BG     = (255, 235, 235)
OK_BG      = (235, 250, 235)

class PlanPDF(FPDF):
    def header(self):
        if self.page_no() == 1: return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*MED_GRAY)
        self.cell(0, 8, "Digital Realty - Resilient Sync Plan", new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.set_draw_color(*MSFT_BLUE); self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y()); self.ln(4)
    def footer(self):
        self.set_y(-15); self.set_font("Helvetica", "I", 8); self.set_text_color(*MED_GRAY)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}  |  CONFIDENTIAL", align="C")
    def section_title(self, text, color=MSFT_BLUE):
        self.set_font("Helvetica", "B", 14); self.set_text_color(*color)
        self.cell(0, 10, text, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.set_draw_color(*color); self.set_line_width(0.8)
        self.line(10, self.get_y(), 200, self.get_y()); self.ln(4)
    def subsection(self, text, color=DARK_GRAY):
        self.set_font("Helvetica", "B", 11); self.set_text_color(*color)
        self.cell(0, 7, text, new_x=XPos.LEFT, new_y=YPos.NEXT); self.ln(2)
    def body(self, text, bold=False):
        self.set_font("Helvetica", "B" if bold else "", 10); self.set_text_color(*DARK_GRAY)
        self.set_x(10); self.multi_cell(190, 5.5, text, new_x=XPos.LEFT, new_y=YPos.NEXT); self.ln(2)
    def bullet(self, text, color=DARK_GRAY):
        self.set_font("Helvetica", "", 10); self.set_text_color(*color)
        self.set_x(15); self.cell(5, 5.5, chr(149), new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.multi_cell(170, 5.5, text, new_x=XPos.LEFT, new_y=YPos.NEXT); self.ln(1)
    def numbered(self, num, text, num_color=MSFT_BLUE):
        self.set_x(15); self.set_font("Helvetica", "B", 10); self.set_text_color(*num_color)
        self.cell(8, 5.5, f"{num}.", new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.set_font("Helvetica", "", 10); self.set_text_color(*DARK_GRAY)
        self.multi_cell(167, 5.5, text, new_x=XPos.LEFT, new_y=YPos.NEXT); self.ln(1)
    def code_block(self, code):
        self.set_fill_color(*CODE_BG); self.set_font("Courier", "", 8)
        self.set_text_color(*DARK_GRAY); lines = code.strip().split("\n")
        h = len(lines) * 4.2 + 6
        if self.get_y() + h > 270: self.add_page()
        self.rect(12, self.get_y(), 186, h, "F"); self.ln(3)
        for l in lines:
            self.set_x(15); self.cell(180, 4.2, l, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.ln(4)
    def colored_box(self, title, text, bg, title_color=DARK_GRAY):
        self.set_fill_color(*bg); lines = text.strip().split("\n")
        h = len(lines) * 5 + 16
        if self.get_y() + h > 270: self.add_page()
        y0 = self.get_y(); self.rect(12, y0, 186, h, "F")
        self.set_xy(15, y0 + 3); self.set_font("Helvetica", "B", 10); self.set_text_color(*title_color)
        self.cell(180, 6, title, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 9); self.set_text_color(*DARK_GRAY)
        for l in lines:
            self.set_x(15); self.multi_cell(178, 5, l, new_x=XPos.LEFT, new_y=YPos.NEXT)
        self.set_y(y0 + h + 3)
    def check_space(self, h=30):
        if self.get_y() + h > 270: self.add_page()

pdf = PlanPDF(); pdf.alias_nb_pages(); pdf.set_auto_page_break(auto=True, margin=20)

# ── TITLE ──────────────────────────────────────────────────────────────────────
pdf.add_page(); pdf.ln(35)
pdf.set_font("Helvetica", "B", 28); pdf.set_text_color(*MSFT_BLUE)
pdf.cell(0, 14, "Resilient Lakehouse Sync", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.set_font("Helvetica", "", 16); pdf.set_text_color(*MED_GRAY)
pdf.cell(0, 10, "Plan to Eliminate Recurring Failures", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.ln(6); pdf.set_draw_color(*RED); pdf.set_line_width(1.2)
pdf.line(50, pdf.get_y(), 160, pdf.get_y()); pdf.ln(10)
pdf.set_font("Helvetica", "", 11); pdf.set_text_color(*DARK_GRAY)
pdf.cell(0, 7, "Error Capture + Non-Standard Schemas + Large Table Handling", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.cell(0, 7, f"Generated: {datetime.datetime.now().strftime('%B %d, %Y')}", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.ln(20)
pdf.set_font("Helvetica", "B", 11); pdf.set_text_color(*RED)
pdf.cell(0, 8, "GOAL: This is the LAST time we fix sync failures.", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.set_font("Helvetica", "", 10); pdf.set_text_color(*MED_GRAY)
pdf.cell(0, 7, "Every known failure mode is addressed with defense-in-depth.", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)

# ── ROOT CAUSE ANALYSIS ───────────────────────────────────────────────────────
pdf.add_page()
pdf.section_title("1. Root Cause Analysis - Why Failures Keep Repeating", RED)
pdf.body("After 30+ workflow runs and 10 commits, there are 5 distinct failure categories. Each has been addressed piecemeal but never comprehensively. This plan addresses ALL of them in one implementation.")

pdf.ln(2)
pdf.colored_box(
    "FAILURE #1: Zero Error Visibility",
    "Problem: run_and_poll() only shows 'Poll 3/60: Failed' with no details.\n"
    "We cannot see WHY the Fabric notebook failed -- no error message, no traceback,\n"
    "no Spark output. This forces blind debugging.\n\n"
    "Impact: Every failure requires guessing the cause, making a fix, waiting 15 min\n"
    "for the workflow, and checking again. Wastes hours per iteration.",
    ERR_BG, RED)
pdf.ln(2)
pdf.colored_box(
    "FAILURE #2: Non-Standard Schemas Not Created",
    "Problem: Dev has schemas like year_2017-year_2022. UAT only has 'dbo'.\n"
    "The notebook tries saveAsTable('year_2017.green_tripdata_2017') but the\n"
    "year_2017 schema doesn't exist in UAT. Spark throws an error.\n\n"
    "Root cause: Fabric Deployment Pipeline copies artifact definitions but\n"
    "does NOT create schemas. Schema creation must be explicit.",
    WARN_BG, ORANGE)
pdf.ln(2)
pdf.colored_box(
    "FAILURE #3: Large Tables Cause Timeout/OOM",
    "Problem: NYC green taxi data tables are multi-GB (3-5GB each).\n"
    "Current code does: (a) src_df.count() - full table scan, (b) subtract() -\n"
    "another full scan, (c) _print_sample() calls .collect() on the full DataFrame.\n"
    "Any of these can trigger OutOfMemory or exceed the Spark session timeout.\n\n"
    "Root cause: The sync was designed for small bronze_* tables (~1000 rows).\n"
    "It was never adapted for multi-GB data.",
    WARN_BG, ORANGE)
pdf.ln(2)
pdf.colored_box(
    "FAILURE #4: Clone Tables Pollute Discovery",
    "Problem: Fabric creates clone tables (e.g., green_tripdata_2017_clone_20260408).\n"
    "These appear in DFS listing and get included in the sync. Clones may reference\n"
    "internal metadata that fails when copied to another workspace.\n\n"
    "Root cause: No filtering of Fabric system-generated clone tables.",
    SECTION_BG, MSFT_BLUE)
pdf.ln(2)
pdf.colored_box(
    "FAILURE #5: Fatal Errors Kill Notebook Silently",
    "Problem: If ANY unhandled exception occurs early in the notebook (during\n"
    "discovery, schema creation, or Spark initialization), the entire notebook\n"
    "dies with zero output. The job status just shows 'Failed' with no diagnostics.\n\n"
    "Root cause: No top-level error handling wrapping the entire notebook code.",
    ERR_BG, RED)

# ── THE PLAN ──────────────────────────────────────────────────────────────────
pdf.add_page()
pdf.section_title("2. The Plan - 5 Fixes, One Implementation", GREEN)
pdf.body("Each fix addresses one failure category. Together they make the sync bulletproof for any lakehouse size, any schema type, and any failure scenario.")

pdf.ln(2)
pdf.subsection("FIX A: Comprehensive Error Capture (run_and_poll)", RED)
pdf.body("Changes to: promote-with-schema-validation.yml")
pdf.numbered(1, "Capture the FULL job status JSON response on failure, not just the status string.")
pdf.numbered(2, "Extract .failureReason, .error.errorCode, .error.message from the Fabric API response and print them in the GitHub Actions log.")
pdf.numbered(3, "After the notebook completes (success or failure), attempt to read a status marker file from OneLake that the notebook writes. This gives us the notebook's OWN diagnostic output even when Fabric job API gives minimal info.")
pdf.numbered(4, "On failure, also try the Fabric Spark session API to get application logs (GET /v1/workspaces/{ws}/sparks/{app}/sessions/{session}).")

pdf.check_space(50)
pdf.colored_box(
    "STATUS MARKER PATTERN",
    "The notebook writes a JSON status file to OneLake at the very end:\n"
    "  Tables/___sync_status.json\n\n"
    "Content: {status, tables_synced, tables_failed, errors, timestamp}\n\n"
    "On failure, the try/except writes what it can before re-raising.\n"
    "The workflow reads this file via OneLake DFS after polling finishes,\n"
    "giving us the notebook's perspective on what happened.",
    SECTION_BG, MSFT_BLUE)

pdf.check_space(50)
pdf.ln(2)
pdf.subsection("FIX B: Non-Standard Schema Support (gen_nb_payload.py)", ORANGE)
pdf.body("Changes to: gen_nb_payload.py (inner notebook code)")
pdf.numbered(1, "Before syncing ANY tables, enumerate ALL unique schema names from the discovered table list.")
pdf.numbered(2, "For each non-default schema (anything other than 'dbo' and empty string), run CREATE SCHEMA IF NOT EXISTS via spark.sql().")
pdf.numbered(3, "Verify each schema was created successfully. If creation fails, log the error but continue -- some schemas may already exist.")
pdf.numbered(4, "After schema creation, verify by listing schemas: spark.sql('SHOW SCHEMAS').collect() and print the full list.")

pdf.code_block(
    "# Pre-create all non-default schemas\n"
    "schemas_needed = [s for s in SCHEMA_TABLES.keys() if s and s != 'dbo']\n"
    "print(f'Creating {len(schemas_needed)} non-default schema(s)')\n"
    "for schema in schemas_needed:\n"
    "    try:\n"
    "        spark.sql(f'CREATE SCHEMA IF NOT EXISTS `{schema}`')\n"
    "        print(f'  Schema `{schema}`: OK')\n"
    "    except Exception as e:\n"
    "        print(f'  Schema `{schema}`: FAILED - {e}')\n\n"
    "# Verify schemas exist\n"
    "existing = [r[0] for r in spark.sql('SHOW SCHEMAS').collect()]\n"
    "print(f'Schemas in lakehouse: {existing}')")

pdf.check_space(60)
pdf.ln(2)
pdf.subsection("FIX C: Large Table Handling (gen_nb_payload.py)", PURPLE)
pdf.body("Changes to: gen_nb_payload.py (inner notebook code)")
pdf.body("This is the most impactful change. Current approach cannot handle multi-GB tables. The new approach uses a tiered strategy based on source table size.")

pdf.numbered(1, "SIZE DETECTION: Instead of src_df.count() (full scan), read the Delta log metadata to estimate row count and file size. This is O(1) -- reads a tiny JSON file, not the entire table.", num_color=PURPLE)
pdf.numbered(2, "TIERED SYNC: Based on estimated size, choose the appropriate sync strategy: (a) Small tables (<100MB): full overwrite as today. (b) Medium tables (100MB-1GB): overwrite but skip sample printing and subtract. (c) Large tables (>1GB): partitioned write using coalesce + overwrite. Skip incremental diff entirely -- overwrite is safer and often faster for large data.", num_color=PURPLE)
pdf.numbered(3, "SKIP EXPENSIVE OPERATIONS: For tables >100MB, skip _print_sample() (no .collect()). For tables >1GB, skip subtract() (no cross-join). For ALL tables, skip _print_schema() if >50 columns.", num_color=PURPLE)
pdf.numbered(4, "SPARK CONFIG: Set spark.sql.adaptive.enabled=true, spark.sql.shuffle.partitions=auto for optimal large table handling. Set spark.sql.files.maxRecordsPerFile to prevent OOM on write.", num_color=PURPLE)
pdf.numbered(5, "PER-TABLE TIMEOUT: Track elapsed time per table. If >10 minutes on a single table, log a warning but continue. If >20 minutes, skip the table and mark as 'timeout'.", num_color=PURPLE)

pdf.add_page()
pdf.code_block(
    "# Size detection via Delta log (O(1), no data scan)\n"
    "def _estimate_table_size(path):\n"
    "    '''Read Delta log to estimate size without scanning data.'''\n"
    "    try:\n"
    "        detail = spark.sql(f\"DESCRIBE DETAIL delta.`{path}`\").collect()[0]\n"
    "        size_bytes = detail['sizeInBytes']\n"
    "        num_files = detail['numFiles']\n"
    "        return size_bytes, num_files\n"
    "    except Exception:\n"
    "        # Fallback: read _delta_log directly\n"
    "        try:\n"
    "            log_path = f'{path}/_delta_log'\n"
    "            files = mssparkutils.fs.ls(log_path)\n"
    "            return -1, len(files)  # unknown size, have file count\n"
    "        except:\n"
    "            return -1, -1\n\n"
    "# Tiered sync based on size\n"
    "SMALL_THRESHOLD = 100 * 1024 * 1024    # 100 MB\n"
    "LARGE_THRESHOLD = 1024 * 1024 * 1024   # 1 GB\n\n"
    "size_bytes, num_files = _estimate_table_size(src_path)\n"
    "if size_bytes > LARGE_THRESHOLD:\n"
    "    # LARGE: partitioned overwrite, no diff\n"
    "    src_df.coalesce(max(1, num_files // 4)).write.format('delta') \\\n"
    "        .mode('overwrite').option('overwriteSchema','true') \\\n"
    "        .saveAsTable(full_name)\n"
    "elif size_bytes > SMALL_THRESHOLD:\n"
    "    # MEDIUM: overwrite, skip sample/diff\n"
    "    src_df.write.format('delta').mode('overwrite') \\\n"
    "        .option('overwriteSchema','true').saveAsTable(full_name)\n"
    "else:\n"
    "    # SMALL: full incremental as before (count, diff, append)")

pdf.check_space(50)
pdf.ln(2)
pdf.subsection("FIX D: Clone Table Filtering", TEAL)
pdf.body("Changes to: discover_fabric_schema.py AND gen_nb_payload.py (inner code)")
pdf.numbered(1, "In discover_fabric_schema.py: Filter out any table name matching *_clone_* pattern during DFS enumeration.")
pdf.numbered(2, "In gen_nb_payload.py (inner code): Double-check at runtime -- skip any table containing '_clone_' in its name.")
pdf.numbered(3, "Log filtered tables so we know what was excluded and why.")

pdf.code_block(
    "# Filter clone tables\n"
    "import re\n"
    "_CLONE_PATTERN = re.compile(r'_clone_\\d{8,}')\n"
    "for schema, tables in SCHEMA_TABLES.items():\n"
    "    original = len(tables)\n"
    "    tables = [t for t in tables if not _CLONE_PATTERN.search(t)]\n"
    "    if len(tables) < original:\n"
    "        print(f'  Filtered {original-len(tables)} clone table(s) from {schema}')\n"
    "    SCHEMA_TABLES[schema] = tables")

pdf.check_space(50)
pdf.ln(2)
pdf.subsection("FIX E: Top-Level Error Handling", RED)
pdf.body("Changes to: gen_nb_payload.py (wrapping logic)")
pdf.numbered(1, "Wrap the ENTIRE notebook inner_code in try/except at the Python level (already done in commit 9719386).")
pdf.numbered(2, "In the except block: print full error type, message, and traceback BEFORE re-raising.")
pdf.numbered(3, "Also write the error to the OneLake status marker file so run_and_poll can read it.")
pdf.numbered(4, "Use import traceback at module level (not inside the except) to avoid import failures in error paths.")

# ── TODO LIST ─────────────────────────────────────────────────────────────────
pdf.add_page()
pdf.section_title("3. Implementation TODOs (Exact Changes)", MSFT_BLUE)

todos = [
    ("A1", "Workflow: run_and_poll captures full JSON", "promote-with-schema-validation.yml", "DONE (commit 9719386)"),
    ("A2", "Workflow: run_and_poll reads ___sync_status.json from OneLake after poll", "promote-with-schema-validation.yml", "TODO"),
    ("B1", "Notebook: CREATE SCHEMA IF NOT EXISTS for all non-dbo schemas", "gen_nb_payload.py", "DONE (commit 9719386)"),
    ("B2", "Notebook: SHOW SCHEMAS verification after creation", "gen_nb_payload.py", "TODO"),
    ("B3", "Notebook: Backtick-quote schema names to handle special chars", "gen_nb_payload.py", "TODO"),
    ("C1", "Notebook: _estimate_table_size() via DESCRIBE DETAIL", "gen_nb_payload.py", "TODO"),
    ("C2", "Notebook: Tiered sync (small/medium/large) based on size", "gen_nb_payload.py", "TODO"),
    ("C3", "Notebook: Skip _print_sample for tables > 100MB", "gen_nb_payload.py", "TODO"),
    ("C4", "Notebook: Spark config for AQE + shuffle", "gen_nb_payload.py", "TODO"),
    ("C5", "Notebook: Per-table timeout protection (20 min max)", "gen_nb_payload.py", "TODO"),
    ("D1", "Discovery: Filter *_clone_* tables in discover_fabric_schema.py", "discover_fabric_schema.py", "TODO"),
    ("D2", "Notebook: Runtime clone filter as safety net", "gen_nb_payload.py", "TODO"),
    ("E1", "Notebook: Top-level try/except wrapping", "gen_nb_payload.py", "DONE (commit 9719386)"),
    ("E2", "Notebook: Write ___sync_status.json on completion/failure", "gen_nb_payload.py", "TODO"),
]

widths = [15, 65, 60, 50]
pdf.set_font("Helvetica", "B", 9); pdf.set_text_color(*WHITE); pdf.set_fill_color(*MSFT_BLUE)
for cell, w in zip(["ID", "Task", "File", "Status"], widths):
    pdf.cell(w, 7, cell, border=1, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
pdf.ln(7)

for tid, task, file, status in todos:
    bg = OK_BG if "DONE" in status else WARN_BG
    pdf.set_fill_color(*bg)
    pdf.set_font("Helvetica", "B", 8); pdf.set_text_color(*DARK_GRAY)
    pdf.cell(15, 7, tid, border=1, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(65, 7, task, border=1, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(60, 7, file, border=1, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
    color = GREEN if "DONE" in status else ORANGE
    pdf.set_text_color(*color)
    pdf.cell(50, 7, status, border=1, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.ln(7)

# ── DEFENSE IN DEPTH ──────────────────────────────────────────────────────────
pdf.add_page()
pdf.section_title("4. Defense in Depth - Why This Won't Break Again", GREEN)

pdf.body("The key principle: EVERY failure scenario has MULTIPLE safety nets. If one defense fails, the next catches it.")

pdf.ln(2)
layers = [
    ("Layer 1: Discovery Filters", "Clone tables filtered out before they enter the pipeline. System dirs filtered. Non-schema dirs filtered.", TEAL),
    ("Layer 2: Schema Pre-Creation", "All non-default schemas created BEFORE any table writes. Verified via SHOW SCHEMAS.", ORANGE),
    ("Layer 3: Size-Aware Sync", "Tables sized via O(1) Delta metadata. Large tables use overwrite (no expensive diff). OOM impossible.", PURPLE),
    ("Layer 4: Per-Table Try/Except", "Each table sync wrapped in try/except. One table failing doesn't kill the rest.", MSFT_BLUE),
    ("Layer 5: Top-Level Try/Except", "Entire notebook wrapped. Fatal errors print diagnostics before dying.", RED),
    ("Layer 6: Status Marker File", "Notebook writes sync results to OneLake. Workflow reads it for diagnostics even on failure.", GREEN),
    ("Layer 7: Full Job Status Capture", "run_and_poll dumps complete Fabric API response on failure. Error code, reason, message all logged.", RED),
]

for title, desc, color in layers:
    pdf.check_space(22)
    pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(*color)
    pdf.cell(0, 7, title, new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9.5); pdf.set_text_color(*DARK_GRAY)
    pdf.set_x(10); pdf.multi_cell(190, 5, desc, new_x=XPos.LEFT, new_y=YPos.NEXT); pdf.ln(3)

pdf.ln(4)
pdf.colored_box(
    "SCENARIO MATRIX: What happens when...",
    "Schema doesn't exist?     -> Layer 2 creates it. Layer 4 catches if creation fails.\n"
    "Table is 5GB?             -> Layer 3 uses overwrite (no diff). Spark AQE handles memory.\n"
    "Clone table discovered?   -> Layer 1 filters it. Layer 3 runtime filter catches stragglers.\n"
    "One table fails to sync?  -> Layer 4 catches, continues to next table.\n"
    "Notebook crashes at start?-> Layer 5 prints traceback. Layer 6 writes partial status.\n"
    "Fabric API gives no info? -> Layer 7 dumps full JSON. Layer 6 has notebook-side status.\n"
    "Spark OOM?                -> Layer 3 prevents it (no collect/subtract on large tables).\n"
    "Table takes >20 minutes?  -> Layer 3 timeout skips it, logs warning, continues.",
    OK_BG, GREEN)

# ── FILES CHANGED ─────────────────────────────────────────────────────────────
pdf.add_page()
pdf.section_title("5. Exact Files Changed")

pdf.subsection("scripts/gen_nb_payload.py (MAJOR REWRITE of inner notebook code)")
pdf.bullet("Add _estimate_table_size() helper using DESCRIBE DETAIL")
pdf.bullet("Add tiered sync logic: small/medium/large table handling")
pdf.bullet("Add clone table filtering (regex pattern)")
pdf.bullet("Add CREATE SCHEMA IF NOT EXISTS + SHOW SCHEMAS verification")
pdf.bullet("Add Spark session config (AQE, shuffle partitions)")
pdf.bullet("Add per-table timeout tracking")
pdf.bullet("Skip expensive ops (_print_sample, subtract) for large tables")
pdf.bullet("Write ___sync_status.json to OneLake on completion/failure")
pdf.bullet("Top-level try/except wrapping (already done)")

pdf.ln(2)
pdf.subsection("scripts/discover_fabric_schema.py")
pdf.bullet("Filter *_clone_* tables during DFS enumeration")
pdf.bullet("Log filtered clone tables for visibility")

pdf.ln(2)
pdf.subsection(".github/workflows/promote-with-schema-validation.yml")
pdf.bullet("run_and_poll: capture full JSON + failure details (already done)")
pdf.bullet("After poll completes: read ___sync_status.json from OneLake for notebook diagnostics")

pdf.ln(4)
pdf.colored_box(
    "COMMIT STRATEGY",
    "All changes in ONE commit. No more piecemeal fixes.\n"
    "Commit message: 'feat: resilient sync - large tables, schema creation,\n"
    "error capture, clone filtering'\n\n"
    "This is the definitive fix. If the workflow still fails after this,\n"
    "we will have FULL diagnostics to identify the exact cause.",
    OK_BG, GREEN)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DigitalRealty_Resilient_Sync_Plan.pdf")
pdf.output(out)
print(f"PDF: {out} ({pdf.page_no()} pages)")
