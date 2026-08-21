"""
Prompt Templates.

Reusable prompt builders for the Enterprise AI Platform.
"""

from __future__ import annotations


def planner_prompt(task: str) -> str:
    return f"""
Task:
{task}

Create a complete execution plan.

Include:
1. Goal
2. Steps
3. Required Agents
4. Required Tools
5. Expected Output
""".strip()


def research_prompt(
    task: str,
    context: str = "",
) -> str:
    return f"""
Task:
{task}

Context:
{context}

Generate:

- Executive Summary
- Key Findings
- References
- Risks
- Next Steps
""".strip()


def coding_prompt(
    task: str,
    language: str = "Python",
    context: str = "",
) -> str:
    return f"""
Task:
{task}

Programming Language:
{language}

Context:
{context}

Produce production-ready code.
""".strip()


def review_prompt(
    code: str,
    context: str = "",
) -> str:
    return f"""
Review the following code.

Context:
{context}

Code:
{code}

Provide:

- Issues
- Security
- Performance
- Improvements
- Final Verdict
""".strip()


def rag_prompt(
    query: str,
    context: str,
) -> str:
    return f"""
Use ONLY the supplied context.

Context:
{context}

Question:
{query}

Answer:
""".strip()


def memory_prompt(
    conversation: str,
) -> str:
    return f"""
Summarize the following conversation.

Extract:

- Facts
- Preferences
- Important Events
- Long-term Memories

Conversation:
{conversation}
""".strip()


def chat_prompt(
    message: str,
) -> str:
    return f"""
User Message:

{message}

Provide the best possible response.
""".strip()