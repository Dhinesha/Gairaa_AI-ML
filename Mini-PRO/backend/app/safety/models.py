from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SafetyDecision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ActionRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    workflow_id: Optional[str] = None
    step_number: int = 1


class ToolOutcome(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    result: Any = None
    success: bool = True
    error: Optional[str] = None
    duration_ms: float = 0.0


class SafetyEvaluationResult(BaseModel):
    decision: SafetyDecision
    reason: str
    rule_triggered: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW
    details: Dict[str, Any] = Field(default_factory=dict)
    sanitized_arguments: Dict[str, Any] = Field(default_factory=dict)
    normalized_hash: Optional[str] = None


class SafetyPolicy(BaseModel):
    max_workflow_steps: int = 20
    max_repeated_calls: int = 3
    max_execution_duration_seconds: float = 300.0
    max_tool_calls: int = 50
    max_retries: int = 3
    loop_cycle_threshold: int = 2
    max_no_progress_steps: int = 3
    auto_block_no_progress: bool = True
    sensitive_tools: List[str] = Field(
        default_factory=lambda: [
            "modify_employee_salary",
            "delete_employee_record",
            "execute_payment",
            "drop_database_table",
            "send_external_email",
            "grant_admin_access",
        ]
    )
    sensitive_argument_patterns: List[str] = Field(
        default_factory=lambda: [
            "password",
            "secret",
            "token",
            "api_key",
            "credit_card",
            "ssn",
        ]
    )


class StepRecord(BaseModel):
    step_number: int
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    normalized_hash: str
    result: Any = None
    result_hash: Optional[str] = None
    success: bool = True
    error: Optional[str] = None
    safety_decision: SafetyDecision = SafetyDecision.ALLOW
    rule_triggered: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW
    duration_ms: float = 0.0


class WorkflowContext(BaseModel):
    workflow_id: str
    task: str
    start_time_epoch: float
    history: List[StepRecord] = Field(default_factory=list)
    policy: SafetyPolicy = Field(default_factory=SafetyPolicy)
    current_retry_count: int = 0
