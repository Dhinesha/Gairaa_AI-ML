import asyncio
import pytest
from fastapi.testclient import TestClient
from backend.app.core.config import settings
from backend.app.database.session import Base, SessionLocal, engine
from backend.app.main import app
from backend.app.models.entities import WorkflowModel, ApprovalRequestModel
from backend.app.services.workflow_engine import workflow_service


@pytest.fixture(scope="session", autouse=True)
def init_db():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_health_and_metrics_endpoints(client):
    """Verify health and Prometheus endpoints."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "degraded")
    assert "database_connected" in data

    metrics_res = client.get("/metrics")
    assert metrics_res.status_code == 200
    assert "safety_engine_workflows_total" in metrics_res.text


def test_normal_successful_workflow(client):
    """Test full multi-step workflow ending in successful completion."""
    # Create workflow with auto_run=False
    create_res = client.post(
        "/api/v1/workflows?auto_run=false",
        json={"task": "Inspect engineering team", "agent_type": "mock:normal_success"},
    )
    assert create_res.status_code == 201
    wf_id = create_res.json()["id"]

    # Execute workflow synchronously using the service
    asyncio.run(workflow_service.run_workflow(wf_id))

    # Inspect workflow details
    detail_res = client.get(f"/api/v1/workflows/{wf_id}")
    assert detail_res.status_code == 200
    wf_data = detail_res.json()

    assert wf_data["status"] == "COMPLETED"
    assert wf_data["step_count"] >= 3
    assert len(wf_data["steps"]) >= 3
    assert wf_data["result_summary"] is not None
    # Verify tool results exist
    assert any(s["tool_name"] == "search_employees" for s in wf_data["steps"])
    assert any(s["tool_name"] == "generate_report" for s in wf_data["steps"])


def test_infinite_loop_prevention_workflow(client):
    """Test that a cyclic agent loop is detected and blocked before runaway execution."""
    create_res = client.post(
        "/api/v1/workflows?auto_run=false",
        json={"task": "Run data synchronization", "agent_type": "mock:infinite_loop"},
    )
    assert create_res.status_code == 201
    wf_id = create_res.json()["id"]

    # Execute
    asyncio.run(workflow_service.run_workflow(wf_id))

    detail_res = client.get(f"/api/v1/workflows/{wf_id}")
    wf_data = detail_res.json()

    assert wf_data["status"] == "BLOCKED"
    assert "infinite loop" in wf_data["termination_reason"].lower()

    # Verify safety event was recorded
    events_res = client.get(f"/api/v1/workflows/{wf_id}/events")
    events = events_res.json()
    assert len(events) >= 1
    assert any(e["decision"] == "BLOCK" for e in events)


def test_repeated_calls_prevention_workflow(client):
    """Test that repeated identical calls are halted."""
    create_res = client.post(
        "/api/v1/workflows?auto_run=false",
        json={"task": "Find John Doe", "agent_type": "mock:repeated_calls"},
    )
    assert create_res.status_code == 201
    wf_id = create_res.json()["id"]

    asyncio.run(workflow_service.run_workflow(wf_id))

    detail_res = client.get(f"/api/v1/workflows/{wf_id}")
    wf_data = detail_res.json()
    assert wf_data["status"] == "BLOCKED"
    assert "repeated tool-call" in wf_data["termination_reason"].lower()


def test_sensitive_action_and_approval_workflow(client):
    """
    Test end-to-end sensitive action flow:
    1. Workflow runs and encounters sensitive tool -> PAUSED_APPROVAL
    2. Approval request generated
    3. Reviewer approves -> resumes and completes
    """
    create_res = client.post(
        "/api/v1/workflows?auto_run=false",
        json={"task": "Adjust compensation for Elena", "agent_type": "mock:sensitive_action"},
    )
    assert create_res.status_code == 201
    wf_id = create_res.json()["id"]

    # Step 1: Initial run pauses at approval gate
    asyncio.run(workflow_service.run_workflow(wf_id))

    detail_res = client.get(f"/api/v1/workflows/{wf_id}")
    wf_data = detail_res.json()
    assert wf_data["status"] == "PAUSED_APPROVAL"
    assert len(wf_data["approvals"]) >= 1

    approval_id = wf_data["approvals"][0]["id"]
    assert wf_data["approvals"][0]["status"] == "PENDING"
    assert wf_data["approvals"][0]["tool_name"] == "modify_employee_salary"

    # Step 2: Reviewer approves with authorization header
    approve_res = client.post(
        f"/api/v1/approvals/{approval_id}/approve",
        headers={"x-user-role": "admin"},
        json={"reviewed_by": "vp-engineering", "comment": "Approved following merit review."},
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "APPROVED"

    # Step 3: Run resume
    asyncio.run(workflow_service.run_workflow(wf_id, is_resume=True, approved_step_id=approval_id))

    # Verify workflow transitioned to COMPLETED
    resumed_res = client.get(f"/api/v1/workflows/{wf_id}")
    resumed_data = resumed_res.json()
    assert resumed_data["status"] == "COMPLETED"


def test_stop_and_retry_workflow(client):
    """Test manual workflow stop and safe retry."""
    create_res = client.post(
        "/api/v1/workflows?auto_run=false",
        json={"task": "Test stopping", "agent_type": "mock:infinite_loop"},
    )
    wf_id = create_res.json()["id"]

    # Stop workflow
    stop_res = client.post(f"/api/v1/workflows/{wf_id}/stop")
    assert stop_res.status_code == 200
    assert stop_res.json()["status"] == "STOPPED"

    # Retry workflow
    retry_res = client.post(f"/api/v1/workflows/{wf_id}/retry")
    assert retry_res.status_code == 200
    assert retry_res.json()["status"] == "PENDING"
    assert retry_res.json()["step_count"] == 0


def test_analytics_api(client):
    """Verify aggregated metrics response."""
    res = client.get("/api/v1/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "total_workflows" in data
    assert "successful_workflows" in data
    assert "blocked_workflows" in data
    assert "tool_distribution" in data
    assert data["total_workflows"] >= 1


def test_safety_config_endpoints(client):
    """Verify safety configuration get and update."""
    get_res = client.get("/api/v1/safety/config")
    assert get_res.status_code == 200
    cfg = get_res.json()
    assert cfg["max_workflow_steps"] >= 5

    # Update config
    cfg["max_workflow_steps"] = 25
    put_res = client.put("/api/v1/safety/config", json=cfg)
    assert put_res.status_code == 200
    assert put_res.json()["max_workflow_steps"] == 25


def test_auth_signup_and_login_flow(client):
    """Verify native backend authentication stored in safety_engine.db."""
    import uuid
    test_email = f"test.{uuid.uuid4().hex[:8]}@loopguard.ai"

    # 1. Sign up new user
    signup_res = client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Test Researcher",
            "email": test_email,
            "password": "strongPassword123",
            "role": "student",
            "organization": "Department of AI",
        },
    )
    assert signup_res.status_code == 201
    user_data = signup_res.json()
    assert user_data["email"] == test_email
    assert user_data["role"] == "student"
    assert "id" in user_data

    # 2. Duplicate email should fail with 400
    dup_res = client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Test Duplicate",
            "email": test_email,
            "password": "anotherPassword",
            "role": "student",
        },
    )
    assert dup_res.status_code == 400

    # 3. Successful login with correct password
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_email, "password": "strongPassword123"},
    )
    assert login_res.status_code == 200
    assert login_res.json()["email"] == test_email

    # 4. Failed login with wrong password
    bad_login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_email, "password": "wrongPasswordXYZ"},
    )
    assert bad_login_res.status_code == 401

    # 5. List users
    users_res = client.get("/api/v1/auth/users")
    assert users_res.status_code == 200
    assert any(u["email"] == test_email for u in users_res.json())


def test_database_sample_and_explainer_endpoints(client):
    """Verify database explainer sample endpoint."""
    res = client.get("/api/v1/database/sample")
    assert res.status_code == 200
    data = res.json()
    assert data["table_count"] >= 1
    assert "students" in [t["name"] for t in data["tables"]]
    assert len(data["summary_en"]) > 10


