# Lambert — History

## Project Context

Digital Realty Microsoft Fabric demo. Creating PDF demo guides for three use cases. Existing PDFs in repo: DigitalRealty_3UseCase_Demo_Guide.pdf, DigitalRealty_Lakehouse_Schema_Evolution.pdf, DigitalRealty_Schema_Evolution_Demo_Guide.pdf, DigitalRealty_StoryDemo_Guide.pdf. Python PDF generation scripts exist (generate_3usecase_guide.py, generate_schema_evolution_pdf.py). User: Saurabh.

## Learnings

### 2025-01-29: Comprehensive Demo Workflow PDF Created

**Task:** Created `DigitalRealty_3UseCase_Demo_Workflow.pdf` - a complete step-by-step presenter guide for the 3 Use Case demo.

**Pattern Used:** Extended the existing DemoGuidePDF class from `generate_3usecase_guide.py`. Key design elements:
- WorkflowPDF class extending FPDF with color-coded action tags (DO, CLICK, TYPE, SAY, EXPECT, VERIFY)
- Section banners with Microsoft blue (#0078D4) theme
- Action methods for consistent formatting
- Helper methods: `_safe()` for Unicode to Latin-1 conversion, `_wrap()` for text wrapping

**Content Structure (16 pages):**
1. Title page with demo overview
2. Pre-demo setup checklist
3. Use Case 1: Lakehouse Schema Evolution (CI/CD) - pain point, solution flow, value prop, Q&A, fallbacks
4. Use Case 2: Power BI Performance Optimization - BPA analyzer, memory analysis, before/after comparison
5. Use Case 3: Automated Quality & Governance - data quality checks, security layers, compliance
6. Competitive comparison table (Fabric vs Databricks vs Snowflake)
7. Recommended next steps with phased timeline

**Key Design Decisions:**
- Talk track boxes (light blue background) for presenter guidance
- Value boxes (light green background) to highlight business impact specific to Digital Realty
- Q&A sections grouped by category: Technical Depth, Security/Compliance, Migration/Timeline
- Fallback plans (3 options per use case) for resilience during live demos
- Honest competitive assessment with star ratings

**Technical Challenge:** FPDF uses Latin-1 encoding by default. Had to enhance `_safe()` method to:
1. Replace Unicode characters with ASCII equivalents (em-dash -> --, arrows -> ->)
2. Use `encode('latin-1', 'ignore').decode('latin-1')` to strip remaining non-Latin-1 characters

**File Paths:**
- Script: `generate_3usecase_workflow.py` (38 KB)
- Output: `DigitalRealty_3UseCase_Demo_Workflow.pdf` (25 KB, 16 pages)

**Reusable Pattern for Future PDFs:**
- Color scheme constants (BLUE, DARK, LIGHT_GRAY, etc.)
- Action color mapping dictionary
- Helper methods for safe text handling and wrapping
- Consistent section structure: Setup -> Pain Point -> Solution Flow -> Value Prop -> Q&A -> Fallbacks
