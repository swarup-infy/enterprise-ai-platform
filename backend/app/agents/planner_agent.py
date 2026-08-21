"""
Planner Agent.

Breaks complex user goals into executable plans.
"""

from __future__ import annotations

from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService


class PlannerAgent(BaseAgent):
    """
    Planning agent responsible for task decomposition.
    """

    SYSTEM_PROMPT = """
You are an expert AI Planning Agent.

Your job is to:
- Understand the user's objective.
- Break it into logical steps.
- Identify required tools.
- Identify required agents.
- Produce an execution plan.

Return only Markdown.
""".strip()

    def __init__(self) -> None:
        super().__init__(
            name="planner",
            description="Task Planning Agent",
        )

        self.llm = LLMService()

    # ==========================================================================
    # Run
    # ==========================================================================

    async def run(
        self,
        task: str,
        **kwargs,
    ) -> str:
        """
        Generate an execution plan.
        """

        prompt = f"""
Create a detailed execution plan.

Task:
{task}

Include:
1. Goal
2. Required Steps
3. Required Tools
4. Required Agents
5. Expected Output
6. Risks
"""

        return await self.llm.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
        )