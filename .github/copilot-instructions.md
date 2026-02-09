# Project Guidelines

## Overview

CodeToDocs is a Go CLI tool that analyzes Git diffs and uses LLMs to auto-generate documentation in three formats: Technical (engineers), Product (PMs), and AI Context (JSON for RAG). Distributed as a single static binary with zero runtime dependencies.

See [docs/PRD.md](../docs/PRD.md) for the full product requirements.

## Code Style

- **Language:** Go 1.22+
- Follow standard Go conventions: `gofmt`, `go vet`, effective Go idioms
- Use `internal/` for all non-public packages — nothing under `internal/` should be imported externally
- Package names: short, lowercase, single-word (e.g., `config`, `git`, `llm`, `generator`, `tui`)
- Error handling: return `error` values, wrap with `fmt.Errorf("context: %w", err)` for stack context
- Use `go:embed` for template files in `templates/` — they are embedded into the binary at compile time

## Architecture

```
cmd/root.go              # Cobra CLI entry point
internal/config/         # Viper-based YAML config loader (.codetodocs/config.yaml)
internal/git/            # Diff analysis & file reading via go-git/v5 (no system git)
internal/llm/            # LLM provider adapters (OpenAI, Anthropic, Ollama)
internal/generator/      # Core orchestration: prompting, parsing, file writing
internal/templates/      # go:embed assets for default templates
internal/tui/            # lipgloss styling & bubbletea spinners
templates/               # Raw template sources (technical_doc.md, product_doc.md, ai_context.json)
```

**Key design decisions:**
- Single LLM call per file generates all three doc outputs (Technical, Product, AI Context) simultaneously using structured/JSON output to minimize latency and cost
- Git operations use `go-git/v5` natively — never shell out to `git`
- API keys are read from environment variables only (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`), never stored in config files
- Invalid LLM JSON responses trigger automatic retry (up to 3 attempts)

**Generated documentation layout in user repos:**
```
.codetodocs/config.yaml       # User config (provider, model, output_dir, target_branch)
docs/technical/{file}.md      # Engineer-facing: implementation details, setup, edge cases
docs/product/{file}.md        # PM-facing: feature summaries, business rules, user impact
docs/ai/{file}.json           # Agent-facing: structured JSON (signatures, types, complexity)
```

## Build and Test

```bash
go mod tidy                    # Sync dependencies
go build -o codetodocs ./cmd   # Build binary
go test ./...                  # Run all tests
go vet ./...                   # Static analysis
```

Cross-compile targets: `GOOS=linux`, `GOOS=darwin GOARCH=arm64`, `GOOS=darwin GOARCH=amd64`, `GOOS=windows`

CLI start time must be < 50ms.

## Project Conventions

- **CLI commands:** `codetodocs init` (scaffold config + templates) and `codetodocs run` (generate/update docs)
- **Config format:** YAML at `.codetodocs/config.yaml` with keys: `provider`, `model`, `output_dir`, `target_branch`
- **Ignore files:** Respect both `.gitignore` and `.codetodocsignore`
- **SpecKit workflow:** This repo uses SpecKit for spec-driven development. Feature work follows: Constitution → Specify → Clarify → Plan → Tasks → Implement. Feature branches use `###-feature-name` naming (e.g., `001-cli-skeleton`). Specs live in `specs/###-feature-name/`

## Dependencies

| Package | Purpose |
|---------|---------|
| `spf13/cobra` | CLI command routing |
| `spf13/viper` | YAML/env config parsing |
| `go-git/v5` | Native Git implementation |
| `charmbracelet/lipgloss` | Terminal styling |
| `charmbracelet/bubbletea` | Interactive TUI (spinners, prompts) |
| `net/http` or `tmc/langchaingo` | LLM API client |

## Security

- **API keys must never appear in config files or be committed.** Read exclusively from environment variables.
- Validate and sanitize all LLM responses before writing to disk.
- Template files are embedded at compile time — user-facing templates in `.codetodocs/templates/` are copies that users may customize.
