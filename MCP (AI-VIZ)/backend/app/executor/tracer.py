"""
Tracer script – this module is run INSIDE an isolated subprocess.
It uses sys.settrace to capture every line/call/return/exception event.
Results are printed as JSON to stdout and read by the parent process.

SECURITY: This script itself is the code that runs inside the sandbox.
The sandbox.py launches it as a child process with restrictions.
"""
import sys
import json
import io
import ast
import time
import traceback
import copy
import builtins
import signal
import os

# ──────────────────────────────────────────────────────────────────────────── #
# BLOCKED IMPORTS                                                               #
# ──────────────────────────────────────────────────────────────────────────── #
BLOCKED_MODULES = {
    "os", "sys", "subprocess", "socket", "shutil", "pathlib",
    "pickle", "shelve", "marshal", "importlib", "ctypes", "multiprocessing",
    "threading", "concurrent", "asyncio", "signal", "resource",
    "pty", "termios", "tty", "readline", "rlcompleter",
    "_thread", "gc", "weakref", "inspect", "dis",
}

BLOCKED_BUILTINS = {"open", "exec", "eval", "compile", "__import__",
                     "input", "breakpoint"}


def make_safe_builtins():
    safe = {k: v for k, v in vars(builtins).items()
            if k not in BLOCKED_BUILTINS}

    def safe_import(name, *args, **kwargs):
        if name.split(".")[0] in BLOCKED_MODULES:
            raise ImportError(
                f"Import of '{name}' is blocked for security reasons."
            )
        return original_import(name, *args, **kwargs)

    original_import = builtins.__import__
    safe["__import__"] = safe_import
    return safe


# ──────────────────────────────────────────────────────────────────────────── #
# TRACER STATE                                                                  #
# ──────────────────────────────────────────────────────────────────────────── #
_steps = []
_step_counter = [0]
_output_buffer = io.StringIO()
_call_stack = []
_source_lines = []
_last_vars = {}
_execution_time = 0.0


def _safe_repr(v):
    """Convert a value to a JSON-safe representation."""
    if isinstance(v, (int, float, bool, str, type(None))):
        return v
    elif isinstance(v, (list, tuple)):
        try:
            return [_safe_repr(x) for x in v]
        except Exception:
            return str(v)
    elif isinstance(v, dict):
        try:
            return {str(k): _safe_repr(vv) for k, vv in list(v.items())[:50]}
        except Exception:
            return str(v)
    else:
        try:
            return repr(v)
        except Exception:
            return "<unrepresentable>"


def _capture_vars(frame):
    """Extract local variables from frame, filtering internals."""
    skip = {"__builtins__", "__name__", "__doc__", "__package__",
            "__loader__", "__spec__", "__file__", "__cached__",
            "_steps", "_step_counter", "_output_buffer", "_call_stack",
            "_source_lines", "_last_vars", "_execution_time",
            "safe_builtins"}
    out = {}
    for k, v in frame.f_locals.items():
        if k.startswith("_") or k in skip:
            continue
        try:
            out[k] = _safe_repr(v)
        except Exception:
            out[k] = "<error>"
    return out


def _get_source_line(lineno):
    if 1 <= lineno <= len(_source_lines):
        return _source_lines[lineno - 1].rstrip()
    return ""


def _make_description(event, frame, arg):
    func = frame.f_code.co_name
    lineno = frame.f_lineno
    src = _get_source_line(lineno).strip()

    if event == "call":
        if func == "<module>":
            return f"Starting execution of the program."
        return f"Function '{func}' is called."
    elif event == "return":
        ret = _safe_repr(arg)
        if func == "<module>":
            return "Program execution finished."
        return f"Function '{func}' returns {ret!r}."
    elif event == "exception":
        exc_type, exc_val, _ = arg
        return f"Exception raised: {exc_type.__name__}: {exc_val}"
    elif event == "line":
        stripped = src
        if "=" in stripped and not stripped.startswith("if") and not stripped.startswith("while"):
            return f"Executing: {stripped}"
        elif stripped.startswith("return"):
            return f"Returning from function."
        elif stripped.startswith("print"):
            return f"Printing output: {stripped}"
        elif stripped.startswith("for"):
            return f"Loop iteration: {stripped}"
        elif stripped.startswith("if") or stripped.startswith("elif"):
            return f"Checking condition: {stripped}"
        elif stripped.startswith("def"):
            return f"Defining function: {stripped}"
        elif stripped.startswith("class"):
            return f"Defining class: {stripped}"
        return f"Executing line {lineno}: {stripped}"
    return f"Event: {event} at line {lineno}"


def _tracer(frame, event, arg):
    global _last_vars
    func_name = frame.f_code.co_name

    # Skip internal frames
    if frame.f_code.co_filename != "<string>":
        return _tracer

    lineno = frame.f_lineno
    _step_counter[0] += 1
    step_num = _step_counter[0]

    current_vars = _capture_vars(frame)

    # Manage call stack
    if event == "call":
        if func_name != "<module>":
            _call_stack.append(func_name)
    elif event == "return":
        if func_name != "<module>" and _call_stack and _call_stack[-1] == func_name:
            _call_stack.pop()

    # Determine event label
    event_label = event
    loop_info = None
    condition_info = None

    # Detect loop variable changes
    src_stripped = _get_source_line(lineno).strip()
    if src_stripped.startswith("for "):
        event_label = "loop_iter"
        # extract loop var and iter
        parts = src_stripped.split("in", 1)
        if len(parts) == 2:
            loop_var = parts[0].replace("for", "").strip()
            loop_iter = parts[1].rstrip(":").strip()
            loop_info = {"variable": loop_var, "iterator": loop_iter,
                          "current_value": current_vars.get(loop_var)}
    elif src_stripped.startswith("if ") or src_stripped.startswith("elif "):
        event_label = "condition"
        condition_info = {"expression": src_stripped.rstrip(":")}

    current_output = _output_buffer.getvalue()

    step = {
        "step": step_num,
        "line": lineno,
        "event": event_label,
        "function_name": func_name if func_name != "<module>" else None,
        "variables": current_vars,
        "call_stack": list(_call_stack),
        "output": current_output,
        "exception": None,
        "source_line": _get_source_line(lineno),
        "description": _make_description(event, frame, arg),
        "loop_info": loop_info,
        "condition_info": condition_info,
    }

    if event == "exception":
        exc_type, exc_val, _ = arg
        step["exception"] = f"{exc_type.__name__}: {exc_val}"
        step["event"] = "exception"

    if event == "return" and func_name != "<module>":
        step["return_value"] = _safe_repr(arg)
        step["event"] = "return"

    _steps.append(step)
    _last_vars = current_vars
    return _tracer


def run_traced(code: str, source_lines: list):
    global _source_lines, _execution_time
    _source_lines = source_lines

    safe_globals = {
        "__builtins__": make_safe_builtins(),
        "__name__": "__main__",
    }

    # Redirect stdout
    sys.stdout = _output_buffer

    start = time.time()
    error_info = None

    try:
        compiled = compile(code, "<string>", "exec")
        sys.settrace(_tracer)
        exec(compiled, safe_globals)  # noqa: S102 – sandboxed context
    except SyntaxError as e:
        error_info = {
            "type": "SyntaxError",
            "message": str(e.msg),
            "line": e.lineno,
            "text": e.text or "",
        }
    except Exception as e:
        tb = traceback.extract_tb(sys.exc_info()[2])
        lineno = tb[-1].lineno if tb else None
        error_info = {
            "type": type(e).__name__,
            "message": str(e),
            "line": lineno,
            "traceback": traceback.format_exc(),
        }
    finally:
        sys.settrace(None)
        _execution_time = time.time() - start
        sys.stdout = sys.__stdout__

    final_output = _output_buffer.getvalue()

    result = {
        "steps": _steps,
        "total_steps": len(_steps),
        "final_output": final_output,
        "final_error": error_info,
        "execution_time": round(_execution_time, 4),
    }

    return result


if __name__ == "__main__":
    # Read code from stdin (passed by sandbox.py)
    raw = sys.stdin.read()
    data = json.loads(raw)
    user_code = data["code"]
    source_lines = user_code.splitlines()

    result = run_traced(user_code, source_lines)
    # Write result to stdout as single JSON line
    sys.stdout.write(json.dumps(result))
    sys.stdout.flush()
