from typing import Any, Optional
from backend.app.safety.models import (
    ActionRequest,
    RiskLevel,
    SafetyDecision,
    SafetyEvaluationResult,
    ToolOutcome,
    WorkflowContext,
)
from backend.app.safety.normalizer import (
    compute_result_hash,
    compute_tool_call_hash,
    sanitize_arguments,
)


class NoProgressDetector:
    """
    Tracks step outcomes and detects when repeated actions produce no meaningful progress
    or identical static/error results.
    """

    @classmethod
    def evaluate_pre_execution(
        cls,
        action: ActionRequest,
        context: WorkflowContext,
        action_hash: Optional[str] = None,
    ) -> Optional[SafetyEvaluationResult]:
        """
        Pre-execution check: block action if the agent has repeatedly produced
        identical non-productive results or consecutive errors.
        """
        policy = context.policy
        if not policy.auto_block_no_progress:
            return None

        history = context.history
        if len(history) < policy.max_no_progress_steps:
            return None

        if action_hash is None:
            action_hash = compute_tool_call_hash(action.tool_name, action.arguments)

        max_stagnant = policy.max_no_progress_steps

        # Check the last 'max_stagnant' steps in history
        recent_steps = history[-max_stagnant:]

        # Case 1: Consecutive identical error/failure outcomes
        all_failed = all(not step.success for step in recent_steps)
        if all_failed and len(recent_steps) >= max_stagnant:
            args_sanitized = sanitize_arguments(action.arguments, policy.sensitive_argument_patterns)
            return SafetyEvaluationResult(
                decision=SafetyDecision.BLOCK,
                reason=(
                    f"No-progress block: the last {max_stagnant} consecutive actions failed with unhandled "
                    f"errors without recovery. Proposed action '{action.tool_name}' halted to prevent resource waste."
                ),
                rule_triggered="NO_PROGRESS_CONSECUTIVE_ERRORS",
                risk_level=RiskLevel.HIGH,
                details={
                    "consecutive_failures": max_stagnant,
                    "recent_errors": [s.error for s in recent_steps],
                },
                sanitized_arguments=args_sanitized,
                normalized_hash=action_hash,
            )

        # Case 2: Identical result hashes for the same tool with identical or stagnant outputs
        same_tool_steps = [s for s in history if s.tool_name == action.tool_name]
        if len(same_tool_steps) >= max_stagnant:
            recent_same = same_tool_steps[-max_stagnant:]
            first_hash = recent_same[0].result_hash
            if first_hash and all(s.result_hash == first_hash for s in recent_same):
                args_sanitized = sanitize_arguments(action.arguments, policy.sensitive_argument_patterns)
                return SafetyEvaluationResult(
                    decision=SafetyDecision.BLOCK,
                    reason=(
                        f"No-progress block: tool '{action.tool_name}' has produced identical output "
                        f"{max_stagnant} times with zero informational progress. Halting execution."
                    ),
                    rule_triggered="NO_PROGRESS_IDENTICAL_RESULTS",
                    risk_level=RiskLevel.MEDIUM,
                    details={
                        "tool_name": action.tool_name,
                        "identical_result_count": max_stagnant,
                        "result_hash": first_hash,
                    },
                    sanitized_arguments=args_sanitized,
                    normalized_hash=action_hash,
                )

        return None

    @classmethod
    def evaluate_outcome(cls, outcome: ToolOutcome) -> str:
        """Calculate and return the result hash for auditing and progress tracking."""
        return compute_result_hash(outcome.result if outcome.success else outcome.error)
