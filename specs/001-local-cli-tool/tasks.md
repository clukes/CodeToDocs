# Tasks: CodeToDocs Prompt-Driven Agent Tool

**Input**: Design documents from `/specs/001-local-cli-tool/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Included for the bootstrap installer (Python code with testable logic). Prompt files are tested manually by invoking them in an AI coding agent — no automated tests.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. Note: US0 (Bootstrap Installer) is implemented LAST despite being P0 priority, because it bundles content created by US1–US4.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US0, US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure

- [ ] T001 Create project directory structure per plan.md: `installer/src/codetodocs/`, `installer/src/codetodocs/assets/prompts/`, `installer/src/codetodocs/assets/templates/`, `installer/tests/fixtures/`, `.github/prompts/`, `.codetodocs/templates/`
- [ ] T002 Create pyproject.toml with hatchling build backend, `codetodocs` entry point, Python ≥3.10, and project metadata in `installer/pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Default templates referenced by ALL prompt files and bundled by the installer. Must be complete before any user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until these templates exist

- [ ] T003 [P] Create technical documentation template with sections: Purpose, Architecture, Setup/Installation, Running, Configuration, Key APIs, Edge Cases, Dependencies in `.codetodocs/templates/technical_doc.md`
- [ ] T004 [P] Create product documentation template with sections: Purpose, Features, Business Rules, User Impact, Configuration/Policies in `.codetodocs/templates/product_doc.md`
- [ ] T005 [P] Create AI context JSON template following the schema contract (with `_codetodocs`, `component`, `modules`, `api`, `types`, `configuration`, `dependencies`, `metrics` fields) in `.codetodocs/templates/ai_context.json`

**Checkpoint**: All three templates validated against contracts/ai-context-schema.md and data-model.md entity definitions

---

## Phase 3: User Story 1 — Repository Initialization (Priority: P1) 🎯 MVP

**Goal**: The `/codetodocs.init` prompt command scaffolds `.codetodocs/` with config.yaml and templates so the tool is ready to generate documentation.

**Independent Test**: Invoke `/codetodocs.init` in a repository with no `.codetodocs/` directory and verify that config.yaml (with `output_dir: docs/`, `target_branch: main`) and all three template files are created. Invoke again and verify it reports "already initialized" without overwriting.

### Implementation for User Story 1

- [ ] T006 [US1] Create `codetodocs.init.prompt.md` with YAML frontmatter (`description`, `agent: agent`), purpose section, prerequisite check, step-by-step scaffold workflow (check `.codetodocs/` existence → create config.yaml with defaults → create templates → report summary), idempotency guard, and error handling per contracts/prompt-commands.md in `.github/prompts/codetodocs.init.prompt.md`
- [ ] T007 [P] [US1] Create default `config.yaml` for development/testing with `output_dir: docs/` and `target_branch: main` per contracts/config-schema.md in `.codetodocs/config.yaml`

**Checkpoint**: `/codetodocs.init` can be invoked in Copilot on a test repo. Config and templates are created. Re-running reports "already initialized."

---

## Phase 4: User Story 2 — Full-Scan Documentation Generation (Priority: P2)

**Goal**: The `/codetodocs.run` prompt command generates technical, product, and AI context documentation for all components in the repository from scratch.

**Independent Test**: Invoke `/codetodocs.run` on an initialized repository with source files and no existing docs. Verify three artifacts per component (or one set for the whole repo). Verify outputs conform to templates and include the `<!-- CodeToDocs | ... -->` header marker.

### Implementation for User Story 2

- [ ] T008 [US2] Create `codetodocs.run.prompt.md` with YAML frontmatter, full-scan mode instructions: read config.yaml → resolve components (or single implicit component using repo name per FR-023) → detect overlapping component paths and emit a configuration warning (assign file to first matching component) → group unmatched files into implicit "uncategorized" component when components are defined → discover source files per component (respecting .gitignore and .codetodocsignore per FR-006/FR-007; report invalid .codetodocsignore patterns and continue with valid ones) → read templates → generate tri-audience documentation per component → prepend HTML comment header marker with component name and ISO 8601 timestamp per FR-027 → write to `{output_dir}/technical/{component}.md`, `{output_dir}/product/{component}.md`, `{output_dir}/ai/{component}.json` → handle custom documents per FR-025 → report summary per FR-013 → self-correction validation per FR-009 → component-level error isolation per FR-010, in `.github/prompts/codetodocs.run.prompt.md`

**T008 FR Verification Checklist** (validate during implementation):
- [ ] FR-002: Run prompt generates/updates docs
- [ ] FR-003: Three artifacts per component
- [ ] FR-004: Reads all source files in component
- [ ] FR-006: Respects .gitignore
- [ ] FR-007: Respects .codetodocsignore (including invalid pattern handling)
- [ ] FR-009: Self-correction on invalid output
- [ ] FR-010: Continues on component failure
- [ ] FR-013: Reports progress and results
- [ ] FR-023: Single-component repo uses repo name
- [ ] FR-024: Honors components list from config
- [ ] FR-025: Generates custom documents
- [ ] FR-027: Prepends header marker with metadata
- [ ] Overlapping component path detection + warning
- [ ] Uncategorized component for unmatched files

**Checkpoint**: `/codetodocs.run` generates 3 documentation files for a test repo. Outputs contain correct header markers and conform to template structure.

---

## Phase 5: User Story 3 — Incremental Documentation Update (Priority: P3)

**Goal**: The `/codetodocs.run` prompt command detects changes via Git diff and updates only affected components' documentation.

**Independent Test**: Make source changes on a feature branch, invoke `/codetodocs.run`, verify only changed components' docs are updated. Verify unchanged components' docs are untouched. Verify deleted component directory produces orphaned header.

### Implementation for User Story 3

- [ ] T009 [US3] Extend `codetodocs.run.prompt.md` with incremental mode: detect existing docs to determine mode → run `git diff {target_branch}...HEAD --name-only` to find changed files → map changed files to components → for trivial-only changes, skip component and report per FR-014 → for deleted files within a component, regenerate docs → for deleted component directory, prepend `<!-- ORPHANED: Component directory deleted -->` header → read full component files (context) plus diff (focus) for affected components → regenerate only affected components' docs → report incremental summary, in `.github/prompts/codetodocs.run.prompt.md`

**Checkpoint**: On a branch with changes, `/codetodocs.run` updates only the affected component's docs. Unchanged component docs have identical timestamps.

---

## Phase 6: User Story 4 — Documentation Coverage Status (Priority: P4)

**Goal**: The `/codetodocs.status` prompt command reports which components have documentation, which are missing, and which are potentially stale.

**Independent Test**: Invoke `/codetodocs.status` on a repository with partial documentation. Verify the report lists documented, undocumented, partially documented, and potentially stale components with coverage percentage.

### Implementation for User Story 4

- [ ] T010 [US4] Create `codetodocs.status.prompt.md` with YAML frontmatter, coverage reporting workflow: read config.yaml → resolve components → check `{output_dir}/technical/`, `{output_dir}/product/`, `{output_dir}/ai/` for each component → parse `<!-- CodeToDocs | ... | Generated: {timestamp} -->` header from existing docs → compare generation timestamp against source file modification times for staleness → classify each component (Documented / Partially documented / Undocumented / Potentially stale) → calculate coverage percentage → format and display report per contracts/prompt-commands.md output format, in `.github/prompts/codetodocs.status.prompt.md`

**Checkpoint**: `/codetodocs.status` produces an accurate coverage report matching the contract output format.

---

## Phase 7: User Story 0 — Bootstrap Installer (Priority: P0)

**Goal**: The `uvx codetodocs` command copies all prompt files and templates into a user's repository with idempotent behavior.

**Independent Test**: Run `uvx codetodocs` (or `python -m codetodocs`) in a test Git repo with no CodeToDocs files. Verify 6 files are copied. Run again and verify all 6 are skipped. Verify non-Git-repo warning.

**Note**: Implemented after US1–US4 because the installer bundles prompt files and templates created in those phases.

### Implementation for User Story 0

- [ ] T011 [P] [US0] Create package `__init__.py` with `__version__` constant in `installer/src/codetodocs/__init__.py` and `__main__.py` entry point (calls `cli.main()`) in `installer/src/codetodocs/__main__.py`
- [ ] T012 [US0] Implement idempotent file-copy module with asset manifest (6 source→target mappings per data-model.md), Git repo detection, `--force` override, `--dry-run` simulation, and summary reporting in `installer/src/codetodocs/copy.py`
- [ ] T013 [US0] Implement CLI argument parser with `--target-dir`, `--force`, `--dry-run`, `--version`, `--help` flags, output formatting (copied/skipped lists, count summary, next-step message), and exit codes (0=success, 1=error) per contracts/cli.md in `installer/src/codetodocs/cli.py`
- [ ] T014 [US0] Bundle all prompt files and templates as package assets: copy `.github/prompts/codetodocs.*.prompt.md` to `installer/src/codetodocs/assets/prompts/` and `.codetodocs/templates/*` to `installer/src/codetodocs/assets/templates/`, add `__init__.py` files to each assets subdirectory for `importlib.resources` traversal
- [ ] T015 [US0] Create installer tests: test idempotent copy (fresh + re-run), test `--force` overwrite, test `--dry-run` output, test non-Git-repo warning, test `--version` flag in `installer/tests/test_copy.py` and `installer/tests/test_cli.py`

**Checkpoint**: `cd /tmp/test-repo && git init && python -m codetodocs` copies 6 files. Re-running skips all 6. `--dry-run` shows plan without copying. `--force` overwrites.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and cleanup across all user stories

- [ ] T016 [P] Create README.md with project overview, installation (`uvx codetodocs`), usage workflow (`/codetodocs.init` → `/codetodocs.run` → `/codetodocs.status`), configuration reference, component setup example, and custom documents example
- [ ] T017 Verify all three prompt files are under 500 lines and 10K characters per research.md size constraints; refactor any that exceed limits
- [ ] T018 Run quickstart.md validation: execute full end-to-end workflow (install → init → run → status) on a test repository and verify all outputs
- [ ] T019 Invoke all three prompt commands (`/codetodocs.init`, `/codetodocs.run`, `/codetodocs.status`) in a second AI coding agent platform (e.g., Cursor or Windsurf) on the same test repository used in T018 and verify consistent output structure across platforms per FR-011 and SC-005

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) for directory structure — BLOCKS all user stories
- **US1 Init (Phase 3)**: Depends on Foundational (Phase 2) for templates
- **US2 Full-Scan (Phase 4)**: Depends on Foundational (Phase 2) for templates; independent of US1
- **US3 Incremental (Phase 5)**: Depends on US2 (Phase 4) — extends the same run prompt file
- **US4 Status (Phase 6)**: Depends on Foundational (Phase 2); independent of US1/US2/US3
- **US0 Installer (Phase 7)**: Depends on ALL prompt files and templates (Phases 2–6) — bundles them
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Depends on Foundational only — can start after templates exist
- **US2 (P2)**: Depends on Foundational only — can start in parallel with US1
- **US3 (P3)**: Depends on US2 — extends the same `.github/prompts/codetodocs.run.prompt.md` file
- **US4 (P4)**: Depends on Foundational only — can start in parallel with US1 and US2
- **US0 (P0)**: Depends on US1, US2, US3, US4 — bundles all content as installer assets

### Within Each User Story

- Prompt files reference templates (created in Foundational)
- Init prompt can be tested independently after creation
- Run prompt (full-scan) can be tested independently after creation
- Run prompt (incremental) extends full-scan — must be tested on a branch with changes
- Status prompt can be tested independently on a repo with partial docs
- Installer is testable only after all assets are bundled

### Parallel Opportunities

- T003, T004, T005 (all 3 templates) can run in parallel
- T006 and T007 (init prompt + config.yaml) can run in parallel
- T006 (US1), T008 (US2), T010 (US4) can all run in parallel after Foundational
- T011 (package init) can run in parallel with other US0 tasks
- T016 (README) can run in parallel with T017/T018

---

## Parallel Example: After Foundational Phase

```bash
# After templates are created, these can all start in parallel:
Task T006: "Create codetodocs.init.prompt.md"         # US1
Task T008: "Create codetodocs.run.prompt.md (full-scan)" # US2
Task T010: "Create codetodocs.status.prompt.md"        # US4

# After T008 completes:
Task T009: "Extend codetodocs.run.prompt.md (incremental)" # US3

# After ALL prompt files complete:
Task T011-T015: "Bootstrap installer tasks"            # US0
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (3 templates)
3. Complete Phase 3: US1 — Init prompt
4. Complete Phase 4: US2 — Run prompt (full-scan)
5. **STOP and VALIDATE**: Test init + run on a real repository. User can generate docs.

### Incremental Delivery

1. Setup + Foundational → Templates ready
2. Add US1 (Init) → User can scaffold config ✓
3. Add US2 (Full-Scan) → User can generate docs from scratch ✓ (MVP!)
4. Add US3 (Incremental) → User can update docs incrementally ✓
5. Add US4 (Status) → User can check coverage ✓
6. Add US0 (Installer) → One-command install for new users ✓
7. Polish → README, validation, refinement

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (Init prompt) + US3 (Incremental — after US2)
   - Developer B: US2 (Run prompt — full-scan)
   - Developer C: US4 (Status prompt)
3. After all prompts: anyone can do US0 (Installer)

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- US0 is P0 (highest user-facing priority) but implemented last because it bundles content from US1–US4
- Prompt files are ≤500 lines / ≤10K chars (Windsurf hard limit)
- Templates are referenced externally from prompts, not embedded inline
- All generated docs include `<!-- CodeToDocs | Component: {name} | Generated: {timestamp} -->` header marker
- For JSON docs, use `_codetodocs` metadata object instead of HTML comment
- Commit after each task or logical group
- Stop at any checkpoint to validate the story independently
