# Digital Realty Fabric -- Prompt Creation Guide

A comprehensive guide explaining how the Custom Agent Prompt was designed, why each section matters, and how to maintain and adapt it for other projects.

---

## 1. Why This Prompt Was Created

### The Problem

AI coding assistants (GitHub Copilot, Claude, ChatGPT, etc.) are powerful but generic. When working on a complex domain-specific project like a Microsoft Fabric data platform, the AI lacks critical context:

- **It does not know the codebase structure** -- which files matter, which are auto-generated vs hand-authored
- **It does not know the domain quirks** -- Fabric's schema-enabled lakehouse behavior, the two-token auth requirement, the DFS system directory filtering
- **It does not know your conventions** -- schema-as-code, never-use-Fabric-UI, migration naming, notebook numbering
- **It does not know the bugs you have already found** -- the 7 commits worth of fixes that took hours to discover
- **It does not know the team structure** -- which agent handles what, when to delegate vs do it yourself

### The Solution

A **custom system prompt** encodes all of this institutional knowledge into a document that an AI agent can consume at the start of every session. This eliminates the "cold start problem" where every new conversation requires re-explaining the project context.

### Who Benefits

| Audience | Benefit |
|----------|---------|
| **You (future sessions)** | Every new AI session starts with full project context. No re-explaining. |
| **New team members** | Onboarding document that covers architecture, conventions, and gotchas |
| **Custom agents** | Can be used as system prompt for GitHub Copilot agents, GPTs, or Claude Projects |
| **Automated tooling** | Scripts can reference the prompt for context-aware code generation |

---

## 2. How Each Section Was Designed

### Design Principles

1. **Specificity over generality** -- Include actual workspace IDs, file paths, and error codes. Generic instructions produce generic results.
2. **Examples over explanations** -- Show the actual curl commands, the actual log output format, the actual JSON structure.
3. **Failure modes alongside happy paths** -- Document what goes wrong, not just what should happen.
4. **Actionable instructions** -- Every section should help the agent DO something, not just KNOW something.
5. **Layered depth** -- Quick reference for simple tasks, deep detail for complex debugging.

### Information Sources

The prompt was built by examining:
- Every file in the repository (notebooks, scripts, workflows, configs)
- Git history (7 commits worth of bug fixes and their root causes)
- Fabric REST API behavior discovered through testing
- Environment configurations and workspace mappings
- The Squad agent team structure and routing rules

---

## 3. The Stanza Structure (Section-by-Section)

### Section 1: Agent Identity

**What it contains:** Name, role, core competencies, behavioral guidelines.

**Why it matters:** Sets the agent's "personality" and boundaries. Without this, the agent might:
- Suggest modifying schemas through the Fabric UI (violates the project's core principle)
- Skip environments (go directly from Dev to Prod)
- Use implicit schema inference instead of explicit StructType

**Design notes:**
- The behavioral guidelines are phrased as imperatives ("Always validate...", "Schema changes MUST...")
- Core competencies tell the agent what it is qualified to do
- The owner field establishes who to ask when unclear

### Section 2: Project Context

**What it contains:** What the project is, the problem it solves, architecture overview, key constraints.

**Why it matters:** Provides the "big picture" that prevents the agent from making architecturally wrong decisions. An agent that does not know Fabric Git integration doesn't track table schemas might suggest storing schemas in Fabric metadata instead of code.

**Design notes:**
- The ASCII architecture diagram gives spatial understanding of the CI/CD flow
- The medallion architecture explanation (Bronze/Silver/Gold) is critical for understanding which notebooks do what
- Key constraints are numbered and explicit -- these are the non-negotiable rules of the platform

### Section 3: Codebase Map

**What it contains:** Complete directory tree, file descriptions, auto-generated vs hand-authored flags.

**Why it matters:** This is the agent's "map of the territory." Without it, the agent cannot:
- Know where to find the schema registry (notebooks/00_schema_registry.py)
- Know that migration files follow a specific naming convention (V###__description.py)
- Distinguish between hand-authored files (safe to edit) and auto-generated ones (will be overwritten)

**Design notes:**
- The tree uses indentation to show hierarchy
- Each file has a one-line description
- The key files table calls out the most important files and their roles
- Squad agent directories are included to support team-aware operations

### Section 4: Technical Knowledge Base

**What it contains:** Fabric REST API patterns, OneLake DFS patterns, schema-enabled lakehouse behavior, Delta log parsing, deployment lifecycle.

**Why it matters:** This is the domain-specific knowledge that no AI has by default. Fabric's API behaviors (the two-token requirement, the HTTP 400 on schema-enabled lakehouses, the silent empty response without Storage token) are all learned through painful debugging.

**Design notes:**
- Organized by sub-topic (4.1, 4.2, 4.3...) for easy reference
- Includes actual code snippets and curl commands
- The type mapping table is directly useful for code generation
- Each pattern includes the "why" (not just the "what")

**Sub-sections explained:**

| Sub-section | Purpose |
|-------------|---------|
| 4.1 Fabric REST API | Auth patterns, key endpoints, notebook execution lifecycle |
| 4.2 OneLake DFS | How to list and read files from OneLake storage |
| 4.3 Schema-Enabled Lakehouses | The special behaviors that break standard patterns |
| 4.4 Delta Log Parsing | How to extract schemas from Delta transaction logs |
| 4.5 Deployment vs Data Copy | Critical distinction: Pipeline copies definitions, not data |

### Section 5: Conventions and Rules

**What it contains:** Coding standards, naming conventions, environment configuration format, TMDL best practices.

**Why it matters:** Consistency. An agent that generates code following different conventions creates maintenance burden and confusion. This section ensures:
- New tables follow the `bronze_`/`silver_` naming convention
- New migrations follow the `V###__description.py` pattern
- Schemas are always explicit (StructType), never inferred
- PowerShell scripts use the standard auth pattern

**Design notes:**
- Presented as a lookup table for quick reference
- Rules are phrased as "always" or "never" where appropriate
- The environment JSON structure is shown as a template

### Section 6: CI/CD Workflow Reference

**What it contains:** Step-by-step breakdown of the 4-job promotion workflow, schema discovery flow, notebook generation flow.

**Why it matters:** The CI/CD pipeline is the most complex part of the project. An agent that does not understand the 4-job structure might:
- Try to add steps to the wrong job
- Not realize that schema discovery happens in Job 1 but data copy happens in Job 3
- Miss the artifact passing between jobs

**Design notes:**
- Each job is numbered with its name and purpose
- The schema discovery flow is shown as a decision tree (pseudocode flowchart)
- The notebook generation flow explains the transformation from JSON schema to base64-encoded notebook

### Section 7: Known Issues and Gotchas

**What it contains:** Complete list of bugs found, common failure modes, Fabric API quirks.

**Why it matters:** This is perhaps the MOST VALUABLE section. These bugs took hours to find and fix. Without this section, any agent (or human) working on the project would have to rediscover them.

**Design notes:**
- The bugs table includes Impact and Fix columns -- not just what was wrong, but what was done
- The failure modes table is organized by Symptom -> Cause -> Debug approach
- API quirks include workarounds, not just warnings
- Presented in a troubleshooting-friendly format

### Section 8: Environment Reference

**What it contains:** Workspace IDs, lakehouse IDs, pipeline IDs, GitHub Actions secrets and variables, OneLake RBAC roles.

**Why it matters:** Hard-coded reference data that the agent needs for:
- Constructing API URLs
- Validating configurations
- Understanding the environment topology
- Setting up new workflows

**Design notes:**
- Organized by category (workspaces, lakehouses, pipeline, secrets)
- IDs are shown in monospace for copy-paste
- The OneLake RBAC roles table shows the security model at a glance

### Section 9: Squad Team Reference

**What it contains:** Agent roster, routing rules, delegation guidelines.

**Why it matters:** The project uses an 11-agent Squad system. Without this section, the agent cannot:
- Route work to the right specialist
- Know when to fan out (spawn multiple agents)
- Understand the Scribe's automatic background role

**Design notes:**
- The roster table includes Role, Domain, and Charter file path
- Routing rules are a simple lookup table
- Delegation guidelines are phrased as rules, not suggestions

### Section 10: Debugging Playbook

**What it contains:** Step-by-step debugging procedures, curl commands for verification, log format reference.

**Why it matters:** When something goes wrong, the agent needs to know HOW to investigate. This section provides:
- A systematic approach to debugging workflow failures
- Actual commands to verify table promotion
- The log format so the agent can parse output correctly

**Design notes:**
- Organized by scenario (failing workflow, missing tables, schema-enabled lakehouse)
- Includes actual curl commands with placeholder IDs
- The log format section shows what "good" output looks like

### Appendix: Quick Reference Card

**What it contains:** Common commands, table summary, auth scopes, file change impact matrix.

**Why it matters:** Quick lookup for routine tasks. The "File Change Impact" table is especially useful -- it tells the agent "if you change X, you must also update Y."

---

## 4. How to Maintain the Prompt

### When to Update

| Trigger | What to Update |
|---------|----------------|
| New table added to schema registry | Section 3 (Codebase Map), Appendix (Tables), Section 5 (if new convention) |
| New bug discovered and fixed | Section 7 (Known Issues), Section 10 (Debugging Playbook) |
| New workflow added | Section 3 (directory structure), Section 6 (CI/CD Reference) |
| New squad agent added | Section 9 (Squad Team Reference) |
| Workspace ID changes | Section 8 (Environment Reference) |
| New script or notebook | Section 3 (Codebase Map), Section 5 (if new convention) |
| Fabric API behavior changes | Section 4 (Technical Knowledge Base), Section 7 (API Quirks) |

### How to Update

1. **Edit the Markdown file** (DigitalRealty_Custom_Agent_Prompt.md)
2. **Regenerate the PDF** by running the Python generation script
3. **Commit both** in the same PR
4. **Test the updated prompt** by starting a new AI session and asking it a question that requires the new information

### What NOT to Include

- **Secrets or credentials** -- Never put actual tokens, passwords, or connection strings in the prompt
- **Volatile data** -- Don't include information that changes weekly (sprint goals, current bugs in progress)
- **Personal preferences** -- Keep it to project conventions, not individual style choices
- **Speculation** -- Only include verified behavior. If unsure, add a "TBD" or "Verify" note.

---

## 5. Best Practices for Agent Prompts

### Structure

1. **Start with identity and mission** -- Set the agent's role before giving it information
2. **Layer from general to specific** -- Project overview -> codebase map -> technical details -> debugging
3. **Include both "what" and "why"** -- Conventions without rationale are hard to apply correctly
4. **Use tables for structured data** -- Easier to parse than paragraphs
5. **Use code blocks for anything technical** -- Commands, configs, API responses

### Content

1. **Be specific** -- "Use `StructType` for schemas" is better than "use explicit schemas"
2. **Include failure modes** -- What goes wrong matters more than what goes right
3. **Show examples** -- One good example is worth ten sentences of explanation
4. **Document workarounds** -- If the platform has bugs, the agent needs to know how to work around them
5. **Include a debugging playbook** -- The most common use of an agent prompt is during troubleshooting

### Format

1. **Use Markdown** -- Universal, readable, version-controllable
2. **Keep sections independent** -- Each section should be useful on its own
3. **Use consistent heading levels** -- H1 for the title, H2 for major sections, H3 for sub-sections
4. **Include a table of contents** -- For long prompts, navigation matters
5. **Use horizontal rules** -- Separate major sections visually

### Maintenance

1. **Version control the prompt** -- It should live in the repository, not in a personal document
2. **Update alongside code changes** -- Schema changes should trigger prompt updates
3. **Review periodically** -- At least monthly, check if the prompt matches reality
4. **Generate a PDF for sharing** -- Not everyone has a Markdown viewer
5. **Test with fresh sessions** -- Periodically start a new AI session to verify the prompt works

---

## 6. Customization Guide

### Adapting for Other Projects

The 10-section structure is designed to be universal. Here is how to adapt each section for a different project:

#### Section 1: Agent Identity
Replace the Fabric-specific competencies with your project's technology stack. Keep the behavioral guidelines pattern -- they are the most impactful part.

#### Section 2: Project Context
Write the "elevator pitch" for your project. What is it? Who uses it? What problem does it solve? Include an architecture diagram.

#### Section 3: Codebase Map
Generate a directory tree and annotate each file. Mark auto-generated vs hand-authored. This section requires the most effort but pays off the most.

#### Section 4: Technical Knowledge Base
Document the domain-specific knowledge that an AI would not know. For Fabric, it was the two-token auth and schema-enabled lakehouse behavior. For your project, it might be your ORM's quirks, your API gateway's caching behavior, or your database's locking semantics.

#### Section 5: Conventions and Rules
List your coding standards, naming conventions, and process rules. If you have a style guide, reference it. If you do not, this is a good time to create one.

#### Section 6: CI/CD Workflow Reference
Document your pipeline. Even if it is a simple build-test-deploy, the agent needs to know what runs when and what triggers what.

#### Section 7: Known Issues and Gotchas
Start a running list of bugs, workarounds, and platform quirks. This section grows over time and becomes increasingly valuable.

#### Section 8: Environment Reference
List your environments, their configurations, and how to access them. Include IDs, URLs, and any access patterns.

#### Section 9: Team Reference
If you use a multi-agent system, document the roster and routing. If not, you can replace this with a "key contacts" or "code owners" section.

#### Section 10: Debugging Playbook
Write the debugging procedures you wish you had when you started. "How do I check if X is working?" for every major component.

### Template

Here is a minimal template for a new project:

```markdown
# {Project Name} -- Custom Agent Prompt

## Section 1: Agent Identity
Name: {Agent Name}
Role: {Role Description}
Mission: {One-sentence mission}

## Section 2: Project Context
{What this project is and why it exists}

## Section 3: Codebase Map
{Directory tree with annotations}

## Section 4: Technical Knowledge Base
{Domain-specific knowledge the AI needs}

## Section 5: Conventions and Rules
{Coding standards, naming conventions}

## Section 6: CI/CD Workflow Reference
{Pipeline documentation}

## Section 7: Known Issues and Gotchas
{Bugs, workarounds, platform quirks}

## Section 8: Environment Reference
{IDs, URLs, configs}

## Section 9: Team Reference
{Contacts, code owners, or agent roster}

## Section 10: Debugging Playbook
{How to investigate common failures}
```

---

## Summary

The Digital Realty Custom Agent Prompt is not just a reference document -- it is an **executable specification** for an AI agent. Every section has a purpose:

| Section | One-Word Purpose |
|---------|-----------------|
| Identity | Boundaries |
| Context | Understanding |
| Codebase Map | Navigation |
| Knowledge Base | Expertise |
| Conventions | Consistency |
| CI/CD Reference | Process |
| Known Issues | Prevention |
| Environment | Configuration |
| Team Reference | Delegation |
| Debugging | Recovery |

Together, they transform a generic AI assistant into a domain expert that can work on the Digital Realty Fabric platform as effectively as a team member who has been on the project from day one.
