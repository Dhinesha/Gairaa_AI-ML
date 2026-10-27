from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ConnectRepoRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL (e.g. https://github.com/owner/repo or owner/repo)")
    token: Optional[str] = Field(None, description="Optional GitHub PAT")

class RepositoryInfo(BaseModel):
    owner: str
    repo: str
    name: str
    description: Optional[str] = ""
    default_branch: str = "main"
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    url: str = ""
    is_local_demo: bool = False

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user', 'assistant', or 'system'")
    content: str

class ToolCallLog(BaseModel):
    id: str
    tool_name: str
    arguments: Dict[str, Any]
    status: str = "pending"  # "pending", "running", "success", "error"
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: Optional[float] = None

class PendingAction(BaseModel):
    action_id: str
    tool_name: str
    action_type: str = "create_github_issue"
    description: str
    arguments: Dict[str, Any]

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    repo_url: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    tool_executions: List[ToolCallLog] = []
    requires_confirmation: bool = False
    pending_action: Optional[PendingAction] = None

class ConfirmActionRequest(BaseModel):
    action_id: str
    confirmed: bool
    arguments: Optional[Dict[str, Any]] = None

class CodeIssue(BaseModel):
    file_path: str
    line_number: int
    issue_type: str
    severity: str  
    message: str
    snippet: Optional[str] = None
    recommendation: Optional[str] = None

class CodeAnalysisResult(BaseModel):
    file_path: str
    issues: List[CodeIssue] = []
    total_issues: int = 0
    high_severity: int = 0
    medium_severity: int = 0
    low_severity: int = 0

class TestCaseFailure(BaseModel):
    test_name: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    error_message: str
    traceback: str

class TestRunResult(BaseModel):
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    failures: List[TestCaseFailure] = []
    raw_output: str = ""
    success: bool = True

class ProjectHealth(BaseModel):
    repository: str
    total_files: int = 0
    python_files: int = 0
    test_files: int = 0
    tests_total: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    test_pass_percentage: float = 100.0
    code_issues_high: int = 0
    code_issues_medium: int = 0
    code_issues_low: int = 0
    total_todos: int = 0
    recent_commits: int = 0
    open_issues: int = 0
    health_score: int = 100
    rating: str = "Good"  

class TodoItem(BaseModel):
    file_path: str
    line_number: int
    tag: str  # TODO, FIXME, HACK, XXX
    text: str
