"""
Memory Agent.

Stores, retrieves, summarizes and manages long-term memory
for the Enterprise AI Platform.
"""

from __future__ import annotations

from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService


class MemoryAgent(BaseAgent):
    """
    Long-term memory agent.
    """

    SYSTEM_PROMPT = """
You are an expert Memory Agent.

Responsibilities:
- Store important information
- Retrieve relevant memories
- Summarize long conversations
- Remove duplicate memories
- Produce concise memory entries

Always return Markdown.
""".strip()

    def __init__(self) -> None:
        super().__init__(
            name="memory",
            description="Long-Term Memory Agent",
        )

        self.llm = LLMService()

    # ==========================================================================
    # Run
    # ==========================================================================

    async def run(
        self,
        task: str,
        memory: str = "",
        context: str = "",
        **kwargs,
    ) -> str:
        """
        Execute a memory task.
        """

        prompt = f"""
Task:
{task}

Existing Memory:
{memory}

Context:
{context}

Produce:

1. Relevant Memories
2. New Memories to Store
3. Summary
4. Suggested Memory Updates
"""

        return await self.llm.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
        )