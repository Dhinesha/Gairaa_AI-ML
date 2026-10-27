import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.utils.helpers import logger

class GitService:
    """Local Git helper service for running diffs or inspecting commits in cloned repositories."""

    @staticmethod
    def get_local_diff(repo_dir: Path, commit_sha: str = "HEAD~1") -> Dict[str, Any]:
        """Runs git diff for local repository if git is initialized."""
        if not (repo_dir / ".git").exists():
            return {
                "commit_id": "HEAD",
                "author": "Local Developer",
                "message": "Local uncommitted changes",
                "files_changed": []
            }
        
        try:
            cmd = ["git", "diff", "--stat", commit_sha]
            res = subprocess.run(cmd, cwd=str(repo_dir), capture_output=True, text=True, check=True)
            return {
                "commit_id": commit_sha,
                "author": "Local Developer",
                "message": "Diff output",
                "raw_stat": res.stdout,
                "files_changed": []
            }
        except Exception as e:
            logger.warning(f"Git diff error: {e}")
            return {
                "commit_id": commit_sha,
                "error": str(e),
                "files_changed": []
            }
