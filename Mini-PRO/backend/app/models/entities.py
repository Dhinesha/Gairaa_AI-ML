import datetime
import uuid
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from backend.app.database.session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class WorkflowModel(Base):
    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    task = Column(Text, nullable=False)
    agent_type = Column(String(64), nullable=False, default="mock:normal_success")
    status = Column(String(32), nullable=False, default="PENDING", index=True)
    step_count = Column(Integer, default=0)
    config_override = Column(JSON, nullable=True)
    result_summary = Column(Text, nullable=True)
    termination_reason = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    execution_duration_seconds = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    steps = relationship("WorkflowStepModel", back_populates="workflow", cascade="all, delete-orphan", order_by="WorkflowStepModel.step_number")
    events = relationship("SafetyEventModel", back_populates="workflow", cascade="all, delete-orphan", order_by="SafetyEventModel.created_at.desc()")
    approvals = relationship("ApprovalRequestModel", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowStepModel(Base):
    __tablename__ = "workflow_steps"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    step_number = Column(Integer, nullable=False)
    tool_name = Column(String(128), nullable=False)
    raw_arguments = Column(JSON, nullable=True)
    sanitized_arguments = Column(JSON, nullable=True)
    tool_result = Column(JSON, nullable=True)
    duration_ms = Column(Float, default=0.0)
    status = Column(String(32), default="SUCCESS")  # SUCCESS, FAILED, BLOCKED, SKIPPED
    safety_decision = Column(String(32), default="ALLOW")
    rule_triggered = Column(String(128), nullable=True)
    risk_level = Column(String(32), default="LOW")
    normalized_hash = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    workflow = relationship("WorkflowModel", back_populates="steps")


class SafetyEventModel(Base):
    __tablename__ = "safety_events"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id = Column(String(36), nullable=True)
    event_type = Column(String(64), nullable=False, index=True)  # REPEATED_CALL, LOOP_DETECTED, NO_PROGRESS, LIMIT_EXCEEDED, APPROVAL_REQUIRED, ACTION_BLOCKED
    severity = Column(String(32), nullable=False, default="HIGH")  # INFO, WARNING, HIGH, CRITICAL
    rule_name = Column(String(128), nullable=False)
    details = Column(JSON, nullable=True)
    decision = Column(String(32), nullable=False, default="BLOCK")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    workflow = relationship("WorkflowModel", back_populates="events")


class ApprovalRequestModel(Base):
    __tablename__ = "approval_requests"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id = Column(String(36), nullable=True)
    tool_name = Column(String(128), nullable=False)
    tool_arguments = Column(JSON, nullable=True)
    risk_level = Column(String(32), default="HIGH")
    reason = Column(Text, nullable=False)
    status = Column(String(32), default="PENDING", index=True)  # PENDING, APPROVED, REJECTED
    reviewed_by = Column(String(128), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    workflow = relationship("WorkflowModel", back_populates="approvals")


class SafetyPolicyConfigModel(Base):
    __tablename__ = "safety_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), default="Default Production Safety Policy", unique=True)
    is_active = Column(Boolean, default=True)
    max_workflow_steps = Column(Integer, default=20)
    max_repeated_calls = Column(Integer, default=3)
    max_execution_duration_seconds = Column(Float, default=300.0)
    max_tool_calls = Column(Integer, default=50)
    max_retries = Column(Integer, default=3)
    loop_cycle_threshold = Column(Integer, default=2)
    max_no_progress_steps = Column(Integer, default=3)
    auto_block_no_progress = Column(Boolean, default=True)
    sensitive_tools = Column(JSON, default=list)
    sensitive_argument_patterns = Column(JSON, default=list)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    action = Column(String(64), nullable=False, index=True)
    actor = Column(String(128), default="system")
    resource_type = Column(String(64), nullable=False)
    resource_id = Column(String(64), nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(128), nullable=False)
    email = Column(String(128), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(32), default="student", nullable=False)  # student, developer, security_lead
    organization = Column(String(128), default="Department of AI & Data Science")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

