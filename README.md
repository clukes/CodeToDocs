# CodeToDocs

Prompt-driven documentation generator for AI coding agents. Analyzes your codebase and generates documentation in three formats — Technical (engineers), Product (PMs), and AI Context (JSON for RAG) — per component.

## Installation

Inside a repo run:

```bash
uvx codetodocs
```

Also works with `pipx run codetodocs` or `pip install codetodocs`.

This copies prompt files and templates into your repository.

## Usage

Open your AI coding agent (GitHub Copilot, Cursor, or Windsurf) and run these commands:

### 1. Initialize

```
/codetodocs.init
```

Scaffolds `.codetodocs/` with `config.yaml` and default templates. Safe to re-run — idempotent.

### 2. Generate Documentation

```
/codetodocs.run
```

Generates tri-audience documentation for every component:
- **Full-scan mode**: When no docs exist yet — reads all source files
- **Incremental mode**: When docs exist — diffs against `target_branch`, updates only affected components

### 3. Check Coverage

```
/codetodocs.status
```

Reports which components are documented, stale, partially documented, or missing:

```
Documentation Coverage Report
═══════════════════════════════

Components: 3 total

  ✓ frontend       — Documented (generated 2026-02-08T10:00:00Z)
  ⚠ backend        — Potentially stale (source modified after docs)
  ✗ shared-utils   — Undocumented

Coverage: 33% (1/3 fully documented)
```

## Generated Output

```
docs/
├── technical/{component}.md   # Engineer-facing: architecture, APIs, setup
├── product/{component}.md     # PM-facing: features, business rules, user impact
└── ai/{component}.json        # Agent-facing: structured JSON for RAG retrieval
```

## Configuration

```yaml
# .codetodocs/config.yaml

output_dir: docs/          # Where docs are written
target_branch: main        # Branch to diff against

# Optional: Define components for monorepos
components:
  - name: frontend
    paths:
      - apps/web/
      - packages/ui/
    description: React web application

  - name: backend
    paths:
      - apps/api/
    description: Node.js API server

# Optional: Custom document types
documents:
  - name: runbook
    template: .codetodocs/templates/runbook.md
    output: docs/operations/{component}-runbook.md
    audience: SRE/Operations team

# Optional: Exclude default document types (technical, product, ai_context)
exclude_defaults:
  - ai_context
```

For single-component repositories, omit the `components` section — the entire repo is treated as one component named after the repository directory.

## How It Works

CodeToDocs is implemented entirely as **prompt files** (`.github/prompts/codetodocs.*.prompt.md`). When you invoke a command, the AI coding agent reads the prompt and executes the instructions using its own LLM — no separate API keys, no external services.

The bootstrap installer (`uvx codetodocs`) simply copies these files into your repo. After that, it's not needed again.

## Ignore Files

CodeToDocs respects:
- `.gitignore` — always applied
- `.codetodocsignore` — optional, additive exclusions using gitignore-style patterns

## Development

```bash
git clone <repo-url>
cd CodeToDocs
cd installer
uv venv && source .venv/bin/activate
uv pip install -e . && uv pip install pytest

# Run tests
python -m pytest tests/ -v

# Test prompt files
# Open in VS Code with Copilot → /codetodocs.init, /codetodocs.run, /codetodocs.status
```

## License

MIT
