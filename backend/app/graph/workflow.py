"""
LangGraph Workflow.

Coordinates all AI agents in the Enterprise AI Platform.
"""

from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.coding_agent import CodingAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.research_agent import ResearchAgent
from app.agents.review_agent import ReviewAgent


# ==============================================================================
# Workflow State
# ==============================================================================


class WorkflowState(TypedDict):
    task: str
    plan: str
    research: str
    code: str
    review: str
    memory: str
    final_answer: str


# ==============================================================================
# Agents
# ==============================================================================

planner = PlannerAgent()
researcher = ResearchAgent()
coder = CodingAgent()
reviewer = ReviewAgent()
memory = MemoryAgent()


# ==============================================================================
# Nodes
# ==============================================================================


async def planning_node(state: WorkflowState):
    state["plan"] = await planner.execute(state["task"])
    return state


async def research_node(state: WorkflowState):
    state["research"] = await researcher.execute(
        task=state["task"],
        context=state["plan"],
    )
    return state


async def coding_node(state: WorkflowState):
    state["code"] = await coder.execute(
        task=state["task"],
        context=state["research"],
    )
    return state


async def review_node(state: WorkflowState):
    state["review"] = await reviewer.execute(
        task=state["task"],
        code=state["code"],
        context=state["research"],
    )
    return state


async def memory_node(state: WorkflowState):
    state["memory"] = await memory.execute(
        task=state["task"],
        context=state["review"],
    )

    state["final_answer"] = state["review"]

    return state


# ==============================================================================
# Graph
# ==============================================================================

builder = StateGraph(WorkflowState)

builder.add_node("planner", planning_node)
builder.add_node("research", research_node)
builder.add_node("coding", coding_node)
builder.add_node("review", review_node)
builder.add_node("memory", memory_node)

builder.add_edge(START, "planner")
builder.add_edge("planner", "research")
builder.add_edge("research", "coding")
builder.add_edge("coding", "review")
builder.add_edge("review", "memory")
builder.add_edge("memory", END)

workflow = builder.compile()


# ==============================================================================
# Public API
# ==============================================================================


async def run_workflow(task: str) -> dict:
    """
    Execute the complete multi-agent workflow.
    """

    return await workflow.ainvoke(
        {
            "task": task,
            "plan": "",
            "research": "",
            "code": "",
            "review": "",
            "memory": "",
            "final_answer": "",
        }
    )