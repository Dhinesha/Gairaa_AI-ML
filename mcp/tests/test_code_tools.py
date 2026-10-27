import pytest
from backend.services.code_analyzer import CodeAnalyzer

def test_ast_syntax_error_detection():
    bad_code = "def invalid_syntax(:"
    res = CodeAnalyzer.analyze_source_code(bad_code, "test.py")
    assert res["total_issues"] == 1
    assert res["high_severity"] == 1
    assert res["issues"][0]["issue_type"] == "SyntaxError"

def test_ast_unused_import_and_bare_except():
    code = """
import os
import sys

def process():
    try:
        x = 10
    except:
        pass
"""
    res = CodeAnalyzer.analyze_source_code(code, "test.py")
    issue_types = [i["issue_type"] for i in res["issues"]]
    assert "BareExcept" in issue_types
    assert "UnusedImport" in issue_types

def test_ast_long_function_and_complexity():
    # Generate function with > 30 lines and multiple branches
    branches = "\n    ".join([f"if i == {i}: print({i})" for i in range(12)])
    code = f"""
def complex_fn():
    {branches}
    # padding lines
    """ + "\n    ".join(["x = 1"] * 25)
    
    res = CodeAnalyzer.analyze_source_code(code, "test.py")
    issue_types = [i["issue_type"] for i in res["issues"]]
    assert "LongFunction" in issue_types
    assert "HighComplexity" in issue_types

def test_todo_scanner():
    files = {
        "auth.py": "# TODO: Add token expiration\n# FIXME: Fix connection timeout",
        "utils.py": "# Regular comment\n# HACK: Hardcoded string"
    }
    todos = CodeAnalyzer.scan_for_todos(files)
    tags = [t["tag"] for t in todos]
    assert "TODO" in tags
    assert "FIXME" in tags
    assert "HACK" in tags
    assert len(todos) == 3
