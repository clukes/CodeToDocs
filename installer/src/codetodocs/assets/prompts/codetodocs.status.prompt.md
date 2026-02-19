---
description: "Report documentation coverage status for all components"
agent: 'agent'
---

# /codetodocs.status — Documentation Coverage Report

You are an AI agent executing the `/codetodocs.status` command for CodeToDocs. Your job is to analyze the repository and report which components have documentation, which are missing, and which are potentially stale.

---

## Step 1 — Verify Prerequisites

1. Check that `.codetodocs/config.yaml` exists in the repository root.
   - If it does **not** exist, output the following message and **stop**:
     > Configuration not found. Run `/codetodocs.init` to set up CodeToDocs.
2. Read and parse `.codetodocs/config.yaml`. Extract:
   - `output_dir` (default: `docs/`)
   - `target_branch` (default: `main`)
   - `components` (optional list)
   - `documents` (optional list of custom document definitions)
   - `exclude_defaults` (optional list of excluded default types: `technical`, `product`, `ai_context`)

---

## Step 2 — Resolve Components

Use the same resolution logic as `/codetodocs.run`:

1. **If `components` is defined** in config → use the list as-is. Each entry has `name`, `paths`, and optional `description`.
2. **If `components` is NOT defined** → treat the entire repository as a single component whose `name` is the repository directory name (the basename of the repo root). Its `paths` is `["."]`.

After resolution, you must have a list of one or more components, each with a `name` and `paths`.

If the resolved list is empty, output:
> No components found in configuration.

Then **stop**.

---

## Step 3 — Check Coverage for Each Component

For every resolved component, perform the following checks:

### 3a. Check Artifact Existence

Look for the **default artifacts that are not excluded** by `exclude_defaults`:

| Artifact | Path | Excluded if |
|----------|------|-------------|
| Technical doc | `{output_dir}/technical/{component-name}.md` | `exclude_defaults` contains `technical` |
| Product doc | `{output_dir}/product/{component-name}.md` | `exclude_defaults` contains `product` |
| AI context | `{output_dir}/ai/{component-name}.yaml` | `exclude_defaults` contains `ai_context` |

Skip checking for any artifact type listed in `exclude_defaults` — do not count it as missing.

If `documents` is defined in config, also check for each custom document. Resolve the custom document output path using the pattern from `output`, replacing `{component}` with the component name.

Record which artifacts exist and which are missing.

### 3b. Parse Generation Timestamps

For each artifact that **exists**, extract its generation timestamp:

- **Markdown files** (`.md`): Read the first line and parse the header comment:
  ```
  <!-- CodeToDocs | Component: {name} | Generated: {ISO-8601-timestamp} -->
  ```
  Extract the `Generated:` value.

- **YAML files** (`.yaml`): Read the file and extract the value at `_codetodocs.generated`.

If the header marker is missing or cannot be parsed, treat the artifact as "exists but unknown age" — skip the staleness check for that specific artifact.

### 3c. Check Staleness

For each artifact with a valid generation timestamp:

1. Run `git log -1 --format="%aI" -- {paths}` where `{paths}` are the component's source paths. This returns the ISO-8601 date of the most recent source modification.
2. Compare the source modification date against the artifact's generation timestamp.
3. If the source modification date is **after** the generation timestamp → the artifact is **potentially stale**.

If **any** artifact for a component is stale, the component is considered potentially stale.

### 3d. Classify Each Component

Based on the checks above, assign one status to each component:

| Status | Symbol | Condition |
|--------|--------|-----------|
| **Documented** | `✓` | All expected artifacts exist and none are stale |
| **Potentially stale** | `⚠` | All expected artifacts exist but source was modified after generation |
| **Partially documented** | `△` | Some but not all expected artifacts exist |
| **Undocumented** | `✗` | No artifacts exist at all |

"All expected artifacts" means the non-excluded default artifacts **plus** any custom documents defined in config. Excluded defaults are not considered expected.

### 3e. Calculate Coverage

```
coverage = (fully_documented_count / total_component_count) × 100
```

Only components classified as **Documented** (`✓`) count toward the numerator. Round to the nearest whole number.

---

## Step 4 — Display the Report

Output the report in this exact format:

```
Documentation Coverage Report
═══════════════════════════════

Components: {N} total

  {symbol} {component-name}       — {status-label}
  ...

Coverage: {X}% ({documented}/{total} fully documented)

Run /codetodocs.run to update documentation.
```

### Status label formats

- `✓` → `Documented (generated {timestamp})`
- `⚠` → `Potentially stale (source modified after docs)`
- `✗` → `Undocumented`
- `△` → `Partially documented (missing: {comma-separated list of missing artifact types})`

Use short artifact type names in the missing list: `technical`, `product`, `ai`, or the custom document `name`.

### Formatting rules

- List components in the order they appear in config (or alphabetically if single-component).
- Align status symbols in a column for readability.
- Use the generation timestamp from the **oldest** artifact when displaying the `Documented` label.
- The final line (`Run /codetodocs.run ...`) should always appear, regardless of coverage percentage.

---

## Error Handling Summary

| Situation | Action |
|-----------|--------|
| Missing `.codetodocs/config.yaml` | Print message directing user to run `/codetodocs.init`. Stop. |
| No components resolved | Print "No components found in configuration." Stop. |
| Unparseable header marker | Treat artifact as existing but skip staleness check for it |
| `git log` fails or returns empty | Skip staleness check; do not mark as stale |
| Output directory doesn't exist | All components are Undocumented |

---

## Important Constraints

- Do **not** modify any files. This command is read-only.
- Do **not** generate or update any documentation. Only report status.
- Respect `.gitignore` and `.codetodocsignore` when resolving source paths for staleness checks.
- Keep the output concise and scannable. Do not add extra commentary beyond the report format.
