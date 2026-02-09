<!--
  Sync Impact Report
  ==================
  Version change: N/A → 1.0.0 (initial creation)
  Modified principles: N/A (first version)
  Added sections:
    - Core Principles (6 principles derived from PRD v1.1)
    - Technical Stack & Constraints
    - Development Workflow
    - Governance
  Removed sections: N/A
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ no update needed (generic)
    - .specify/templates/spec-template.md ✅ no update needed (generic)
    - .specify/templates/tasks-template.md ✅ no update needed (generic)
    - .specify/templates/checklist-template.md ✅ no update needed (generic)
    - .specify/templates/agent-file-template.md ✅ no update needed (generic)
  Follow-up TODOs: None
-->

# CodeToDocs Constitution

## Core Principles

### I. Single Binary, Zero Dependencies

CodeToDocs MUST be distributed as a single, statically compiled
Go binary with no external runtime dependencies. Users MUST be
able to download and run the tool without installing any
prerequisites (no system Git, no Node.js, no Python, etc.).

- All Git operations MUST use `go-git/v5` (pure Go).
- All templates MUST be embedded via `go:embed` directives.
- The binary MUST compile to Windows (`.exe`), macOS
  (ARM + Intel), and Linux from a single codebase.

**Rationale:** Frictionless adoption is the primary growth lever
for a developer tool. A single binary eliminates "works on my
machine" failures and removes installation as a barrier.

### II. Local-First, Manual Control

The tool MUST NOT run automatically in the background, watch
file systems, or hook into Git events without explicit user
invocation. Documentation generation is triggered only by:

- A manual CLI command (`codetodocs run`).
- An explicit agent invocation (`/codetodocs` or `@codetodocs`).

The tool MUST NOT modify global editor settings, inject itself
into general AI chat contexts, or persist background processes.

**Rationale:** Developers must trust that their tools are
predictable. Implicit side-effects erode trust and cause
unexpected LLM costs.

### III. Tri-Audience Output (NON-NEGOTIABLE)

Every processed source file MUST produce exactly three distinct
documentation artifacts:

1. **Technical Docs** (`docs/technical/{filename}.md`) — targeted
   at engineers; covers implementation, edge cases, dependencies.
2. **Product Docs** (`docs/product/{filename}.md`) — targeted at
   PMs/stakeholders; covers business value, rules, user impact.
3. **AI Context** (`docs/ai/{filename}.json`) — targeted at AI
   agents/RAG systems; strict JSON schema with signatures, types,
   exports, and complexity scores.

All three artifacts SHOULD be generated from a single LLM call
per file using Structured Outputs / JSON Mode to minimize latency
and cost. If a single-call approach fails, the system MUST fall
back to individual calls rather than omitting any artifact.

**Rationale:** This is the core value proposition. Each audience
has fundamentally different needs; a single doc format serves
none of them well.

### IV. Git-Native Intelligence

The tool MUST integrate deeply with Git as its primary source of
change detection and context:

- Diff analysis MUST compare `HEAD` against a configurable target
  branch (default: `main`).
- The tool MUST read full file content (for context) alongside
  the diff (for focus) when generating updates.
- The tool MUST respect `.gitignore` and a custom
  `.codetodocsignore` file for exclusion rules.
- Trivial changes (comment-only, formatting-only) SHOULD be
  detected and skipped to avoid unnecessary LLM calls.

**Rationale:** Git is the universal source of truth for code
changes. Leveraging diffs enables incremental documentation
updates that are both cheaper and more accurate than full rescans.

### V. Security by Default

- API keys MUST NEVER be stored in configuration files
  (`.codetodocs/config.yaml` or any other committed file).
- API keys MUST only be read from environment variables
  (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).
- The tool MUST NOT log, print, or transmit API keys in any
  output (stdout, stderr, log files, error messages).

**Rationale:** A developer tool that leaks secrets to version
control is a liability. Environment-variable-only key management
is the industry-standard minimum.

### VI. Resilience & Performance

- The CLI MUST start in under 50 milliseconds.
- If an LLM returns invalid JSON, the tool MUST automatically
  retry up to 3 times before reporting failure.
- Failures in one file's documentation MUST NOT halt processing
  of remaining files; errors MUST be collected and reported at
  the end of the run.
- The `init` command MUST complete full repo setup in under
  5 seconds.

**Rationale:** Developer tools that are slow or brittle get
uninstalled. Graceful degradation ensures partial progress is
never lost.

## Technical Stack & Constraints

The following technology choices are binding for the project:

| Component       | Choice                          | Locked? |
|-----------------|---------------------------------|---------|
| Language        | Go 1.22+                        | Yes     |
| CLI Framework   | `spf13/cobra`                   | Yes     |
| Configuration   | `spf13/viper` (YAML + Env)      | Yes     |
| Git Library     | `go-git/v5`                     | Yes     |
| TUI / Styling   | `charmbracelet/lipgloss` + `bubbletea` | Yes |
| LLM Client      | `net/http` or `tmc/langchaingo` | Flexible |
| LLM Providers   | OpenAI, Anthropic, Ollama       | Extensible |

- All configuration MUST live in `.codetodocs/config.yaml`.
- The project MUST follow the directory layout defined in the
  PRD (§5.2): `cmd/`, `internal/`, `templates/`.
- New dependencies MUST be justified against the Single Binary
  principle (Principle I). CGo dependencies are prohibited unless
  no pure-Go alternative exists and the dependency is critical.

## Development Workflow

Development follows a phased approach aligned with the PRD
milestones:

1. **Phase 1 — Constitution (MVP):** Go module setup, CLI
   skeleton, `init` command with template and config injection.
2. **Phase 2 — Crawler (Zero State):** File system walker
   (respecting ignore rules), full-scan documentation generation,
   "State of the World" LLM prompts.
3. **Phase 3 — Updater (Incremental):** Git diff triggers,
   comparison logic (Old Doc + New Code → New Doc), trivial
   change detection and skip optimization.
4. **Phase 4 — Distribution:** GitHub Action / Dockerfile,
   Homebrew Tap, cross-platform release binaries.

**Quality gates for each phase:**

- All new code MUST have corresponding tests.
- All three documentation output types (Principle III) MUST be
  validated with snapshot or golden-file tests once Phase 2 is
  reached.
- CLI commands MUST be tested with integration tests exercising
  real (or in-memory) Git repositories via `go-git/v5`.

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

**Version**: 1.0.0 | **Ratified**: 2026-02-09 | **Last Amended**: 2026-02-09
