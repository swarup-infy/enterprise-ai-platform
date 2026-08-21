"""
Coding Agent.

Generates, reviews, refactors and explains code.
"""

from __future__ import annotations

from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService


class CodingAgent(BaseAgent):
    """
    AI Coding Agent.
    """

    SYSTEM_PROMPT = """
You are a Senior FAANG Software Engineer.

Responsibilities:
- Write production-ready code
- Follow best practices
- Use clean architecture
- Optimize performance
- Add proper error handling
- Write maintainable code
- Never output incomplete code

Always return Markdown.
""".strip()

    def __init__(self) -> None:
        super().__init__(
            name="coding",
            description="AI Coding Agent",
        )

        self.llm = LLMService()

    # ==========================================================================
    # Run
    # ==========================================================================

    async def run(
        self,
        task: str,
        language: str = "Python",
        context: str = "",
        **kwargs,
    ) -> str:
        """
        Execute coding task.
        """

        prompt = f"""
Task:
{task}

Programming Language:
{language}

Additional Context:
{context}

Generate:

1. Solution
2. Production-ready Code
3. Explanation
4. Complexity Analysis
5. Possible Improvements
"""

        return await self.llm.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
        )