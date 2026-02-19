---
description: "Initialize CodeToDocs configuration for the current repository"
agent: 'agent'
---

# `/codetodocs.init` — Initialize CodeToDocs

## Purpose

This command creates `.codetodocs/config.yaml` by analyzing the current repository and walking the user through configuration choices. Templates and prompt files should already be in place from the bootstrap installer.

**Created file:**

- `.codetodocs/config.yaml` — Runtime configuration (output directory, target branch, components)

## Instructions

Follow these steps exactly in order. Do not skip steps.

### Step 1: Prerequisite Check

1. Verify this is a Git repository by checking for a `.git/` directory or running `git rev-parse --is-inside-work-tree`.
2. If NOT a Git repository → report error: "Not a Git repository. Please run `git init` first." and **stop**.

### Step 2: Verify Installer Assets

Check that the bootstrap installer has already copied the required files:

**Required prompt files:**
- `.github/prompts/codetodocs.init.prompt.md`
- `.github/prompts/codetodocs.run.prompt.md`
- `.github/prompts/codetodocs.status.prompt.md`

**Required template files:**
- `.codetodocs/templates/technical_doc.md`
- `.codetodocs/templates/product_doc.md`
- `.codetodocs/templates/ai_context.yaml`

If any of these files are missing:
- List the missing files.
- Report: "Missing files. Please run the CodeToDocs installer first to install prompt files and templates. See: https://github.com/clukes/CodeToDocs#installation"
- **Stop execution here.**

If all files are present → proceed to Step 3.

### Step 3: Idempotency Guard

1. Check if `.codetodocs/config.yaml` already exists.
2. If it **does** exist:
   - Display the current config contents.
   - Ask: "Configuration already exists. Do you want to re-run setup and overwrite it? (yes/no)"
   - If **no** → **stop execution**.
   - If **yes** → proceed to Step 4 (existing config will be overwritten at the end).
3. If it does **not** exist → proceed to Step 4.

### Step 4: Detect Default Branch

1. Try to detect the default branch automatically:
   - Run: `git remote show origin 2>/dev/null | grep 'HEAD branch' | sed 's/.*: //'`
   - If that fails, try: `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||'`
   - If that fails, check if `main` branch exists: `git rev-parse --verify main 2>/dev/null`
   - If that fails, check if `master` branch exists: `git rev-parse --verify master 2>/dev/null`
2. Present the detected branch (or "main" as fallback) and ask the user to confirm:
   - "Detected default branch: `{branch}`. Is this correct, or would you like to use a different branch?"
3. Store the confirmed value as `target_branch`.

### Step 5: Detect Output Directory

1. Check if common documentation directories already exist: `docs/`, `documentation/`, `doc/`.
2. Suggest a default:
   - If `docs/` exists → suggest `docs/`
   - Otherwise → suggest `docs/`
3. Ask the user: "Where should generated documentation be written? (default: `docs/`)"
4. Validate the response:
   - Must be a relative path (no leading `/`).
   - Must not escape the repo root (`../`).
5. Store the confirmed value as `output_dir`.

### Step 6: Analyze Repository for Components

1. Scan the repository's top-level directory structure.
2. Look for signals that indicate a monorepo with multiple components:
   - Directories like `apps/`, `packages/`, `services/`, `modules/`, `libs/`
   - Multiple `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `*.csproj`, or `pom.xml` files at different levels
   - Workspace configuration in root `package.json` (workspaces field), `pnpm-workspace.yaml`, `Cargo.toml` (workspace members), etc.
3. Based on the analysis, determine and suggest one of:
   - **Single-component repo**: "This looks like a single-component repository. The whole repo will be documented as one unit named `{repo-directory-name}`."
   - **Multi-component repo**: "This looks like a monorepo. I found these potential components:" followed by a suggested list with names and paths.
4. Ask the user to confirm:
   - For single-component: "Is this correct, or do you want to define specific components?"
   - For multi-component: "Are these components correct? You can add, remove, or rename them."
5. If the user defines components, for each component collect:
   - `name` — identifier (must be valid as a filename: alphanumeric, hyphens, underscores)
   - `paths` — list of directories/files belonging to this component
   - `description` — (optional) brief description of the component
6. Validate:
   - Component names must be unique.
   - Each path must exist in the repository.
   - Warn if paths overlap across components (file assigned to first match).

### Step 7: Ask About Custom Document Types

1. Ask: "CodeToDocs generates three document types by default: Technical (engineers), Product (PMs), and AI Context (YAML). Do you want to add any custom document types? (yes/no)"
2. If **no** → proceed to Step 7b.
3. If **yes** → for each custom document, collect:
   - `name` — identifier for the document type (e.g., `runbook`, `onboarding`)
   - `audience` — who the document is for (e.g., "SRE/Operations team")
   - Inform the user: "You'll need to create a template file at `.codetodocs/templates/{name}.md` for this document type."
   - Build the entry with:
     - `template`: `.codetodocs/templates/{name}.md`
     - `output`: `{output_dir}/{name}/{component}.md` (using the output_dir from Step 5)
4. Ask: "Add another custom document type? (yes/no)" — repeat until done.

### Step 7b: Ask About Excluding Default Document Types

1. Ask: "Do you want to exclude any of the default document types? The defaults are: Technical (engineers), Product (PMs), AI Context (JSON). (yes/no)"
2. If **no** → proceed to Step 8.
3. If **yes** → present the three defaults and let the user select which to exclude:
   - `technical` — Engineer-facing documentation
   - `product` — PM-facing documentation
   - `ai_context` — AI/RAG-facing YAML
4. Validate:
   - Each entry must be one of: `technical`, `product`, `ai_context`.
   - Cannot exclude all three defaults unless at least one custom document was added in Step 7. If the user tries to exclude all defaults with no custom documents, warn: "You must keep at least one document type. Either keep a default or add a custom document type."
5. Store the confirmed list as `exclude_defaults`.

### Step 8: Write Configuration File

Generate and write `.codetodocs/config.yaml` using the collected values.

**For a single-component repo:**

```yaml
# CodeToDocs Configuration
# See: https://github.com/codetodocs/codetodocs

# Directory where generated documentation is written (relative to repo root)
output_dir: {output_dir}

# Branch to diff against for incremental documentation updates
target_branch: {target_branch}
```

**For a multi-component repo (add components section):**

```yaml
# CodeToDocs Configuration
# See: https://github.com/codetodocs/codetodocs

# Directory where generated documentation is written (relative to repo root)
output_dir: {output_dir}

# Branch to diff against for incremental documentation updates
target_branch: {target_branch}

# Component definitions
components:
  - name: {component_name}
    paths:
      - {path}
    description: "{description}"
```

**If custom documents were added, append:**

```yaml
# Custom document types
documents:
  - name: {name}
    template: .codetodocs/templates/{name}.md
    output: {output_dir}/{name}/{component}.md
    audience: "{audience}"
```

**If any defaults were excluded in Step 7b, append:**

```yaml
# Excluded default document types (valid: technical, product, ai_context)
exclude_defaults:
  - {excluded_type}
```

### Step 9: Report Summary

After the config file is written, report:

```
CodeToDocs initialized successfully!

Configuration written to .codetodocs/config.yaml

  Target branch:  {target_branch}
  Output dir:     {output_dir}
  Components:     {count} ({names or "entire repo"})
  Custom docs:    {count or "none"}
  Excluded defaults: {comma-separated list or "none"}

Templates installed:
  - .codetodocs/templates/technical_doc.md   (engineer-facing)
  - .codetodocs/templates/product_doc.md     (PM-facing)
  - .codetodocs/templates/ai_context.yaml    (AI/RAG-facing)
  - .codetodocs/templates/{name}.md          (only if custom documents were added)

Review and adjust these templates if you want to customize the structure
or sections of your generated documentation.

Next step: Run /codetodocs.run to generate documentation.
```

List one line per custom document template if any were added in Step 7. Omit the custom lines if none were added.
If any defaults were excluded, omit the excluded template lines from the "Templates installed" list.

## Error Handling

- **Not a Git repository** → Report error and stop. Do not create any files.
- **Missing installer assets** → Report missing files, instruct user to run bootstrap installer, and stop.
- **Invalid input** → Re-prompt with explanation of the constraint (e.g., "Component names can only contain letters, numbers, hyphens, and underscores").
- **File write failure** → Report the specific error (file path, error message) and stop.
