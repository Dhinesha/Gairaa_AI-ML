import subprocess
import re
import shlex
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.utils.helpers import logger

APPROVED_COMMAND_PREFIXES = [
    "pytest",
    "python -m pytest",
    "python -m unittest",
    "unittest"
]

class TestRunnerService:
    """
    Executes and parses test suites (pytest, unittest) with strict command whitelist validation.
    """

    @staticmethod
    def validate_command(command: str) -> str:
        """Ensure command is strictly an approved test command, preventing command injection."""
        cmd_clean = command.strip()
        is_valid = any(cmd_clean == prefix or cmd_clean.startswith(prefix + " ") for prefix in APPROVED_COMMAND_PREFIXES)
        if not is_valid:
            raise PermissionError(
                f"Command '{command}' is not permitted. Only 'pytest' or 'python -m unittest' commands are allowed for security."
            )
        return cmd_clean

    @classmethod
    def run_tests_in_dir(cls, working_dir: Path, test_command: str = "pytest") -> Dict[str, Any]:
        """
        Runs tests in the specified directory and parses the results.
        """
        cls.validate_command(test_command)
        
        if not working_dir.exists():
            raise FileNotFoundError(f"Working directory '{working_dir}' does not exist.")

        # Determine python executable to use
        python_exe = sys.executable
        cmd_args = shlex.split(test_command)
        if cmd_args[0] == "pytest":
            cmd_args = [python_exe, "-m", "pytest"] + cmd_args[1:]
        elif cmd_args[0] == "unittest":
            cmd_args = [python_exe, "-m", "unittest"] + cmd_args[1:]
        elif cmd_args[0] == "python":
            cmd_args[0] = python_exe

        # Always add verbose / concise output flags if pytest
        if "pytest" in test_command and "-v" not in cmd_args:
            cmd_args.append("-v")

        logger.info(f"Running test command: {' '.join(cmd_args)} in {working_dir}")

        try:
            process = subprocess.run(
                cmd_args,
                cwd=str(working_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=30,
                shell=False
            )
            raw_output = process.stdout
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "failures": [{
                    "test_name": "Timeout",
                    "error_message": "Test execution exceeded 30s timeout.",
                    "traceback": "",
                    "file_path": None,
                    "line_number": None
                }],
                "raw_output": "Test execution timed out after 30 seconds.",
                "success": False
            }
        except Exception as e:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "failures": [{
                    "test_name": "ExecutionError",
                    "error_message": str(e),
                    "traceback": "",
                    "file_path": None,
                    "line_number": None
                }],
                "raw_output": str(e),
                "success": False
            }

        return cls.parse_test_output(raw_output, exit_code)

    @staticmethod
    def parse_test_output(output: str, exit_code: int) -> Dict[str, Any]:
        """
        Parses pytest or unittest summary output into structured test metrics.
        """
        total = 0
        passed = 0
        failed = 0
        skipped = 0
        failures = []

        # Pytest summary line regex: e.g. "== 1 failed, 2 passed, 1 skipped in 0.12s =="
        summary_match = re.search(r'(=+\s*)(.*?in\s+[0-9\.]+s.*)', output)
        if summary_match:
            summary_text = summary_match.group(2)
            passed_m = re.search(r'(\d+)\s+passed', summary_text)
            failed_m = re.search(r'(\d+)\s+failed', summary_text)
            skipped_m = re.search(r'(\d+)\s+skipped', summary_text)

            if passed_m:
                passed = int(passed_m.group(1))
            if failed_m:
                failed = int(failed_m.group(1))
            if skipped_m:
                skipped = int(skipped_m.group(1))
            total = passed + failed + skipped
        else:
            # Check for unittest style: "FAILED (failures=1)" or "Ran 3 tests in 0.001s \n OK"
            ran_m = re.search(r'Ran\s+(\d+)\s+tests?', output)
            if ran_m:
                total = int(ran_m.group(1))
                fail_m = re.search(r'failures=(\d+)', output)
                err_m = re.search(r'errors=(\d+)', output)
                num_failures = (int(fail_m.group(1)) if fail_m else 0) + (int(err_m.group(1)) if err_m else 0)
                failed = num_failures
                passed = total - failed

        # Extract detailed failures
        # Pytest failure section starts with "=== FAILURES ==="
        if "FAILURES" in output:
            failure_blocks = output.split("FAILURES ===================================")[-1]
            failure_blocks = failure_blocks.split("================ short test summary info =")[0]
            
            # Match individual test failure blocks starting with "___ test_name ___"
            test_cases = re.split(r'_{3,}\s*(.*?)\s*_{3,}', failure_blocks)
            for i in range(1, len(test_cases), 2):
                test_name = test_cases[i].strip()
                tb_content = test_cases[i+1] if i+1 < len(test_cases) else ""
                
                # Extract file and line
                file_line_m = re.search(r'([a-zA-Z0-9_\-\./\\]+\.py):(\d+):', tb_content)
                file_path = file_line_m.group(1) if file_line_m else None
                line_no = int(file_line_m.group(2)) if file_line_m else None

                # Extract error message
                err_line_m = re.search(r'([A-Za-z]+Error:.*)', tb_content)
                error_msg = err_line_m.group(1) if err_line_m else "Assertion or Runtime Error"

                failures.append({
                    "test_name": test_name,
                    "file_path": file_path,
                    "line_number": line_no,
                    "error_message": error_msg.strip(),
                    "traceback": tb_content.strip()[:1000]
                })

        # Fallback if pytest failed but no specific failure blocks parsed
        if exit_code != 0 and not failures and total > 0:
            failures.append({
                "test_name": "Test Suite Failures",
                "file_path": None,
                "line_number": None,
                "error_message": "Tests reported failure status. Check raw output for details.",
                "traceback": output[-1500:]
            })

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "failures": failures,
            "raw_output": output,
            "success": (exit_code == 0)
        }

    @staticmethod
    def analyze_test_failure(test_name: str, error_message: str, traceback: str, file_path: str = "") -> Dict[str, Any]:
        """
        Deep root-cause diagnostic of test failures with recommended fixes.
        """
        root_cause = "Unknown test failure."
        recommendation = "Review assertion condition and stack trace."
        component = "General"

        # Pattern: Expected 401 but received 500
        if "500" in error_message or "500" in traceback:
            root_cause = "The API endpoint or authentication logic returned HTTP 500 (Internal Server Error) instead of the expected 401 Unauthorized or 400 Bad Request."
            recommendation = "Wrap credential validation in a try/except block that catches invalid password exceptions and raises an HTTPException(status_code=401, detail='Invalid credentials')."
            component = "Authentication / Error Handling"
        elif "AssertionError" in error_message:
            root_cause = f"Assertion failed: {error_message}."
            recommendation = "Check the return value against the expected output in the test fixture."
            component = "Assertion Validation"
        elif "KeyError" in error_message:
            root_cause = f"Missing dictionary key: {error_message}."
            recommendation = "Use .get() with a default value or verify the payload schema includes all required keys."
            component = "Data Contract"
        elif "TypeError" in error_message:
            root_cause = f"Type mismatch: {error_message}."
            recommendation = "Verify parameter types and ensure arguments are properly converted before function invocation."
            component = "Type System"

        return {
            "test_name": test_name,
            "file_path": file_path,
            "error_message": error_message,
            "component": component,
            "root_cause": root_cause,
            "recommended_fix": recommendation
        }
