from typing import Dict, Any, Optional
from pathlib import Path
from backend.services.test_runner import TestRunnerService
from backend.config import settings

async def run_tests(owner: str = "demo", repo: str = "demo_repo", test_command: str = "pytest") -> Dict[str, Any]:
    """
    Run pytest or unittest in the repository test suite and return detailed test counts and failures.
    Only approved test commands (pytest, python -m pytest, python -m unittest) are permitted.
    """
    target_dir = settings.DEMO_REPO_PATH
    # In demo mode or if target is local
    if not target_dir.exists():
        return {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "failures": [],
            "raw_output": f"Directory '{target_dir}' not found.",
            "success": False
        }
    
    return TestRunnerService.run_tests_in_dir(target_dir, test_command=test_command)

async def analyze_test_failure(test_name: str, error_message: str, traceback: str = "", file_path: str = "") -> Dict[str, Any]:
    """
    Diagnose a failing test case, identify root cause (e.g. 500 instead of 401), and recommend a fix.
    """
    return TestRunnerService.analyze_test_failure(
        test_name=test_name,
        error_message=error_message,
        traceback=traceback,
        file_path=file_path
    )
