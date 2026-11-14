from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.entities import (
    AuditLogModel,
    SafetyEventModel,
    SafetyPolicyConfigModel,
)
from backend.app.safety.engine import default_safety_engine
from backend.app.schemas.workflow import (
    SafetyEventResponse,
    SafetyPolicyConfigSchema,
)

router = APIRouter(prefix="/safety", tags=["Safety"])


@router.get("/events", response_model=List[SafetyEventResponse])
def get_safety_events(
    severity: Optional[str] = None,
    rule_name: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Retrieve safety events and alerts across all workflows."""
    query = db.query(SafetyEventModel).order_by(SafetyEventModel.created_at.desc())
    if severity:
        query = query.filter(SafetyEventModel.severity == severity.upper())
    if rule_name:
        query = query.filter(SafetyEventModel.rule_name == rule_name)
    return query.limit(limit).all()


@router.get("/config", response_model=SafetyPolicyConfigSchema)
def get_safety_config(db: Session = Depends(get_db)):
    """Retrieve active system safety thresholds, loop policies, and sensitive tool allowlists."""
    config = db.query(SafetyPolicyConfigModel).filter(SafetyPolicyConfigModel.is_active == True).first()
    if not config:
        # Create default config if none exists
        default_p = default_safety_engine.evaluate.__self__.evaluate.__doc__
        config = SafetyPolicyConfigModel(
            name="Default Production Safety Policy",
            is_active=True,
            max_workflow_steps=20,
            max_repeated_calls=3,
            max_execution_duration_seconds=300.0,
            max_tool_calls=50,
            max_retries=3,
            loop_cycle_threshold=2,
            max_no_progress_steps=3,
            auto_block_no_progress=True,
            sensitive_tools=[
                "modify_employee_salary",
                "delete_employee_record",
                "execute_payment",
                "drop_database_table",
                "send_external_email",
                "grant_admin_access",
            ],
            sensitive_argument_patterns=[
                "password", "secret", "token", "api_key", "credit_card", "ssn",
            ],
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


@router.put("/config", response_model=SafetyPolicyConfigSchema)
def update_safety_config(
    payload: SafetyPolicyConfigSchema,
    db: Session = Depends(get_db),
):
    """Update global safety thresholds, cycle parameters, and sensitive operations with audit tracking."""
    config = db.query(SafetyPolicyConfigModel).filter(SafetyPolicyConfigModel.is_active == True).first()
    if not config:
        config = SafetyPolicyConfigModel()
        db.add(config)

    config.name = payload.name
    config.max_workflow_steps = payload.max_workflow_steps
    config.max_repeated_calls = payload.max_repeated_calls
    config.max_execution_duration_seconds = payload.max_execution_duration_seconds
    config.max_tool_calls = payload.max_tool_calls
    config.max_retries = payload.max_retries
    config.loop_cycle_threshold = payload.loop_cycle_threshold
    config.max_no_progress_steps = payload.max_no_progress_steps
    config.auto_block_no_progress = payload.auto_block_no_progress
    config.sensitive_tools = payload.sensitive_tools
    config.sensitive_argument_patterns = payload.sensitive_argument_patterns

    db.add(AuditLogModel(
        action="SAFETY_POLICY_UPDATED",
        actor="admin",
        resource_type="safety_policy",
        resource_id=str(config.id),
        details=payload.model_dump(),
    ))
    db.commit()
    db.refresh(config)
    return config


@router.get("/rules")
def list_safety_rules():
    """List all registered detectors, policies, and gate rules."""
    return [
        {
            "id": "REPEATED_TOOL_CALL_DETECTED",
            "name": "Repeated Identical / Equivalent Tool Calls",
            "description": "Detects identical or structurally equivalent tool calls exceeding threshold",
            "default_threshold": 3,
            "action": "BLOCK",
        },
        {
            "id": "INFINITE_LOOP_PREVENTION",
            "name": "Cyclic Infinite Loop Prevention",
            "description": "Detects multi-step repetitive cycles (A -> B -> A -> B) using n-gram sequence matching",
            "default_threshold": 2,
            "action": "BLOCK",
        },
        {
            "id": "NO_PROGRESS_DETECTION",
            "name": "Outcome Stagnation & No-Progress Detection",
            "description": "Halts execution when consecutive actions yield zero delta or unhandled errors",
            "default_threshold": 3,
            "action": "BLOCK",
        },
        {
            "id": "EXECUTION_BUDGET_LIMITS",
            "name": "Execution Step & Timeout Guardian",
            "description": "Enforces workflow step budget, duration limits, and max retries",
            "action": "BLOCK",
        },
        {
            "id": "SENSITIVE_OPERATION_APPROVAL",
            "name": "Risk-Based Human Authorization Gate",
            "description": "Routes sensitive, destructive, or critical operations to approval center",
            "action": "REQUIRE_APPROVAL",
        },
    ]
