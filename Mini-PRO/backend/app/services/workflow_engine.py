import asyncio
import datetime
import logging
import time
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from backend.app.agent.gemini_agent import GeminiAgent
from backend.app.agent.mock_agent import DeterministicMockAgent
from backend.app.core.redis_client import cache_client
from backend.app.database.session import SessionLocal
from backend.app.models.entities import (
    ApprovalRequestModel,
    AuditLogModel,
    SafetyEventModel,
    WorkflowModel,
    WorkflowStepModel,
)
from backend.app.monitoring.metrics import (
    ACTIVE_WORKFLOWS_GAUGE,
    SAFETY_EVENTS_TOTAL,
    STEPS_TOTAL,
    WORKFLOW_DURATION_HISTOGRAM,
    WORKFLOWS_TOTAL,
)
from backend.app.safety.engine import default_safety_engine
from backend.app.safety.models import (
    ActionRequest,
    RiskLevel,
    SafetyDecision,
    SafetyPolicy,
    StepRecord,
    ToolOutcome,
    WorkflowContext,
)
from backend.app.safety.normalizer import (
    compute_result_hash,
    compute_tool_call_hash,
    sanitize_arguments,
)
from backend.app.tools.registry import default_tool_registry

logger = logging.getLogger("workflow.engine")


class WorkflowExecutionService:
    """
    Coordinates end-to-end agent workflow execution, enforces safety gates,
    records steps, manages pauses for human approval, and ensures thread/process safety.
    """

    def __init__(self):
        self.safety_engine = default_safety_engine
        self.tool_registry = default_tool_registry

    def _get_agent(self, agent_type: str):
        if agent_type.startswith("gemini"):
            return GeminiAgent()
        return DeterministicMockAgent(scenario=agent_type)

    def _build_policy(self, config_override: Optional[Dict[str, Any]]) -> SafetyPolicy:
        policy = SafetyPolicy()
        if not config_override:
            return policy

        if "max_workflow_steps" in config_override and config_override["max_workflow_steps"]:
            policy.max_workflow_steps = int(config_override["max_workflow_steps"])
        if "max_repeated_calls" in config_override and config_override["max_repeated_calls"]:
            policy.max_repeated_calls = int(config_override["max_repeated_calls"])
        if "max_execution_duration_seconds" in config_override and config_override["max_execution_duration_seconds"]:
            policy.max_execution_duration_seconds = float(config_override["max_execution_duration_seconds"])
        if "loop_cycle_threshold" in config_override and config_override["loop_cycle_threshold"]:
            policy.loop_cycle_threshold = int(config_override["loop_cycle_threshold"])
        return policy

    async def run_workflow(self, workflow_id: str, is_resume: bool = False, approved_step_id: Optional[str] = None):
        """
        Main execution loop for a workflow.
        Can run as a background task.
        """
        # Concurrency guard: acquire lock to prevent duplicate concurrent runs
        lock_name = f"wf_{workflow_id}"
        if not cache_client.acquire_lock(lock_name, timeout_seconds=60):
            logger.warning(f"Workflow {workflow_id} is already actively running. Execution request ignored.")
            return

        db: Session = SessionLocal()
        ACTIVE_WORKFLOWS_GAUGE.inc()
        start_epoch = time.time()

        try:
            workflow: WorkflowModel = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
            if not workflow:
                logger.error(f"Workflow {workflow_id} not found in database.")
                return

            # Check if stopped or completed
            if workflow.status in ("COMPLETED", "BLOCKED", "STOPPED") and not is_resume:
                logger.info(f"Workflow {workflow_id} already in terminal state {workflow.status}.")
                return

            workflow.status = "RUNNING"
            db.commit()

            policy = self._build_policy(workflow.config_override)
            agent = self._get_agent(workflow.agent_type)

            # Rebuild historical StepRecords from DB
            existing_steps = (
                db.query(WorkflowStepModel)
                .filter(WorkflowStepModel.workflow_id == workflow_id)
                .order_by(WorkflowStepModel.step_number)
                .all()
            )

            history_records = []
            for s in existing_steps:
                if s.status != "BLOCKED":
                    history_records.append(
                        StepRecord(
                            step_number=s.step_number,
                            tool_name=s.tool_name,
                            arguments=s.raw_arguments or {},
                            normalized_hash=s.normalized_hash or compute_tool_call_hash(s.tool_name, s.raw_arguments or {}),
                            result=s.tool_result,
                            result_hash=compute_result_hash(s.tool_result),
                            success=(s.status == "SUCCESS"),
                            safety_decision=SafetyDecision(s.safety_decision) if s.safety_decision in SafetyDecision.__members__ else SafetyDecision.ALLOW,
                            rule_triggered=s.rule_triggered,
                            risk_level=RiskLevel(s.risk_level) if s.risk_level in RiskLevel.__members__ else RiskLevel.LOW,
                            duration_ms=s.duration_ms,
                        )
                    )

            context = WorkflowContext(
                workflow_id=workflow_id,
                task=workflow.task,
                start_time_epoch=start_epoch,
                history=history_records,
                policy=policy,
            )

            # Check if this run is resuming after an approved action
            pending_approved_action: Optional[ActionRequest] = None
            if is_resume and approved_step_id:
                app_req = db.query(ApprovalRequestModel).filter(
                    ApprovalRequestModel.workflow_id == workflow_id,
                    ApprovalRequestModel.status == "APPROVED"
                ).order_by(ApprovalRequestModel.created_at.desc()).first()
                if app_req:
                    pending_approved_action = ActionRequest(
                        tool_name=app_req.tool_name,
                        arguments=app_req.tool_arguments or {},
                        workflow_id=workflow_id,
                        step_number=len(history_records) + 1,
                    )

            # Step-by-step Execution Loop
            while True:
                # Check for external stop request
                db.refresh(workflow)
                if workflow.status == "STOPPED":
                    logger.info(f"Workflow {workflow_id} was stopped by user request.")
                    break

                current_step_num = len(context.history) + 1

                # If we have an approved action pending execution from a resume event
                if pending_approved_action:
                    proposed_action = pending_approved_action
                    pending_approved_action = None  # Consume it
                    logger.info(f"Executing previously approved action '{proposed_action.tool_name}' on resume.")
                    safety_result = self.safety_engine.evaluate(proposed_action, context)
                    # Force ALLOW since an authorized human explicitly approved it
                    safety_result.decision = SafetyDecision.ALLOW
                    safety_result.reason = f"Human authorized execution (Approved by reviewer)."
                else:
                    # Agent proposes next action
                    agent_action = await agent.propose_next_action(
                        task=workflow.task,
                        history=context.history,
                        step_number=current_step_num,
                    )

                    # If agent indicates task is finished
                    if agent_action.is_finish:
                        workflow.status = "COMPLETED"
                        workflow.result_summary = agent_action.final_answer or "Task successfully achieved."
                        workflow.completed_at = datetime.datetime.utcnow()
                        workflow.execution_duration_seconds = round(time.time() - start_epoch, 2)
                        workflow.step_count = len(context.history)
                        
                        WORKFLOWS_TOTAL.labels(agent_type=workflow.agent_type, status="COMPLETED").inc()
                        WORKFLOW_DURATION_HISTOGRAM.observe(workflow.execution_duration_seconds)

                        db.add(AuditLogModel(
                            action="WORKFLOW_COMPLETED",
                            actor="system",
                            resource_type="workflow",
                            resource_id=workflow_id,
                            details={"result": workflow.result_summary, "steps": workflow.step_count},
                        ))
                        db.commit()
                        logger.info(f"Workflow {workflow_id} completed successfully in {workflow.step_count} steps.")
                        break

                    proposed_action = ActionRequest(
                        tool_name=agent_action.tool_name,
                        arguments=agent_action.arguments,
                        workflow_id=workflow_id,
                        step_number=current_step_num,
                    )

                    # Inspect proposed action through Safety Engine
                    safety_result = self.safety_engine.evaluate(proposed_action, context)

                STEPS_TOTAL.labels(tool_name=proposed_action.tool_name, decision=safety_result.decision.value).inc()

                # -----------------------------------------------------
                # DECISION 1: REQUIRE_APPROVAL
                # -----------------------------------------------------
                if safety_result.decision == SafetyDecision.REQUIRE_APPROVAL:
                    workflow.status = "PAUSED_APPROVAL"
                    workflow.step_count = current_step_num
                    workflow.execution_duration_seconds = round(time.time() - start_epoch, 2)

                    # Save step record
                    step_entity = WorkflowStepModel(
                        workflow_id=workflow_id,
                        step_number=current_step_num,
                        tool_name=proposed_action.tool_name,
                        raw_arguments=proposed_action.arguments,
                        sanitized_arguments=safety_result.sanitized_arguments,
                        status="BLOCKED",
                        safety_decision="REQUIRE_APPROVAL",
                        rule_triggered=safety_result.rule_triggered,
                        risk_level=safety_result.risk_level.value,
                        normalized_hash=safety_result.normalized_hash,
                    )
                    db.add(step_entity)
                    db.flush()

                    # Create Approval Request
                    approval_req = ApprovalRequestModel(
                        workflow_id=workflow_id,
                        step_id=step_entity.id,
                        tool_name=proposed_action.tool_name,
                        tool_arguments=proposed_action.arguments,
                        risk_level=safety_result.risk_level.value,
                        reason=safety_result.reason,
                        status="PENDING",
                    )
                    db.add(approval_req)

                    # Record Safety Event
                    event_entity = SafetyEventModel(
                        workflow_id=workflow_id,
                        step_id=step_entity.id,
                        event_type="APPROVAL_REQUIRED",
                        severity="HIGH",
                        rule_name=safety_result.rule_triggered or "APPROVAL_REQUIRED",
                        details=safety_result.details,
                        decision="REQUIRE_APPROVAL",
                    )
                    db.add(event_entity)
                    SAFETY_EVENTS_TOTAL.labels(event_type="APPROVAL_REQUIRED", severity="HIGH").inc()

                    db.add(AuditLogModel(
                        action="APPROVAL_REQUESTED",
                        actor="safety_gate",
                        resource_type="workflow",
                        resource_id=workflow_id,
                        details={"tool": proposed_action.tool_name, "reason": safety_result.reason},
                    ))
                    db.commit()
                    logger.info(f"Workflow {workflow_id} paused at step {current_step_num} awaiting approval.")
                    break

                # -----------------------------------------------------
                # DECISION 2: BLOCK
                # -----------------------------------------------------
                elif safety_result.decision == SafetyDecision.BLOCK:
                    workflow.status = "BLOCKED"
                    workflow.termination_reason = safety_result.reason
                    workflow.completed_at = datetime.datetime.utcnow()
                    workflow.step_count = current_step_num
                    workflow.execution_duration_seconds = round(time.time() - start_epoch, 2)

                    # Save blocked step
                    step_entity = WorkflowStepModel(
                        workflow_id=workflow_id,
                        step_number=current_step_num,
                        tool_name=proposed_action.tool_name,
                        raw_arguments=proposed_action.arguments,
                        sanitized_arguments=safety_result.sanitized_arguments,
                        status="BLOCKED",
                        safety_decision="BLOCK",
                        rule_triggered=safety_result.rule_triggered,
                        risk_level=safety_result.risk_level.value,
                        normalized_hash=safety_result.normalized_hash,
                    )
                    db.add(step_entity)
                    db.flush()

                    # Record Safety Event
                    event_type = safety_result.rule_triggered or "ACTION_BLOCKED"
                    event_entity = SafetyEventModel(
                        workflow_id=workflow_id,
                        step_id=step_entity.id,
                        event_type=event_type,
                        severity="CRITICAL" if "LOOP" in event_type else "HIGH",
                        rule_name=event_type,
                        details=safety_result.details,
                        decision="BLOCK",
                    )
                    db.add(event_entity)
                    SAFETY_EVENTS_TOTAL.labels(
                        event_type=event_type,
                        severity="CRITICAL" if "LOOP" in event_type else "HIGH",
                    ).inc()

                    WORKFLOWS_TOTAL.labels(agent_type=workflow.agent_type, status="BLOCKED").inc()

                    db.add(AuditLogModel(
                        action="WORKFLOW_BLOCKED",
                        actor="safety_gate",
                        resource_type="workflow",
                        resource_id=workflow_id,
                        details={"rule": safety_result.rule_triggered, "reason": safety_result.reason},
                    ))
                    db.commit()
                    logger.warning(f"Workflow {workflow_id} BLOCKED at step {current_step_num}: {safety_result.reason}")
                    break

                # -----------------------------------------------------
                # DECISION 3: ALLOW -> Execute Tool
                # -----------------------------------------------------
                else:
                    outcome: ToolOutcome = await self.tool_registry.execute(
                        tool_name=proposed_action.tool_name,
                        arguments=proposed_action.arguments,
                    )

                    # Record step in database
                    step_entity = WorkflowStepModel(
                        workflow_id=workflow_id,
                        step_number=current_step_num,
                        tool_name=proposed_action.tool_name,
                        raw_arguments=proposed_action.arguments,
                        sanitized_arguments=safety_result.sanitized_arguments,
                        tool_result=outcome.result if outcome.success else {"error": outcome.error},
                        duration_ms=outcome.duration_ms,
                        status="SUCCESS" if outcome.success else "FAILED",
                        safety_decision="ALLOW",
                        risk_level="LOW",
                        normalized_hash=safety_result.normalized_hash,
                    )
                    db.add(step_entity)

                    # Update context history
                    step_rec = self.safety_engine.record_step_result(
                        step_number=current_step_num,
                        action=proposed_action,
                        outcome=outcome,
                        safety_result=safety_result,
                    )
                    context.history.append(step_rec)
                    workflow.step_count = len(context.history)
                    workflow.execution_duration_seconds = round(time.time() - start_epoch, 2)
                    db.commit()

                    # Yield control briefly to allow other async tasks
                    await asyncio.sleep(0.02)

        except Exception as e:
            logger.exception(f"Unexpected execution error in workflow {workflow_id}: {e}")
            try:
                wf = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
                if wf:
                    wf.status = "FAILED"
                    wf.error_message = str(e)
                    wf.completed_at = datetime.datetime.utcnow()
                    db.commit()
            except Exception:
                pass
        finally:
            ACTIVE_WORKFLOWS_GAUGE.dec()
            cache_client.release_lock(lock_name)
            db.close()


workflow_service = WorkflowExecutionService()
