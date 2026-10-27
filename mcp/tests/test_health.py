import pytest
from pathlib import Path
from backend.services.test_runner import TestRunnerService
from backend.services.code_analyzer import CodeAnalyzer
from backend.mcp_server.tools.health_tools import get_project_health

def test_command_whitelist_validation():
    # Valid commands
    assert TestRunnerService.validate_command("pytest") == "pytest"
    assert TestRunnerService.validate_command("pytest tests/") == "pytest tests/"
    assert TestRunnerService.validate_command("python -m pytest") == "python -m pytest"
    assert TestRunnerService.validate_command("python -m unittest") == "python -m unittest"

    # Unauthorized commands must raise PermissionError
    with pytest.raises(PermissionError):
        TestRunnerService.validate_command("rm -rf /")

    with pytest.raises(PermissionError):
        TestRunnerService.validate_command("cat /etc/passwd")

    with pytest.raises(PermissionError):
        TestRunnerService.validate_command("curl http://malicious.site")

def test_parse_pytest_output():
    sample_pytest_output = """
============================= test session starts =============================
tests/test_auth.py ..F                                                   [100%]

=================================== FAILURES ===================================
__________________________ test_login_invalid_password __________________________
tests/test_auth.py:28: in test_login_invalid_password
    assert response["status_code"] == 401
E   AssertionError: Expected 401 but received 500
=========================== short test summary info ===========================
FAILED tests/test_auth.py::test_login_invalid_password - AssertionError: Expected 401 but received 500
========================= 1 failed, 2 passed in 0.15s =========================
"""
    result = TestRunnerService.parse_test_output(sample_pytest_output, exit_code=1)
    assert result["total"] == 3
    assert result["passed"] == 2
    assert result["failed"] == 1
    assert len(result["failures"]) == 1
    assert result["failures"][0]["test_name"] == "test_login_invalid_password"
    assert "Expected 401 but received 500" in result["failures"][0]["error_message"]

def test_analyze_test_failure():
    diag = TestRunnerService.analyze_test_failure(
        test_name="test_login_invalid_password",
        error_message="AssertionError: Expected 401 but received 500",
        traceback="ValueError: Invalid password",
        file_path="tests/test_auth.py"
    )
    assert "500" in diag["root_cause"]
    assert "401" in diag["root_cause"]
    assert "Authentication" in diag["component"]

@pytest.mark.asyncio
async def test_get_project_health():
    health = await get_project_health("demo", "demo_repo")
    assert "health_score" in health
    assert 0 <= health["health_score"] <= 100
    assert "tests" in health
    assert "code_issues" in health
    assert "rating" in health
