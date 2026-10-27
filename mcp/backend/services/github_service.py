import os
import httpx
from typing import Dict, Any, List, Optional
from pathlib import Path
from backend.config import settings
from backend.utils.helpers import logger

class GitHubService:
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.GITHUB_TOKEN
        self.base_url = "https://api.github.com"
        
    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-DevOps-Assistant-MCP"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _is_local_demo(self, owner: str, repo: str) -> bool:
        return (
            owner.lower() in ("demo", "local", "sample") 
            or repo.lower() in ("demo_repo", "sample_repo", "local_repo")
        )

    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repository details from GitHub API or local demo repo."""
        if self._is_local_demo(owner, repo):
            return {
                "name": repo,
                "repo": repo,
                "owner": owner,
                "full_name": f"{owner}/{repo}",
                "description": "Local demonstration repository for AI DevOps Assistant testing.",
                "default_branch": "main",
                "stars": 42,
                "forks": 7,
                "open_issues": 1,
                "url": "http://localhost:8000/demo_repo",
                "is_local_demo": True
            }

        url = f"{self.base_url}/repos/{owner}/{repo}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers=self._headers())
            if res.status_code == 404:
                raise ValueError(
                    f"GitHub repository '{owner}/{repo}' not found.\n"
                    "Possible reasons:\n"
                    "1. Repository does not exist or URL is mistyped.\n"
                    "2. Repository is private and requires a valid GITHUB_TOKEN.\n"
                    "3. GitHub token does not have permission."
                )
            if res.status_code in (401, 403):
                msg = res.json().get("message", "Forbidden")
                raise PermissionError(f"GitHub API error ({res.status_code}): {msg}. Please check your GITHUB_TOKEN or rate limit.")
            res.raise_for_status()
            data = res.json()
            return {
                "name": data.get("name"),
                "repo": repo,
                "owner": (data.get("owner") or {}).get("login", owner),
                "full_name": data.get("full_name"),
                "description": data.get("description") or "No description provided.",
                "default_branch": data.get("default_branch", "main"),
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "open_issues": data.get("open_issues_count", 0),
                "url": data.get("html_url", ""),
                "is_local_demo": False
            }

    async def list_repository_files(self, owner: str, repo: str, path: str = "") -> List[str]:
        """List files and folders inside repository or directory path."""
        if self._is_local_demo(owner, repo):
            target_dir = settings.DEMO_REPO_PATH / path
            if not target_dir.exists():
                return []
            results = []
            for item in sorted(target_dir.iterdir()):
                rel = item.relative_to(settings.DEMO_REPO_PATH).as_posix()
                if item.is_dir():
                    results.append(rel + "/")
                else:
                    results.append(rel)
            return results

        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path.strip('/')}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers=self._headers())
            if res.status_code == 404:
                return []
            res.raise_for_status()
            data = res.json()
            if isinstance(data, dict) and data.get("type") == "file":
                return [data.get("name")]
            return [
                (item.get("path") + ("/" if item.get("type") == "dir" else ""))
                for item in data
            ]

    async def read_repository_file(self, owner: str, repo: str, path: str) -> str:
        """Read text content of a file from repository."""
        if self._is_local_demo(owner, repo):
            target_file = settings.DEMO_REPO_PATH / path
            if not target_file.exists():
                raise FileNotFoundError(f"File '{path}' not found in demo repository.")
            return target_file.read_text(encoding="utf-8", errors="replace")

        import base64
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path.strip('/')}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers=self._headers())
            if res.status_code == 404:
                raise FileNotFoundError(f"File '{path}' not found in '{owner}/{repo}'.")
            res.raise_for_status()
            data = res.json()
            content_encoded = data.get("content", "")
            encoding = data.get("encoding")
            if encoding == "base64":
                return base64.b64decode(content_encoded).decode("utf-8", errors="replace")
            return content_encoded

    async def get_recent_commits(self, owner: str, repo: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent GitHub commits."""
        if self._is_local_demo(owner, repo):
            return [
                {
                    "commit_id": "c7a9f12d8",
                    "author": "Dhinesha Gnanavel",
                    "message": "fix: update authentication login logic and add unit tests",
                    "date": "2026-09-14T18:30:00Z",
                    "changed_files": ["auth.py", "tests/test_auth.py"]
                },
                {
                    "commit_id": "b3e8a45c1",
                    "author": "Dhinesha Gnanavel",
                    "message": "feat: initial authentication endpoints and schemas",
                    "date": "2026-09-13T11:20:00Z",
                    "changed_files": ["auth.py", "requirements.txt", "README.md"]
                }
            ][:limit]

        url = f"{self.base_url}/repos/{owner}/{repo}/commits?per_page={limit}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers=self._headers())
            res.raise_for_status()
            commits = res.json()
            results = []
            for c in commits:
                sha = c.get("sha", "")[:7]
                commit_info = c.get("commit") or {}
                author_info = commit_info.get("author") or {}
                results.append({
                    "commit_id": sha,
                    "full_sha": c.get("sha"),
                    "author": author_info.get("name", "Unknown"),
                    "message": (commit_info.get("message") or "").split("\n")[0],
                    "date": author_info.get("date", ""),
                    "changed_files": []
                })
            return results

    async def get_commit_diff(self, owner: str, repo: str, commit_sha: str = "") -> Dict[str, Any]:
        """Fetch files changed and patch diff for a commit."""
        if self._is_local_demo(owner, repo):
            return {
                "commit_id": commit_sha or "c7a9f12d8",
                "author": "Dhinesha Gnanavel",
                "message": "fix: update authentication login logic and add unit tests",
                "files_changed": [
                    {
                        "filename": "auth.py",
                        "status": "modified",
                        "additions": 14,
                        "deletions": 3,
                        "patch": "@@ -40,7 +40,18 @@ def authenticate_user(username, password):\n+    # TODO: Add token expiration\n+    if password == 'invalid':\n+        raise ValueError('Invalid password provided')\n"
                    },
                    {
                        "filename": "tests/test_auth.py",
                        "status": "added",
                        "additions": 28,
                        "deletions": 0,
                        "patch": "@@ -0,0 +1,28 @@\n+import pytest\n+from auth import authenticate_user\n"
                    }
                ]
            }

        async with httpx.AsyncClient(timeout=10.0) as client:
            if not commit_sha:
                # Retrieve the latest commit first
                commits = await self.get_recent_commits(owner, repo, limit=1)
                if not commits:
                    raise ValueError(f"No commits found in repository {owner}/{repo}")
                commit_sha = commits[0]["full_sha"]

            url = f"{self.base_url}/repos/{owner}/{repo}/commits/{commit_sha}"
            res = await client.get(url, headers=self._headers())
            res.raise_for_status()
            data = res.json()
            files_changed = []
            for f in data.get("files", []):
                files_changed.append({
                    "filename": f.get("filename"),
                    "status": f.get("status"),
                    "additions": f.get("additions", 0),
                    "deletions": f.get("deletions", 0),
                    "patch": f.get("patch", "Binary or large diff truncated")
                })
            commit_obj = data.get("commit") or {}
            author_obj = commit_obj.get("author") or {}
            return {
                "commit_id": data.get("sha", "")[:7],
                "author": author_obj.get("name", "Unknown"),
                "message": commit_obj.get("message", ""),
                "files_changed": files_changed
            }

    async def get_repository_issues(self, owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]:
        """Retrieve repository issues."""
        if self._is_local_demo(owner, repo):
            return [
                {
                    "id": 1,
                    "number": 1,
                    "title": "Authentication returns HTTP 500 on invalid credentials",
                    "state": "open",
                    "author": "Dhinesha",
                    "created_at": "2026-09-14T20:10:00Z",
                    "body": "When invalid credentials are supplied to authenticate_user(), an unhandled ValueError causes 500 error."
                }
            ]

        url = f"{self.base_url}/repos/{owner}/{repo}/issues?state={state}&per_page=20"
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers=self._headers())
            res.raise_for_status()
            issues = res.json()
            return [
                {
                    "id": item.get("id"),
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "state": item.get("state"),
                    "author": (item.get("user") or {}).get("login", "Unknown"),
                    "created_at": item.get("created_at"),
                    "body": item.get("body") or ""
                }
                for item in issues
                if "pull_request" not in item  # Exclude pull requests which GitHub returns in issues endpoint
            ]

    async def create_github_issue(self, owner: str, repo: str, title: str, body: str) -> Dict[str, Any]:
        """Create a GitHub issue after user confirmation."""
        if self._is_local_demo(owner, repo):
            return {
                "id": 28,
                "number": 28,
                "title": title,
                "body": body,
                "state": "open",
                "html_url": f"http://localhost:8000/{owner}/{repo}/issues/28",
                "message": "Demo issue created successfully in demo repository."
            }

        if not self.token:
            raise PermissionError("A GITHUB_TOKEN is required to create an issue on GitHub. Please configure GITHUB_TOKEN in .env.")

        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {"title": title, "body": body}
            res = await client.post(url, headers=self._headers(), json=payload)
            if res.status_code in (401, 403):
                raise PermissionError("Unauthorized to create issue. Ensure your GITHUB_TOKEN has 'repo' or 'issues:write' permission.")
            res.raise_for_status()
            data = res.json()
            return {
                "id": data.get("id"),
                "number": data.get("number"),
                "title": data.get("title"),
                "body": data.get("body"),
                "state": data.get("state"),
                "html_url": data.get("html_url"),
                "message": f"GitHub issue #{data.get('number')} created successfully!"
            }
