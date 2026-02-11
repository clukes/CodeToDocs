# CodeToDocs

Bootstrap installer for CodeToDocs — a prompt-driven documentation generator for AI coding agents.

## Installation

```bash
uvx --from "git+https://github.com/clukes/CodeToDocs.git#subdirectory=installer" codetodocs
```

Or via pip:

```bash
pip install "git+https://github.com/clukes/CodeToDocs.git#subdirectory=installer"
```

## Usage

```bash
# Install prompt files and templates into your repository
codetodocs

# Show what would be copied without copying
codetodocs --dry-run

# Overwrite existing files
codetodocs --force

# Install into a specific directory
codetodocs --target-dir /path/to/repo
```
