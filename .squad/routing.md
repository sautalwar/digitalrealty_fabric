# Work Routing

How to decide who handles what.

## Routing Table

| Work Type | Route To | Examples |
|-----------|----------|----------|
| Demo architecture & strategy | Dallas | Demo flow design, use case sequencing, story arcs |
| Fabric notebooks & schema code | Ripley | PySpark, Delta Lake, medallion architecture, schema evolution |
| HTML presentations & slides | Parker | HTML/CSS/JS slide decks, animations, interactive demos |
| Demo guides & PDF content | Lambert | Talk tracks, walkthrough scripts, competitive prep |
| Testing & validation | Kane | Verify demos work, edge cases, data quality validation |
| Visual design & branding | Brett | Layout, color, typography, visual polish |
| CI/CD pipelines & DevOps | Bishop | GitHub Actions, deployment scripts, pipeline automation |
| Power BI & DAX | Ash | Semantic models, DAX optimization, BPA rules, DirectLake |
| Code review | Dallas | Review PRs, check quality, architectural decisions |
| Scope & priorities | Dallas | What to build next, trade-offs, decisions |
| Session logging | Scribe | Automatic — never needs routing |

## Issue Routing

| Label | Action | Who |
|-------|--------|-----|
| `squad` | Triage: analyze issue, assign `squad:{member}` label | Lead |
| `squad:{name}` | Pick up issue and complete the work | Named member |

### How Issue Assignment Works

1. When a GitHub issue gets the `squad` label, the **Lead** triages it — analyzing content, assigning the right `squad:{member}` label, and commenting with triage notes.
2. When a `squad:{member}` label is applied, that member picks up the issue in their next session.
3. Members can reassign by removing their label and adding another member's label.
4. The `squad` label is the "inbox" — untriaged issues waiting for Lead review.

## Rules

1. **Eager by default** — spawn all agents who could usefully start work, including anticipatory downstream work.
2. **Scribe always runs** after substantial work, always as `mode: "background"`. Never blocks.
3. **Quick facts → coordinator answers directly.** Don't spawn an agent for "what port does the server run on?"
4. **When two agents could handle it**, pick the one whose domain is the primary concern.
5. **"Team, ..." → fan-out.** Spawn all relevant agents in parallel as `mode: "background"`.
6. **Anticipate downstream work.** If a feature is being built, spawn the tester to write test cases from requirements simultaneously.
7. **Issue-labeled work** — when a `squad:{member}` label is applied to an issue, route to that member. The Lead handles all `squad` (base label) triage.
