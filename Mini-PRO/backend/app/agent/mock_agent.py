from typing import List
from backend.app.agent.base import BaseAgent, ProposedAction
from backend.app.safety.models import StepRecord


class DeterministicMockAgent(BaseAgent):
    """
    Deterministic mock agent implementing test scenarios:
    1. mock:normal_success — standard 3-step pipeline finishing successfully.
    2. mock:infinite_loop — cyclic A -> B -> A -> B loop pattern.
    3. mock:repeated_calls — repeated identical calls to search_employees.
    4. mock:no_progress — stagnant calls returning unchanged static payload.
    5. mock:sensitive_action — sensitive salary modification requiring human authorization.
    6. mock:timeout_failure — flaky tool failure for retry/timeout evaluation.
    """

    def __init__(self, scenario: str = "mock:normal_success"):
        self.scenario = scenario.lower().strip()

    async def propose_next_action(
        self,
        task: str,
        history: List[StepRecord],
        step_number: int,
    ) -> ProposedAction:
        scenario = self.scenario

        # -------------------------------------------------------------
        # SCENARIO 1: Normal Multi-Step Success
        # -------------------------------------------------------------
        if scenario in ("mock:normal_success", "normal", "success"):
            # Step 1: Search employees
            if step_number == 1 or len(history) == 0:
                return ProposedAction(
                    tool_name="search_employees",
                    arguments={"department": "Engineering", "limit": 5},
                )
            # Step 2: Get details for first employee found
            elif step_number == 2 or len(history) == 1:
                return ProposedAction(
                    tool_name="get_employee_details",
                    arguments={"employee_id": "EMP-101"},
                )
            # Step 3: Generate report
            elif step_number == 3 or len(history) == 2:
                return ProposedAction(
                    tool_name="generate_report",
                    arguments={
                        "title": "Engineering Staff Readiness Report",
                        "records": ["EMP-101", "EMP-102"],
                        "format": "markdown",
                    },
                )
            # Step 4: Complete
            else:
                return ProposedAction(
                    tool_name="",
                    arguments={},
                    is_finish=True,
                    final_answer="Workflow completed successfully: Verified engineering personnel and generated report REP-101.",
                )

        # -------------------------------------------------------------
        # SCENARIO 2: Infinite Cyclic Loop (A -> B -> A -> B...)
        # -------------------------------------------------------------
        elif scenario in ("mock:infinite_loop", "infinite_loop", "loop"):
            # Alternates tool_a and tool_b endlessly
            if step_number % 2 == 1:
                return ProposedAction(
                    tool_name="tool_a",
                    arguments={"lookup": "data_feed"},
                )
            else:
                return ProposedAction(
                    tool_name="tool_b",
                    arguments={"sync": "cache"},
                )

        # -------------------------------------------------------------
        # SCENARIO 3: Repeated Identical Tool Calls
        # -------------------------------------------------------------
        elif scenario in ("mock:repeated_calls", "repeated_calls", "repeat"):
            # Same tool with exact same arguments repeatedly
            return ProposedAction(
                tool_name="search_employees",
                arguments={"query": "John Doe", "department": "Engineering"},
            )

        # -------------------------------------------------------------
        # SCENARIO 4: No Progress / Stagnant Output
        # -------------------------------------------------------------
        elif scenario in ("mock:no_progress", "no_progress", "stagnant"):
            # Same static tool producing unchanged outcome repeatedly
            return ProposedAction(
                tool_name="repeating_static_tool",
                arguments={"ping": "health_check"},
            )

        # -------------------------------------------------------------
        # SCENARIO 5: Sensitive Action Requiring Approval & Safe Recovery
        # -------------------------------------------------------------
        elif scenario in ("mock:sensitive_action", "sensitive", "approval"):
            # Step 1: Search employee
            if len(history) == 0:
                return ProposedAction(
                    tool_name="search_employees",
                    arguments={"query": "Elena Rostova", "department": "Finance"},
                )
            # Step 2: Propose sensitive salary modification
            elif len(history) == 1:
                return ProposedAction(
                    tool_name="modify_employee_salary",
                    arguments={
                        "employee_id": "EMP-204",
                        "new_salary": 155000.0,
                        "reason": "Q4 Performance Merit Compensation Adjustment",
                    },
                )
            # Step 3: If resumed and step 2 was approved and executed
            else:
                return ProposedAction(
                    tool_name="",
                    arguments={},
                    is_finish=True,
                    final_answer="Sensitive compensation adjustment successfully reviewed, approved, and applied for employee EMP-204.",
                )

        # -------------------------------------------------------------
        # SCENARIO 6: Flaky Tool / Timeout Failure
        # -------------------------------------------------------------
        elif scenario in ("mock:timeout_failure", "failure", "timeout"):
            return ProposedAction(
                tool_name="flaky_error_tool",
                arguments={"action": f"sync_cluster_attempt_{step_number}"},
            )

        # -------------------------------------------------------------
        # SCENARIO 7: AI Database Explainer & Teacher
        # -------------------------------------------------------------
        elif scenario in ("mock:db_explainer", "db_explainer", "teach_database", "database_explainer"):
            # Check if task asks for a dangerous destructive query
            if "drop" in task.lower() or "delete" in task.lower():
                return ProposedAction(
                    tool_name="modify_database_table",
                    arguments={"table_name": "students", "action": "DROP_TABLE"},
                )

            # Step 1: Inspect database schema & foreign keys
            if step_number == 1 or len(history) == 0:
                return ProposedAction(
                    tool_name="inspect_uploaded_db",
                    arguments={"target": "uploaded_schema", "include_foreign_keys": True},
                )
            # Step 2: Query distribution & sample statistics
            elif step_number == 2 or len(history) == 1:
                return ProposedAction(
                    tool_name="query_uploaded_db",
                    arguments={
                        "query": "SELECT department, COUNT(*) as count, AVG(gpa) as avg_gpa FROM students GROUP BY department",
                        "limit": 10,
                    },
                )
            # Step 3: Synthesize pedagogical teaching explanation
            elif step_number == 3 or len(history) == 2:
                return ProposedAction(
                    tool_name="explain_database",
                    arguments={"topic": "RelationalArchitecture", "language": "both"},
                )
            # Conclude with report
            else:
                return ProposedAction(
                    tool_name="generate_report",
                    arguments={"title": "Comprehensive Database Teaching Report (Bilingual)"},
                    is_finish=True,
                    final_answer=(
                        "Database Teaching Analysis Completed Successfully: Inspected 3 normalized tables, "
                        "analyzed student GPA distributions, verified 2 foreign key relationships, and generated "
                        "student-friendly explanations in both English and Tamil."
                    ),
                )

        # Fallback default
        else:
            return ProposedAction(
                tool_name="",
                arguments={},
                is_finish=True,
                final_answer=f"Executed default task '{task}' successfully.",
            )
