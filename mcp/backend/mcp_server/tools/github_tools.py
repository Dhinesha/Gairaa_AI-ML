from typing import Dict, Any, List, Optional
from backend.services.github_service import GitHubService

github_service = GitHubService()

async def get_repository_info(owner: str, repo: str) -> Dict[str, Any]:
    """Retrieve basic repository information such as description, default branch, stars, and open issues."""
    return await github_service.get_repository_info(owner, repo)

async def list_repository_files(owner: str, repo: str, path: str = "") -> List[str]:
    """List files and folders inside the repository or subdirectory."""
    return await github_service.list_repository_files(owner, repo, path)

async def read_repository_file(owner: str, repo: str, path: str) -> str:
    """Read source code or configuration file from the repository."""
    return await github_service.read_repository_file(owner, repo, path)

async def get_recent_commits(owner: str, repo: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve recent GitHub commits with author, message, date, and commit ID."""
    return await github_service.get_recent_commits(owner, repo, limit)

async def get_repository_issues(owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]:
    """Retrieve open, closed, or all GitHub issues for the repository."""
    return await github_service.get_repository_issues(owner, repo, state)

async def create_github_issue(owner: str, repo: str, title: str, body: str) -> Dict[str, Any]:
    """Create a new GitHub issue in the repository."""
    return await github_service.create_github_issue(owner, repo, title, body)
