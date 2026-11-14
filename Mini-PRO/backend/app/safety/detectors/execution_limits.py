import time
from typing import Optional
from backend.app.safety.models import (
    ActionRequest,
    RiskLevel,
    SafetyDecision,
    SafetyEvaluationResult,
    WorkflowContext,
)


class ExecutionLimitsDetector:
    """Enforces execution budget limits: max steps, max duration, max tool calls, max retries."""

    @staticmethod
    def evaluate(
        action: ActionRequest,
        context: WorkflowContext,
    ) -> Optional[SafetyEvaluationResult]:
        policy = context.policy
        current_time = time.time()
        elapsed_seconds = current_time - context.start_time_epoch

        # 1. Check max execution duration
        if elapsed_seconds > policy.max_execution_duration_seconds:
            return SafetyEvaluationResult(
                decision=SafetyDecision.BLOCK,
                reason=(
                    f"Workflow execution timeout exceeded: {elapsed_seconds:.1f}s elapsed "
                    f"(limit: {policy.max_execution_duration_seconds}s)."
                ),
                rule_triggered="MAX_DURATION_EXCEEDED",
                risk_level=RiskLevel.HIGH,
                details={
                    "elapsed_seconds": round(elapsed_seconds, 2),
                    "max_duration_seconds": policy.max_execution_duration_seconds,
                },
            )

        # 2. Check max workflow steps
        # action.step_number is 1-indexed
        if action.step_number > policy.max_workflow_steps:
            return SafetyEvaluationResult(
                decision=SafetyDecision.BLOCK,
                reason=(
                    f"Maximum workflow steps limit exceeded: attempted step {action.step_number} "
                    f"(limit: {policy.max_workflow_steps})."
                ),
                rule_triggered="MAX_STEPS_EXCEEDED",
                risk_level=RiskLevel.HIGH,
                details={
                    "step_number": action.step_number,
                    "max_workflow_steps": policy.max_workflow_steps,
                },
            )

        # 3. Check total tool calls executed in history
        if len(context.history) >= policy.max_tool_calls:
            return SafetyEvaluationResult(
                decision=SafetyDecision.BLOCK,
                reason=(
                    f"Maximum tool calls budget reached: {len(context.history)} calls executed "
                    f"(limit: {policy.max_tool_calls})."
                ),
                rule_triggered="MAX_TOOL_CALLS_EXCEEDED",
                risk_level=RiskLevel.HIGH,
                details={
                    "executed_tool_calls": len(context.history),
                    "max_tool_calls": policy.max_tool_calls,
                },
            )

        # 4. Check retries limit
        if context.current_retry_count > policy.max_retries:
            return SafetyEvaluationResult(
                decision=SafetyDecision.BLOCK,
                reason=(
                    f"Maximum retries limit exceeded: {context.current_retry_count} retries "
                    f"(limit: {policy.max_retries})."
                ),
                rule_triggered="MAX_RETRIES_EXCEEDED",
                risk_level=RiskLevel.MEDIUM,
                details={
                    "retry_count": context.current_retry_count,
                    "max_retries": policy.max_retries,
                },
            )

        return None
