from typing import Dict, Any
from backend.services.github_service import GitHubService
from backend.services.code_analyzer import CodeAnalyzer
from backend.services.test_runner import TestRunnerService
from backend.config import settings

github_service = GitHubService()

async def get_project_health(owner: str = "demo", repo: str = "demo_repo") -> Dict[str, Any]:
    """
    Generate an overall project health report including file statistics, test pass rate,
    AST code smell counts, TODO counts, commit activity, open issues, and health score (0-100).
    """
    # 1. Fetch file list
    files = await github_service.list_repository_files(owner, repo)
    total_files = len(files)
    python_files = [f for f in files if f.endswith(".py")]
    test_files = [f for f in python_files if "test" in f.lower()]

    # 2. Analyze code issues and scan TODOs
    high_issues = 0
    med_issues = 0
    low_issues = 0
    files_content = {}

    for py_file in python_files[:15]:  # Analyze up to first 15 python files for quick responsiveness
        try:
            content = await github_service.read_repository_file(owner, repo, py_file)
            files_content[py_file] = content
            analysis = CodeAnalyzer.analyze_source_code(content, file_path=py_file)
            high_issues += analysis.get("high_severity", 0)
            med_issues += analysis.get("medium_severity", 0)
            low_issues += analysis.get("low_severity", 0)
        except Exception:
            continue

    todos = CodeAnalyzer.scan_for_todos(files_content)
    total_todos = len(todos)

    # 3. Test metrics
    test_res = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
    if github_service._is_local_demo(owner, repo) and settings.DEMO_REPO_PATH.exists():
        try:
            test_res = TestRunnerService.run_tests_in_dir(settings.DEMO_REPO_PATH, "pytest")
        except Exception:
            pass

    tests_total = test_res.get("total", 0)
    tests_passed = test_res.get("passed", 0)
    tests_failed = test_res.get("failed", 0)
    
    if tests_total > 0:
        test_pass_pct = round((tests_passed / tests_total) * 100, 1)
    else:
        test_pass_pct = 100.0 if not test_files else 50.0

    # 4. Commits and issues
    recent_commits = 0
    try:
        commits = await github_service.get_recent_commits(owner, repo, limit=10)
        recent_commits = len(commits)
    except Exception:
        pass

    open_issues = 0
    try:
        issues = await github_service.get_repository_issues(owner, repo, state="open")
        open_issues = len(issues)
    except Exception:
        pass

    # 5. Compute overall health score (0-100)
    score = 100
    if tests_total > 0:
        score -= int(tests_failed * 15)
    score -= int(high_issues * 10)
    score -= int(med_issues * 3)
    score -= int(min(total_todos, 10) * 1)
    score -= int(min(open_issues, 5) * 2)
    score = max(10, min(100, score))

    if score >= 85:
        rating = "Excellent"
    elif score >= 70:
        rating = "Good"
    elif score >= 50:
        rating = "Moderate"
    else:
        rating = "Critical"

    return {
        "repository": f"{owner}/{repo}",
        "total_files": total_files,
        "python_files": len(python_files),
        "test_files": len(test_files),
        "tests": {
            "total": tests_total,
            "passed": tests_passed,
            "failed": tests_failed,
            "pass_percentage": test_pass_pct
        },
        "code_issues": {
            "high": high_issues,
            "medium": med_issues,
            "low": low_issues,
            "total": high_issues + med_issues + low_issues
        },
        "todos": total_todos,
        "recent_commits": recent_commits,
        "open_issues": open_issues,
        "health_score": score,
        "rating": rating
    }
