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

The tool is distributed as a **set of prompt files** (`.md`) that are copied into any repository — zero compiled code, zero build step. A lightweight bootstrap installer (`uvx codetodocs` or `npx codetodocs`) automates copying these files into any repo with a single command. It follows the same pattern as SpecKit: agent prompt files that orchestrate documentation generation through the AI assistant already available in the developer's editor.

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
* **One-Command Setup:** A user must be able to run `uvx codetodocs` (or `npx codetodocs`) in any repo to copy all prompt files and templates, then invoke `/codetodocs.init` to configure.
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

**Core Requirement:** Every source file processed must generate three distinct artifacts to serve different stakeholders.

**Trigger & Processing:**
* **Input:** Source code content + Git Diff (if updating).
* **Processing:** The agent reads each file, applies the prompt instructions, and generates all three outputs per file.

**Output 1: Technical Docs (Target: Engineers)**
* **Location:** `docs/technical/{filename}.md`
* **Focus:** Implementation details, "How to work with this code."
* **Content:**
    * **Setup/Usage:** How to import or instantiate this module.
    * **Key Functions:** Technical explanation of the main methods.
    * **Edge Cases:** Known limitations or specific error handling logic.
    * **Dependencies:** What external libraries this file relies on.

**Output 2: Product Docs (Target: PMs/Stakeholders)**
* **Location:** `docs/product/{filename}.md`
* **Focus:** Business value, "What does this actually do for the user/business?"
* **Content:**
    * **Feature Summary:** High-level description of functionality in plain English (no code).
    * **Business Rules:** Specific logic that impacts the business (e.g., "Users must be verified to see X").
    * **User Impact:** How changes in this file affect the end-user experience.

**Output 3: AI Context (Target: Agents/RAG)**
* **Location:** `docs/ai/{filename}.json`
* **Focus:** Machine-readable structural facts.
* **Content:**
    * Strict JSON schema containing signatures, types, exports, and complexity scores.

### 4.4. Configuration
* **File:** `.codetodocs/config.yaml`.
* **Settings:**
    * `output_dir`: (default: `docs/`)
    * `target_branch`: (default: `main`)

---

## 5. Technical Architecture

### 5.1. Stack
* **Implementation:** Prompt files (Markdown) — no compiled language.
* **Bootstrap Installer:** Lightweight Python package (via `uvx`) or Node package (via `npx`) that copies files into the target repo. The installer is a thin file-copy script — it does not run at documentation-generation time.
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
│           └── ai_context.json
└── docs/
    └── PRD.md
```

**Generated Documentation Layout (User Repo after init + run):**
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
│       └── ai_context.json
├── docs/
│   ├── technical/       # "How it works"
│   │   ├── auth.md
│   │   └── payment.md
│   ├── product/         # "What it does"
│   │   ├── auth.md
│   │   └── payment.md
│   └── ai/              # "Structure & Facts"
│       ├── auth.json
│       └── payment.json
```

## 6. Non-Functional Requirements
1.  **Portability:** Must work with any AI coding agent that supports prompt files (VS Code + Copilot, Cursor, etc.).
2.  **Security:** No API keys are managed by this tool — the agent's own authentication handles LLM access.
3.  **Determinism:** Prompt instructions MUST be specific enough to produce consistent output structure across different agent models and invocations.
4.  **One-Command Install:** `uvx codetodocs` or `npx codetodocs` must copy all files into the current repo in under 5 seconds. The installer must not modify any existing files.
5.  **Simplicity:** The installer is a thin file-copy script. The actual documentation logic lives entirely in prompt files.

---

## 7. Milestones

### Phase 0: The "Installer" (Bootstrap)
* [ ] Python package with `pyproject.toml` for `uvx codetodocs`.
* [ ] Node package with `package.json` for `npx codetodocs` (optional alternative).
* [ ] Installer script that copies prompt files + templates into the current repo.
* [ ] Idempotent: skip files that already exist, never overwrite.

### Phase 1: The "Constitution" (MVP)
* [ ] Prompt file structure and `codetodocs.init.prompt.md`.
* [ ] Default templates (technical, product, AI context).
* [ ] `config.yaml` schema and defaults.

### Phase 2: The "Crawler" (Zero State)
* [ ] `codetodocs.run.prompt.md` for full-scan documentation.
* [ ] File discovery logic in prompt (respecting `.gitignore` + `.codetodocsignore`).
* [ ] Per-file tri-audience generation instructions.

### Phase 3: The "Updater" (Incremental)
* [ ] Git diff detection logic in run prompt.
* [ ] Incremental update mode: only process changed files.
* [ ] Trivial change detection guidance (skip comment-only / formatting-only).

### Phase 4: Polish
* [ ] `codetodocs.status.prompt.md` for documentation coverage reporting.
* [ ] Refinement of prompt instructions for output consistency.
* [ ] User documentation and README.