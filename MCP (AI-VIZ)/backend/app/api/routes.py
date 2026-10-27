"""
FastAPI REST API routes.
All MCP tool calls are also exposed here so the React frontend
can communicate via HTTP while MCP server runs independently.
"""
from fastapi import APIRouter, HTTPException
from typing import Any, Dict

from app.models.schemas import (
    AnalyzeRequest, ExecuteRequest, TraceRequest,
    ExplainRequest, ExplainErrorRequest, FlowRequest,
    MCPToolCallRequest,
)
from app.analyzer.ast_analyzer import analyze_code
from app.executor.sandbox import execute_code, trace_code
from app.services.explainer import explain_code, explain_error
from app.services.flow_generator import generate_flow

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "service": "CodeFlow MCP Backend"}


# ──────────────────────────────────────────────────────────────────────────── #
#  Analysis                                                                     #
# ──────────────────────────────────────────────────────────────────────────── #

@router.post("/analyze")
async def api_analyze(req: AnalyzeRequest) -> Dict[str, Any]:
    """Analyze Python code structure using AST (no execution)."""
    try:
        result = analyze_code(req.code)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────── #
#  Execution                                                                    #
# ──────────────────────────────────────────────────────────────────────────── #

@router.post("/execute")
async def api_execute(req: ExecuteRequest) -> Dict[str, Any]:
    """Execute Python code in a sandbox and return output."""
    try:
        result = execute_code(req.code, timeout=req.timeout or 10)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────── #
#  Tracing                                                                      #
# ──────────────────────────────────────────────────────────────────────────── #

@router.post("/trace")
async def api_trace(req: TraceRequest) -> Dict[str, Any]:
    """Execute Python code with full sys.settrace instrumentation."""
    try:
        result = trace_code(req.code, timeout=req.timeout or 10)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────── #
#  Explanation                                                                  #
# ──────────────────────────────────────────────────────────────────────────── #

@router.post("/explain")
async def api_explain(req: ExplainRequest) -> Dict[str, Any]:
    """Generate a beginner-friendly explanation of the code."""
    try:
        result = explain_code(req.code, req.trace)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain-error")
async def api_explain_error(req: ExplainErrorRequest) -> Dict[str, Any]:
    """Generate a beginner-friendly explanation for a Python error."""
    try:
        result = explain_error(
            req.code, req.error,
            error_type=req.error_type,
            error_line=req.error_line,
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────── #
#  Flow graph                                                                   #
# ──────────────────────────────────────────────────────────────────────────── #

@router.post("/flow")
async def api_flow(req: FlowRequest) -> Dict[str, Any]:
    """Generate a React Flow-compatible execution graph from code."""
    try:
        result = generate_flow(req.code)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────── #
#  MCP bridge – allows frontend to call MCP tools over HTTP                    #
# ──────────────────────────────────────────────────────────────────────────── #

MCP_TOOLS_META = [
    {
        "name": "analyze_python_code",
        "description": "Analyze Python code structure using AST without executing it.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source code to analyze"},
            },
            "required": ["code"],
        },
    },
    {
        "name": "execute_python_code",
        "description": "Execute Python code in a sandboxed environment and return output.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source code to execute"},
                "timeout": {"type": "integer", "description": "Timeout in seconds (default 10)"},
            },
            "required": ["code"],
        },
    },
    {
        "name": "trace_python_execution",
        "description": "Execute Python code with sys.settrace instrumentation to capture every step.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source code to trace"},
                "timeout": {"type": "integer", "description": "Timeout in seconds (default 10)"},
            },
            "required": ["code"],
        },
    },
    {
        "name": "inspect_variables",
        "description": "Inspect variables at a specific step in the execution trace.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "execution_id": {"type": "string", "description": "Execution identifier"},
                "step_number": {"type": "integer", "description": "Step number to inspect"},
            },
            "required": ["execution_id", "step_number"],
        },
    },
    {
        "name": "explain_code",
        "description": "Generate a beginner-friendly explanation of Python code.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source code to explain"},
                "trace": {"type": "array", "description": "Optional execution trace"},
            },
            "required": ["code"],
        },
    },
    {
        "name": "explain_error",
        "description": "Explain a Python error in beginner-friendly terms with fix suggestions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source code"},
                "error": {"type": "string", "description": "Error message"},
                "error_type": {"type": "string", "description": "Error type (optional)"},
                "error_line": {"type": "integer", "description": "Error line number (optional)"},
            },
            "required": ["code", "error"],
        },
    },
    {
        "name": "generate_flow",
        "description": "Generate a React Flow-compatible execution graph from Python code.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source code"},
            },
            "required": ["code"],
        },
    },
]


@router.get("/mcp/tools")
async def mcp_list_tools() -> Dict[str, Any]:
    """List all available MCP tools with their schemas."""
    return {"success": True, "tools": MCP_TOOLS_META}


@router.post("/mcp/call")
async def mcp_call_tool(req: MCPToolCallRequest) -> Dict[str, Any]:
    """Call an MCP tool by name with arguments. Routes to the appropriate handler."""
    tool = req.tool_name
    args = req.arguments

    try:
        if tool == "analyze_python_code":
            result = analyze_code(args.get("code", ""))
            return {"success": True, "tool": tool, "result": result}

        elif tool == "execute_python_code":
            result = execute_code(
                args.get("code", ""),
                timeout=args.get("timeout", 10),
            )
            return {"success": True, "tool": tool, "result": result}

        elif tool == "trace_python_execution":
            result = trace_code(
                args.get("code", ""),
                timeout=args.get("timeout", 10),
            )
            return {"success": True, "tool": tool, "result": result}

        elif tool == "inspect_variables":
            # Return dummy variable inspection for demo
            # In a full implementation this would use a session store
            return {
                "success": True,
                "tool": tool,
                "result": {
                    "execution_id": args.get("execution_id", ""),
                    "step_number": args.get("step_number", 0),
                    "variables": {},
                    "note": "Use trace_python_execution and index into the steps array."
                },
            }

        elif tool == "explain_code":
            result = explain_code(
                args.get("code", ""),
                args.get("trace"),
            )
            return {"success": True, "tool": tool, "result": result}

        elif tool == "explain_error":
            result = explain_error(
                args.get("code", ""),
                args.get("error", ""),
                error_type=args.get("error_type"),
                error_line=args.get("error_line"),
            )
            return {"success": True, "tool": tool, "result": result}

        elif tool == "generate_flow":
            result = generate_flow(args.get("code", ""))
            return {"success": True, "tool": tool, "result": result}

        else:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown MCP tool: {tool}",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
