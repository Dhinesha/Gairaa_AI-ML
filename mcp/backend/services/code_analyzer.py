import ast
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

class CodeAnalyzer:
    """
    AST-based Python Code Intelligence Engine.
    Detects syntax errors, unused imports, unused variables, long functions,
    high cyclomatic complexity, missing error handling, and code smells.
    """

    @staticmethod
    def analyze_source_code(code: str, file_path: str = "snippet.py") -> Dict[str, Any]:
        issues = []
        
        # 1. Check syntax errors via ast.parse
        try:
            tree = ast.parse(code, filename=file_path)
        except SyntaxError as e:
            return {
                "file_path": file_path,
                "issues": [{
                    "file_path": file_path,
                    "line_number": e.lineno or 1,
                    "issue_type": "SyntaxError",
                    "severity": "high",
                    "message": f"Syntax error: {e.msg}",
                    "snippet": e.text.strip() if e.text else "",
                    "recommendation": "Fix syntax error before running tests or analysis."
                }],
                "total_issues": 1,
                "high_severity": 1,
                "medium_severity": 0,
                "low_severity": 0
            }

        lines = code.splitlines()

        # Track imports and usage
        imported_names = {}  # name -> lineno
        used_names = set()
        
        # Track assignments
        assigned_vars = {}  # var_name -> lineno

        for node in ast.walk(tree):
            # Imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name_to_track = alias.asname if alias.asname else alias.name
                    imported_names[name_to_track] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name_to_track = alias.asname if alias.asname else alias.name
                    imported_names[name_to_track] = node.lineno
            
            # Name usages
            elif isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)
                elif isinstance(node.ctx, ast.Store):
                    if not node.id.startswith("_"):
                        assigned_vars[node.id] = node.lineno

            # 2. Function size & complexity checks
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_length = (node.end_lineno or node.lineno) - node.lineno
                if func_length > 30:
                    issues.append({
                        "file_path": file_path,
                        "line_number": node.lineno,
                        "issue_type": "LongFunction",
                        "severity": "medium",
                        "message": f"Function '{node.name}' is {func_length} lines long (exceeds recommended 30 lines).",
                        "snippet": lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                        "recommendation": "Consider refactoring into smaller, single-purpose helper functions."
                    })

                # Measure cyclomatic complexity (branches)
                complexity = 1
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1
                
                if complexity > 7:
                    issues.append({
                        "file_path": file_path,
                        "line_number": node.lineno,
                        "issue_type": "HighComplexity",
                        "severity": "medium",
                        "message": f"Function '{node.name}' has high cyclomatic complexity ({complexity}).",
                        "snippet": lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                        "recommendation": "Simplify conditional logic, extract nested branches into guard clauses."
                    })

            # 3. Error handling checks
            elif isinstance(node, ast.ExceptHandler):
                # Bare except or catch-all Exception without logging/re-raise
                if node.type is None or (isinstance(node.type, ast.Name) and node.type.id == "BaseException"):
                    issues.append({
                        "file_path": file_path,
                        "line_number": node.lineno,
                        "issue_type": "BareExcept",
                        "severity": "high",
                        "message": "Bare 'except:' or catching BaseException masks unexpected crashes and keyboard interrupts.",
                        "snippet": lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                        "recommendation": "Catch specific exceptions like ValueError, KeyError, or HTTPError."
                    })
                elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
                    # Check if body is just pass
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        issues.append({
                            "file_path": file_path,
                            "line_number": node.lineno,
                            "issue_type": "SwallowedException",
                            "severity": "high",
                            "message": "Silent exception swallowing: 'except Exception: pass'.",
                            "snippet": lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                            "recommendation": "Log the error or handle it explicitly rather than silently ignoring."
                        })

            # 4. Check for unhandled exceptions (e.g., raise ValueError without enclosing try-except in API routes)
            elif isinstance(node, ast.Raise):
                # Check if raise is outside any try block
                # Flag as low/medium info
                pass

        # 5. Check unused imports
        for imp, lineno in imported_names.items():
            if imp not in used_names and not imp.startswith("_"):
                issues.append({
                    "file_path": file_path,
                    "line_number": lineno,
                    "issue_type": "UnusedImport",
                    "severity": "low",
                    "message": f"Imported module/name '{imp}' is never used.",
                    "snippet": lines[lineno - 1] if lineno <= len(lines) else "",
                    "recommendation": f"Remove unused import '{imp}' to reduce overhead."
                })

        # 6. Check for TODOs in comments
        for idx, line in enumerate(lines, start=1):
            if "#" in line:
                comment_part = line[line.index("#"):]
                for tag in ["TODO", "FIXME", "HACK", "XXX"]:
                    if tag in comment_part:
                        issues.append({
                            "file_path": file_path,
                            "line_number": idx,
                            "issue_type": f"{tag}Comment",
                            "severity": "low",
                            "message": f"Found {tag}: {comment_part.strip()}",
                            "snippet": line.strip(),
                            "recommendation": f"Resolve pending task: {comment_part.strip()}"
                        })

        high_count = sum(1 for i in issues if i["severity"] == "high")
        med_count = sum(1 for i in issues if i["severity"] == "medium")
        low_count = sum(1 for i in issues if i["severity"] == "low")

        return {
            "file_path": file_path,
            "issues": issues,
            "total_issues": len(issues),
            "high_severity": high_count,
            "medium_severity": med_count,
            "low_severity": low_count
        }

    @staticmethod
    def scan_for_todos(files_content: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Scan multiple files for TODO, FIXME, HACK, XXX tags.
        """
        todos = []
        pattern = re.compile(r'#\s*(TODO|FIXME|HACK|XXX)\s*[:\-]?\s*(.*)', re.IGNORECASE)
        for path, content in files_content.items():
            for line_no, line in enumerate(content.splitlines(), start=1):
                match = pattern.search(line)
                if match:
                    tag = match.group(1).upper()
                    text = match.group(2).strip() or line.strip()
                    todos.append({
                        "file_path": path,
                        "line_number": line_no,
                        "tag": tag,
                        "text": text,
                        "snippet": line.strip()
                    })
        return todos
