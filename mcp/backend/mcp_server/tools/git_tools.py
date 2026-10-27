from typing import Dict, Any
from backend.services.github_service import GitHubService

github_service = GitHubService()

async def get_commit_diff(owner: str = "demo", repo: str = "demo_repo", commit_sha: str = "") -> Dict[str, Any]:
    """
    Compare two commits or retrieve the changed files and patch diffs for the latest or specified commit.
    """
    return await github_service.get_commit_diff(owner, repo, commit_sha)
