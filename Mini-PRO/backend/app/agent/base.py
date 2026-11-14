from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.app.safety.models import StepRecord


class ProposedAction(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    is_finish: bool = False
    final_answer: Optional[str] = None


class BaseAgent(ABC):
    """Abstract interface for AI agent execution."""

    @abstractmethod
    async def propose_next_action(
        self,
        task: str,
        history: List[StepRecord],
        step_number: int,
    ) -> ProposedAction:
        """Inspect context and history, then propose the next tool call or workflow completion."""
        pass
