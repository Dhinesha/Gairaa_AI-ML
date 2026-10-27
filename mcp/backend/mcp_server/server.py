import sys
import asyncio
from typing import Dict, Any, List, Optional
from mcp.server.mcpserver import MCPServer
from backend.utils.helpers import logger
from backend.mcp_server.tools.github_tools import (
    get_repository_info as _get_repo_info,
    list_repository_files as _list_repo_files,
    read_repository_file as _read_repo_file,
    get_recent_commits as _get_commits,
    get_repository_issues as _get_issues,
    create_github_issue as _create_issue
)
from backend.mcp_server.tools.code_tools import (
    analyze_code as _analyze_code,
    find_todos as _find_todos
)
from backend.mcp_server.tools.test_tools import (
    run_tests as _run_tests,
    analyze_test_failure as _analyze_test_failure
)
from backend.mcp_server.tools.git_tools import (
    get_commit_diff as _get_commit_diff
)
from backend.mcp_server.tools.health_tools import (
    get_project_health as _get_project_health
)

def create_mcp_server() -> MCPServer:
    server = MCPServer(
        name="DevOpsAssistantMCP",
        version="1.0.0",
        description="Standardized MCP Server for GitHub, Test Runner, and Code Analysis tools."
    )
    @server.tool()
    async def get_repository_info(owner: str, repo: str) -> Dict[str, Any]:
        """Retrieve basic repository information including name, description, default branch, stars, and open issues."""
        logger.info(f"MCP Tool invoked: get_repository_info(owner={owner}, repo={repo})")
        return await _get_repo_info(owner, repo)
    @server.tool()
    async def list_repository_files(owner: str, repo: str, path: str = "") -> List[str]:
        """List files and folders inside the repository or a specific directory path."""
        logger.info(f"MCP Tool invoked: list_repository_files(owner={owner}, repo={repo}, path='{path}')")
        return await _list_repo_files(owner, repo, path)
    @server.tool()
    async def read_repository_file(owner: str, repo: str, path: str) -> str:
        """Read source code or configuration files from the repository."""
        logger.info(f"MCP Tool invoked: read_repository_file(owner={owner}, repo={repo}, path='{path}')")
        return await _read_repo_file(owner, repo, path)
    @server.tool()
    async def get_recent_commits(owner: str, repo: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent repository commits with author, message, date, and commit ID."""
        logger.info(f"MCP Tool invoked: get_recent_commits(owner={owner}, repo={repo}, limit={limit})")
        return await _get_commits(owner, repo, limit)
    @server.tool()
    async def get_repository_issues(owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]:
        """Retrieve GitHub issues for the repository (state: 'open', 'closed', or 'all')."""
        logger.info(f"MCP Tool invoked: get_repository_issues(owner={owner}, repo={repo}, state='{state}')")
        return await _get_issues(owner, repo, state)
    @server.tool()
    async def create_github_issue(owner: str, repo: str, title: str, body: str) -> Dict[str, Any]:
        """Create a new GitHub issue in the repository. IMPORTANT: Call only after explicit user confirmation."""
        logger.info(f"MCP Tool invoked: create_github_issue(owner={owner}, repo={repo}, title='{title}')")
        return await _create_issue(owner, repo, title, body)
    @server.tool()
    async def analyze_code(file_path: str, code: str = "", owner: str = "demo", repo: str = "demo_repo") -> Dict[str, Any]:
        """Analyze source code with Python AST for syntax errors, unused imports, long functions, complexity, and code smells."""
        logger.info(f"MCP Tool invoked: analyze_code(file_path='{file_path}')")
        return await _analyze_code(file_path=file_path, code=code, owner=owner, repo=repo)
    @server.tool()
    async def run_tests(owner: str = "demo", repo: str = "demo_repo", test_command: str = "pytest") -> Dict[str, Any]:
        """Run tests using pytest or unittest on the repository and return total, passed, failed, and traceback details."""
        logger.info(f"MCP Tool invoked: run_tests(owner={owner}, repo={repo}, cmd='{test_command}')")
        return await _run_tests(owner=owner, repo=repo, test_command=test_command)

    @server.tool()
    async def analyze_test_failure(test_name: str, error_message: str, traceback: str = "", file_path: str = "") -> Dict[str, Any]:
        """Diagnose a failed test case and explain the likely root cause and recommended code fix."""
        logger.info(f"MCP Tool invoked: analyze_test_failure(test_name='{test_name}')")
        return await _analyze_test_failure(test_name, error_message, traceback, file_path)
    @server.tool()
    async def get_project_health(owner: str = "demo", repo: str = "demo_repo") -> Dict[str, Any]:
        """Generate an overall project health summary with test rates, code smells, TODO counts, and a 0-100 score."""
        logger.info(f"MCP Tool invoked: get_project_health(owner={owner}, repo={repo})")
        return await _get_project_health(owner, repo)

    @server.tool()
    async def get_commit_diff(owner: str = "demo", repo: str = "demo_repo", commit_sha: str = "") -> Dict[str, Any]:
        """Retrieve changed files and git diff patches for the latest or specified commit."""
        logger.info(f"MCP Tool invoked: get_commit_diff(owner={owner}, repo={repo})")
        return await _get_commit_diff(owner, repo, commit_sha)
    @server.tool()
    async def find_todos(owner: str = "demo", repo: str = "demo_repo", path: str = "") -> List[Dict[str, Any]]:
        """Search repository files for TODO, FIXME, HACK, and XXX comments with line numbers."""
        logger.info(f"MCP Tool invoked: find_todos(owner={owner}, repo={repo})")
        return await _find_todos(owner, repo, path)

    return server

mcp_server_instance = create_mcp_server()

if __name__ == "__main__":
    logger.info("Starting MCP Server over stdio transport...")
    asyncio.run(mcp_server_instance.run_stdio_async())
