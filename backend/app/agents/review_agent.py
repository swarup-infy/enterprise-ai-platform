"""
Review Agent.

Reviews code, architecture, documentation and AI outputs
for correctness, quality and best practices.
"""

from __future__ import annotations

from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService


class ReviewAgent(BaseAgent):
    """
    AI Review Agent.
    """

    SYSTEM_PROMPT = """
You are a Senior Staff Software Engineer at a FAANG company.

Responsibilities:
- Review code quality
- Detect bugs
- Identify security issues
- Suggest performance improvements
- Check architecture
- Ensure clean code principles
- Produce actionable feedback

Always return Markdown.
""".strip()

    def __init__(self) -> None:
        super().__init__(
            name="review",
            description="AI Review Agent",
        )

        self.llm = LLMService()

    # ==========================================================================
    # Run
    # ==========================================================================

    async def run(
        self,
        task: str,
        code: str = "",
        context: str = "",
        **kwargs,
    ) -> str:
        """
        Review code or content.
        """

        prompt = f"""
Task:
{task}

Context:
{context}

Content to Review:
{code}

Generate:

1. Overall Assessment
2. Strengths
3. Issues Found
4. Security Concerns
5. Performance Improvements
6. Architecture Review
7. Best Practices
8. Final Recommendations
"""

        return await self.llm.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
        )