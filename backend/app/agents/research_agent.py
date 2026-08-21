"""
Research Agent.

Performs web/document research and produces
well-structured summaries for downstream agents.
"""

from __future__ import annotations

from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService


class ResearchAgent(BaseAgent):
    """
    Research specialist.
    """

    SYSTEM_PROMPT = """
You are an expert AI Research Agent.

Responsibilities:
- Gather relevant information.
- Summarize findings.
- Highlight important facts.
- Cite available sources.
- Mention uncertainty if information is insufficient.

Return Markdown only.
""".strip()

    def __init__(self) -> None:
        super().__init__(
            name="research",
            description="Research Agent",
        )

        self.llm = LLMService()

    # ==========================================================================
    # Run
    # ==========================================================================

    async def run(
        self,
        task: str,
        context: str = "",
        **kwargs,
    ) -> str:
        """
        Execute research.
        """

        prompt = f"""
Task:
{task}

Available Context:
{context}

Generate:

1. Executive Summary
2. Key Findings
3. Important Facts
4. Risks / Limitations
5. Suggested Next Steps
"""

        return await self.llm.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
        )