import asyncio
import inspect
import time
from typing import Any, Callable, Dict, List, Optional
from backend.app.safety.models import ToolOutcome
from backend.app.tools.mock_tools import (
    tool_delete_employee_record,
    tool_explain_database,
    tool_flaky_error_tool,
    tool_generate_report,
    tool_get_employee_details,
    tool_inspect_uploaded_db,
    tool_lookup_feed,
    tool_modify_database_table,
    tool_modify_employee_salary,
    tool_query_uploaded_db,
    tool_repeating_static_tool,
    tool_search_employees,
    tool_sync_cache,
)


class ToolRegistry:
    """
    Central tool registry and execution supervisor.
    Executes permitted tools safely, enforces timeouts, and formats structured outcomes.
    """

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._descriptions: Dict[str, str] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register("search_employees", tool_search_employees, "Search employee directory by name/dept")
        self.register("get_employee_details", tool_get_employee_details, "Retrieve full employee profile record")
        self.register("generate_report", tool_generate_report, "Compile records into a formatted executive summary report")
        self.register("modify_employee_salary", tool_modify_employee_salary, "SENSITIVE: Modifies compensation structure")
        self.register("delete_employee_record", tool_delete_employee_record, "CRITICAL: Permanently purge employee profile")
        self.register("repeating_static_tool", tool_repeating_static_tool, "Returns unchanged static result for no-progress testing")
        self.register("flaky_error_tool", tool_flaky_error_tool, "Simulates network timeout/error for resilience testing")
        self.register("tool_a", tool_lookup_feed, "Mock action A for cyclic loop testing")
        self.register("tool_b", tool_sync_cache, "Mock action B for cyclic loop testing")
        self.register("inspect_uploaded_db", tool_inspect_uploaded_db, "Inspect schema and foreign keys of uploaded database")
        self.register("query_uploaded_db", tool_query_uploaded_db, "Execute safe analytical queries on uploaded dataset")
        self.register("explain_database", tool_explain_database, "Generate pedagogical teaching report for uploaded database in Tamil and English")
        self.register("modify_database_table", tool_modify_database_table, "SENSITIVE: Schema drop/alter mutation requiring Human Approval")

    def register(self, name: str, fn: Callable, description: str = ""):
        self._tools[name.lower().strip()] = fn
        self._descriptions[name.lower().strip()] = description

    def get_tool(self, name: str) -> Optional[Callable]:
        return self._tools.get(name.lower().strip())

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {"name": name, "description": desc}
            for name, desc in sorted(self._descriptions.items())
        ]

    async def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        timeout_seconds: float = 15.0,
    ) -> ToolOutcome:
        """Safely executes a registered tool with timeout enforcement and error isolation."""
        clean_name = tool_name.lower().strip()
        fn = self.get_tool(clean_name)
        if not fn:
            return ToolOutcome(
                tool_name=tool_name,
                arguments=arguments,
                result=None,
                success=False,
                error=f"Tool '{tool_name}' is not registered or permitted.",
                duration_ms=0.0,
            )

        start = time.perf_counter()
        try:
            if inspect.iscoroutinefunction(fn):
                coro = fn(**arguments)
                res = await asyncio.wait_for(coro, timeout=timeout_seconds)
            else:
                loop = asyncio.get_event_loop()
                res = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: fn(**arguments)),
                    timeout=timeout_seconds,
                )

            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return ToolOutcome(
                tool_name=tool_name,
                arguments=arguments,
                result=res,
                success=True,
                error=None,
                duration_ms=round(elapsed_ms, 2),
            )
        except asyncio.TimeoutError:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return ToolOutcome(
                tool_name=tool_name,
                arguments=arguments,
                result=None,
                success=False,
                error=f"Tool '{tool_name}' timed out after {timeout_seconds}s.",
                duration_ms=round(elapsed_ms, 2),
            )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return ToolOutcome(
                tool_name=tool_name,
                arguments=arguments,
                result=None,
                success=False,
                error=str(exc),
                duration_ms=round(elapsed_ms, 2),
            )


default_tool_registry = ToolRegistry()
