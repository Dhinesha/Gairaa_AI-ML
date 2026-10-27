import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.config import settings
from backend.models.schemas import (
    ConnectRepoRequest, RepositoryInfo, ChatRequest, ChatResponse,
    ConfirmActionRequest, ProjectHealth
)
from backend.agent.agent import devops_agent
from backend.mcp_server.server import mcp_server_instance
from backend.services.github_service import GitHubService
from backend.utils.helpers import logger, parse_github_url, sanitize_log_message

app = FastAPI(
    title="AI DevOps Assistant MCP Backend",
    version="1.0.0",
    description="Backend API coordinating AI Agent, MCP Client, and FastMCP Server."
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CURRENT_REPO = {
    "url": "demo/demo_repo",
    "owner": "demo",
    "repo": "demo_repo",
    "info": None
}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = round((time.time() - start_time) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} returned {response.status_code} ({duration}ms)")
    return response

@app.get("/")
async def root():
    return {
        "service": "AI DevOps Assistant using MCP",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health-check")
async def health_check():
    mcp_tools = await mcp_server_instance.list_tools()
    return {
        "status": "healthy",
        "mcp_server": {
            "status": "connected",
            "name": "DevOpsAssistantMCP",
            "tools_count": len(mcp_tools)
        },
        "gemini_api": {
            "configured": bool(settings.GEMINI_API_KEY),
            "model": "gemini-flash-latest"
        },
        "github_api": {
            "token_configured": bool(settings.GITHUB_TOKEN),
            "rate_limit_authenticated": bool(settings.GITHUB_TOKEN)
        },
        "active_repo": CURRENT_REPO
    }

@app.post("/api/connect")
async def connect_repository(payload: ConnectRepoRequest):
    owner, repo = parse_github_url(payload.repo_url)
    if not owner or not repo:
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub repository format. Please use 'https://github.com/owner/repo' or 'owner/repo'."
        )

    gh_service = GitHubService(token=payload.token or settings.GITHUB_TOKEN)
    try:
        info_data = await gh_service.get_repository_info(owner, repo)
        CURRENT_REPO["url"] = payload.repo_url
        CURRENT_REPO["owner"] = owner
        CURRENT_REPO["repo"] = repo
        CURRENT_REPO["info"] = info_data
        logger.info(f"Successfully connected repository: {owner}/{repo}")
        return {
            "status": "connected",
            "repository": info_data
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        logger.error(f"Error connecting repository: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to connect repository: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    try:
        active_url = payload.repo_url or CURRENT_REPO["url"]
        return await devops_agent.chat(
            user_message=payload.message,
            history=payload.history,
            repo_url=active_url
        )
    except Exception as e:
        logger.error(f"Chat processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.post("/api/confirm")
async def confirm_action(payload: ConfirmActionRequest):
    try:
        result = await devops_agent.execute_confirmed_action(
            action_id=payload.action_id,
            confirmed=payload.confirmed
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error executing confirmed action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tools")
async def list_tools():
    tools = await mcp_server_instance.list_tools()
    return [
        {
            "name": t.name,
            "description": t.description,
            "input_schema": t.input_schema if hasattr(t, "input_schema") else {}
        }
        for t in tools
    ]

@app.post("/api/tools/execute")
async def execute_tool_direct(request: Request):
    """Directly invokes an MCP tool for diagnostics or manual runs."""
    body = await request.json()
    tool_name = body.get("tool_name")
    arguments = body.get("arguments", {})

    if not tool_name:
        raise HTTPException(status_code=400, detail="Missing 'tool_name' field.")

    res = await mcp_server_instance.call_tool(tool_name, arguments)
    return {"status": "success", "result": res}

@app.get("/api/repo-health")
async def repo_health():
    owner = CURRENT_REPO["owner"]
    repo = CURRENT_REPO["repo"]
    res = await mcp_server_instance.call_tool("get_project_health", {"owner": owner, "repo": repo})
    content = getattr(res, "structured_content", None)
    if not content and hasattr(res, "content"):
        import json
        text_joined = "\n".join([c.text for c in res.content if hasattr(c, "text")])
        try:
            content = json.loads(text_joined)
        except Exception:
            content = text_joined
            
    if isinstance(content, dict) and "result" in content:
        content = content["result"]
    return content or {}
