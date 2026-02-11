# Feature Specification: CodeToDocs Prompt-Driven Agent Tool

**Feature Branch**: `001-local-cli-tool`  
**Created**: 2026-02-09  
**Status**: Draft  
**Input**: User description: "Build the CodeToDocs prompt-driven agent tool with init and run commands, Git diff analysis, and tri-audience documentation generation — implemented entirely as prompt files with no compiled code."

## User Scenarios & Testing *(mandatory)*

### User Story 0 — One-Command Bootstrap Install (Priority: P0)

A developer discovers CodeToDocs and wants to add it to their existing repository. They run a single command (`uvx codetodocs`) which copies all prompt files and templates into their repo, so they can immediately invoke `/codetodocs.init`.

**Why this priority**: Without the files in the repo, no agent commands can be invoked. The installer eliminates the manual file-copy step and is the first thing a new user does.

**Independent Test**: Run the installer command in a Git repository with no CodeToDocs files and verify that all expected prompt files and template files are copied into the correct locations.

**Acceptance Scenarios**:

1. **Given** a Git repository with no CodeToDocs files, **When** the user runs `uvx codetodocs`, **Then** the prompt files are copied to `.github/prompts/codetodocs.*.prompt.md` and templates are copied to `.codetodocs/templates/`.
2. **Given** a repository that already has some or all CodeToDocs files, **When** the user runs the installer, **Then** existing files are NOT overwritten, and the installer reports which files were skipped.
3. **Given** the installer completes, **When** the user inspects the output, **Then** it lists all files copied and instructs the user to run `/codetodocs.init` next.
4. **Given** the current directory is not a Git repository, **When** the user runs the installer, **Then** it prints a warning but still copies the files (Git is needed at documentation-generation time, not at install time).

---

### User Story 1 — Repository Initialization (Priority: P1)

A developer copies the CodeToDocs prompt files into their repository and invokes the init command via their AI coding assistant. The agent scaffolds configuration and templates so that the tool is ready to generate documentation on subsequent runs.

**Why this priority**: Without initialization there is no configuration, no templates, and no output directories. Every other command depends on this scaffolding existing first.

**Independent Test**: Invoke the init command in a repository with no `.codetodocs/` directory and verify that the expected directory structure, configuration file, and template files are created with correct defaults.

**Acceptance Scenarios**:

1. **Given** a Git repository with the CodeToDocs prompt files in `.github/prompts/` but no `.codetodocs/` directory, **When** the user invokes `/codetodocs.init`, **Then** a `.codetodocs/` directory is created containing `config.yaml` with default values (`output_dir: docs/`, `target_branch: main`) and a `templates/` subdirectory containing the default technical, product, and AI context template files.
2. **Given** a Git repository that already has a `.codetodocs/` directory with existing configuration, **When** the user invokes `/codetodocs.init`, **Then** the agent reports that the project is already initialized and does not overwrite existing files.
3. **Given** the init command completes successfully, **When** the user inspects the agent output, **Then** it includes a summary of all created files and a brief explanation of how to run documentation generation.

---

### User Story 2 — Full-Scan Documentation Generation (Priority: P2)

A developer has just initialized CodeToDocs in their repository and wants to generate documentation for the entire codebase from scratch ("zero state"). They invoke the run command and the agent produces technical, product, and AI context docs for each component (or the entire repo if it's not a monorepo).

**Why this priority**: Full-scan is the first real value delivery — it creates the initial documentation baseline. Without it, incremental updates have no foundation to build upon.

**Independent Test**: Invoke the run command on an initialized repository with several source files and verify that three documentation artifacts are created per component (or one set for the whole repo if no components are defined).

**Acceptance Scenarios**:

1. **Given** an initialized repository with source files and no `components` defined in config, **When** the user invokes `/codetodocs.run`, **Then** the agent creates three artifacts for the entire repo: `docs/technical/{repo-name}.md`, `docs/product/{repo-name}.md`, and `docs/ai/{repo-name}.yaml`.
2. **Given** an initialized repository with multiple `components` defined in config (e.g., frontend, backend), **When** the user invokes `/codetodocs.run`, **Then** the agent creates three artifacts per component: `docs/technical/{component}.md`, `docs/product/{component}.md`, and `docs/ai/{component}.yaml`.
3. **Given** the repository contains files matching patterns in `.gitignore` or `.codetodocsignore`, **When** documentation generation runs, **Then** those files are excluded from processing.
4. **Given** a component is processed, **When** the agent generates documentation, **Then** the technical doc contains purpose, architecture, setup/installation, running instructions, configuration, key APIs, edge cases, and dependencies; the product doc contains purpose, features, business rules, user impact, and configuration/policies; and the AI context YAML contains component structure, key modules, public API signatures, and configuration schema.
5. **Given** the generation run encounters issues with a component, **When** the agent processes that component, **Then** it reports the issue and continues processing remaining components.
6. **Given** the generation run completes, **When** the agent reports results, **Then** a summary is displayed listing successful components, skipped components, and any components with errors.
7. **Given** custom `documents` are defined in config, **When** the user invokes `/codetodocs.run`, **Then** the agent also generates those custom documents using the specified templates and output paths.

---

### User Story 3 — Incremental Documentation Update (Priority: P3)

A developer has an existing documentation baseline and has made changes to source files on a feature branch. They invoke the run command and the agent updates only the documentation for components that have changed files, using the Git diff to focus on what actually changed.

**Why this priority**: Incremental updates are the core ongoing value — they keep documentation in sync with code changes without regenerating everything. However, they depend on the full-scan baseline (P2) existing first.

**Independent Test**: Make changes to a tracked source file on a branch, invoke the run command, and verify that only documentation for the affected component is updated while unchanged components' docs remain untouched.

**Acceptance Scenarios**:

1. **Given** an initialized repository with existing documentation AND changes on the current branch relative to the target branch, **When** the user invokes `/codetodocs.run`, **Then** the agent identifies which components contain changed files and regenerates documentation only for those components.
2. **Given** a component with changed files and existing documentation, **When** the agent processes it, **Then** it reads the full component (for context) and the diff (for focus), and the resulting documentation reflects the changes.
3. **Given** a component where all changes are trivial (comment-only or formatting-only edits), **When** the agent analyzes the diff, **Then** it skips documentation regeneration for that component and reports it as "skipped (trivial changes only)."
4. **Given** a file was deleted on the current branch but was not the last file in its component, **When** the agent processes the diff, **Then** the component's documentation is regenerated to reflect the removal.
5. **Given** an entire component's directory was deleted, **When** the agent processes the diff, **Then** the corresponding documentation files are flagged for removal by prepending a warning header (e.g., `<!-- ORPHANED: Component directory deleted -->`), but NOT automatically deleted.

---

### User Story 4 — Documentation Coverage Status (Priority: P4)

A developer wants to see which components in their repository have documentation and which are missing or stale. They invoke the status command to get a coverage report.

**Why this priority**: Visibility into documentation gaps helps developers prioritize which components to document next. However, it depends on the generation workflow (P2/P3) existing first.

**Independent Test**: Invoke the status command on a repository with partial documentation and verify that the report accurately lists covered, missing, and potentially stale components.

**Acceptance Scenarios**:

1. **Given** a repository with some components documented and some not, **When** the user invokes `/codetodocs.status`, **Then** the agent reports a list of documented components, undocumented components, and documentation coverage percentage.
2. **Given** a documented component that has been modified since its documentation was last generated, **When** the status command runs, **Then** the component is flagged as "potentially stale" by comparing the embedded generation timestamp against source file modification times.

---

### Edge Cases

- What happens when the repository has no commits yet? The agent should report a clear error indicating that at least one commit is required for diff-based operations.
- What happens when the target branch specified in config does not exist? The agent should report an error naming the missing branch and suggesting the user check the `target_branch` setting.
- What happens when a source file is binary (images, compiled assets)? The agent should detect non-text files and skip them, reporting them as skipped.
- What happens when the repository is extremely large (thousands of files)? The prompt should instruct the agent to process components (not individual files), which bounds the cognitive load per generation.
- What happens when the configured output directory already contains manually written documentation? The agent only overwrites files it previously generated (identifiable by the `<!-- CodeToDocs | ... -->` HTML comment header) and leaves other files untouched.
- What happens when the `.codetodocsignore` file has invalid patterns? The agent should report which patterns are invalid and continue processing with the valid patterns.
- What happens when the prompt files are missing from `.github/prompts/`? The agent cannot be invoked — the user should run `uvx codetodocs` to install the prompt files, or copy them manually. This is a prerequisite, not a runtime error.
- What happens when a file belongs to multiple components (overlapping paths)? The agent should report a configuration warning and assign the file to the first matching component.
- What happens when `components` is defined but a file doesn't match any component path? The agent includes the file in a default "uncategorized" component. Files explicitly excluded by `.gitignore` or `.codetodocsignore` do not trigger warnings.
- What happens when a custom document template is missing? The agent should report the missing template and skip generating that custom document.
- What happens when a user wants different output paths for different components? Users can override output paths per component in the `documents` config section.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a `/codetodocs.init` prompt command that instructs the agent to scaffold a `.codetodocs/` directory containing `config.yaml` and a `templates/` subdirectory with default template files.
- **FR-002**: System MUST provide a `/codetodocs.run` prompt command that instructs the agent to generate or update documentation for components in the repository.
- **FR-003**: System MUST produce three documentation artifacts per **component** (not per file): a technical Markdown doc, a product Markdown doc, and an AI context JSON file.
- **FR-004**: The run prompt MUST instruct the agent to read all source files within a component when generating documentation for that component.
- **FR-005**: The run prompt MUST instruct the agent to detect changed files by comparing HEAD against the configured target branch using Git diff, then determine which components are affected.
- **FR-006**: The run prompt MUST instruct the agent to respect `.gitignore` rules when determining which files to process.
- **FR-007**: The run prompt MUST instruct the agent to respect a `.codetodocsignore` file (if present) for additional exclusion rules beyond `.gitignore`.
- **FR-008**: Prompt files MUST NOT require any API keys, environment variables, or external credentials — the agent's own authentication handles LLM access.
- **FR-009**: The run prompt MUST instruct the agent to self-correct if generated output does not conform to the template structure.
- **FR-010**: The run prompt MUST instruct the agent to continue processing remaining components when documentation generation fails for an individual component, and report all issues at the end.
- **FR-011**: System MUST work with any AI coding agent that supports prompt files (GitHub Copilot, Cursor, Windsurf, etc.).
- **FR-012**: The init prompt MUST create a `config.yaml` supporting these settings: `output_dir`, `target_branch`, `components`, and `documents`.
- **FR-013**: The run prompt MUST instruct the agent to report progress and results (components processed, components skipped, errors encountered).
- **FR-014**: The run prompt SHOULD instruct the agent to use semantic analysis to determine whether changes are trivial (not warranting documentation regeneration) during incremental updates at the component level — no strict rule is imposed; the agent decides based on whether changes affect documented behavior.
- **FR-015**: Default template files MUST be included in the prompt instructions or referenced from a known location so the agent can create them during initialization.
- **FR-016**: The init prompt MUST NOT overwrite an existing `.codetodocs/` directory when invoked on an already-initialized repository.
- **FR-017**: The AI context JSON template MUST define a schema containing component purpose, key modules, public API signatures, types, configuration schema, and complexity metrics.
- **FR-018**: System MUST provide a `/codetodocs.status` prompt command that instructs the agent to report documentation coverage (documented components, undocumented components, potentially stale components).
- **FR-019**: System MUST provide a bootstrap installer runnable via `uvx codetodocs` (Python) that copies all prompt files and templates into the current repository. An `npx codetodocs` (Node) alternative MAY be added in a future iteration.
- **FR-020**: The bootstrap installer MUST be idempotent — it MUST NOT overwrite or modify any existing files in the target repository.
- **FR-021**: The bootstrap installer MUST report which files were copied and which were skipped (already present).
- **FR-023**: When no `components` are defined in config, the system MUST treat the entire repository as a single component using the repository name.
- **FR-024**: The config MUST support a `components` list where each component specifies `name`, `paths`, and `description`.
- **FR-025**: The config MUST support a `documents` list for defining custom documents beyond the three defaults, each with `name`, `template`, `output`, and `audience`.
- **FR-026**: *(Removed — the `documents` configuration in FR-025 allows users to define custom documents with arbitrary output paths. For the three default document types, the output path is derived from `output_dir`. If a user needs a different path for a default type, they can redefine it as a custom document.)*
- **FR-027**: Generated documentation files MUST include an HTML comment header with structured metadata (component name, generation timestamp in ISO 8601 format) to identify CodeToDocs-generated files and enable staleness detection. Example: `<!-- CodeToDocs | Component: frontend | Generated: 2026-02-09T14:30:00Z -->`. For JSON files, use a `_codetodocs` metadata object.

### Key Entities

- **Source File**: A text-based file tracked by Git in the repository. Attributes: file path, file content, language/type, diff (relative to target branch).
- **Component**: A logical unit of the codebase (service, library, app, or module). Attributes: name, paths (list of directories/files), description. For simple repos, the entire repo is one implicit component.
- **Configuration**: Settings controlling tool behavior. Attributes: output directory path, target branch name, components list, custom documents list. Stored in `.codetodocs/config.yaml`.
- **Documentation Artifact**: A generated output file. Three default types: Technical (Markdown), Product (Markdown), AI Context (JSON). Each is keyed to a specific **component** by component name. Custom documents can also be defined.
- **Template**: A formatting guide defining the structure of each documentation output type. Stored in `.codetodocs/templates/`. User-customizable.
- **Prompt Command**: A `.github/prompts/codetodocs.*.prompt.md` file containing agent instructions for a specific operation (init, run, status).
- **Ignore Rules**: Patterns defining which files to exclude from processing. Sources: `.gitignore` (always respected) and `.codetodocsignore` (optional, additive exclusions).
- **Custom Document**: A user-defined additional document type beyond the three defaults. Attributes: name, template path, output path pattern, target audience.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can go from running a single install command to having a fully initialized configuration by invoking one more agent command (`/codetodocs.init`).
- **SC-002**: For every component processed, exactly three documentation artifacts are produced (technical, product, AI context) with no missing outputs.
- **SC-003**: 90% of documentation generation runs on a typical repository (under 50 source files) produce structurally valid output: Markdown docs contain all section headings defined in the template; AI context JSON passes validation against the schema in `contracts/ai-context-schema.md`.
- **SC-004**: Incremental documentation updates process only components containing changed files, skipping unchanged components entirely.
- **SC-005**: The tool works across at least two different AI coding agent platforms (e.g., GitHub Copilot and Cursor) with consistent results.
- **SC-006**: The tool correctly excludes all files matching `.gitignore` and `.codetodocsignore` patterns, with zero false inclusions.
- **SC-007**: A developer unfamiliar with CodeToDocs can install and run it (`uvx codetodocs` + invoke init + invoke run) within 5 minutes by following the README alone.
- **SC-008**: For monorepos with multiple defined components, documentation is correctly partitioned — each component's docs reflect only that component's code.

## Assumptions

- The user's repository is a valid Git repository with at least one commit.
- The user has an AI coding agent (GitHub Copilot, Cursor, Windsurf, etc.) that supports prompt file invocation.
- Source files are text-based; binary files are out of scope for documentation generation.
- The agent platform provides built-in tools for reading files, running terminal commands (including `git`), and creating/editing files.
- LLM access is handled by the agent platform — no separate API keys or provider configuration is needed.
- Distribution is via a lightweight bootstrap installer (`uvx codetodocs`) that copies files into the repo. Manual file copy is also supported.

## Out of Scope

- GitHub Actions workflow or any CI/CD automation.
- Standalone CLI binary or compiled code of any kind.
- Direct LLM API integration (API keys, provider selection, retry logic).
- Automated background execution, file watchers, or Git hooks.
- Web UI or dashboard for viewing generated documentation.
- Support for editors/environments without AI agent prompt file capabilities.

## Clarifications

### Session 2026-02-09

- Q: What constitutes a "trivial change" for skipping documentation regeneration? → A: Let the agent decide based on semantic analysis (no strict rule).
- Q: How should files not matching any component path be handled? → A: Include in an "uncategorized" component; no warning for explicitly ignored files.
- Q: How should the agent determine when documentation was last generated (for staleness detection)? → A: Embed a timestamp comment in each generated doc.
- Q: What should happen when an entire component's directory is deleted? → A: Flag for removal only (add a warning header to the doc); do not auto-delete.
- Q: What format should the header marker take for identifying CodeToDocs-generated files? → A: HTML comment with structured metadata (invisible when rendered), e.g., `<!-- CodeToDocs | Component: frontend | Generated: 2026-02-09T14:30:00Z -->`.
