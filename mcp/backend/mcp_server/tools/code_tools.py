from typing import Dict, Any, List, Optional
from backend.services.code_analyzer import CodeAnalyzer
from backend.services.github_service import GitHubService

github_service = GitHubService()

async def analyze_code(file_path: str, code: str = "", owner: str = "demo", repo: str = "demo_repo") -> Dict[str, Any]:
    """
    Analyze source code using Python AST for syntax errors, unused imports, unused variables,
    long functions, high cyclomatic complexity, missing error handling, and code smells.
    If code is omitted, it will automatically fetch the file content from the repository.
    """
    if not code:
        try:
            code = await github_service.read_repository_file(owner, repo, file_path)
        except Exception as e:
            return {
                "file_path": file_path,
                "error": f"Failed to read file '{file_path}': {str(e)}",
                "issues": [],
                "total_issues": 0
            }
    
    return CodeAnalyzer.analyze_source_code(code, file_path=file_path)

async def find_todos(owner: str = "demo", repo: str = "demo_repo", path: str = "") -> List[Dict[str, Any]]:
    """
    Search repository files for TODO, FIXME, HACK, and XXX comments with line numbers and snippets.
    """
    files = await github_service.list_repository_files(owner, repo, path)
    files_content = {}
    
    for f in files:
        if f.endswith("/") or not (f.endswith(".py") or f.endswith(".md") or f.endswith(".txt") or f.endswith(".js") or f.endswith(".ts")):
            continue
        try:
            content = await github_service.read_repository_file(owner, repo, f)
            files_content[f] = content
        except Exception:
            continue
            
    return CodeAnalyzer.scan_for_todos(files_content)
