from pydantic import BaseModel
from typing import Any, Optional, List, Dict


class CodeRequest(BaseModel):
    code: str


class AnalyzeRequest(BaseModel):
    code: str


class ExecuteRequest(BaseModel):
    code: str
    timeout: Optional[int] = 10


class TraceRequest(BaseModel):
    code: str
    timeout: Optional[int] = 10


class ExplainRequest(BaseModel):
    code: str
    trace: Optional[List[Dict[str, Any]]] = None


class ExplainErrorRequest(BaseModel):
    code: str
    error: str
    error_type: Optional[str] = None
    error_line: Optional[int] = None


class FlowRequest(BaseModel):
    code: str


class InspectRequest(BaseModel):
    execution_id: str
    step_number: int


class MCPToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]


# Response Models

class TraceStep(BaseModel):
    step: int
    line: int
    event: str  # call, return, line, exception, assignment, loop_iter, condition
    function_name: Optional[str] = None
    variables: Dict[str, Any] = {}
    call_stack: List[str] = []
    output: Optional[str] = None
    exception: Optional[str] = None
    source_line: Optional[str] = None
    description: Optional[str] = None
    loop_info: Optional[Dict[str, Any]] = None
    condition_info: Optional[Dict[str, Any]] = None


class TraceResponse(BaseModel):
    steps: List[TraceStep]
    total_steps: int
    final_output: str
    final_error: Optional[str] = None
    execution_time: float


class AnalyzeResponse(BaseModel):
    functions: List[Dict[str, Any]]
    variables: List[str]
    classes: List[str]
    loops: List[Dict[str, Any]]
    conditions: List[Dict[str, Any]]
    imports: List[str]
    return_statements: List[int]
    function_calls: List[Dict[str, Any]]
    line_count: int
    complexity: str


class ExecuteResponse(BaseModel):
    stdout: str
    stderr: str
    status: str  # success, error, timeout
    execution_time: float
    error_type: Optional[str] = None
    error_line: Optional[int] = None
    error_message: Optional[str] = None


class FlowNode(BaseModel):
    id: str
    type: str  # start, end, statement, condition, loop, function_call, return, output
    label: str
    line: Optional[int] = None
    data: Dict[str, Any] = {}


class FlowEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None
    animated: bool = False


class FlowResponse(BaseModel):
    nodes: List[FlowNode]
    edges: List[FlowEdge]


class ExplainResponse(BaseModel):
    summary: str
    steps_explanation: List[Dict[str, Any]]
    variables_explanation: str
    output_explanation: str
    beginner_tip: str


class ExplainErrorResponse(BaseModel):
    error_type: str
    error_message: str
    problematic_line: Optional[int]
    explanation: str
    fix_suggestion: str
    example_fix: Optional[str] = None
