# Implementation Plan: CodeToDocs Prompt-Driven Agent Tool

**Branch**: `001-local-cli-tool` | **Date**: 2026-02-09 | **Spec**: [spec.md](specs/001-local-cli-tool/spec.md)
**Input**: Feature specification from `/specs/001-local-cli-tool/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build the complete CodeToDocs prompt-driven agent tool: a bootstrap installer (`uvx codetodocs`), three self-contained prompt files (init, run, status), default templates, and configuration schema. No compiled code at runtime — the installer copies files; the prompts instruct the agent to scaffold, generate, and report documentation in three formats (technical, product, AI context) per component.

## Technical Context

**Language/Version**: Python 3.10+ (bootstrap installer only); Markdown (prompt files — runtime)  
**Primary Dependencies**: None at runtime; `shutil`, `pathlib`, `importlib.resources` for installer  
**Storage**: File system only — YAML config, Markdown/YAML templates, Markdown/YAML output  
**Testing**: Manual invocation across 2+ agent platforms (Copilot, Cursor); pytest for installer  
**Target Platform**: Any OS with Git and an AI coding agent  
**Project Type**: Single project — hybrid (Python package for installer + Markdown prompt files)  
**Performance Goals**: N/A — agent-driven, no latency requirements  
**Constraints**: Zero runtime dependencies; prompt files must be agent-agnostic; installer must be idempotent  
**Scale/Scope**: Prompt files handle repos up to ~50 source files per component; installer handles ~10 files to copy

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Pre-Design | Post-Design | Notes |
|---|-----------|------------|-------------|-------|
| I | Prompt-Driven, Zero Dependencies | PASS | PASS | Prompt files are pure Markdown; installer is a thin file-copy script with no runtime participation. Design confirms: `installer/` is a Python package that copies files only — it does not participate in doc generation. |
| II | Agent-Native, Manual Control | PASS | PASS | All three commands (`init`, `run`, `status`) require explicit user invocation. No watchers, hooks, or background processes in any contract. |
| III | Tri-Audience Output (NON-NEGOTIABLE) | PASS | PASS | Every component produces exactly three artifacts: `technical/{component}.md`, `product/{component}.md`, `ai/{component}.yaml`. Confirmed in data model + prompt command contracts. |
| IV | Git-Native Intelligence | PASS | PASS | Run command diffs against `target_branch`; reads full files + diffs; respects `.gitignore` + `.codetodocsignore`. Incremental mode confirmed in contracts. |
| V | Security by Default | PASS | PASS | No API keys anywhere. Config contains only `output_dir`, `target_branch`, `components`, `documents`. Prompts never touch credentials. |
| VI | Determinism & Resilience | PASS | PASS | Templates define exact structure (technical, product, AI context YAML schema). Self-correction instruction in run prompt. Component-level error isolation confirmed. |

**Gate result: PASS** — No violations pre- or post-design.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Bootstrap installer (Python package)
installer/
├── pyproject.toml           # Package config for uvx/pip
├── src/
│   └── codetodocs/
│       ├── __init__.py
│       ├── __main__.py      # Entry point for `uvx codetodocs`
│       ├── cli.py           # CLI argument parsing
│       ├── copy.py          # Idempotent file-copy logic
│       └── assets/          # Bundled files to copy into user repos
│           ├── prompts/
│           │   ├── codetodocs.init.prompt.md
│           │   ├── codetodocs.run.prompt.md
│           │   └── codetodocs.status.prompt.md
│           └── templates/
│               ├── technical_doc.md
│               ├── product_doc.md
│               └── ai_context.yaml
└── tests/
    ├── test_cli.py
    ├── test_copy.py
    └── fixtures/

# Prompt files (also at repo root for development/testing)
.github/prompts/
├── codetodocs.init.prompt.md
├── codetodocs.run.prompt.md
└── codetodocs.status.prompt.md

# Default templates (also at repo root for development/testing)
.codetodocs/
├── config.yaml
└── templates/
    ├── technical_doc.md
    ├── product_doc.md
    └── ai_context.yaml
```

**Structure Decision**: Hybrid — a Python package under `installer/` for the bootstrap CLI, plus prompt files and templates at the repo root for development and testing. The installer bundles the prompt files and templates as package assets.

## Complexity Tracking

No Constitution Check violations — this section is intentionally empty.
