"""
AST Analyzer – extracts structural information from Python source code
using the ast module. Never executes any code.
"""
import ast
import textwrap
from typing import Any, Dict, List


class ASTAnalyzer:
    def __init__(self, code: str):
        self.code = textwrap.dedent(code)
        self.lines = self.code.splitlines()
        self.tree: ast.Module | None = None
        self.parse_error: str | None = None

        try:
            self.tree = ast.parse(self.code)
        except SyntaxError as e:
            self.parse_error = str(e)

    # ------------------------------------------------------------------ #
    #  Public API                                                           #
    # ------------------------------------------------------------------ #

    def analyze(self) -> Dict[str, Any]:
        if self.tree is None:
            return {
                "error": self.parse_error,
                "functions": [],
                "variables": [],
                "classes": [],
                "loops": [],
                "conditions": [],
                "imports": [],
                "return_statements": [],
                "function_calls": [],
                "line_count": len(self.lines),
                "complexity": "unknown",
            }

        return {
            "functions": self._get_functions(),
            "variables": self._get_variables(),
            "classes": self._get_classes(),
            "loops": self._get_loops(),
            "conditions": self._get_conditions(),
            "imports": self._get_imports(),
            "return_statements": self._get_return_lines(),
            "function_calls": self._get_function_calls(),
            "line_count": len(self.lines),
            "complexity": self._estimate_complexity(),
        }

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _get_functions(self) -> List[Dict[str, Any]]:
        funcs = []
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [a.arg for a in node.args.args]
                funcs.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "end_line": node.end_lineno,
                        "args": args,
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "docstring": ast.get_docstring(node),
                        "decorators": [
                            ast.unparse(d) for d in node.decorator_list
                        ],
                    }
                )
        return funcs

    def _get_variables(self) -> List[str]:
        names: set[str] = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        names.add(t.id)
            elif isinstance(node, ast.AugAssign):
                if isinstance(node.target, ast.Name):
                    names.add(node.target.id)
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    names.add(node.target.id)
            elif isinstance(node, (ast.For, ast.comprehension)):
                if isinstance(node.target if hasattr(node, "target") else None, ast.Name):
                    names.add(node.target.id)
        # Remove function/class names
        func_names = {n["name"] for n in self._get_functions()}
        class_names = {c["name"] for c in self._get_classes()}
        return sorted(names - func_names - class_names)

    def _get_classes(self) -> List[Dict[str, Any]]:
        classes = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                classes.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "bases": [ast.unparse(b) for b in node.bases],
                    }
                )
        return classes

    def _get_loops(self) -> List[Dict[str, Any]]:
        loops = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.For):
                loops.append(
                    {
                        "type": "for",
                        "line": node.lineno,
                        "end_line": node.end_lineno,
                        "target": ast.unparse(node.target),
                        "iter": ast.unparse(node.iter),
                    }
                )
            elif isinstance(node, ast.While):
                loops.append(
                    {
                        "type": "while",
                        "line": node.lineno,
                        "end_line": node.end_lineno,
                        "condition": ast.unparse(node.test),
                    }
                )
        return loops

    def _get_conditions(self) -> List[Dict[str, Any]]:
        conds = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.If):
                conds.append(
                    {
                        "type": "if",
                        "line": node.lineno,
                        "end_line": node.end_lineno,
                        "condition": ast.unparse(node.test),
                        "has_else": len(node.orelse) > 0,
                    }
                )
        return conds

    def _get_imports(self) -> List[str]:
        imports = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports

    def _get_return_lines(self) -> List[int]:
        return [
            node.lineno
            for node in ast.walk(self.tree)
            if isinstance(node, ast.Return)
        ]

    def _get_function_calls(self) -> List[Dict[str, Any]]:
        calls = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                try:
                    name = ast.unparse(node.func)
                    args = [ast.unparse(a) for a in node.args]
                    calls.append(
                        {"name": name, "line": node.lineno, "args": args}
                    )
                except Exception:
                    pass
        return calls

    def _estimate_complexity(self) -> str:
        """Simple McCabe-style complexity estimate."""
        score = 1
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                                  ast.With, ast.Assert)):
                score += 1
        if score <= 3:
            return "simple"
        elif score <= 7:
            return "moderate"
        else:
            return "complex"


def analyze_code(code: str) -> Dict[str, Any]:
    """Convenience wrapper."""
    return ASTAnalyzer(code).analyze()
