# Product Requirements Document (PRD)

| **Project Name** | **CodeToDocs** |
| :--- | :--- |
| **Version** | 2.0 (Prompt-Driven) |
| **Status** | Draft |
| **Type** | Developer Tool / Agent Prompts |
| **Implementation** | Prompt files (Markdown) — no compiled code |
| **License** | Open Source (MIT/Apache 2.0) |

---

## 1. Executive Summary
**CodeToDocs** is an open-source, prompt-driven tool designed to solve the "stale documentation" problem in modern software development. It automates the maintenance of documentation by analyzing **Git diffs** and using AI coding agents (GitHub Copilot, Cursor, etc.) to generate updates.

The tool is distributed as a **set of prompt files** (`.md`) that are copied into any repository — zero compiled code, zero build step. A lightweight bootstrap installer automates copying these files into any repo with a single command — installed directly from GitHub source. It follows the same pattern as SpecKit: agent prompt files that orchestrate documentation generation through the AI assistant already available in the developer's editor.

---

## 2. Purpose & Audiences
The primary purpose is to provide comprehensive, auto-updating documentation for a repository. This documentation serves a variety of audiences with distinct needs:

1.  **New Developers:** Onboarding and understanding code changes quickly.
2.  **Existing Developers:** Keeping up-to-date with changes and the current state of the codebase.
3.  **AI Agents:** Providing structured context for tools like GitHub Copilot, Cursor, and future AI assistants (RAG-optimized).
4.  **Product Managers/Stakeholders:** High-level summaries of the repository and changes without overwhelming technical details.
5.  **Open Source Contributors:** Clear documentation to encourage contributions and reduce friction.

---

## 3. User Experience (UX) Goals
* **One-Command Setup:** A user must be able to install the bootstrap CLI from GitHub source and run `codetodocs` in any repo to copy all prompt files and templates, then invoke `/codetodocs.init` to configure.
* **Manual Control:** The tool does **not** run automatically in the background. It is triggered manually by the developer via a specific agent command (e.g., `/codetodocs.run`).
* **Native Agent Integration:** The tool IS an agent command — no separate binary, no bridge layer. It works wherever the developer's AI assistant works (VS Code + Copilot, Cursor, etc.).

---

## 4. Core Functional Requirements

### 4.1. Initialization (`/codetodocs.init` command)
* **Goal:** Establish the configuration and templates for the repository.
* **Behavior:**
    * Check for the existence of `.codetodocs/`.
    * **Create Templates:** Write default templates (Technical Markdown, Product Markdown, AI JSON) into `.codetodocs/templates/` to allow user customization.
    * **Setup:** Create `.codetodocs/config.yaml` with sensible defaults.
* **UX:** The agent confirms each step and reports completion with a summary of created files.

### 4.2. Git Integration
* **Diff Analysis:** The agent must identify changed files between `HEAD` and a target branch (default: `main`) using Git commands or agent tools.
* **Context Awareness:**
    * It must read the **full content** of the changed file (for context) and the **diff** (for focus).
    * It must respect `.gitignore` and a custom `.codetodocsignore`.

### 4.3. Documentation Outputs (The "Tri-Audience" Strategy)

**Core Requirement:** Each **component** (or the entire repository if not a monorepo) generates three distinct documentation artifacts to serve different stakeholders. Documentation is at the component level, not per-file.

**Component Definition:**
* A **component** is a logical unit of the codebase — a service, library, app, or module.
* For simple repositories, the entire repo is treated as a single component.
* For monorepos, users define multiple components (e.g., `frontend`, `backend`, `shared-lib`).
* Components are specified in `.codetodocs/config.yaml`.

**Trigger & Processing:**
* **Input:** All source files within the component + Git Diff (if updating).
* **Processing:** The agent reads the component's codebase holistically, applies the prompt instructions, and generates one set of docs per component.

**Output 1: Technical Docs (Target: Engineers)**
* **Location:** `docs/technical/{component}.md` (default) or custom path
* **Focus:** Implementation details, "How to work with this component."
* **Content:**
    * **Purpose:** What this component does and why it exists.
    * **Architecture:** High-level structure, key modules, and data flow.
    * **Setup & Installation:** How to set up the development environment.
    * **Running:** How to run, build, and test the component.
    * **Configuration:** Environment variables, config files, and settings.
    * **Key APIs/Functions:** Technical explanation of the main interfaces.
    * **Edge Cases:** Known limitations, error handling, and gotchas.
    * **Dependencies:** External libraries and services this component relies on.

**Output 2: Product Docs (Target: PMs/Stakeholders)**
* **Location:** `docs/product/{component}.md` (default) or custom path
* **Focus:** Business value, "What does this component do for the user/business?"
* **Content:**
    * **Purpose:** Plain-English description of functionality.
    * **Features:** Key capabilities and user-facing functionality.
    * **Business Rules:** Policies and logic that impact the business (e.g., "Users must be verified to see X").
    * **User Impact:** How this component affects the end-user experience.
    * **Configuration & Policies:** Business-relevant settings and constraints.

**Output 3: AI Context (Target: Agents/RAG)**
* **Location:** `docs/ai/{component}.yaml` (default) or custom path
* **Focus:** Machine-readable structural facts for the entire component.
* **Content:**
    * Component purpose and responsibilities.
    * Key modules, classes, and their relationships.
    * Public API signatures and types.
    * Configuration schema.

### 4.4. Configuration
* **File:** `.codetodocs/config.yaml`.
* **Core Settings:**
    * `output_dir`: (default: `docs/`) — Base directory for generated documentation.
    * `target_branch`: (default: `main`) — Branch to diff against for incremental updates.

* **Component Definition:**
    * `components`: A list defining the logical components of the repository.
    * Each component specifies:
        * `name`: Identifier used in output filenames.
        * `paths`: List of directory/file paths that belong to this component.
        * `description`: Brief description of the component's purpose.
    * If `components` is omitted or empty, the entire repository is treated as a single component named after the repo.

* **Custom Documents:**
    * `documents`: Optional list of additional document definitions beyond the three defaults.
    * Each document specifies:
        * `name`: Document identifier.
        * `template`: Path to a custom template file.
        * `output`: Custom output path (overrides default location).
        * `audience`: Target audience description.
    * Users can also override the output paths for the default documents (technical, product, ai) per component.

**Example Configuration:**
```yaml
# .codetodocs/config.yaml
output_dir: docs/
target_branch: main

# Component definitions (omit for single-component repos)
components:
  - name: frontend
    paths:
      - apps/web/
      - packages/ui/
    description: React web application and shared UI components
  - name: backend
    paths:
      - apps/api/
      - packages/db/
    description: Node.js API server and database layer
  - name: shared
    paths:
      - packages/common/
    description: Shared utilities and types

# Optional: Custom documents beyond the defaults
documents:
  - name: runbook
    template: .codetodocs/templates/runbook.md
    output: docs/operations/{component}-runbook.md
    audience: SRE/Operations team
```

---

## 5. Technical Architecture

### 5.1. Stack
* **Implementation:** Prompt files (Markdown) — no compiled language.
* **Bootstrap Installer:** Lightweight Python package (installed from GitHub source via `uvx` or `pip`) that copies files into the target repo. The installer is a thin file-copy script — it does not run at documentation-generation time.
* **Execution Environment:** Any AI coding agent (GitHub Copilot, Cursor, Windsurf, etc.).
* **Git:** Agent's built-in Git tools or terminal `git` commands.
* **LLM:** The agent's own model — no separate API keys or LLM client needed.
* **Inspiration:** SpecKit (`.github/prompts/speckit.*.prompt.md`).

### 5.2. File Structure

**Project Layout (CodeToDocs itself):**
```text
codetodocs/
├── installer/
│   ├── pyproject.toml               # Python package config (for uvx)
│   ├── package.json                  # Node package config (for npx)
│   └── codetodocs_install.py         # Installer script: copies files into target repo
├── files/                            # Source files that get copied into user repos
│   ├── .github/
│   │   └── prompts/
│   │       ├── codetodocs.init.prompt.md
│   │       ├── codetodocs.run.prompt.md
│   │       └── codetodocs.status.prompt.md
│   └── .codetodocs/
│       └── templates/
│           ├── technical_doc.md
│           ├── product_doc.md
│           └── ai_context.yaml
└── docs/
    └── PRD.md
```

**Generated Documentation Layout (User Repo after init + run):**

*Single-component repository:*
```text
my-repo/
├── .github/
│   └── prompts/
│       ├── codetodocs.init.prompt.md
│       ├── codetodocs.run.prompt.md
│       └── codetodocs.status.prompt.md
├── .codetodocs/
│   ├── config.yaml
│   └── templates/
│       ├── technical_doc.md
│       ├── product_doc.md
│       └── ai_context.yaml
├── docs/
│   ├── technical/
│   │   └── my-repo.md       # Single technical doc for entire repo
│   ├── product/
│   │   └── my-repo.md       # Single product doc for entire repo
│   └── ai/
│       └── my-repo.yaml     # Single AI context for entire repo
```

*Multi-component (monorepo) repository:*
```text
my-monorepo/
├── .github/
│   └── prompts/
│       └── codetodocs.*.prompt.md
├── .codetodocs/
│   ├── config.yaml          # Defines components: frontend, backend, shared
│   └── templates/
│       └── ...
├── docs/
│   ├── technical/
│   │   ├── frontend.md      # Technical docs for frontend component
│   │   ├── backend.md       # Technical docs for backend component
│   │   └── shared.md        # Technical docs for shared component
│   ├── product/
│   │   ├── frontend.md
│   │   ├── backend.md
│   │   └── shared.md
│   └── ai/
│       ├── frontend.yaml
│       ├── backend.yaml
│       └── shared.yaml
```

## 6. Non-Functional Requirements
1.  **Portability:** Must work with any AI coding agent that supports prompt files (VS Code + Copilot, Cursor, etc.).
2.  **Security:** No API keys are managed by this tool — the agent's own authentication handles LLM access.
3.  **Determinism:** Prompt instructions MUST be specific enough to produce consistent output structure across different agent models and invocations.
4.  **One-Command Install:** The installer must copy all files into the current repo in under 5 seconds. The installer must not modify any existing files.
5.  **Simplicity:** The installer is a thin file-copy script. The actual documentation logic lives entirely in prompt files.

---

## 7. Milestones

### Phase 0: The "Installer" (Bootstrap)
* [ ] Python package with `pyproject.toml` — installed from GitHub source (not published to PyPI).
* [ ] Installer script that copies prompt files + templates into the current repo.
* [ ] Idempotent: skip files that already exist, never overwrite.

### Phase 1: The "Constitution" (MVP)
* [ ] Prompt file structure and `codetodocs.init.prompt.md`.
* [ ] Default templates (technical, product, AI context).
* [ ] `config.yaml` schema and defaults.

### Phase 2: The "Crawler" (Zero State)
* [ ] `codetodocs.run.prompt.md` for full-scan documentation.
* [ ] File discovery logic in prompt (respecting `.gitignore` + `.codetodocsignore`).
* [ ] Component detection and per-component tri-audience generation instructions.
* [ ] Support for both single-component repos and monorepos with multiple components.

### Phase 3: The "Updater" (Incremental)
* [ ] Git diff detection logic in run prompt.
* [ ] Incremental update mode: regenerate docs only for components with changed files.
* [ ] Trivial change detection guidance (skip component regeneration for trivial-only changes).

### Phase 4: Polish
* [ ] `codetodocs.status.prompt.md` for documentation coverage reporting.
* [ ] Refinement of prompt instructions for output consistency.
* [ ] User documentation and README.