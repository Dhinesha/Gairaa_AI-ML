import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class WorkflowCreateRequest(BaseModel):
    task: str = Field(..., description="The objective or instruction for the AI agent")
    agent_type: str = Field(
        default="mock:normal_success",
        description="Agent preset: mock:normal_success, mock:infinite_loop, mock:repeated_calls, mock:no_progress, mock:sensitive_action, gemini",
    )
    max_steps: Optional[int] = Field(default=None, description="Max steps override")
    max_repeated_calls: Optional[int] = Field(default=None, description="Max repeated calls override")
    max_duration_seconds: Optional[float] = Field(default=None, description="Max execution seconds override")
    loop_cycle_threshold: Optional[int] = Field(default=None, description="Loop cycles threshold override")


class StepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    step_number: int
    tool_name: str
    raw_arguments: Optional[Dict[str, Any]] = None
    sanitized_arguments: Optional[Dict[str, Any]] = None
    tool_result: Optional[Any] = None
    duration_ms: float
    status: str
    safety_decision: str
    rule_triggered: Optional[str] = None
    risk_level: str
    normalized_hash: Optional[str] = None
    timestamp: datetime.datetime


class SafetyEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workflow_id: str
    step_id: Optional[str] = None
    event_type: str
    severity: str
    rule_name: str
    details: Optional[Dict[str, Any]] = None
    decision: str
    created_at: datetime.datetime


class ApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workflow_id: str
    step_id: Optional[str] = None
    tool_name: str
    tool_arguments: Optional[Dict[str, Any]] = None
    risk_level: str
    reason: str
    status: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime.datetime] = None
    comment: Optional[str] = None
    created_at: datetime.datetime


class ApprovalActionRequest(BaseModel):
    reviewed_by: str = Field(default="admin-reviewer", description="Authorized reviewer identity")
    comment: Optional[str] = Field(default="Reviewed and confirmed safety policy compliance.", description="Review comment")


class WorkflowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task: str
    agent_type: str
    status: str
    step_count: int
    config_override: Optional[Dict[str, Any]] = None
    result_summary: Optional[str] = None
    termination_reason: Optional[str] = None
    error_message: Optional[str] = None
    execution_duration_seconds: float
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None


class WorkflowDetailResponse(WorkflowResponse):
    steps: List[StepResponse] = Field(default_factory=list)
    events: List[SafetyEventResponse] = Field(default_factory=list)
    approvals: List[ApprovalResponse] = Field(default_factory=list)


class SafetyPolicyConfigSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = "Default Production Safety Policy"
    is_active: bool = True
    max_workflow_steps: int = 20
    max_repeated_calls: int = 3
    max_execution_duration_seconds: float = 300.0
    max_tool_calls: int = 50
    max_retries: int = 3
    loop_cycle_threshold: int = 2
    max_no_progress_steps: int = 3
    auto_block_no_progress: bool = True
    sensitive_tools: List[str] = Field(default_factory=list)
    sensitive_argument_patterns: List[str] = Field(default_factory=list)


class AnalyticsResponse(BaseModel):
    total_workflows: int
    successful_workflows: int
    blocked_workflows: int
    loop_detected_workflows: int
    approval_pending_count: int
    failed_workflows: int
    running_workflows: int
    avg_duration_seconds: float
    tool_distribution: Dict[str, int]
    severity_distribution: Dict[str, int]
    recent_events: List[SafetyEventResponse]
