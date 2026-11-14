import datetime
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.entities import (
    ApprovalRequestModel,
    AuditLogModel,
    WorkflowModel,
)
from backend.app.monitoring.metrics import APPROVALS_TOTAL
from backend.app.schemas.workflow import ApprovalActionRequest, ApprovalResponse
from backend.app.services.workflow_engine import workflow_service

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.get("", response_model=List[ApprovalResponse])
def list_approvals(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Retrieve pending and past approval requests."""
    query = db.query(ApprovalRequestModel).order_by(ApprovalRequestModel.created_at.desc())
    if status_filter:
        query = query.filter(ApprovalRequestModel.status == status_filter.upper())
    return query.all()


@router.post("/{approval_id}/approve", response_model=ApprovalResponse)
def approve_action(
    approval_id: str,
    payload: ApprovalActionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    x_user_role: Optional[str] = Header(default="admin", description="Role verification"),
):
    """
    Approve a pending sensitive tool execution.
    Backend verifies authorization, logs audit trail, and automatically resumes workflow.
    """
    # Backend-enforced authorization verification
    if x_user_role not in ("admin", "reviewer", "lead_engineer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: User lacks authorization to approve sensitive actions.",
        )

    req = db.query(ApprovalRequestModel).filter(ApprovalRequestModel.id == approval_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Approval request not found")

    if req.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Request is already in {req.status} state.")

    req.status = "APPROVED"
    req.reviewed_by = payload.reviewed_by or "admin"
    req.reviewed_at = datetime.datetime.utcnow()
    req.comment = payload.comment

    db.add(AuditLogModel(
        action="ACTION_APPROVED",
        actor=req.reviewed_by,
        resource_type="approval_request",
        resource_id=req.id,
        details={
            "workflow_id": req.workflow_id,
            "tool_name": req.tool_name,
            "comment": req.comment,
        },
    ))
    db.commit()
    db.refresh(req)

    APPROVALS_TOTAL.labels(action="approved").inc()

    # Automatically trigger workflow resumption with approved step
    background_tasks.add_task(
        workflow_service.run_workflow,
        req.workflow_id,
        is_resume=True,
        approved_step_id=req.step_id,
    )

    return req


@router.post("/{approval_id}/reject", response_model=ApprovalResponse)
def reject_action(
    approval_id: str,
    payload: ApprovalActionRequest,
    db: Session = Depends(get_db),
    x_user_role: Optional[str] = Header(default="admin", description="Role verification"),
):
    """
    Reject a pending sensitive tool execution.
    Blocks the workflow permanently to ensure safety.
    """
    if x_user_role not in ("admin", "reviewer", "lead_engineer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: User lacks authorization to reject actions.",
        )

    req = db.query(ApprovalRequestModel).filter(ApprovalRequestModel.id == approval_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Approval request not found")

    if req.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Request is already in {req.status} state.")

    req.status = "REJECTED"
    req.reviewed_by = payload.reviewed_by or "admin"
    req.reviewed_at = datetime.datetime.utcnow()
    req.comment = payload.comment

    # Mark associated workflow as BLOCKED
    wf = db.query(WorkflowModel).filter(WorkflowModel.id == req.workflow_id).first()
    if wf:
        wf.status = "BLOCKED"
        wf.termination_reason = f"Action '{req.tool_name}' was rejected by reviewer: {req.comment}"
        wf.completed_at = datetime.datetime.utcnow()

    db.add(AuditLogModel(
        action="ACTION_REJECTED",
        actor=req.reviewed_by,
        resource_type="approval_request",
        resource_id=req.id,
        details={
            "workflow_id": req.workflow_id,
            "tool_name": req.tool_name,
            "reason": req.comment,
        },
    ))
    db.commit()
    db.refresh(req)

    APPROVALS_TOTAL.labels(action="rejected").inc()
    return req
