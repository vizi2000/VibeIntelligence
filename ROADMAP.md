# VibeIntelligence (VI) - Project Roadmap

*Last Updated: August 13, 2025*

This document serves as the single source of truth for the VibeIntelligence project's vision, development roadmap, and current status. It replaces all previous status and planning documents.

---

## 🎯 Project Vision

VibeIntelligence (VI) is the central governance platform for our entire development ecosystem. It provides a unified dashboard to scan, analyze, document, and manage all our software projects.

Our core architectural strategy is to integrate VI with **`agent-zero`**, which will serve as our foundational "Operating System" for all AI agent tasks. VI will delegate tasks (e.g., scanning, analysis, documentation generation) to `agent-zero`, which will execute them using a robust, extensible, multi-agent framework. This allows VI to focus on its core domain of project management and UI, while `agent-zero` handles the complexities of agentic workflows.

---

## 📊 Current State Summary (as of Initial Scan)

The initial analysis by VibeIntelligence revealed the following:
- **Total Projects:** ~350
- **Total Size:** ~20 GB
- **Duplicate Groups:** 122 (most critical: 18 versions of `Xpress Delivery`)
- **Undocumented Projects:** 180
- **Projects without Git:** 330

This data underscores the critical need for this platform to enforce order and standards.

---

## 🗺️ Development Roadmap

### Sprint 1: Stabilization & Core Features

*Goal: Fix critical bugs, implement essential commands, and align the project with the new vision.*

- **[BUG] Fix Health Score Calculation:**
  - **Task:** Implement a reliable scoring algorithm in `analyzer_agent.py`.
  - **Acceptance Criteria:** Projects display a calculated percentage instead of "NaN%".

- **[BUG] Ensure UI Updates After Scan:**
  - **Task:** Fix the frontend state management so that project cards visually refresh after a scan is complete.
  - **Acceptance Criteria:** A project's health score, tech stack, etc., updates on the dashboard without a manual page reload.

- **[BUG] Fix Missing API Endpoints:**
  - **Task:** Implement the `/api/v1/health` and `/api/v1/agents/stats` endpoints.
  - **Acceptance Criteria:** Endpoints return a 200 OK response with the correct data payload.

- **[FEATURE] Implement `vi` CLI:**
  - **Task:** Add a CLI entrypoint to the backend using Typer.
  - **Sub-task:** Implement `vi init <project_name>` to create projects from a standard template.
  - **Sub-task:** Implement `vi archive <project_name>` to move projects to the archive folder.
  - **Acceptance Criteria:** The CLI is executable and can create/archive projects.

- **[TECH DEBT] Rename Internal Components:**
  - **Task:** Refactor all internal references, service names, and container names from "Zenith Coder" to "VibeIntelligence" or "vi".
  - **Acceptance Criteria:** No references to "zenith" remain in the codebase or configuration.

### Sprint 2: Knowledge & Integration

*Goal: Integrate the `agent-zero` framework and implement the core knowledge base features.*

- **[FEATURE] Implement Vector Knowledge Base:**
  - **Task:** Integrate ChromaDB into the `analyzer_agent.py` workflow.
  - **Acceptance Criteria:** During a scan, the content of `.md` files is vectorized and stored in a persistent ChromaDB collection.

- **[FEATURE] Implement Natural Language Query:**
  - **Task:** Create a new API endpoint (`/api/v1/ai/query`) that uses the vector DB to answer questions about projects.
  - **Acceptance Criteria:** A user can ask "What is the purpose of project X?" and get an answer based on its README.

- **[INTEGRATION] `agent-zero` Integration (Phase 1):**
  - **Task:** Refactor the `scanner_agent.py` and `analyzer_agent.py` logic into standalone "tools" that can be consumed by `agent-zero`.
  - **Acceptance Criteria:** `VibeIntelligence` can successfully delegate a "scan" task to `agent-zero`.

### Sprint 3: UI Polish & Advanced Features

*Goal: Complete the user interface and implement the remaining core application features.*

- **[UI] Complete Dashboard Components:**
  - **Task:** Implement the missing "AI Assistant" and "Agent Activity" cards on the main dashboard.
  - **Acceptance Criteria:** The dashboard is fully populated with all intended components.

- **[FEATURE] Implement Documentation Generation:**
  - **Task:** Wire up the "Generate Docs" button to trigger a `documentation_agent` task in `agent-zero`.
  - **Acceptance Criteria:** Clicking the button generates a basic `README.md` for a project.

- **[FEATURE] Implement Project Deployment:**
  - **Task:** Wire up the "Deploy" button to trigger a `deployment_agent` task.
  - **Acceptance Criteria:** The feature can execute a project's `deploy.sh` script or similar.

---

## 🔭 Future Vision (Post-MVP)

- **Integration with `agenticSeek`:** Add `agenticSeek` as a specialized tool in the `agent-zero` toolbox for private web browsing and research tasks.
- **Advanced Monetization & Skill Tracking:** Complete the monetization and developer skill-tracking features.
- **Full CI/CD Integration:** Automate the deployment and testing of `VibeIntelligence` itself.
