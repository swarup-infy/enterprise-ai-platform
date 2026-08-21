"""
LangGraph Nodes.

Individual workflow nodes used by the Enterprise AI Platform.
"""

from __future__ import annotations

from app.agents.coding_agent import CodingAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.research_agent import ResearchAgent
from app.agents.review_agent import ReviewAgent

planner = PlannerAgent()
researcher = ResearchAgent()
coder = CodingAgent()
reviewer = ReviewAgent()
memory = MemoryAgent()


async def planner_node(state: dict) -> dict:
    """Planning node."""
    state["plan"] = await planner.execute(
        task=state["task"],
    )
    return state


async def research_node(state: dict) -> dict:
    """Research node."""
    state["research"] = await researcher.execute(
        task=state["task"],
        context=state["plan"],
    )
    return state


async def coding_node(state: dict) -> dict:
    """Coding node."""
    state["code"] = await coder.execute(
        task=state["task"],
        context=state["research"],
    )
    return state


async def review_node(state: dict) -> dict:
    """Review node."""
    state["review"] = await reviewer.execute(
        task=state["task"],
        code=state["code"],
        context=state["research"],
    )
    return state


async def memory_node(state: dict) -> dict:
    """Memory node."""
    state["memory"] = await memory.execute(
        task=state["task"],
        context=state["review"],
    )

    state["final_answer"] = state["review"]

    return state


__all__ = [
    "planner_node",
    "research_node",
    "coding_node",
    "review_node",
    "memory_node",
]