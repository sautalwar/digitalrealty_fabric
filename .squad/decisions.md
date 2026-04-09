# Squad Decisions

## Active Decisions

### 1. Single-File HTML Presentation Architecture

**Date:** 2024-12-19  
**Author:** Parker (Presentation Developer)  
**Status:** Implemented

Chose **single self-contained HTML file** with all CSS and JavaScript inline for `DigitalRealty_3UseCase_Presentation.html`.

**Rationale:**
- ✅ Complete offline portability — no internet required
- ✅ Zero installation — works in any browser
- ✅ Version control friendly — single file to track
- ✅ Email/share friendly — one attachment
- ✅ Print friendly — preserves all slides
- ✅ Fast loading — no HTTP requests

**Alternatives Considered:**
1. React/Vue SPA — Rejected: requires build process
2. reveal.js / impress.js — Rejected: external dependencies
3. PowerPoint export to HTML — Rejected: bloated output
4. Multi-file HTML + CSS + JS — Rejected: harder to share

**Implementation:** Dark theme (#1e1e1e) with Fabric blue (#0078d4), CSS Grid/Flexbox, keyboard navigation, 32 slides.

---

### 2. PDF Workflow Pattern for Demo Guides

**Date:** 2025-01-29  
**Author:** Lambert (Content Writer)  
**Status:** Implemented

Adopted **structured workflow PDF pattern** with action tags, talk tracks, and fallback plans for `DigitalRealty_3UseCase_Demo_Workflow.pdf`.

**Rationale:**
- Demo PDFs must be executable by ANY presenter
- Talk tracks prevent awkward silence during loading
- Value props keep demos business-focused, not feature tours
- Fallback plans reduce demo anxiety and give presenters confidence
- Action tags make PDF scannable during live presentation

**Key Elements:**
- [DO] = physical action, [CLICK] = UI interaction, [TYPE] = keyboard input, [SAY] = talk track, [EXPECT] = validation, [VERIFY] = checkpoint
- Color-coded boxes: blue for talk tracks, green for business value
- Honest competitive comparison (acknowledges trade-offs)
- Hard questions grouped by category with prepared responses

**Reusable Components:**
- `action(tag, text)` — Color-coded action rendering
- `talk_track_box(text)` — Light blue box for presenter guidance
- `value_box(text)` — Light green box for business value
- `qa_item(question, answer)` — Formatted Q&A pairs

**Impact:**
- For presenters: Complete script reduces prep time, fallback plans reduce anxiety
- For content team: Reusable pattern for future demo PDFs
- For sales/field: Competitive comparison gives honest positioning

---

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
