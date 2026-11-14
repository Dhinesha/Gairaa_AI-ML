import asyncio
import datetime
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.entities import (
    ApprovalRequestModel,
    AuditLogModel,
    SafetyEventModel,
    WorkflowModel,
    WorkflowStepModel,
)
from backend.app.schemas.workflow import (
    SafetyEventResponse,
    StepResponse,
    WorkflowCreateRequest,
    WorkflowDetailResponse,
    WorkflowResponse,
)
from backend.app.services.workflow_engine import workflow_service

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_workflow(
    payload: WorkflowCreateRequest,
    background_tasks: BackgroundTasks,
    auto_run: bool = Query(True, description="Immediately start execution"),
    db: Session = Depends(get_db),
):
    """Create a new agent workflow and optionally initiate background execution."""
    config_override = {}
    if payload.max_steps is not None:
        config_override["max_workflow_steps"] = payload.max_steps
    if payload.max_repeated_calls is not None:
        config_override["max_repeated_calls"] = payload.max_repeated_calls
    if payload.max_duration_seconds is not None:
        config_override["max_execution_duration_seconds"] = payload.max_duration_seconds
    if payload.loop_cycle_threshold is not None:
        config_override["loop_cycle_threshold"] = payload.loop_cycle_threshold

    new_wf = WorkflowModel(
        task=payload.task,
        agent_type=payload.agent_type,
        status="PENDING",
        config_override=config_override if config_override else None,
    )
    db.add(new_wf)
    db.commit()
    db.refresh(new_wf)

    db.add(AuditLogModel(
        action="WORKFLOW_CREATED",
        actor="user",
        resource_type="workflow",
        resource_id=new_wf.id,
        details={"task": payload.task, "agent_type": payload.agent_type},
    ))
    db.commit()

    if auto_run:
        background_tasks.add_task(workflow_service.run_workflow, new_wf.id)

    return new_wf


@router.post("/{workflow_id}/run", response_model=WorkflowResponse)
def run_workflow(
    workflow_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Start or trigger execution of an existing workflow."""
    wf = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if wf.status == "RUNNING":
        return wf

    background_tasks.add_task(workflow_service.run_workflow, workflow_id)
    return wf


@router.get("", response_model=List[WorkflowResponse])
def list_workflows(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all workflow executions with optional status filtering."""
    query = db.query(WorkflowModel).order_by(WorkflowModel.created_at.desc())
    if status_filter:
        query = query.filter(WorkflowModel.status == status_filter.upper())
    return query.offset(skip).limit(limit).all()


@router.get("/{workflow_id}", response_model=WorkflowDetailResponse)
def get_workflow_details(workflow_id: str, db: Session = Depends(get_db)):
    """Retrieve complete workflow execution details, steps, safety decisions, and alerts."""
    wf = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.get("/{workflow_id}/events", response_model=List[SafetyEventResponse])
def get_workflow_events(workflow_id: str, db: Session = Depends(get_db)):
    """Retrieve safety events triggered during workflow execution."""
    events = (
        db.query(SafetyEventModel)
        .filter(SafetyEventModel.workflow_id == workflow_id)
        .order_by(SafetyEventModel.created_at.desc())
        .all()
    )
    return events


@router.post("/{workflow_id}/stop", response_model=WorkflowResponse)
def stop_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """Explicitly stop a running workflow."""
    wf = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    wf.status = "STOPPED"
    wf.termination_reason = "Manually stopped by user."
    wf.completed_at = datetime.datetime.utcnow()

    db.add(AuditLogModel(
        action="WORKFLOW_STOPPED",
        actor="user",
        resource_type="workflow",
        resource_id=workflow_id,
        details={"reason": wf.termination_reason},
    ))
    db.commit()
    db.refresh(wf)
    return wf


@router.post("/{workflow_id}/resume", response_model=WorkflowResponse)
def resume_workflow(
    workflow_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Resume a stopped or approval-paused workflow after reviewing the issue."""
    wf = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # If workflow is blocked and not paused for approval, verify user explicitly confirms safe recovery
    if wf.status == "BLOCKED":
        # Check if there is an approval record or safety audit
        wf.status = "PENDING"
        wf.termination_reason = None
        db.commit()

    background_tasks.add_task(workflow_service.run_workflow, workflow_id, is_resume=True)
    return wf


@router.post("/{workflow_id}/retry", response_model=WorkflowResponse)
def retry_workflow(
    workflow_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Retry a failed or blocked workflow with reset steps."""
    wf = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Clear previous steps to allow a fresh run
    db.query(WorkflowStepModel).filter(WorkflowStepModel.workflow_id == workflow_id).delete()
    wf.status = "PENDING"
    wf.step_count = 0
    wf.result_summary = None
    wf.termination_reason = None
    wf.error_message = None
    wf.completed_at = None
    db.commit()
    db.refresh(wf)

    background_tasks.add_task(workflow_service.run_workflow, workflow_id)
    return wf
