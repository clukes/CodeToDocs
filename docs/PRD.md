# Product Requirements Document (PRD)

| **Project Name** | **CodeToDocs** |
| :--- | :--- |
| **Version** | 1.1 (Refined) |
| **Status** | Draft |
| **Type** | Developer Tool / CLI |
| **Language** | Go (Golang) |
| **License** | Open Source (MIT/Apache 2.0) |

---

## 1. Executive Summary
**CodeToDocs** is an open-source, local-first CLI tool designed to solve the "stale documentation" problem in modern software development. It automates the maintenance of documentation by analyzing **Git diffs** and using Large Language Models (LLMs) to generate updates.

The tool is distributed as a **single, static binary** (zero dependencies) to ensure a seamless developer experience.

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
* **Zero-Config Start:** A user must be able to download the binary and run `codetodocs init` to fully configure their repo in < 5 seconds.
* **Manual Control:** The tool does **not** run automatically in the background. It is triggered manually by the developer (`codetodocs run`) or via a specific agent command.
* **Custom Agent Integration:** The tool is designed to be invoked as a distinct capability (e.g., `/codetodocs` or `@codetodocs`), similar to how `/speckit` works. It does not implicitly pollute general chat contexts.

---

## 4. Core Functional Requirements

### 4.1. Initialization (`init` command)
* **Goal:** Establish the "Constitution" of the repository.
* **Behavior:**
    * Check for the existence of `.codetodocs/`.
    * **Eject Templates:** Extract embedded default templates (Human Markdown, AI JSON, Config YAML) into `.codetodocs/templates/` to allow user customization.
    * **Setup:** Initialize the `.codetodocs/config.yaml` with sensible defaults.
* **UX:** Display a spinner during setup and a success checkmark upon completion (using `bubbletea`).
* **Agent Output:** Instead of modifying global instructions, output a success message telling the user how to register the tool as a custom agent or alias (e.g., *"To use with Copilot, add this alias..."*).

### 4.2. Git Integration
* **Diff Analysis:** The tool must identify changed files between `HEAD` and a target branch (default: `main`).
* **Context Awareness:**
    * It must read the **full content** of the changed file (for context) and the **diff** (for focus).
    * It must respect `.gitignore` and a custom `.codetodocsignore`.

### 4.3. Documentation Outputs (The "Tri-Audience" Strategy)

**Core Requirement:** Every source file processed must generate three distinct artifacts to serve different stakeholders.

**Trigger & Processing:**
* **Input:** Source code content + Git Diff (if updating).
* **Optimization:** The system should ideally use a **single LLM call** per file to generate all three outputs simultaneously (using Structured Outputs/JSON Mode) to reduce latency and cost.

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
    * **Business Rules:** specific logic that impacts the business (e.g., "Users must be verified to see X").
    * **User Impact:** How changes in this file affect the end-user experience.

**Output 3: AI Context (Target: Agents/RAG)**
* **Location:** `docs/ai/{filename}.json`
* **Focus:** Machine-readable structural facts.
* **Content:**
    * Strict JSON schema containing signatures, types, exports, and complexity scores.
### 4.4. Configuration
* **File:** `.codetodocs/config.yaml`.
* **Settings:**
    * `provider`: (openai | anthropic | ollama)
    * `model`: (gpt-4o, claude-3.5-sonnet, llama-3)
    * `output_dir`: (default: `docs/`)
    * `target_branch`: (default: `main`)

---

## 5. Technical Architecture

### 5.1. Stack
* **Language:** Go (1.22+) - chosen for speed, type safety, and single-binary distribution.
* **CLI Framework:** `spf13/cobra` (Command routing).
* **Configuration:** `spf13/viper` (YAML/Env parsing).
* **Git:** `go-git/v5` (Native Git implementation; no system git dependency).
* **TUI:** `charmbracelet/lipgloss` (Styling) & `bubbletea` (Interactivity).
* **LLM Client:** Standard `net/http` or `tmc/langchaingo`.

### 5.2. File Structure

**Project Layout:**
```text
codetodocs/
├── cmd/
│   └── root.go          # Entry point (Cobra)
├── internal/
│   ├── config/          # Viper config loader
│   ├── git/             # Diff logic & File reading
│   ├── llm/             # API Client Adapters
│   ├── generator/       # Core Logic (Prompting & File Writing)
│   ├── templates/       # Embedded assets (go:embed)
│   └── tui/             # Lipgloss styles & Spinners
└── templates/           # Raw source files to embed
    ├── technical_doc.md # Template for Engineering docs
    ├── product_doc.md   # Template for PM docs
    ├── ai_context.json  # Template for AI docs
    └── agent_instructions.md
```

**Generated Documentation Layout (User Repo):**
```text
my-repo/
├── .codetodocs/         # Configuration & Templates
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
1.  **Performance:** The CLI must start in < 50ms.
2.  **Portability:** Must compile to Windows (`.exe`), macOS (ARM/Intel), and Linux.
3.  **Security:** API Keys must **never** be stored in `config.yaml`. They must only be read from Environment Variables (`OPENAI_API_KEY`).
4.  **Reliability:** If the LLM returns invalid JSON, the tool must retry automatically (up to 3 times).

---

## 7. Milestones

### Phase 1: The "Constitution" (MVP)
* [ ] Go module setup & CLI skeleton.
* [ ] `init` command (Templates & Config injection).

### Phase 2: The "Crawler" (Zero State)
* [ ] Implement file system walker (respecting `.gitignore`).
* [ ] Create "Full Scan" logic to document the entire repo from scratch.
* [ ] specific "State of the World" LLM prompts (ignoring diffs, focusing on absolute state).

### Phase 3: The "Updater" (Incremental)
* [ ] Implement Git Diff triggers.
* [ ] Create "Comparison Logic": (Old Doc + New Code) -> New Doc.
* [ ] Optimization: Skip LLM calls for trivial changes (comments/formatting).

### Phase 4: Distribution
* [ ] GitHub Action (Dockerfile).
* [ ] Homebrew Tap.