"""
Python Tool.

Safely executes Python code for AI agents inside a
sandboxed subprocess.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Any

from app.tools.base_tool import BaseTool


class PythonTool(BaseTool):
    """
    Execute Python code safely.
    """

    def __init__(self) -> None:
        super().__init__(
            name="python",
            description="Execute Python code in an isolated process.",
        )

    # ==========================================================================
    # Execute
    # ==========================================================================

    async def execute(
        self,
        code: str,
        timeout: int = 30,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute Python code.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            script = Path(temp_dir) / "script.py"
            script.write_text(
                code,
                encoding="utf-8",
            )

            try:
                result = subprocess.run(
                    ["python", str(script)],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False,
                )

                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode,
                }

            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": "Execution timed out.",
                    "return_code": -1,
                }

            except Exception as exc:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": str(exc),
                    "return_code": -1,
                }