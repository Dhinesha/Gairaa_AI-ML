from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.entities import (
    ApprovalRequestModel,
    SafetyEventModel,
    WorkflowModel,
    WorkflowStepModel,
)
from backend.app.schemas.workflow import AnalyticsResponse, SafetyEventResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    """Retrieve real aggregated dashboard analytics from database."""
    total_workflows = db.query(WorkflowModel).count()
    successful_workflows = db.query(WorkflowModel).filter(WorkflowModel.status == "COMPLETED").count()
    blocked_workflows = db.query(WorkflowModel).filter(WorkflowModel.status == "BLOCKED").count()
    failed_workflows = db.query(WorkflowModel).filter(WorkflowModel.status == "FAILED").count()
    running_workflows = db.query(WorkflowModel).filter(WorkflowModel.status == "RUNNING").count()
    approval_pending_count = db.query(ApprovalRequestModel).filter(ApprovalRequestModel.status == "PENDING").count()

    # Loop detected count (from safety events)
    loop_detected_workflows = (
        db.query(func.count(func.distinct(SafetyEventModel.workflow_id)))
        .filter(SafetyEventModel.event_type.like("%LOOP%"))
        .scalar()
        or 0
    )

    # Average execution duration for finished workflows
    avg_duration = (
        db.query(func.avg(WorkflowModel.execution_duration_seconds))
        .filter(WorkflowModel.execution_duration_seconds > 0)
        .scalar()
        or 0.0
    )

    # Tool execution distribution
    tool_steps = db.query(WorkflowStepModel.tool_name).all()
    tool_counts = Counter(s.tool_name for s in tool_steps if s.tool_name)

    # Severity distribution
    severity_events = db.query(SafetyEventModel.severity).all()
    sev_counts = Counter(e.severity for e in severity_events if e.severity)

    # Recent safety events
    recent_events = (
        db.query(SafetyEventModel)
        .order_by(SafetyEventModel.created_at.desc())
        .limit(10)
        .all()
    )

    return AnalyticsResponse(
        total_workflows=total_workflows,
        successful_workflows=successful_workflows,
        blocked_workflows=blocked_workflows,
        loop_detected_workflows=loop_detected_workflows,
        approval_pending_count=approval_pending_count,
        failed_workflows=failed_workflows,
        running_workflows=running_workflows,
        avg_duration_seconds=round(float(avg_duration), 2),
        tool_distribution=dict(tool_counts.most_common(10)),
        severity_distribution=dict(sev_counts),
        recent_events=[SafetyEventResponse.model_validate(e) for e in recent_events],
    )

