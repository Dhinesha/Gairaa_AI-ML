"""
Deterministic local explanation engine.
Produces beginner-friendly explanations from AST analysis and execution traces.
Designed to be swapped for an LLM later (set OPENAI_API_KEY in .env).
"""
import os
import ast
from typing import Any, Dict, List, Optional


# ──────────────────────────────────────────────────────────────────────────── #
#  Code explanation                                                              #
# ──────────────────────────────────────────────────────────────────────────── #

def explain_code(code: str, trace: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Explain what the code does in beginner-friendly language."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {
            "summary": f"This code has a syntax error: {e.msg} on line {e.lineno}.",
            "steps_explanation": [],
            "variables_explanation": "Cannot determine variables due to syntax error.",
            "output_explanation": "No output produced due to syntax error.",
            "beginner_tip": "A syntax error means Python cannot understand the code structure. Check the highlighted line.",
        }

    # Gather code elements
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    loops = [n for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While))]
    conditions = [n for n in ast.walk(tree) if isinstance(n, ast.If)]
    imports = [alias.name for n in ast.walk(tree) if isinstance(n, ast.Import) for alias in n.names]
    lines = code.strip().splitlines()

    # Build summary
    parts = []
    parts.append(f"This program has {len(lines)} line(s) of Python code.")
    if funcs:
        parts.append(f"It defines {len(funcs)} function(s): {', '.join(funcs)}.")
    if loops:
        loop_types = []
        for l in loops:
            loop_types.append("for loop" if isinstance(l, ast.For) else "while loop")
        parts.append(f"It uses {', '.join(set(loop_types))}.")
    if conditions:
        parts.append(f"It has {len(conditions)} conditional statement(s).")
    if imports:
        parts.append(f"It imports: {', '.join(imports)}.")

    summary = " ".join(parts)

    # Build step-by-step explanation from trace
    steps_explanation = []
    if trace:
        for step in trace[:20]:  # limit to first 20 for readability
            steps_explanation.append({
                "step": step.get("step"),
                "line": step.get("line"),
                "explanation": step.get("description", ""),
                "source": step.get("source_line", ""),
            })

    # Variables explanation
    vars_set = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    vars_set.add(t.id)
    vars_explanation = (
        f"This code uses {len(vars_set)} variable(s): {', '.join(sorted(vars_set))}." 
        if vars_set else "This code does not create any variables."
    )

    # Output explanation
    print_calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                   and isinstance(n.func, ast.Name) and n.func.id == "print"]
    if print_calls:
        output_explanation = f"This code has {len(print_calls)} print statement(s) that produce output."
    else:
        output_explanation = "This code does not produce any printed output."

    # Tip
    beginner_tip = _get_beginner_tip(tree)

    return {
        "summary": summary,
        "steps_explanation": steps_explanation,
        "variables_explanation": vars_explanation,
        "output_explanation": output_explanation,
        "beginner_tip": beginner_tip,
    }


def _get_beginner_tip(tree: ast.AST) -> str:
    """Return a relevant beginner tip based on code structure."""
    has_recursion = _detect_recursion(tree)
    has_loop = any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(tree))
    has_func = any(isinstance(n, ast.FunctionDef) for n in ast.walk(tree))

    if has_recursion:
        return ("💡 This code uses recursion – a function that calls itself. "
                "Recursion is useful for problems that can be broken into smaller identical sub-problems.")
    elif has_loop:
        return ("💡 Loops let Python repeat actions without writing the same code multiple times. "
                "Each iteration updates the loop variable.")
    elif has_func:
        return ("💡 Functions are reusable blocks of code. "
                "They receive input (arguments) and return a result.")
    else:
        return "💡 Python executes code from top to bottom, one line at a time."


def _detect_recursion(tree: ast.AST) -> bool:
    """Check if any function calls itself."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            for child in ast.walk(node):
                if (isinstance(child, ast.Call)
                        and isinstance(child.func, ast.Name)
                        and child.func.id == func_name):
                    return True
    return False


# ──────────────────────────────────────────────────────────────────────────── #
#  Error explanation                                                             #
# ──────────────────────────────────────────────────────────────────────────── #

ERROR_EXPLANATIONS = {
    "NameError": {
        "explanation": "Python tried to use a variable or function that hasn't been defined yet. "
                       "This usually means you forgot to assign a value to the variable before using it, "
                       "or you misspelled the variable name.",
        "fix": "Make sure the variable is defined (assigned a value) before you use it.",
    },
    "TypeError": {
        "explanation": "Python tried to perform an operation on values of the wrong type. "
                       "For example, adding a string and a number directly doesn't work.",
        "fix": "Convert values to compatible types first. For example, use int() or str() to convert values.",
    },
    "ValueError": {
        "explanation": "A function received an argument of the right type but an inappropriate value. "
                       "For example, int('abc') fails because 'abc' cannot be converted to an integer.",
        "fix": "Check that the values passed to functions are valid for that function.",
    },
    "IndexError": {
        "explanation": "You tried to access an element at an index that doesn't exist in the list. "
                       "Remember that Python list indices start at 0.",
        "fix": "Check that your index is within the valid range (0 to len(list)-1).",
    },
    "KeyError": {
        "explanation": "You tried to access a key in a dictionary that doesn't exist.",
        "fix": "Use dict.get(key, default) to safely access keys, or check 'if key in dict' first.",
    },
    "ZeroDivisionError": {
        "explanation": "The program tried to divide a number by zero, which is mathematically undefined.",
        "fix": "Add a check before division: 'if divisor != 0:' to avoid this error.",
    },
    "AttributeError": {
        "explanation": "You tried to access a property or method that doesn't exist on this type of object.",
        "fix": "Check the correct method names for this type. Use help() or dir() to see available methods.",
    },
    "ImportError": {
        "explanation": "Python could not import the requested module. Either the module doesn't exist, "
                       "isn't installed, or is blocked for security reasons.",
        "fix": "Make sure the module is installed (pip install module_name) and that the name is spelled correctly.",
    },
    "RecursionError": {
        "explanation": "The program called itself too many times without stopping. "
                       "This usually means your recursive function is missing a base case.",
        "fix": "Add a base case to your recursive function that stops the recursion.",
    },
    "SyntaxError": {
        "explanation": "Python cannot understand the code structure because of a typo, "
                       "missing colon, bracket, or other syntax issue.",
        "fix": "Look at the highlighted line for a missing colon (:), parenthesis, or quotation mark.",
    },
    "TimeoutError": {
        "explanation": "The code took too long to execute. This often happens with infinite loops "
                       "or very slow algorithms.",
        "fix": "Check for infinite loops (while True without a break) or optimize your algorithm.",
    },
}


def explain_error(
    code: str,
    error: str,
    error_type: Optional[str] = None,
    error_line: Optional[int] = None,
) -> Dict[str, Any]:
    """Produce a beginner-friendly explanation for a Python error."""
    # Try to detect error type from error string
    if error_type is None:
        for etype in ERROR_EXPLANATIONS:
            if etype in error:
                error_type = etype
                break
        if error_type is None:
            error_type = "RuntimeError"

    info = ERROR_EXPLANATIONS.get(error_type, {
        "explanation": f"An error of type '{error_type}' occurred during execution.",
        "fix": "Read the error message carefully and check the highlighted line.",
    })

    # Extract line number from error message if not provided
    if error_line is None:
        import re
        m = re.search(r"line (\d+)", error)
        if m:
            error_line = int(m.group(1))

    # Get the problematic source line
    example_fix = None
    if error_line and code:
        lines = code.splitlines()
        if 1 <= error_line <= len(lines):
            problem_line = lines[error_line - 1].strip()
            if error_type == "ZeroDivisionError" and "/" in problem_line:
                example_fix = f"# Before:\n{problem_line}\n# After:\nif divisor != 0:\n    {problem_line}"
            elif error_type == "NameError":
                # Try to extract the undefined name
                import re
                m2 = re.search(r"name '(\w+)' is not defined", error)
                if m2:
                    undef = m2.group(1)
                    example_fix = f"# Add this BEFORE line {error_line}:\n{undef} = <your_value_here>"

    return {
        "error_type": error_type,
        "error_message": error,
        "problematic_line": error_line,
        "explanation": info["explanation"],
        "fix_suggestion": info["fix"],
        "example_fix": example_fix,
    }


# ──────────────────────────────────────────────────────────────────────────── #
#  Step-level explanations (used by trace tool)                                 #
# ──────────────────────────────────────────────────────────────────────────── #

def explain_step(step: Dict[str, Any]) -> str:
    """Generate a one-sentence explanation for a single trace step."""
    event = step.get("event", "")
    line = step.get("line", "?")
    func = step.get("function_name")
    src = step.get("source_line", "").strip()

    if event == "call":
        return f"Line {line}: Python enters the function '{func}'."
    elif event == "return":
        ret_val = step.get("return_value", "")
        return f"Line {line}: Function '{func}' returns the value {ret_val!r}."
    elif event == "exception":
        return f"Line {line}: An error occurred — {step.get('exception', '')}."
    elif event == "loop_iter":
        info = step.get("loop_info", {})
        var = info.get("variable", "")
        val = info.get("current_value", "")
        return f"Line {line}: Loop iteration — {var} = {val}."
    elif event == "condition":
        info = step.get("condition_info", {})
        expr = info.get("expression", src)
        return f"Line {line}: Checking condition: {expr}"
    elif "=" in src and not src.startswith("if") and not src.startswith("while"):
        return f"Line {line}: Assignment — {src}"
    elif src.startswith("print"):
        output = step.get("output", "")
        return f"Line {line}: Printing to screen: {src}"
    else:
        return f"Line {line}: {src}"
