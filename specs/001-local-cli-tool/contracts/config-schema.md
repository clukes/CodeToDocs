# Contract: Configuration Schema (`config.yaml`)

**Location**: `.codetodocs/config.yaml`

## Schema

```yaml
# Required: No (file is created by /codetodocs.init)
# Format: YAML

# Where generated docs are written (relative to repo root)
# Type: string
# Default: "docs/"
output_dir: docs/

# Branch to diff against for incremental updates
# Type: string
# Default: "main"
target_branch: main

# Component definitions (omit for single-component repos)
# Type: array of Component objects
# Default: (none — entire repo treated as single component)
components:
  - name: frontend          # Required: string identifier
    paths:                   # Required: array of directory/file paths
      - apps/web/
      - packages/ui/
    description: "React web application and shared UI components"  # Optional

  - name: backend
    paths:
      - apps/api/
    description: "Node.js API server"

# Custom document types beyond the three defaults
# Type: array of CustomDocument objects
# Default: (none)
documents:
  - name: runbook                                    # Required: string identifier
    template: .codetodocs/templates/runbook.md        # Required: path to template
    output: docs/operations/{component}-runbook.md    # Required: output path with {component} placeholder
    audience: "SRE/Operations team"                   # Optional: description of target audience
```

## Validation Rules

| Field | Rule |
|-------|------|
| `output_dir` | Must be a relative path (no leading `/`). Must not escape repo root (`../`). |
| `target_branch` | Must be a valid Git ref name. Agent should verify it exists with `git rev-parse`. |
| `components[].name` | Must be unique across all components. Must be valid as a filename (alphanumeric, hyphens, underscores). |
| `components[].paths` | Each path must exist in the repository. Overlapping paths across components produce a warning (file assigned to first match). |
| `documents[].template` | Must point to an existing file. If missing, agent reports error and skips that document. |
| `documents[].output` | Must contain `{component}` placeholder. Must be a relative path. |

## Defaults (created by `/codetodocs.init`)

```yaml
output_dir: docs/
target_branch: main
```

No `components` or `documents` sections by default — the agent treats the entire repo as one component and generates only the three default document types.
