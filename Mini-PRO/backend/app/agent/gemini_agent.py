import json
import logging
import os
from typing import List
from backend.app.agent.base import BaseAgent, ProposedAction
from backend.app.core.config import settings
from backend.app.safety.models import StepRecord
from backend.app.tools.registry import default_tool_registry

logger = logging.getLogger("agent.gemini")


class GeminiAgent(BaseAgent):
    """
    LLM-powered agent using Google Gemini (via google-genai SDK).
    Enabled when GEMINI_API_KEY environment variable is configured.
    """

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.model = model or settings.GEMINI_MODEL or "gemini-1.5-flash"
        self._client = None
        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized Gemini Client with model {self.model}")
            except Exception as e:
                logger.warning(f"Could not initialize google-genai client: {e}")

    async def propose_next_action(
        self,
        task: str,
        history: List[StepRecord],
        step_number: int,
    ) -> ProposedAction:
        if not self._client:
            # Informative fallback if API key not provided
            return ProposedAction(
                tool_name="search_employees",
                arguments={"query": task[:20]},
                is_finish=False,
            )

        # Build prompt with available tools and execution history
        available_tools = default_tool_registry.list_tools()
        history_summary = []
        for s in history:
            history_summary.append({
                "step": s.step_number,
                "tool": s.tool_name,
                "arguments": s.arguments,
                "result": s.result if s.success else s.error,
                "success": s.success,
            })

        system_instruction = (
            "You are an AI assistant executing tools to accomplish user tasks.\n"
            "Analyze the task and previous steps. Respond ONLY with valid JSON in this format:\n"
            "If calling a tool:\n"
            '{"action": "call_tool", "tool_name": "<name>", "arguments": {<args>}}\n'
            "If finished:\n"
            '{"action": "finish", "final_answer": "<summary of final outcome>"}\n'
            f"Available tools: {json.dumps(available_tools)}"
        )

        user_prompt = (
            f"Task: {task}\n"
            f"Execution Step: {step_number}\n"
            f"Previous Step History: {json.dumps(history_summary, default=str)}\n"
            "What is your next action?"
        )

        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=[system_instruction, user_prompt],
            )
            raw_text = response.text.strip()
            # Clean markdown code block if present
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            data = json.loads(raw_text.strip())

            if data.get("action") == "finish":
                return ProposedAction(
                    tool_name="",
                    arguments={},
                    is_finish=True,
                    final_answer=data.get("final_answer", "Task complete."),
                )
            else:
                return ProposedAction(
                    tool_name=data.get("tool_name", "search_employees"),
                    arguments=data.get("arguments", {}),
                    is_finish=False,
                )
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return ProposedAction(
                tool_name="",
                arguments={},
                is_finish=True,
                final_answer=f"Gemini execution concluded with note: {str(e)}",
            )
