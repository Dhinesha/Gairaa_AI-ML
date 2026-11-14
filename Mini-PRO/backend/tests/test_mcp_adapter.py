import asyncio
import time
import pytest
from backend.app.safety.engine import SafetyEngine
from backend.app.safety.models import (
    SafetyDecision,
    SafetyPolicy,
    StepRecord,
    WorkflowContext,
)
from backend.app.tools.mcp_adapter import MCPToolAdapter


@pytest.fixture
def test_context():
    return WorkflowContext(
        workflow_id="wf-mcp-test-01",
        task="Test MCP tool safety interception",
        start_time_epoch=time.time(),
        policy=SafetyPolicy(
            max_workflow_steps=5,
            max_repeated_calls=2,
            sensitive_tools=["mcp_send_webhook"],
        ),
    )


def test_mcp_tool_discovery():
    """Verify MCP adapter tool discovery."""
    async def _test():
        adapter = MCPToolAdapter(server_name="test_mcp_server")
        tools = await adapter.connect_and_discover(transport_type="mock")
        assert len(tools) >= 2
        tool_names = [t["name"] for t in tools]
        assert "mcp_query_database" in tool_names
        assert "mcp_send_webhook" in tool_names

    asyncio.run(_test())


def test_mcp_guarded_allowed_tool_execution(test_context):
    """Permitted safe MCP tool executes and outcome is captured."""
    async def _test():
        adapter = MCPToolAdapter(server_name="test_mcp_server")
        await adapter.connect_and_discover(transport_type="mock")

        safety_result, outcome = await adapter.execute_mcp_tool_guarded(
            tool_name="mcp_query_database",
            arguments={"query": "SELECT count(*) FROM users"},
            context=test_context,
        )

        assert safety_result.decision == SafetyDecision.ALLOW
        assert outcome is not None
        assert outcome.success is True
        assert outcome.result["tool"] == "mcp_query_database"

    asyncio.run(_test())


def test_mcp_guarded_sensitive_tool_interception(test_context):
    """Sensitive MCP tool call is intercepted with REQUIRE_APPROVAL."""
    async def _test():
        adapter = MCPToolAdapter(server_name="test_mcp_server")
        await adapter.connect_and_discover(transport_type="mock")

        # mcp_send_webhook is listed in sensitive_tools
        safety_result, outcome = await adapter.execute_mcp_tool_guarded(
            tool_name="mcp_send_webhook",
            arguments={"url": "https://external.api/deliver"},
            context=test_context,
        )

        assert safety_result.decision == SafetyDecision.REQUIRE_APPROVAL
        assert outcome is None  # Must NOT execute before approval!

    asyncio.run(_test())
