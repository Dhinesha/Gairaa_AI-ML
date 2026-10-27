"""
CodeFlow MCP – FastAPI Application Entry Point

This backend serves:
1. REST API endpoints (/api/*) consumed by the React frontend
2. MCP bridge endpoints (/api/mcp/*) that proxy MCP tool calls
3. The MCP server runs separately on port 8001
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.routes import router

load_dotenv()

app = FastAPI(
    title="CodeFlow MCP Backend",
    description="AI-Powered Python Code Execution Visualizer – Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow all origins for development – tighten in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {
        "service": "CodeFlow MCP Backend",
        "version": "1.0.0",
        "docs": "/docs",
        "api": "/api",
        "mcp_tools": "/api/mcp/tools",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
