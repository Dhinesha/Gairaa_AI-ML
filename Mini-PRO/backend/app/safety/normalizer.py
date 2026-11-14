import hashlib
import json
import re
from typing import Any, Dict, List, Set, Union


def _normalize_value(val: Any) -> Any:
    """Recursively normalize data for deterministic hashing."""
    if isinstance(val, dict):
        return {
            str(k).strip().lower(): _normalize_value(v)
            for k, v in sorted(val.items(), key=lambda item: str(item[0]).strip().lower())
        }
    elif isinstance(val, (list, tuple, set)):
        # If set or list of primitives, sort when possible for order-insensitive equivalence
        normalized_items = [_normalize_value(x) for x in val]
        # Only sort if items are sortable primitives
        try:
            return sorted(normalized_items, key=lambda x: json.dumps(x, sort_keys=True))
        except Exception:
            return normalized_items
    elif isinstance(val, str):
        # Trim leading/trailing whitespace
        s = val.strip()
        # Check if numeric string that can be canonicalized
        try:
            if "." in s:
                f = float(s)
                return round(f, 6)
            else:
                return int(s)
        except ValueError:
            return s
    elif isinstance(val, float):
        return round(val, 6)
    elif isinstance(val, (int, bool)) or val is None:
        return val
    else:
        return str(val)


def normalize_arguments(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return a recursively canonicalized representation of arguments."""
    if not args:
        return {}
    return _normalize_value(args)


def canonical_json_string(obj: Any) -> str:
    """Generate a stable, deterministically formatted JSON string."""
    normalized = _normalize_value(obj)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_sha256(data: str) -> str:
    """Return SHA-256 hex digest of a string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def compute_tool_call_hash(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Compute a deterministic hash for a tool name and arguments pair."""
    normalized_name = tool_name.strip().lower()
    canonical_args = canonical_json_string(arguments)
    combined = f"{normalized_name}::{canonical_args}"
    return compute_sha256(combined)


def compute_result_hash(result: Any) -> str:
    """Compute a deterministic hash for an execution result."""
    canonical_res = canonical_json_string(result)
    return compute_sha256(canonical_res)


def sanitize_arguments(
    arguments: Dict[str, Any],
    sensitive_patterns: Union[List[str], Set[str]] = None
) -> Dict[str, Any]:
    """
    Sanitize sensitive keys (passwords, tokens, keys) in arguments for safe audit/UI display.
    """
    if sensitive_patterns is None:
        sensitive_patterns = {"password", "secret", "token", "api_key", "credit_card", "ssn", "auth"}
    else:
        sensitive_patterns = set(str(p).lower() for p in sensitive_patterns)

    def _sanitize_recursive(val: Any) -> Any:
        if isinstance(val, dict):
            sanitized = {}
            for k, v in val.items():
                k_lower = str(k).lower()
                is_sensitive = any(pat in k_lower for pat in sensitive_patterns)
                if is_sensitive:
                    sanitized[k] = "[REDACTED]"
                else:
                    sanitized[k] = _sanitize_recursive(v)
            return sanitized
        elif isinstance(val, list):
            return [_sanitize_recursive(item) for item in val]
        else:
            return val

    return _sanitize_recursive(arguments)


def are_arguments_equivalent(args_a: Dict[str, Any], args_b: Dict[str, Any]) -> bool:
    """Check whether two argument sets are structurally and semantically equivalent."""
    return canonical_json_string(args_a) == canonical_json_string(args_b)
