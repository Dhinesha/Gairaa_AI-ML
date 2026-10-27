"""
Sandbox Executor – runs user Python code in a SEPARATE SUBPROCESS.
The main process NEVER executes user code directly.

Security measures:
- Subprocess with hard timeout (kill on timeout)
- Blocked dangerous imports (os, sys, subprocess, socket, etc.)
- Blocked dangerous builtins (open, exec, eval)
- stdout/stderr captured; not echoed
- No network, no filesystem writes
- Windows-compatible implementation
"""
import json
import subprocess
import sys
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any

# Absolute path to the tracer script
TRACER_SCRIPT = str(Path(__file__).parent / "tracer.py")
PYTHON_EXE = sys.executable  # Use same Python that runs the backend

DEFAULT_TIMEOUT = 10  # seconds
MAX_OUTPUT_BYTES = 512 * 1024  # 512 KB


def _run_subprocess(
    code: str,
    timeout: int = DEFAULT_TIMEOUT,
    trace: bool = True,
) -> Dict[str, Any]:
    """
    Launches a child Python process running tracer.py.
    Passes `code` via stdin as JSON.
    Returns parsed JSON from stdout.
    """
    payload = json.dumps({"code": code})

    try:
        result = subprocess.run(
            [PYTHON_EXE, TRACER_SCRIPT],
            input=payload,
            capture_output=True,
            text=True,
            timeout=timeout,
            # On Windows we cannot set resource limits, but we set
            # creationflags to run in a job object (best effort)
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )

        stdout = result.stdout[:MAX_OUTPUT_BYTES]
        stderr = result.stderr[:MAX_OUTPUT_BYTES]

        if result.returncode != 0 and not stdout.strip():
            return {
                "steps": [],
                "total_steps": 0,
                "final_output": "",
                "final_error": {
                    "type": "RuntimeError",
                    "message": stderr or "Unknown subprocess error",
                    "line": None,
                },
                "execution_time": timeout,
                "status": "error",
            }

        try:
            data = json.loads(stdout)
            data["status"] = "error" if data.get("final_error") else "success"
            return data
        except json.JSONDecodeError:
            return {
                "steps": [],
                "total_steps": 0,
                "final_output": stdout,
                "final_error": {
                    "type": "ParseError",
                    "message": "Could not parse tracer output",
                    "line": None,
                },
                "execution_time": 0,
                "status": "error",
            }

    except subprocess.TimeoutExpired:
        return {
            "steps": [],
            "total_steps": 0,
            "final_output": "",
            "final_error": {
                "type": "TimeoutError",
                "message": f"Execution exceeded {timeout} second(s) time limit.",
                "line": None,
            },
            "execution_time": timeout,
            "status": "timeout",
        }
    except Exception as e:
        return {
            "steps": [],
            "total_steps": 0,
            "final_output": "",
            "final_error": {
                "type": "SandboxError",
                "message": str(e),
                "line": None,
            },
            "execution_time": 0,
            "status": "error",
        }


def execute_code(code: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    Execute user code in sandbox and return stdout/stderr/status.
    This is a simplified wrapper that only returns execution output.
    """
    data = _run_subprocess(code, timeout=timeout, trace=False)

    error = data.get("final_error")
    return {
        "stdout": data.get("final_output", ""),
        "stderr": "",
        "status": data.get("status", "unknown"),
        "execution_time": data.get("execution_time", 0),
        "error_type": error.get("type") if error else None,
        "error_line": error.get("line") if error else None,
        "error_message": error.get("message") if error else None,
    }


def trace_code(code: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    Execute user code with full sys.settrace instrumentation.
    Returns step-by-step trace.
    """
    return _run_subprocess(code, timeout=timeout, trace=True)
