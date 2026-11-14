import time
import pytest
from backend.app.safety import (
    ActionRequest,
    RiskLevel,
    SafetyDecision,
    SafetyEngine,
    SafetyPolicy,
    StepRecord,
    ToolOutcome,
    WorkflowContext,
    are_arguments_equivalent,
    canonical_json_string,
    compute_tool_call_hash,
    sanitize_arguments,
)


@pytest.fixture
def engine():
    return SafetyEngine()


@pytest.fixture
def base_context():
    return WorkflowContext(
        workflow_id="wf-test-123",
        task="Test safety supervisor capabilities",
        start_time_epoch=time.time(),
        policy=SafetyPolicy(
            max_workflow_steps=5,
            max_repeated_calls=2,
            max_execution_duration_seconds=10.0,
            loop_cycle_threshold=2,
            max_no_progress_steps=2,
            sensitive_tools=["modify_employee_salary", "delete_employee_record"],
        ),
    )


def test_argument_normalization_and_equivalence():
    """Verify that whitespace, key ordering, and types are canonically equivalent."""
    args1 = {"name": " John Doe ", "id": "101", "active": True}
    args2 = {"active": True, "id": 101, "name": "John Doe"}
    
    assert are_arguments_equivalent(args1, args2)
    assert canonical_json_string(args1) == canonical_json_string(args2)
    
    hash1 = compute_tool_call_hash("search_employees", args1)
    hash2 = compute_tool_call_hash("search_employees", args2)
    assert hash1 == hash2


def test_argument_sanitization():
    """Verify that credentials and secrets are masked in logs and displays."""
    raw_args = {
        "user": "admin",
        "api_key": "sk-12345secret",
        "nested": {"token": "bearer-xyz", "safe_field": 42},
    }
    sanitized = sanitize_arguments(raw_args)
    assert sanitized["user"] == "admin"
    assert sanitized["api_key"] == "[REDACTED]"
    assert sanitized["nested"]["token"] == "[REDACTED]"
    assert sanitized["nested"]["safe_field"] == 42


def test_normal_successful_action_allowed(engine, base_context):
    """An ordinary benign action with no history should be ALLOWED."""
    action = ActionRequest(
        tool_name="search_employees",
        arguments={"department": "Engineering"},
        step_number=1,
    )
    result = engine.evaluate(action, base_context)
    assert result.decision == SafetyDecision.ALLOW
    assert result.risk_level == RiskLevel.LOW
    assert result.rule_triggered is None


def test_repeated_identical_tool_calls_blocked(engine, base_context):
    """When a tool is called repeatedly with identical args, it must be BLOCKED."""
    action = ActionRequest(
        tool_name="search_employees",
        arguments={"query": "Alice"},
        step_number=1,
    )
    h = compute_tool_call_hash(action.tool_name, action.arguments)

    # First call allowed
    res1 = engine.evaluate(action, base_context)
    assert res1.decision == SafetyDecision.ALLOW
    
    # Record step 1
    base_context.history.append(
        StepRecord(
            step_number=1,
            tool_name=action.tool_name,
            arguments=action.arguments,
            normalized_hash=h,
            success=True,
            result={"found": 1},
        )
    )

    # Second call allowed (max_repeated_calls is 2)
    action.step_number = 2
    res2 = engine.evaluate(action, base_context)
    assert res2.decision == SafetyDecision.ALLOW

    base_context.history.append(
        StepRecord(
            step_number=2,
            tool_name=action.tool_name,
            arguments=action.arguments,
            normalized_hash=h,
            success=True,
            result={"found": 1},
        )
    )

    # Third call should exceed max_repeated_calls (2) and be BLOCKED
    action.step_number = 3
    res3 = engine.evaluate(action, base_context)
    assert res3.decision == SafetyDecision.BLOCK
    assert res3.rule_triggered == "REPEATED_TOOL_CALL_DETECTED"
    assert "repeated tool-call limit exceeded" in res3.reason.lower()


def test_repeated_equivalent_tool_calls_blocked(engine, base_context):
    """Verify equivalent arguments (different key order / whitespace) trigger repeated call block."""
    action1 = ActionRequest(tool_name="lookup", arguments={"id": 10, "tag": "dev"}, step_number=1)
    action2 = ActionRequest(tool_name="lookup", arguments={"tag": " dev ", "id": "10"}, step_number=2)

    h1 = compute_tool_call_hash(action1.tool_name, action1.arguments)
    base_context.history.append(
        StepRecord(step_number=1, tool_name=action1.tool_name, arguments=action1.arguments, normalized_hash=h1)
    )
    base_context.history.append(
        StepRecord(step_number=2, tool_name=action1.tool_name, arguments=action1.arguments, normalized_hash=h1)
    )

    # Next call with action2 (equivalent)
    res = engine.evaluate(action2, base_context)
    assert res.decision == SafetyDecision.BLOCK
    assert res.rule_triggered == "REPEATED_TOOL_CALL_DETECTED"


def test_infinite_loop_cycle_detection(engine, base_context):
    """
    Test cyclic loop detection: A -> B -> A -> B.
    Threshold is 2 cycles.
    """
    h_a = compute_tool_call_hash("tool_a", {"x": 1})
    h_b = compute_tool_call_hash("tool_b", {"y": 2})

    # History has A, B, A
    base_context.history = [
        StepRecord(step_number=1, tool_name="tool_a", arguments={"x": 1}, normalized_hash=h_a),
        StepRecord(step_number=2, tool_name="tool_b", arguments={"y": 2}, normalized_hash=h_b),
        StepRecord(step_number=3, tool_name="tool_a", arguments={"x": 1}, normalized_hash=h_a),
    ]

    # Propose tool_b to complete cycle: A -> B -> A -> B (2 full cycles of period 2)
    action = ActionRequest(tool_name="tool_b", arguments={"y": 2}, step_number=4)
    result = engine.evaluate(action, base_context)

    assert result.decision == SafetyDecision.BLOCK
    assert result.rule_triggered == "INFINITE_LOOP_PREVENTION"
    assert "infinite loop pattern detected" in result.reason.lower()
    assert result.details["cycle_period"] == 2


def test_no_progress_consecutive_errors(engine, base_context):
    """If last N steps produced unhandled errors, pre-execution gate blocks further waste."""
    base_context.history = [
        StepRecord(step_number=1, tool_name="api_call", arguments={}, normalized_hash="h1", success=False, error="500 Internal Error"),
        StepRecord(step_number=2, tool_name="api_call", arguments={"retry": 1}, normalized_hash="h2", success=False, error="500 Internal Error"),
    ]

    action = ActionRequest(tool_name="api_call", arguments={"retry": 2}, step_number=3)
    result = engine.evaluate(action, base_context)

    assert result.decision == SafetyDecision.BLOCK
    assert result.rule_triggered == "NO_PROGRESS_CONSECUTIVE_ERRORS"


def test_execution_limits_step_budget(engine, base_context):
    """Step number exceeding max_workflow_steps must be blocked."""
    # policy.max_workflow_steps is 5
    action = ActionRequest(tool_name="tool_any", arguments={}, step_number=6)
    result = engine.evaluate(action, base_context)

    assert result.decision == SafetyDecision.BLOCK
    assert result.rule_triggered == "MAX_STEPS_EXCEEDED"


def test_execution_limits_timeout(engine, base_context):
    """Execution past duration limit must be blocked."""
    # Simulate workflow started 20 seconds ago (limit is 10s)
    base_context.start_time_epoch = time.time() - 25.0
    action = ActionRequest(tool_name="tool_any", arguments={}, step_number=2)
    result = engine.evaluate(action, base_context)

    assert result.decision == SafetyDecision.BLOCK
    assert result.rule_triggered == "MAX_DURATION_EXCEEDED"


def test_sensitive_action_requires_approval(engine, base_context):
    """Sensitive tools must return REQUIRE_APPROVAL."""
    action = ActionRequest(
        tool_name="modify_employee_salary",
        arguments={"employee_id": "EMP-992", "new_salary": 180000},
        step_number=1,
    )
    result = engine.evaluate(action, base_context)

    assert result.decision == SafetyDecision.REQUIRE_APPROVAL
    assert result.rule_triggered == "SENSITIVE_TOOL_POLICY"
    assert result.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
