# Contract: Prompt Command Interfaces

**Location**: `.github/prompts/codetodocs.*.prompt.md`

## `/codetodocs.init` — Initialize Repository

**Input**: None (reads current repository state)

**Prerequisites**: Prompt files exist in `.github/prompts/`

**Behavior**:
1. Check if `.codetodocs/` directory exists
2. If exists → report "already initialized", list existing files, exit
3. If not exists → create:
   - `.codetodocs/config.yaml` (with defaults: `output_dir: docs/`, `target_branch: main`)
   - `.codetodocs/templates/technical_doc.md`
   - `.codetodocs/templates/product_doc.md`
   - `.codetodocs/templates/ai_context.json`
4. Report summary of created files
5. Print next step: "Run `/codetodocs.run` to generate documentation"

**Output**: Created files on disk + summary message

**Error cases**:
- `.codetodocs/` already exists → report, do not overwrite

---

## `/codetodocs.run` — Generate/Update Documentation

**Input**: None (reads config + Git state)

**Prerequisites**: `.codetodocs/config.yaml` exists (run `/codetodocs.init` first)

**Behavior**:
1. Read `.codetodocs/config.yaml`
2. Determine mode:
   - If no existing docs in `output_dir` → **full-scan mode**
   - If existing docs present → **incremental mode** (diff against `target_branch`)
3. Resolve components:
   - If `components` defined → use them
   - If not → treat entire repo as single component named after repo directory
4. For full-scan: read all source files per component
5. For incremental: run `git diff {target_branch}...HEAD --name-only`, map changed files to components
6. For each affected component:
   a. Read all source files in component (for context)
   b. Read diff (for focus, in incremental mode)
   c. Read templates from `.codetodocs/templates/`
   d. Generate three artifacts: technical, product, AI context
   e. Prepend header marker: `<!-- CodeToDocs | Component: {name} | Generated: {timestamp} -->`
   f. Write files to `{output_dir}/{type}/{component}.{ext}`
7. If `documents` defined in config → also generate custom documents
8. Report summary: components processed, skipped, errors

**Output**: Documentation files on disk + summary message

**Error cases**:
- Config missing → report error, suggest `/codetodocs.init`
- Target branch doesn't exist → report error, suggest checking `target_branch` setting
- No commits → report error for diff-based operations
- Component generation failure → report error, continue with next component
- Trivial changes only → skip component, report as "skipped (trivial changes only)"
- Deleted component directory → flag docs with orphaned header

---

## `/codetodocs.status` — Report Documentation Coverage

**Input**: None (reads config + file system)

**Prerequisites**: `.codetodocs/config.yaml` exists

**Behavior**:
1. Read `.codetodocs/config.yaml`
2. Resolve components (same logic as run)
3. For each component, check if documentation artifacts exist in `output_dir`
4. For each existing artifact, read the `<!-- CodeToDocs | ... | Generated: {timestamp} -->` header
5. Compare generation timestamp against source file modification times
6. Classify each component:
   - **Documented**: All three artifacts exist
   - **Partially documented**: Some artifacts exist
   - **Undocumented**: No artifacts exist
   - **Potentially stale**: Documented but source files modified after generation timestamp
7. Calculate coverage percentage: (documented components / total components) × 100
8. Report results

**Output format**:

```
Documentation Coverage Report
═══════════════════════════════

Components: 4 total

  ✓ frontend       — Documented (generated 2026-02-08T10:00:00Z)
  ⚠ backend        — Potentially stale (source modified after docs)
  ✗ shared-utils   — Undocumented
  △ data-pipeline  — Partially documented (missing: ai_context)

Coverage: 50% (2/4 fully documented)

Run /codetodocs.run to update documentation.
```

**Error cases**:
- Config missing → report error, suggest `/codetodocs.init`
- No components resolvable → report "no components found"
