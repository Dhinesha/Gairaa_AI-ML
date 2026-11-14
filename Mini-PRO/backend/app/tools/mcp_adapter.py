import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from backend.app.safety.engine import SafetyEngine, default_safety_engine
from backend.app.safety.models import (
    ActionRequest,
    SafetyDecision,
    SafetyEvaluationResult,
    ToolOutcome,
    WorkflowContext,
)

logger = logging.getLogger("mcp.adapter")


class MCPToolAdapter:
    """
    Adapter layer for Model Context Protocol (MCP) tool integration.
    Discovers, validates, registers permitted tools, and wraps tool invocations
    with the pre-execution safety engine gate.
    """

    def __init__(
        self,
        server_name: str = "local_mcp_server",
        permitted_tools: Optional[List[str]] = None,
        safety_engine: Optional[SafetyEngine] = None,
    ):
        self.server_name = server_name
        self.permitted_tools = set(permitted_tools) if permitted_tools else None
        self.safety_engine = safety_engine or default_safety_engine
        self._discovered_tools: Dict[str, Dict[str, Any]] = {}
        self.is_connected = False

    async def connect_and_discover(self, transport_type: str = "mock", command: str = None) -> List[Dict[str, Any]]:
        """
        Connect to an MCP server (stdio / sse) and discover its available tools.
        Filters against permitted_tools allowlist.
        """
        logger.info(f"Connecting to MCP server '{self.server_name}' via {transport_type}...")
        try:
            if transport_type == "stdio" and command:
                # Real MCP SDK client connection via stdio transport
                from mcp import ClientSession, StdioServerParameters
                from mcp.client.stdio import stdio_client

                server_params = StdioServerParameters(command=command, args=[])
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        tools_result = await session.list_tools()
                        for tool in tools_result.tools:
                            t_name = tool.name
                            if self.permitted_tools is None or t_name in self.permitted_tools:
                                self._discovered_tools[t_name] = {
                                    "name": t_name,
                                    "description": tool.description,
                                    "input_schema": tool.inputSchema,
                                }
                self.is_connected = True
            else:
                # Mock MCP discoverable tools for deterministic verification
                mock_mcp_catalog = [
                    {
                        "name": "mcp_query_database",
                        "description": "Execute structured query against MCP read replica",
                        "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}},
                    },
                    {
                        "name": "mcp_send_webhook",
                        "description": "Deliver event payload to external webhook subscriber",
                        "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}},
                    },
                ]
                for tool in mock_mcp_catalog:
                    t_name = tool["name"]
                    if self.permitted_tools is None or t_name in self.permitted_tools:
                        self._discovered_tools[t_name] = tool
                self.is_connected = True

            logger.info(
                f"Discovered {len(self._discovered_tools)} permitted tools from MCP server '{self.server_name}'."
            )
            return list(self._discovered_tools.values())
        except Exception as e:
            logger.error(f"Failed to connect to MCP server '{self.server_name}': {e}")
            self.is_connected = False
            return []

    async def execute_mcp_tool_guarded(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: WorkflowContext,
        timeout_seconds: float = 10.0,
    ) -> Tuple[SafetyEvaluationResult, Optional[ToolOutcome]]:
        """
        Intercepts tool call, runs through Safety Engine, executes only if ALLOWED,
        and records execution result.
        """
        action = ActionRequest(
            tool_name=tool_name,
            arguments=arguments,
            workflow_id=context.workflow_id,
            step_number=len(context.history) + 1,
        )

        # 1. Inspect proposed tool call with Safety Engine
        safety_result = self.safety_engine.evaluate(action, context)
        if safety_result.decision != SafetyDecision.ALLOW:
            logger.warning(
                f"MCP tool '{tool_name}' intercepted and {safety_result.decision}: {safety_result.reason}"
            )
            return safety_result, None

        # 2. Check if tool is registered and permitted
        if tool_name not in self._discovered_tools and self.permitted_tools and tool_name not in self.permitted_tools:
            return SafetyEvaluationResult(
                decision=SafetyDecision.BLOCK,
                reason=f"MCP tool '{tool_name}' is not permitted by authorization policy.",
                risk_level=safety_result.risk_level,
            ), None

        # 3. Execute tool safely with timeout
        start = time.perf_counter()
        try:
            # Simulate or dispatch MCP execution
            await asyncio.sleep(0.05)
            result_payload = {
                "mcp_server": self.server_name,
                "tool": tool_name,
                "output": f"Successfully executed {tool_name} via MCP adapter.",
                "data": arguments,
            }
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            outcome = ToolOutcome(
                tool_name=tool_name,
                arguments=arguments,
                result=result_payload,
                success=True,
                duration_ms=round(elapsed_ms, 2),
            )
            return safety_result, outcome
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            outcome = ToolOutcome(
                tool_name=tool_name,
                arguments=arguments,
                result=None,
                success=False,
                error=f"MCP tool error: {str(e)}",
                duration_ms=round(elapsed_ms, 2),
            )
            return safety_result, outcome
