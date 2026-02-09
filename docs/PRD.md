# Product Requirements Document (PRD)

| **Project Name** | **CodeToDocs** |
| :--- | :--- |
| **Version** | 1.0 (MVP) |
| **Status** | Draft |
| **Type** | Developer Tool / CLI |
| **Language** | Go (Golang) |
| **License** | Open Source (MIT/Apache 2.0) |

---

## 1. Executive Summary
**CodeToDocs** is an open-source tool designed to solve the "stale documentation" problem in modern software development. It automates the maintenance of documentation by analyzing **Git diffs** and using Large Language Models (LLMs) to generate updates.

Its unique value proposition is **"Dual Audience Generation"**:
1.  **Human-Readable:** Standard Markdown for developers (narrative, easy to read).
2.  **AI-Readable:** Strict, structured JSON for AI Agents (RAG-optimized, type-safe).

The purpose is to provide comprehensive auto-updating documentation on a repo. This documentation will serve a variety of audiences:
1. **New Developers:** Onboarding and understanding code changes.
2. **Existing Developers:** Keeping up-to-date with changes and the current state of the codebase.
3. **AI Agents:** Providing structured context for tools like GitHub Copilot, Cursor, and future AI assistants.
4. **Product Managers/Stakeholders:** High-level summaries of repo and changes without technical details.
5. **Open Source Contributors:** Clear documentation to encourage contributions and reduce friction.

The tool is distributed as a **single, static binary** (zero dependencies) to ensure a "Speckit-style" seamless developer experience.

---

## 2. User Experience (UX) Goals
* **Zero-Config Start:** A user must be able to download the binary and run `codetodocs init` to fully configure their repo in < 5 seconds.
* **Agent-First Design:** The tool must integrate natively with GitHub Copilot and Cursor, teaching the AI agent how to use the CLI on behalf of the user.
* **"Invisible" Maintenance:** Documentation updates should happen as part of the PR workflow or local commit process, not as a separate chore.

---

## 3. Core Functional Requirements

### 3.1. Initialization (`init` command)
* **Goal:** Establish the "Constitution" of the repository.
* **Behavior:**
    * Check for the existence of `.codetodocs/`.
    * **Eject Templates:** Extract embedded default templates (Human Markdown, AI JSON, Config YAML) into `.codetodocs/templates/` to allow user customization.
* **UX:** Display a spinner during setup and a success checkmark upon completion (using `bubbletea`).

### 3.2. Git Integration
* **Diff Analysis:** The tool must identify changed files between `HEAD` and a target branch (default: `main`).
* **Context Awareness:**
    * It must read the **full content** of the changed file (for context) and the **diff** (for focus).
    * It must respect `.gitignore` and a custom `.codetodocsignore`.

### 3.3. Dual Audience Generation (`run` command)
* **Input:** A list of changed files from Git.
* **Processing:**
    * For each file, construct a prompt containing the code and the diff.
    * Call the configured LLM (OpenAI/Anthropic/Ollama).
* **Output 1: Human Docs (`docs/human/`)**
    * Format: Markdown (`.md`).
    * Content: High-level summary, "What changed," and usage examples.
* **Output 2: AI Context (`docs/ai/`)**
    * Format: Strict JSON (`.json`).
    * Schema:
        ```json
        {
          "file_path": "src/auth.go",
          "summary": "Handles JWT validation.",
          "signatures": ["func Validate(token string) bool"],
          "dependencies": ["[github.com/golang-jwt/jwt](https://github.com/golang-jwt/jwt)"],
          "complexity_score": 3
        }
        ```
    * *Constraint:* This JSON must be validated against a struct before saving.

### 3.4. Configuration
*