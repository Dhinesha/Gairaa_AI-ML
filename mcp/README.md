# AI DevOps Assistant using Model Context Protocol (MCP)

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastMCP / MCP SDK](https://img.shields.io/badge/MCP-2.2.0-indigo.svg)](https://modelcontextprotocol.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-emerald.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-cyan.svg)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.3-purple.svg)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.0-sky.svg)](https://tailwindcss.com)

An AI-powered DevOps Assistant that leverages the **Model Context Protocol (MCP)** to connect an AI Agent (Google Gemini) with real developer tools, GitHub APIs, Python AST static analyzers, and test execution runners.

---

## 1. Why Model Context Protocol (MCP)?

In traditional AI implementations, external integrations are tightly coupled, hard-coded, and brittle:

```
Traditional Approach (Without MCP):
User → AI → Custom GitHub API Client
          → Custom Pytest Shell Runner
          → Custom AST Analyzer
          (Every integration requires custom schema mapping, error handling, and manual plumbing)
```

With **Model Context Protocol (MCP)**:
```
Standardized Architecture (With MCP):
User → AI Agent (Gemini)
          ↓
     MCP Client
          ↓ (JSON-RPC Protocol)
     MCP Server
     ├── GitHub Tools (Repository info, commits, diff, issues)
     ├── Code Analysis (Python AST, TODO scanner)
     ├── Test Runner (Pytest & Unittest sandbox executor)
     └── Project Health (Composite health scoring & telemetry)
```

### Key Advantages of MCP:
1. **Dynamic Tool Discovery:** The AI Agent dynamically queries `list_tools()` on the MCP Server without needing hard-coded endpoint specifications.
2. **Standardized Tool Contracts:** Tool arguments, types, and descriptions are governed by standardized JSON Schemas.
3. **Security Boundaries:** Sensitive tool operations (like creating issues or modifying repository state) are cleanly isolated behind user confirmation safeguards.
4. **Tool Reusability:** The exact same MCP Server can be mounted into Claude Desktop, Antigravity IDE, Cursor, or any MCP-compliant client.

---

## 2. Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │        React 19 Frontend + Vite        │
                      │  - Repository Connect Bar              │
                      │  - Project Health Gauge (0-100)        │
                      │  - MCP Tool Pipeline Execution Stepper │
                      │  - Conversational DevOps Chat          │
                      │  - Security Confirmation Modal         │
                      └───────────────────┬────────────────────┘
                                          │ HTTP / SSE
                                          ▼
                      ┌────────────────────────────────────────┐
                      │            FastAPI Backend             │
                      │   /api/connect, /api/chat, /api/confirm│
                      └───────────────────┬────────────────────┘
                                          │
                                          ▼
                      ┌────────────────────────────────────────┐
                      │         DevOps AI Agent (LLM)          │
                      │  Gemini 2.5 Flash / Smart Reasoner     │
                      └───────────────────┬────────────────────┘
                                          │
                                          ▼
                      ┌────────────────────────────────────────┐
                      │               MCP Client               │
                      └───────────────────┬────────────────────┘
                                          │ JSON-RPC (stdio / IPC)
                                          ▼
                      ┌────────────────────────────────────────┐
                      │         FastMCP Python Server          │
                      │        (DevOpsAssistantMCP)            │
                      └───────┬─────────────┬─────────────┬────┘
                              │             │             │
                              ▼             ▼             ▼
                      ┌──────────────┐┌───────────┐┌───────────┐
                      │  GitHub API  ││ Python AST││  Pytest   │
                      │ (REST v3)    ││ Analyzer  ││ Runner    │
                      └──────────────┘└───────────┘└───────────┘
```

---

## 3. Catalog of Registered MCP Tools

The MCP Server registers and exposes **12 dedicated DevOps tools**:

| Tool Name | Parameters | Purpose |
|---|---|---|
| `get_repository_info` | `owner`, `repo` | Fetches repository metadata, branch, stars, forks, and open issues |
| `list_repository_files` | `owner`, `repo`, `path` | Recursively lists files and directories in the repository |
| `read_repository_file` | `owner`, `repo`, `path` | Reads and returns source code or configuration files |
| `get_recent_commits` | `owner`, `repo`, `limit` | Returns recent commits with author, hash, message, and date |
| `get_repository_issues` | `owner`, `repo`, `state` | Retrieves open or closed GitHub issues |
| `create_github_issue` | `owner`, `repo`, `title`, `body` | **Mutating Tool:** Creates a GitHub issue (requires confirmation) |
| `analyze_code` | `file_path`, `code`, `owner`, `repo`| Performs AST static analysis (unused vars, bare excepts, complexity) |
| `run_tests` | `owner`, `repo`, `test_command` | Executes pytest or unittest with command whitelist validation |
| `analyze_test_failure` | `test_name`, `error_message`, `traceback` | Diagnoses root cause (e.g. 500 vs 401) and recommends code fixes |
| `get_project_health` | `owner`, `repo` | Computes composite 0-100 project health score and rating |
| `get_commit_diff` | `owner`, `repo`, `commit_sha` | Computes git patch diff and files changed |
| `find_todos` | `owner`, `repo`, `path` | Scans codebase for `TODO`, `FIXME`, `HACK`, and `XXX` tags |

---

## 4. Security & Safety Safeguards

1. **Command Injection Prevention:**
   - The test runner enforces strict whitelist validation (`APPROVED_COMMAND_PREFIXES = ["pytest", "python -m pytest", "python -m unittest"]`). Arbitrary shell commands (`rm`, `curl`, `sh`) are rejected with `PermissionError`.
2. **Explicit Confirmation for Mutating Operations:**
   - Any write operations such as `create_github_issue` suspend the agent loop, returning a `requires_confirmation: true` payload to the UI.
   - The user must explicitly click **Confirm & Create GitHub Issue** before the tool is invoked on GitHub.
3. **Secret Masking:**
   - Log streams automatically mask GitHub PATs and authorization tokens using regex redaction.

---

## 5. Quickstart & Installation

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & **npm**

### Step 1: Clone and Configure Environment

```bash
git clone <repository_url>
cd ai-devops-mcp

# Copy environment template
cp .env.example .env
```

Edit `.env` to provide your API keys:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_personal_access_token_here
PORT=8000
```
*(Note: The system also runs seamlessly in Smart Offline Demo Mode using the built-in `demo_repo` even without API keys!)*

---

### Step 2: Set Up Backend

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run Unit Tests to verify tools
pytest tests/
```

### Step 3: Start FastAPI Backend & MCP Server

```bash
uvicorn backend.main:app --reload --port 8000
```
Backend API will be live at: `http://127.0.0.1:8000`  
API Swagger Documentation: `http://127.0.0.1:8000/docs`

---

### Step 4: Start Frontend Development Server

Open a second terminal window:

```bash
cd frontend
npm install
npm run dev
```
Frontend interface will be live at: `http://localhost:5173`

---

## 6. Docker Compose Deployment

To spin up both backend and frontend in isolated containers:

```bash
docker-compose up --build
```
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`

---

## 7. Step-by-Step Live Demo Walkthrough

1. **Open the Web Interface:**  
   Navigate to `http://localhost:5173`.
2. **Connect Repository:**  
   Click the preset button **Demo Repo (auth.py & failing tests)** or enter any public GitHub URL (e.g., `octocat/Hello-World`). Click **Connect Repository**.
3. **Inspect Project Health:**  
   Review the dynamic score cards (Health Score, Test Pass %, Code Issues, TODOs, Commits).
4. **Ask:** `"Analyze my repository."`  
   Observe the **MCP Tool Pipeline** indicator executing:
   - `✓ get_repository_info`
   - `✓ list_repository_files`
   - `✓ get_recent_commits`
   - `✓ get_project_health`
5. **Ask:** `"Run the tests."`  
   The agent calls `run_tests` via MCP and reports:  
   *2 tests passed, 1 test failed in `test_auth.py`.*
6. **Ask:** `"Why are my tests failing?"`  
   The agent calls:
   - `run_tests`
   - `read_repository_file`
   - `analyze_test_failure`  
   The AI provides a root-cause explanation: `authenticate_user()` raises an unhandled `ValueError` when given an invalid password, resulting in HTTP 500 instead of HTTP 401.
7. **Ask:** `"Create a GitHub issue for this bug."`  
   The agent **does not execute immediately**. Instead, it triggers the **Security Confirmation Modal** showing the proposed Title and Description.
8. **Click:** `[Confirm & Create GitHub Issue]`  
   The issue is created and confirmed on GitHub via MCP.

---

## 8. Running Automated Unit Tests

```bash
# Run all unit tests
pytest tests/ -v
```

Tests verify:
- GitHub tool operations and error handling
- AST syntax checking, unused import/variable detection, complexity rules
- Command whitelist validation and security enforcement
- Pytest and unittest output parsing
- Failure root-cause diagnostics
- Composite health score computation

---

## 9. Project Structure

```text
ai-devops-mcp/
├── backend/
│   ├── agent/
│   │   ├── agent.py               # AI Agent & Gemini MCP Client bridge
│   │   └── prompts.py             # System prompts and security guidelines
│   ├── mcp_server/
│   │   ├── server.py              # Dedicated FastMCP Server (12 Tools)
│   │   └── tools/
│   │       ├── code_tools.py      # AST analysis & TODO scanner tools
│   │       ├── git_tools.py       # Git commit diff tools
│   │       ├── github_tools.py    # GitHub REST API tools
│   │       ├── health_tools.py    # Project health scoring tools
│   │       └── test_tools.py      # Pytest runner & diagnostics tools
│   ├── services/
│   │   ├── code_analyzer.py       # Python AST engine
│   │   ├── git_service.py         # Local git helper
│   │   ├── github_service.py      # GitHub REST client with auth & error handler
│   │   └── test_runner.py         # Subprocess test runner with whitelist validation
│   ├── models/
│   │   └── schemas.py             # Pydantic data contracts
│   ├── utils/
│   │   └── helpers.py             # Sanitized logging and URL parser
│   ├── config.py                  # Environment settings
│   ├── requirements.txt           # Python dependencies
│   └── main.py                    # FastAPI server
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx           # Interactive conversation stream
│   │   │   ├── ConfirmationModal.tsx       # Security action confirmation modal
│   │   │   ├── Header.tsx                  # MCP & LLM system badges
│   │   │   ├── HealthDashboard.tsx         # Visual health metrics cards
│   │   │   ├── RepoConnectBar.tsx          # GitHub repo connection input & presets
│   │   │   ├── ToolExecutionIndicator.tsx  # Real-time MCP tool pipeline stepper
│   │   │   └── ToolsModal.tsx              # Catalog modal for all 12 MCP tools
│   │   ├── services/
│   │   │   └── api.ts                      # REST API client
│   │   ├── types.ts                        # TypeScript interfaces
│   │   ├── App.tsx                         # Main container layout
│   │   └── index.css                       # Glassmorphic Tailwind styles
│   ├── package.json
│   └── vite.config.ts
│
├── demo_repo/                     # Self-contained sample project for live demos
│   ├── auth.py                    # Authentication module with bug and code smells
│   ├── tests/
│   │   └── test_auth.py           # Test suite (2 passed, 1 intentional failure)
│   └── README.md
│
├── tests/                         # Test suite
│   ├── test_github_tools.py
│   ├── test_code_tools.py
│   └── test_health.py
│
├── .env.example
├── .gitignore
├── pytest.ini
├── docker-compose.yml
└── README.md
```

---

## 10. License

MIT License © 2026 AI DevOps Assistant Team
