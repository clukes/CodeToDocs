# Contract: Bootstrap Installer CLI

**Interface**: Command-line tool invoked via `uvx codetodocs`, `pipx run codetodocs`, or `codetodocs`

## Commands

### `codetodocs` (default — install/copy files)

```
codetodocs [OPTIONS]
```

**Options**:

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--target-dir` | path | `.` (cwd) | Directory to install into |
| `--force` | flag | false | Overwrite existing files (opt-in; violates default idempotency) |
| `--dry-run` | flag | false | Show what would be copied without copying |
| `--version` | flag | — | Print version and exit |
| `--help` | flag | — | Print help and exit |

**Behavior**:

1. Resolve `target_dir` to absolute path
2. If `--dry-run`, compute manifest and print without writing
3. For each asset in manifest:
   - If target file exists and `--force` is not set → skip, add to skipped list
   - If target file exists and `--force` is set → overwrite, add to overwritten list
   - If target file does not exist → create parent dirs, copy, add to copied list
4. Print summary report
5. If not a git repo, print warning: "Warning: This directory is not a Git repository. Git is required for documentation generation."
6. Print next step: "Run /codetodocs.init in your AI coding assistant to complete setup."

**Exit codes**:

| Code | Meaning |
|------|---------|
| 0 | Success (files copied and/or skipped) |
| 1 | Error (I/O failure, permission denied) |

**Output format** (stdout):

```
CodeToDocs v0.1.0

Copied:
  .github/prompts/codetodocs.init.prompt.md
  .github/prompts/codetodocs.run.prompt.md
  .github/prompts/codetodocs.status.prompt.md
  .codetodocs/templates/technical_doc.md
  .codetodocs/templates/product_doc.md
  .codetodocs/templates/ai_context.json

Skipped (already exist):
  (none)

✓ 6 files copied, 0 skipped

Next step: Run /codetodocs.init in your AI coding assistant to complete setup.
```

**Output format** (when files exist):

```
CodeToDocs v0.1.0

Copied:
  .codetodocs/templates/ai_context.json

Skipped (already exist):
  .github/prompts/codetodocs.init.prompt.md
  .github/prompts/codetodocs.run.prompt.md
  .github/prompts/codetodocs.status.prompt.md
  .codetodocs/templates/technical_doc.md
  .codetodocs/templates/product_doc.md

✓ 1 file copied, 5 skipped

Next step: Run /codetodocs.init in your AI coding assistant to complete setup.
```
