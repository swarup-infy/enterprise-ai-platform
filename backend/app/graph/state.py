"""
Workflow State.

Shared state object used by the LangGraph workflow.
"""

from __future__ import annotations

from typing import TypedDict


class WorkflowState(TypedDict):
    """
    State shared across all agents.
    """

    # User Input
    task: str

    # Planner
    plan: str

    # Research
    research: str

    # Coding
    code: str

    # Review
    review: str

    # Memory
    memory: str

    # Final Response
    final_answer: str

    # Metadata
    current_agent: str
    next_agent: str
    iteration: int
    success: bool
    error: str | None

    # Tool Execution
    tool_name: str
    tool_result: str

    # Human Approval
    requires_human_approval: bool
    approved: bool