<!--
  Sync Impact Report
  ==================
  Version change: 1.0.0 → 2.0.0 → 2.1.0 → 2.2.0
  Latest change: 2.1.0 → 2.2.0 (MINOR — aligned Principles III and VI with per-component architecture)
  Previous change: 2.0.0 → 2.1.0 (MINOR — added bootstrap installer to Principle I and Phase 0)
  Modified principles:
    - I. "Single Binary, Zero Dependencies" → "Prompt-Driven, Zero Dependencies"
    - II. "Local-First, Manual Control" — preserved, reworded for agent context
    - III. "Tri-Audience Output" — changed scope from per-file to per-component (NON-NEGOTIABLE)
    - IV. "Git-Native Intelligence" — preserved, agent tools replace go-git
    - V. "Security by Default" — simplified (no API key management needed)
    - VI. "Determinism & Resilience" — changed error isolation from per-file to per-component
  Removed sections:
    - Technical Stack & Constraints (Go-specific table removed entirely)
  Added sections:
    - Prompt Architecture & Constraints (replaces Technical Stack)
  Modified sections:
    - Development Workflow (phases rewritten for prompt authoring)
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ no update needed (generic)
    - .specify/templates/spec-template.md ✅ no update needed (generic)
    - .specify/templates/tasks-template.md ✅ no update needed (generic)
    - .specify/templates/checklist-template.md ✅ no update needed (generic)
    - .specify/templates/agent-file-template.md ✅ no update needed (generic)
  Follow-up TODOs:
    - .github/copilot-instructions.md MUST be updated to match
    - specs/001-local-cli-tool/spec.md MUST be updated to match
-->

# CodeToDocs Constitution

## Core Principles

### I. Prompt-Driven, Zero Dependencies

CodeToDocs MUST be implemented entirely as prompt files
(Markdown) that are copied into a repository. There MUST be
no compiled code, no binary, no build step, and no runtime
dependencies **at documentation-generation time**.

- Distribution is copying `.github/prompts/codetodocs.*.prompt.md`
  files and `.codetodocs/` templates into a repository.
- A lightweight **bootstrap installer** (`uvx codetodocs` or
  `npx codetodocs`) MAY be provided to automate the file-copy
  step. The installer is a thin script that copies files — it
  does not participate in documentation generation.
- The tool MUST work with any AI coding agent that supports
  prompt files (GitHub Copilot, Cursor, Windsurf, etc.).
- No programming language, package manager, or build tool is
  required to **use** CodeToDocs after installation.

**Rationale:** Prompt files are the simplest possible distribution
mechanism. A bootstrap installer reduces onboarding friction
from "manually copy ~10 files" to a single command, without
violating the zero-dependency principle at runtime. This follows
the proven SpecKit pattern already in use in this repository.

### II. Agent-Native, Manual Control

The tool MUST NOT run automatically in the background, watch
file systems, or hook into Git events without explicit user
invocation. Documentation generation is triggered only by:

- An explicit agent command (`/codetodocs.init`, `/codetodocs.run`).

The tool MUST NOT modify global editor settings, inject itself
into general AI chat contexts, or persist background processes.
Each prompt file MUST be a self-contained, isolated command.

**Rationale:** Developers must trust that their tools are
predictable. Implicit side-effects erode trust. Agent commands
are inherently explicit — the user types the command.

### III. Tri-Audience Output (NON-NEGOTIABLE)

Every processed component MUST produce exactly three distinct
documentation artifacts:

1. **Technical Docs** (`docs/technical/{component}.md`) — targeted
   at engineers; covers implementation, edge cases, dependencies.
2. **Product Docs** (`docs/product/{component}.md`) — targeted at
   PMs/stakeholders; covers business value, rules, user impact.
3. **AI Context** (`docs/ai/{component}.json`) — targeted at AI
   agents/RAG systems; strict JSON schema with signatures, types,
   exports, and complexity scores.

The prompt instructions MUST guide the agent to generate all
three artifacts for each component. If any artifact cannot be
generated for a component, the agent MUST report it rather than
silently skipping.

**Rationale:** This is the core value proposition. Each audience
has fundamentally different needs; a single doc format serves
none of them well.

### IV. Git-Native Intelligence

The tool MUST leverage Git as its primary source of change
detection and context:

- Diff analysis MUST compare `HEAD` against a configurable target
  branch (default: `main`) using the agent's Git tools or
  terminal commands.
- The prompt MUST instruct the agent to read full file content
  (for context) alongside the diff (for focus) when generating
  updates.
- The prompt MUST instruct the agent to respect `.gitignore` and
  a custom `.codetodocsignore` file for exclusion rules.
- The prompt SHOULD instruct the agent to identify and skip
  trivial changes (comment-only, formatting-only).

**Rationale:** Git is the universal source of truth for code
changes. Leveraging diffs enables incremental documentation
updates that are more accurate than full rescans.

### V. Security by Default

- No API keys are managed by CodeToDocs. The agent's own
  authentication handles LLM access.
- Prompt files MUST NOT instruct the agent to read, store, or
  transmit any secrets or credentials.
- Configuration files (`.codetodocs/config.yaml`) MUST NOT
  contain any sensitive data — only structural settings
  (output directory, target branch).

**Rationale:** By delegating LLM access to the agent platform,
CodeToDocs eliminates the entire category of API key management
security concerns.

### VI. Determinism & Resilience

- Prompt instructions MUST be specific enough to produce
  consistent output structure across different agent models
  and invocations.
- Templates in `.codetodocs/templates/` MUST define the exact
  structure and sections expected in each output type.
- If the agent produces output that doesn't match the expected
  structure, the prompt SHOULD instruct the agent to self-correct.
- Failures in one component's documentation MUST NOT halt
  processing of remaining components; the prompt MUST instruct
  the agent to report errors and continue.

**Rationale:** Prompt-driven tools must compensate for LLM
non-determinism with precise structural templates and clear
validation instructions.

## Prompt Architecture & Constraints

The following conventions are binding for the project:

| Component         | Convention                                     |
|-------------------|------------------------------------------------|
| Prompt location   | `.github/prompts/codetodocs.*.prompt.md`       |
| Config location   | `.codetodocs/config.yaml`                      |
| Template location | `.codetodocs/templates/`                       |
| Output location   | Configurable via `output_dir` (default: `docs/`) |
| Naming pattern    | `codetodocs.<command>.prompt.md`               |

**Prompt file conventions:**
- Each prompt file MUST be self-contained with all instructions
  needed for the agent to execute the command.
- Prompts MUST reference `.codetodocs/config.yaml` for runtime
  configuration (output directory, target branch).
- Prompts MUST reference `.codetodocs/templates/` for output
  structure definitions.
- Prompts MUST NOT depend on any external tooling, scripts, or
  binaries beyond what the agent platform provides natively.

**Configuration schema:**
```yaml
# .codetodocs/config.yaml
output_dir: docs/          # Where generated docs are written
target_branch: main        # Branch to diff against for incremental updates
```

## Development Workflow

Development follows a phased approach aligned with the PRD
milestones:

0. **Phase 0 — Installer (Bootstrap):** Python package for
   `uvx codetodocs`, idempotent file-copy script.
1. **Phase 1 — Constitution (MVP):** Prompt file structure,
   `codetodocs.init.prompt.md`, default templates, config schema.
2. **Phase 2 — Crawler (Zero State):** `codetodocs.run.prompt.md`
   for full-scan documentation, file discovery instructions,
   per-file tri-audience generation.
3. **Phase 3 — Updater (Incremental):** Git diff detection in
   run prompt, incremental update mode, trivial change skip
   guidance.
4. **Phase 4 — Polish:** `codetodocs.status.prompt.md` for
   coverage reporting, prompt refinement for consistency,
   user documentation and README.

**Quality gates for each phase:**

- Prompt files MUST be tested by invoking them in at least two
  different agent platforms (e.g., Copilot + Cursor) to verify
  consistent behavior.
- All three documentation output types (Principle III) MUST be
  validated against the template structures after generation.
- Each prompt command MUST be tested on at least one real
  repository with multiple source files.

## Governance

This constitution is the authoritative source of project
principles and constraints. It supersedes ad-hoc decisions,
PR discussions, and verbal agreements.

- **Amendment process:** Any change to this constitution MUST
  be proposed as a PR with a clear rationale, reviewed by at
  least one maintainer, and merged only after all dependent
  templates and documentation are updated for consistency.
- **Versioning:** The constitution follows Semantic Versioning:
  - **MAJOR** — Principle removal or incompatible redefinition.
  - **MINOR** — New principle or materially expanded guidance.
  - **PATCH** — Clarifications, wording, or typo fixes.
- **Compliance review:** Every PR MUST be checked against these
  principles. The plan-template "Constitution Check" section
  MUST reference the active principles by name.
- **Runtime guidance:** See the agent-file-template for
  development guidelines that operationalize these principles.

**Version**: 2.2.0 | **Ratified**: 2026-02-09 | **Last Amended**: 2026-02-09
