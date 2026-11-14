from typing import Optional
from backend.app.safety.models import (
    ActionRequest,
    RiskLevel,
    SafetyDecision,
    SafetyEvaluationResult,
    WorkflowContext,
)
from backend.app.safety.normalizer import (
    compute_tool_call_hash,
    sanitize_arguments,
)


class RepeatedCallsDetector:
    """
    Detects repeated invocations of the same tool with identical or equivalent arguments.
    Stops runaway execution when the configured limit is exceeded.
    """

    @staticmethod
    def evaluate(
        action: ActionRequest,
        context: WorkflowContext,
        action_hash: Optional[str] = None,
    ) -> Optional[SafetyEvaluationResult]:
        policy = context.policy
        history = context.history
        if not history:
            return None

        if action_hash is None:
            action_hash = compute_tool_call_hash(action.tool_name, action.arguments)

        max_repeats = policy.max_repeated_calls

        # 1. Count consecutive identical calls looking backward from the end of history
        consecutive_count = 0
        for step in reversed(history):
            if step.normalized_hash == action_hash:
                consecutive_count += 1
            else:
                break

        # If adding this call exceeds max_repeated_calls
        if consecutive_count >= max_repeats:
            args_sanitized = sanitize_arguments(action.arguments, policy.sensitive_argument_patterns)
            return SafetyEvaluationResult(
                decision=SafetyDecision.BLOCK,
                reason=(
                    f"Repeated tool-call limit exceeded: tool '{action.tool_name}' with identical "
                    f"or equivalent arguments was already invoked {consecutive_count} consecutive times "
                    f"(maximum allowed: {max_repeats})."
                ),
                rule_triggered="REPEATED_TOOL_CALL_DETECTED",
                risk_level=RiskLevel.HIGH,
                details={
                    "tool_name": action.tool_name,
                    "consecutive_count": consecutive_count,
                    "max_repeated_calls": max_repeats,
                    "call_hash": action_hash,
                },
                sanitized_arguments=args_sanitized,
                normalized_hash=action_hash,
            )

        # 2. Windowed frequency check: within the last 2 * max_repeats steps
        window_size = max_repeats * 2
        recent_steps = history[-window_size:] if len(history) > window_size else history
        frequency_in_window = sum(1 for step in recent_steps if step.normalized_hash == action_hash)

        if frequency_in_window >= max_repeats + 1:
            args_sanitized = sanitize_arguments(action.arguments, policy.sensitive_argument_patterns)
            return SafetyEvaluationResult(
                decision=SafetyDecision.BLOCK,
                reason=(
                    f"High-frequency tool repetition detected: tool '{action.tool_name}' appeared "
                    f"{frequency_in_window} times within the last {len(recent_steps)} steps without progress."
                ),
                rule_triggered="REPEATED_CALL_FREQUENCY_DETECTED",
                risk_level=RiskLevel.HIGH,
                details={
                    "tool_name": action.tool_name,
                    "frequency_in_window": frequency_in_window,
                    "window_size": len(recent_steps),
                    "call_hash": action_hash,
                },
                sanitized_arguments=args_sanitized,
                normalized_hash=action_hash,
            )

        return None
