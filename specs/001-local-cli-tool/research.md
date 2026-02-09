# Research: CodeToDocs Prompt-Driven Agent Tool

**Branch**: `001-local-cli-tool` | **Date**: 2026-02-09

## 1. Bootstrap Installer — Python Packaging for `uvx`

### Decision: Standard `pyproject.toml` with hatchling build backend

**Rationale**: `uvx codetodocs` is an alias for `uv tool run codetodocs`. It installs the `codetodocs` package from PyPI into a cached temporary virtualenv and runs the executable. No uv-specific configuration is needed — a standard PEP 621 `[project.scripts]` entry point is sufficient.

**Key findings**:
- Package name MUST equal command name (`codetodocs`) so `uvx codetodocs` works without `--from`
- Entry point: `[project.scripts] codetodocs = "codetodocs.cli:main"`
- Build backend: hatchling (modern, fast, well-supported by uv)
- Minimum Python: `>=3.10` (for robust `importlib.resources.files()`)
- Cross-compatible with `pip install`, `pipx install`, and `pipx run` with zero extra config

**Alternatives rejected**:
- Poetry: non-standard metadata format, less compatible with uv
- Flit: less flexible for including data files
- setuptools: more boilerplate, hatchling preferred for new projects

## 2. Static Asset Bundling

### Decision: Files inside package + `importlib.resources.files()`

**Rationale**: Prompt files and templates are bundled as package data inside `src/codetodocs/assets/`. Each subdirectory needs `__init__.py` to be traversable via `importlib.resources`.

**Key findings**:
- Hatchling includes all files inside the package directory in the wheel by default
- `importlib.resources.files()` is the officially recommended API (replaces `pkg_resources`)
- Works with zip imports and all PEP 302 import hooks

**Alternatives rejected**:
- `pkg_resources`: deprecated, slower
- `__file__` + `os.path`: breaks with zip imports
- `importlib_resources` backport: not needed with Python ≥3.10

## 3. Prompt File Format & Cross-Agent Compatibility

### Decision: `.prompt.md` with YAML frontmatter (Copilot-native); ≤500 lines per file

**Rationale**: `.prompt.md` is the native format for GitHub Copilot slash commands. Copilot, Cursor, and Windsurf each have different mechanisms — no single format works identically across all three.

**Key findings**:
- Copilot frontmatter: `name`, `description`, `agent`, `model`, `tools`
- Templates should be referenced externally via markdown links, not embedded inline
- All platforms recommend: numbered steps, bullet lists, concrete examples
- Size target: ≤500 lines / ≤10K characters (Windsurf hard limit: 12K chars)
- Structure each prompt: Purpose → Prerequisites → Steps → Error Handling → Validation

**Cross-platform strategy**: Ship `.prompt.md` files for Copilot as primary. Agent Skills format (`SKILL.md`) could be added later for Cursor/Windsurf compatibility — out of scope for this feature.

**Alternatives rejected**:
- Embedding templates inline: bloats prompt files, prevents customization
- Single universal format: doesn't exist across agents; Copilot `.prompt.md` is the most feature-rich

## 4. AI Context JSON Schema

### Decision: Structured component-level JSON with signatures, types, config, and metrics

**Rationale**: The schema is optimized for RAG retrieval and agent consumption — signatures over code snippets, flat type lookups, and qualitative complexity ratings.

**Key fields**:
- `_codetodocs`: Metadata block (component name, generation timestamp, schema version)
- `component`: Name, purpose, languages, entry points
- `modules`: Array of {name, path, description, role} — role is `core`/`integration`/`infrastructure`
- `api`: Sub-categorized by construct kind — `functions`, `classes`, `middleware`
- `types`: Flat array of {name, definition, description}
- `configuration`: Structured variables with types, defaults, required flags
- `dependencies`: Split internal/external with purpose annotations
- `metrics`: Aggregate counts + qualitative `complexity_rating`

**Design decisions**:
- **Signatures only, no code snippets**: Token-efficient, stable, excellent search targets
- **Qualitative complexity**: Full cyclomatic complexity requires AST parsing (violates zero-dependencies); LLM-assessed rating is more practical
- **Flat types array**: Types are referenced cross-module; flat lookup is easier than nested trees
- **`api` sub-categories**: Enables targeted retrieval ("what middleware?" vs "what function?")

## 5. Generated Documentation Header Marker

### Decision: HTML comment with structured metadata

**Format**: `<!-- CodeToDocs | Component: {name} | Generated: {ISO-8601-timestamp} -->`

**For JSON files**: `"_codetodocs": { "component": "name", "generated": "timestamp", "schema_version": "1.0" }`

**Rationale**: Invisible when rendered, machine-parseable, enables both ownership detection (safe overwrites) and staleness detection (timestamp comparison).

## 6. Idempotent File Copy Logic

### Decision: Check-before-write with skip reporting

**Rationale**: The installer must never overwrite existing files (FR-020, FR-022). Each target file is checked for existence before copy; skipped files are reported to the user.

**Algorithm**:
1. Build manifest of {source_asset → target_path} mappings
2. For each mapping: if target exists, add to "skipped" list; else copy and add to "copied" list
3. Report both lists to stdout
4. Exit 0 regardless (idempotent — running twice is safe)
