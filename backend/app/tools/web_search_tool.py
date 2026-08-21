"""
Web Search Tool.

Provides web search capability for AI agents.
"""

from __future__ import annotations

from typing import Any

from duckduckgo_search import DDGS

from app.tools.base_tool import BaseTool


class WebSearchTool(BaseTool):
    """
    Web search tool using DuckDuckGo.
    """

    def __init__(self) -> None:
        super().__init__(
            name="web_search",
            description="Search the web for up-to-date information.",
        )

    # ==========================================================================
    # Execute
    # ==========================================================================

    async def execute(
        self,
        query: str,
        max_results: int = 5,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Search the web.
        """

        results: list[dict[str, Any]] = []

        with DDGS() as ddgs:
            for item in ddgs.text(
                keywords=query,
                max_results=max_results,
            ):
                results.append(
                    {
                        "title": item.get("title"),
                        "url": item.get("href"),
                        "body": item.get("body"),
                    }
                )

        return results

    # ==========================================================================
    # Health Check
    # ==========================================================================

    async def ping(self) -> bool:
        """
        Verify search service availability.
        """

        try:
            await self.execute(
                query="OpenAI",
                max_results=1,
            )
            return True
        except Exception:
            return False