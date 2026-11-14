import logging
from typing import Optional
from backend.app.safety.detectors.execution_limits import ExecutionLimitsDetector
from backend.app.safety.detectors.loop_detector import LoopDetector
from backend.app.safety.detectors.no_progress import NoProgressDetector
from backend.app.safety.detectors.repeated_calls import RepeatedCallsDetector
from backend.app.safety.detectors.risk_policy import RiskPolicyDetector
from backend.app.safety.models import (
    ActionRequest,
    RiskLevel,
    SafetyDecision,
    SafetyEvaluationResult,
    StepRecord,
    ToolOutcome,
    WorkflowContext,
)
from backend.app.safety.normalizer import (
    compute_result_hash,
    compute_tool_call_hash,
    sanitize_arguments,
)

logger = logging.getLogger("safety.engine")


class SafetyEngine:
    """
    Main Pre-Execution Safety Gate and Loop Prevention Supervisor.
    Intercepts and inspects proposed AI agent actions before execution,
    evaluating resource limits, risk policies, repeated calls, infinite loop cycles,
    and no-progress conditions.
    """

    def __init__(self):
        logger.info("Initialized SafetyEngine supervisor.")

    def evaluate(
        self,
        action: ActionRequest,
        context: WorkflowContext,
    ) -> SafetyEvaluationResult:
        """
        Evaluate a proposed action through all safety layers in order of priority:
        1. Execution limits (Timeout, max steps, total calls, retries) -> BLOCK
        2. Risk-based policy gate (Sensitive tools, destructive args) -> REQUIRE_APPROVAL
        3. Repeated tool-call detection (Identical / equivalent args) -> BLOCK
        4. Infinite-loop & cyclic pattern detection -> BLOCK
        5. No-progress detection (Consecutive failures / zero-delta outputs) -> BLOCK
        6. Default -> ALLOW
        """
        policy = context.policy
        action_hash = compute_tool_call_hash(action.tool_name, action.arguments)
        sanitized_args = sanitize_arguments(action.arguments, policy.sensitive_argument_patterns)

        # 1. Gate: Execution Limits & Timeouts
        limits_result = ExecutionLimitsDetector.evaluate(action, context)
        if limits_result:
            limits_result.sanitized_arguments = sanitized_args
            limits_result.normalized_hash = action_hash
            logger.warning(
                f"[GATE: LIMITS] Workflow {context.workflow_id} Step {action.step_number} "
                f"BLOCKED: {limits_result.reason}"
            )
            return limits_result

        # 2. Gate: Risk Policy & Sensitive Action Approval
        risk_result = RiskPolicyDetector.evaluate(action, context)
        if risk_result:
            risk_result.sanitized_arguments = sanitized_args
            risk_result.normalized_hash = action_hash
            logger.info(
                f"[GATE: RISK] Workflow {context.workflow_id} Step {action.step_number} "
                f"REQUIRE_APPROVAL: {risk_result.reason}"
            )
            return risk_result

        # 3. Gate: Repeated Tool-Call Detection
        repeat_result = RepeatedCallsDetector.evaluate(action, context, action_hash=action_hash)
        if repeat_result:
            logger.warning(
                f"[GATE: REPEAT] Workflow {context.workflow_id} Step {action.step_number} "
                f"BLOCKED: {repeat_result.reason}"
            )
            return repeat_result

        # 4. Gate: Infinite Loop & Cyclic Pattern Detection
        loop_result = LoopDetector.evaluate(action, context, action_hash=action_hash)
        if loop_result:
            logger.warning(
                f"[GATE: LOOP] Workflow {context.workflow_id} Step {action.step_number} "
                f"BLOCKED: {loop_result.reason}"
            )
            return loop_result

        # 5. Gate: No-Progress Detection
        no_progress_result = NoProgressDetector.evaluate_pre_execution(action, context, action_hash=action_hash)
        if no_progress_result:
            logger.warning(
                f"[GATE: NO_PROGRESS] Workflow {context.workflow_id} Step {action.step_number} "
                f"BLOCKED: {no_progress_result.reason}"
            )
            return no_progress_result

        # 6. Passed all safety gates: ALLOW
        logger.debug(
            f"[GATE: PASS] Workflow {context.workflow_id} Step {action.step_number} "
            f"Tool '{action.tool_name}' ALLOWED."
        )
        return SafetyEvaluationResult(
            decision=SafetyDecision.ALLOW,
            reason="Action verified and passed all safety gates and loop policies.",
            rule_triggered=None,
            risk_level=RiskLevel.LOW,
            details={"step_number": action.step_number, "tool_name": action.tool_name},
            sanitized_arguments=sanitized_args,
            normalized_hash=action_hash,
        )

    def record_step_result(
        self,
        step_number: int,
        action: ActionRequest,
        outcome: ToolOutcome,
        safety_result: SafetyEvaluationResult,
    ) -> StepRecord:
        """Create a complete audited step record after execution."""
        res_hash = compute_result_hash(outcome.result if outcome.success else outcome.error)
        return StepRecord(
            step_number=step_number,
            tool_name=action.tool_name,
            arguments=action.arguments,
            normalized_hash=safety_result.normalized_hash or compute_tool_call_hash(action.tool_name, action.arguments),
            result=outcome.result,
            result_hash=res_hash,
            success=outcome.success,
            error=outcome.error,
            safety_decision=safety_result.decision,
            rule_triggered=safety_result.rule_triggered,
            risk_level=safety_result.risk_level,
            duration_ms=outcome.duration_ms,
        )


# Singleton instance
default_safety_engine = SafetyEngine()
