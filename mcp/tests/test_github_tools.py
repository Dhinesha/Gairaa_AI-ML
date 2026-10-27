import pytest
from backend.mcp_server.tools.github_tools import (
    get_repository_info,
    list_repository_files,
    read_repository_file,
    get_recent_commits,
    get_repository_issues,
    create_github_issue
)

OWNER = "Dhinesha"
REPO  = "spark-studio"

@pytest.mark.asyncio
async def test_get_repository_info():
    info = await get_repository_info(OWNER, REPO)
    assert info["name"] == REPO
    assert "default_branch" in info
    assert "stars" in info

@pytest.mark.asyncio
async def test_list_repository_files():
    files = await list_repository_files(OWNER, REPO)
    assert isinstance(files, list)
    assert len(files) > 0

@pytest.mark.asyncio
async def test_read_repository_file():
    # First discover a real file, then read it
    files = await list_repository_files(OWNER, REPO)
    assert len(files) > 0
    content = await read_repository_file(OWNER, REPO, files[0])
    assert isinstance(content, str)
    assert len(content) > 0

@pytest.mark.asyncio
async def test_get_recent_commits():
    commits = await get_recent_commits(OWNER, REPO, limit=5)
    assert len(commits) > 0
    assert "author" in commits[0]
    assert "commit_id" in commits[0]

@pytest.mark.asyncio
async def test_get_repository_issues():
    issues = await get_repository_issues(OWNER, REPO)
    # issues list may be empty for a repo with no open issues — just check type
    assert isinstance(issues, list)
    if len(issues) > 0:
        assert "title" in issues[0]

@pytest.mark.asyncio
async def test_create_github_issue():
    res = await create_github_issue(
        OWNER,
        REPO,
        "Test issue title",
        "Test issue description"
    )
    assert "number" in res
    assert res["title"] == "Test issue title"
