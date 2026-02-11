# Project Guidelines

## Overview

CodeToDocs is a prompt-driven agent tool that analyzes Git diffs and uses the AI coding agent's own LLM to auto-generate documentation in three formats: Technical (engineers), Product (PMs), and AI Context (JSON for RAG). Documentation is generated **per component** (or for the entire repository if not a monorepo), not per file. Distributed as a set of prompt files (`.md`) that are copied into any repository — zero compiled code, zero build step, zero dependencies.

A lightweight bootstrap installer automates copying all files into a new repo with a single command. Install directly from GitHub source via `uvx --from "git+https://github.com/clukes/CodeToDocs.git#subdirectory=installer" codetodocs`.

See [docs/PRD.md](docs/PRD.md) for the full product requirements.

## Architecture

CodeToDocs is implemented entirely as prompt files following the SpecKit pattern:

```
.github/prompts/
├── codetodocs.init.prompt.md    # /codetodocs.init — scaffold config & templates
├── codetodocs.run.prompt.md     # /codetodocs.run — generate/update documentation
└── codetodocs.status.prompt.md  # /codetodocs.status — report documentation coverage

.codetodocs/
├── config.yaml                  # User configuration (output_dir, target_branch)
└── templates/
    ├── technical_doc.md         # Template for engineer-facing docs
    ├── product_doc.md           # Template for PM-facing docs
    └── ai_context.yaml          # Schema/template for AI-facing YAML
```

**Key design decisions:**
- No compiled code at runtime — everything is Markdown prompt files
- A thin bootstrap installer (installed from GitHub source) handles initial file copying into repos
- The agent's own LLM handles documentation generation — no separate API keys or provider configuration
- Git operations use the agent's built-in tools or terminal `git` commands
- Each prompt command is self-contained with all instructions needed for execution
- Follows the same pattern as SpecKit (`.github/prompts/speckit.*.prompt.md`)
- Documentation is **per component**, not per file — one set of docs describes an entire component holistically

**Generated documentation layout in user repos (single-component repo):**
```
docs/technical/{repo-name}.md   # Engineer-facing: purpose, architecture, setup, config, APIs
docs/product/{repo-name}.md     # PM-facing: features, business rules, user impact
docs/ai/{repo-name}.yaml        # Agent-facing: structured YAML (modules, signatures, config schema)
```

**Generated documentation layout in user repos (multi-component monorepo):**
```
docs/technical/{component}.md   # One per component (e.g., frontend.md, backend.md)
docs/product/{component}.md     # One per component
docs/ai/{component}.yaml        # One per component
```

## Prompt File Conventions

- Prompt files live in `.github/prompts/` with naming pattern `codetodocs.<command>.prompt.md`
- Each prompt file is self-contained — it includes all instructions the agent needs
- Prompts reference `.codetodocs/config.yaml` for runtime settings
- Prompts reference `.codetodocs/templates/` for output structure definitions
- Prompts MUST NOT depend on any external tooling, scripts, or binaries

## Configuration

```yaml
# .codetodocs/config.yaml
output_dir: docs/          # Where generated docs are written
target_branch: main        # Branch to diff against for incremental updates

# Component definitions (omit for single-component repos)
components:
  - name: frontend
    paths:
      - apps/web/
      - packages/ui/
    description: React web application and shared UI components
  - name: backend
    paths:
      - apps/api/
    description: Node.js API server

# Optional: Custom documents beyond the defaults
documents:
  - name: runbook
    template: .codetodocs/templates/runbook.md
    output: docs/operations/{component}-runbook.md
    audience: SRE/Operations team

# Optional: Exclude specific default document types (technical, product, ai_context)
exclude_defaults:
  - ai_context
```

## Project Conventions

- **Bootstrap install:** `uvx --from "git+https://github.com/clukes/CodeToDocs.git#subdirectory=installer" codetodocs` copies prompt files + templates into a repo
- **Agent commands:** `/codetodocs.init` (scaffold config + templates), `/codetodocs.run` (generate/update docs), `/codetodocs.status` (coverage report)
- **Config format:** YAML at `.codetodocs/config.yaml` with keys: `output_dir`, `target_branch`, `components`, `documents`, `exclude_defaults`
- **Documentation scope:** Per component (or whole repo if no components defined), not per file
- **Ignore files:** Respect both `.gitignore` and `.codetodocsignore`
- **SpecKit workflow:** This repo uses SpecKit for spec-driven development. Feature work follows: Constitution → Specify → Clarify → Plan → Tasks → Implement. Feature branches use `###-feature-name` naming (e.g., `001-local-cli-tool`). Specs live in `specs/###-feature-name/`

## Security

- No API keys are managed by this tool — the agent platform handles LLM access
- Configuration files contain only structural settings (output directory, target branch) — never secrets
- Prompt files MUST NOT instruct the agent to read, store, or transmit any credentials
