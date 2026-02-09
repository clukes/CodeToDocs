# Quickstart: CodeToDocs

**Branch**: `001-local-cli-tool` | **Date**: 2026-02-09

## Developer Setup (working on CodeToDocs itself)

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Git
- An AI coding agent (GitHub Copilot, Cursor, or Windsurf)

### Clone & Install

```bash
git clone <repo-url>
cd CodeToDocs
git checkout 001-local-cli-tool

# Install the bootstrap installer in development mode
cd installer
uv pip install -e .
```

### Project Structure

```
installer/                        # Python package for `uvx codetodocs`
├── pyproject.toml
├── src/codetodocs/
│   ├── cli.py                    # CLI entry point
│   ├── copy.py                   # Idempotent file-copy logic
│   └── assets/                   # Bundled prompt files + templates
└── tests/

.github/prompts/                   # Prompt files (development copies)
├── codetodocs.init.prompt.md
├── codetodocs.run.prompt.md
└── codetodocs.status.prompt.md

.codetodocs/                       # Templates (development copies)
├── config.yaml
└── templates/
```

### Running Tests

```bash
cd installer
uv run pytest
```

### Testing Prompt Files

1. Open the repository in VS Code with GitHub Copilot enabled
2. Open the Copilot chat panel
3. Type `/codetodocs.init` to test the init command
4. Type `/codetodocs.run` to test the run command
5. Type `/codetodocs.status` to test the status command

### Testing the Installer

```bash
# Create a test directory
mkdir /tmp/test-repo && cd /tmp/test-repo && git init

# Run the installer from source
uvx --from /path/to/CodeToDocs/installer codetodocs

# Verify files were copied
ls -la .github/prompts/codetodocs.*.prompt.md
ls -la .codetodocs/templates/
```

## End-User Workflow (using CodeToDocs in their repo)

```bash
# 1. Install prompt files into your repo
uvx codetodocs

# 2. Initialize configuration (in your AI coding agent)
/codetodocs.init

# 3. Generate documentation
/codetodocs.run

# 4. Check coverage
/codetodocs.status
```
