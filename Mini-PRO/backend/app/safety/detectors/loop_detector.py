from typing import List, Optional
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


class LoopDetector:
    """
    Detects infinite loops and repeating multi-step action cycles (e.g. A -> B -> A -> B).
    Evaluates sequence patterns of period K >= 2 up to max_cycle_length.
    """

    MAX_PERIOD_TO_CHECK = 6

    @classmethod
    def evaluate(
        cls,
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

        # Build full sequence including the proposed action
        history_hashes = [step.normalized_hash for step in history]
        sequence = history_hashes + [action_hash]
        history_tools = [step.tool_name for step in history]
        tool_sequence = history_tools + [action.tool_name]

        threshold = policy.loop_cycle_threshold  # Default e.g. 2 cycles

        # Test periods K from 2 up to min(MAX_PERIOD_TO_CHECK, len(sequence) // threshold)
        max_k = min(cls.MAX_PERIOD_TO_CHECK, len(sequence) // threshold)

        for k in range(2, max_k + 1):
            pattern = sequence[-k:]
            pattern_tools = tool_sequence[-k:]

            # Check if sequence ends with 'threshold' copies of pattern
            required_len = k * threshold
            if len(sequence) < required_len:
                continue

            sub_seq = sequence[-required_len:]
            expected = pattern * threshold

            if sub_seq == expected:
                pattern_str = " -> ".join(pattern_tools)
                args_sanitized = sanitize_arguments(action.arguments, policy.sensitive_argument_patterns)
                return SafetyEvaluationResult(
                    decision=SafetyDecision.BLOCK,
                    reason=(
                        f"Infinite loop pattern detected: cyclic sequence of length {k} "
                        f"('{pattern_str}') has completed {threshold} full cycles without workflow progression."
                    ),
                    rule_triggered="INFINITE_LOOP_PREVENTION",
                    risk_level=RiskLevel.CRITICAL,
                    details={
                        "cycle_period": k,
                        "cycle_repetitions": threshold,
                        "pattern_tools": pattern_tools,
                        "pattern_sequence": pattern_str,
                    },
                    sanitized_arguments=args_sanitized,
                    normalized_hash=action_hash,
                )

        return None
