# Agent Workflow Safety & Loop Prevention Engine (LoopGuard)

> A deterministic pre-execution safety supervisor, cyclic loop prevention gate, and human-in-the-loop governance engine for autonomous AI agents and Model Context Protocol (MCP) tools.

---

## 1. System Overview & Architecture

The **Agent Workflow Safety & Loop Prevention Engine** intercepts agent actions *before execution*, evaluates structural/semantic arguments, detects repeating invocation cycles, enforces execution budgets, and routes sensitive operations to an authorized human approval gate.

```
                      +-----------------------------+
                      |    React + Vite Frontend    |
                      |  - Live Operations Center   |
                      |  - Execution Trace Viewer   |
                      |  - Human Approval Center    |
                      |  - Recharts Analytics       |
                      +--------------+--------------+
                                     | HTTP REST (Vite Proxy)
                                     v
                      +-----------------------------+
                      |       FastAPI Backend       |
                      |  - Workflow Orchestrator    |
                      |  - Audit Trail Engine       |
                      |  - Prometheus Metrics       |
                      +--------------+--------------+
                                     |
               +---------------------+---------------------+
               |                                           |
               v                                           v
+-------------------------------+           +-------------------------------+
|      Safety Engine Gate       |           |     Execution Engine          |
|  1. Execution Budget Limits   |           |  - Modular Agent Interface    |
|  2. Risk Policy Gate          |           |  - Deterministic Mock Agents  |
|  3. Repeated Tool-Call Hashes |           |  - Google Gemini LLM Provider |
|  4. Sliding-Window Loop Det.  |           |  - MCP Tool Registry & Client |
|  5. No-Progress Hash Diff     |           +---------------+---------------+
+--------------+----------------+                           |
               | Decision: ALLOW / BLOCK / APPROVAL         |
               +--------------------------------------------+
                                     |
               +---------------------+---------------------+
               |                                           |
               v                                           v
+-------------------------------+           +-------------------------------+
|    Database (SQLAlchemy)      |           |     Redis / Memory Cache      |
|  - SQLite (Local zero-config) |           |  - Concurrency Locks          |
|  - PostgreSQL (Docker Prod)   |           |  - Shared Counters            |
|  - Workflows, Steps, Events   |           |  - Resilient In-Memory Mode   |
+-------------------------------+           +-------------------------------+
```

---

## 2. Core Safety Engine Detectors

| Gate / Detector | Mechanism | Default Policy | Action |
| :--- | :--- | :--- | :--- |
| **Execution Limits** | Enforces step budget, timeout duration, total tool calls, and max retries | Max 20 steps, 300s timeout, 3 retries | `BLOCK` |
| **Risk-Based Gate** | Inspects sensitive tools (`modify_employee_salary`, `delete_record`, `export_db`) | Routes high-risk tools for review | `REQUIRE_APPROVAL` |
| **Repeated Tool Calls** | Recursively normalizes arguments (whitespace, keys, types) & SHA-256 hashes | Max 3 identical calls | `BLOCK` |
| **Cyclic Loop Detection**| Evaluates action sequence with sliding-window n-gram cycles ($A \to B \to A \to B$) | 2 complete cycles of period $K \ge 2$ | `BLOCK` |
| **No-Progress Detection**| Computes outcome hashes; flags consecutive unhandled errors or zero-delta outputs | 3 consecutive identical outputs | `BLOCK` |

---

## 3. Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React, Recharts, Axios.
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn.
- **Database**: SQLite (instant local development) & PostgreSQL (Docker Compose).
- **Cache & Concurrency**: Redis with automatic in-memory fallback.
- **Workflow & AI**: Model Context Protocol (MCP) SDK, Deterministic Mock Agents, Google Gemini provider.
- **Monitoring**: Structured logging & Prometheus metrics (`/metrics`).
- **Testing**: Pytest (backend) & Node.js test runner (frontend).

---

## 4. Quick Start (Windows Laptop)

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm

### Step 1: Clone & Configure Environment
```powershell
cd d:\Mini-PRO

# Create local environment configuration
Copy-Item .env.example .env
```

### Step 2: Install Backend Dependencies
```powershell
# In d:\Mini-PRO
python -m pip install -r backend/requirements.txt
```

### Step 3: Run Backend Server
```powershell
# Starts FastAPI server on http://127.0.0.1:8000
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

### Step 4: Install Frontend & Run Dev Server
In a new PowerShell terminal:
```powershell
cd d:\Mini-PRO\frontend

# Install dependencies (only required on first setup)
npm install --no-audit --no-fund

# Start Vite React dashboard on http://127.0.0.1:5173
npm run dev
```

Open your browser at **http://127.0.0.1:5173** to view the live dashboard!

---

## 5. Running Tests

### Run Backend Unit & Integration Tests (21 tests)
```powershell
cd d:\Mini-PRO
python -m pytest backend/tests/ -v
```

### Run Frontend Integration Tests
```powershell
cd d:\Mini-PRO\frontend
npm test
```

### Build Frontend Production Bundle
```powershell
cd d:\Mini-PRO\frontend
npm run build
```

---

## 6. Docker Compose Deployment (PostgreSQL + Redis)

To run the complete containerized stack:
```powershell
cd d:\Mini-PRO\infra
docker compose up --build -d
```
- Frontend Dashboard: `http://localhost:3000`
- FastAPI Backend: `http://localhost:8000`
- API Documentation (Swagger): `http://localhost:8000/docs`
- Prometheus Metrics: `http://localhost:8000/metrics`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

To stop containers:
```powershell
docker compose down
```

---

## 7. Interactive Test Scenarios

The dashboard features one-click test scenario launchers:

1. **Normal Workflow (`mock:normal_success`)**:
   - Executes multi-step search $\to$ detail lookup $\to$ report generation $\to$ completion.
2. **Cyclic Infinite Loop (`mock:infinite_loop`)**:
   - Alternates `tool_a` and `tool_b`. Safety Engine flags `INFINITE_LOOP_PREVENTION` and terminates workflow.
3. **Repeated Calls (`mock:repeated_calls`)**:
   - Invocations with identical arguments exceed repeat threshold $\to$ BLOCKED.
4. **Sensitive Approval (`mock:sensitive_action`)**:
   - Attempts `modify_employee_salary`. Safety gate pauses workflow with `REQUIRE_APPROVAL`. Reviewer approves in Approval Center, resuming execution to completion.
5. **No Progress (`mock:no_progress`)**:
   - Calls static tool repeatedly; output hashes show zero progression $\to$ BLOCKED.
6. **Real Google Gemini LLM (`gemini`)**:
   - Supply `GEMINI_API_KEY` in `.env` to execute live tasks with Gemini 1.5 Flash.

---

## 8. REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/workflows` | Create a new workflow (supports optional limit overrides) |
| `POST` | `/api/v1/workflows/{id}/run` | Start / trigger workflow execution |
| `GET` | `/api/v1/workflows` | List workflows with status filtering |
| `GET` | `/api/v1/workflows/{id}` | Get workflow execution details, steps, and audit alerts |
| `GET` | `/api/v1/workflows/{id}/events` | Get safety events for a workflow |
| `POST` | `/api/v1/workflows/{id}/stop` | Manually stop a running workflow |
| `POST` | `/api/v1/workflows/{id}/resume` | Resume paused or reviewed workflow |
| `POST` | `/api/v1/workflows/{id}/retry` | Reset steps and retry workflow |
| `GET` | `/api/v1/approvals` | List pending and resolved human approvals |
| `POST` | `/api/v1/approvals/{id}/approve`| Approve sensitive tool execution & resume workflow |
| `POST` | `/api/v1/approvals/{id}/reject` | Reject sensitive tool execution & terminate workflow |
| `GET` | `/api/v1/safety/events` | List all safety violation events with severity filter |
| `GET` | `/api/v1/safety/config` | Retrieve active safety thresholds and sensitive tools |
| `PUT` | `/api/v1/safety/config` | Update safety policy thresholds with audit trail |
| `GET` | `/api/v1/analytics` | Real-time aggregated metrics and tool volume |
| `GET` | `/health` | Service health, database check, and Redis status |
| `GET` | `/metrics` | Prometheus metrics scrape target |

---

## 9. Troubleshooting

- **Port Conflict (8000 or 5173 occupied)**:
  Change ports in `backend/app/main.py` (`--port 8001`) and `frontend/vite.config.ts` (`server: { port: 5174 }`).
- **Redis Offline**:
  The system includes an automatic in-memory fallback cache that handles distributed locks and counters transparently without throwing exceptions.
- **Database Reset**:
  Delete `safety_engine.db` to reset to a clean database slate; tables and default policies will automatically regenerate on startup.
