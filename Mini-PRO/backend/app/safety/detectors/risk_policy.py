import re
from typing import Optional
from backend.app.safety.models import (
    ActionRequest,
    RiskLevel,
    SafetyDecision,
    SafetyEvaluationResult,
    WorkflowContext,
)
from backend.app.safety.normalizer import sanitize_arguments


class RiskPolicyDetector:
    """Evaluates proposed actions against risk and sensitivity policies to gate execution."""

    CRITICAL_PATTERNS = [
        r"drop[_\s]+database",
        r"delete[_\s]+database",
        r"grant[_\s]+admin",
        r"execute[_\s]+payment",
        r"format[_\s]+disk",
        r"rm[_\s]+-rf",
    ]

    @classmethod
    def evaluate(
        cls,
        action: ActionRequest,
        context: WorkflowContext,
    ) -> Optional[SafetyEvaluationResult]:
        policy = context.policy
        tool_name = action.tool_name.strip().lower()
        args_sanitized = sanitize_arguments(action.arguments, policy.sensitive_argument_patterns)

        # 1. Check critical regex patterns
        for pattern in cls.CRITICAL_PATTERNS:
            if re.search(pattern, tool_name):
                return SafetyEvaluationResult(
                    decision=SafetyDecision.REQUIRE_APPROVAL,
                    reason=f"Action '{action.tool_name}' involves a CRITICAL risk operation matching safety rule '{pattern}'.",
                    rule_triggered="CRITICAL_OPERATION_APPROVAL_REQUIRED",
                    risk_level=RiskLevel.CRITICAL,
                    details={
                        "tool_name": action.tool_name,
                        "matched_pattern": pattern,
                        "risk_level": "CRITICAL",
                    },
                    sanitized_arguments=args_sanitized,
                )

        # 2. Check configured sensitive tools list
        for sensitive_tool in policy.sensitive_tools:
            s_name = sensitive_tool.strip().lower()
            if s_name == tool_name or s_name in tool_name:
                # Assess risk level
                risk = RiskLevel.HIGH
                if any(x in tool_name for x in ["delete", "drop", "salary", "payment"]):
                    risk = RiskLevel.CRITICAL
                elif any(x in tool_name for x in ["email", "export", "grant"]):
                    risk = RiskLevel.HIGH
                else:
                    risk = RiskLevel.MEDIUM

                return SafetyEvaluationResult(
                    decision=SafetyDecision.REQUIRE_APPROVAL,
                    reason=(
                        f"Action '{action.tool_name}' is classified as a sensitive operation "
                        f"under policy '{sensitive_tool}' and requires human authorization before execution."
                    ),
                    rule_triggered="SENSITIVE_TOOL_POLICY",
                    risk_level=risk,
                    details={
                        "tool_name": action.tool_name,
                        "matched_policy": sensitive_tool,
                        "risk_level": risk.value,
                    },
                    sanitized_arguments=args_sanitized,
                )

        # 3. Check for destructive flags inside arguments
        destructive_arg_keys = {"force", "cascade", "drop_all", "delete_permanent", "overwrite"}
        for k, v in action.arguments.items():
            k_clean = str(k).strip().lower()
            if k_clean in destructive_arg_keys and bool(v):
                return SafetyEvaluationResult(
                    decision=SafetyDecision.REQUIRE_APPROVAL,
                    reason=(
                        f"Action '{action.tool_name}' contains destructive argument '{k}={v}'. "
                        f"Human authorization is required."
                    ),
                    rule_triggered="DESTRUCTIVE_ARGUMENT_APPROVAL_REQUIRED",
                    risk_level=RiskLevel.HIGH,
                    details={
                        "tool_name": action.tool_name,
                        "argument_key": k,
                        "argument_value": str(v),
                    },
                    sanitized_arguments=args_sanitized,
                )

        return None
