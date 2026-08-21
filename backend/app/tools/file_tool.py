"""
File Tool.

Provides secure file system operations for AI agents.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any


from app.tools.base_tool import BaseTool


class FileTool(BaseTool):
    """
    File system utility tool.
    """

    def __init__(self) -> None:
        super().__init__(
            name="file_tool",
            description="Read, write, copy, move and delete files.",
        )

    # ==========================================================================
    # Execute
    # ==========================================================================

    async def execute(
        self,
        action: str,
        **kwargs: Any,
    ) -> Any:

        actions = {
            "read": self.read,
            "write": self.write,
            "delete": self.delete,
            "copy": self.copy,
            "move": self.move,
            "exists": self.exists,
            "list": self.list_directory,
        }

        if action not in actions:
            raise ValueError(f"Unsupported action: {action}")

        return actions[action](**kwargs)

    # ==========================================================================
    # Read
    # ==========================================================================

    @staticmethod
    def read(path: str) -> str:
        return Path(path).read_text(
            encoding="utf-8",
        )

    # ==========================================================================
    # Write
    # ==========================================================================

    @staticmethod
    def write(
        path: str,
        content: str,
    ) -> str:

        file = Path(path)

        file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file.write_text(
            content,
            encoding="utf-8",
        )

        return str(file)

    # ==========================================================================
    # Delete
    # ==========================================================================

    @staticmethod
    def delete(path: str) -> bool:

        file = Path(path)

        if file.exists():
            file.unlink()

        return True

    # ==========================================================================
    # Copy
    # ==========================================================================

    @staticmethod
    def copy(
        source: str,
        destination: str,
    ) -> str:

        shutil.copy2(
            source,
            destination,
        )

        return destination

    # ==========================================================================
    # Move
    # ==========================================================================

    @staticmethod
    def move(
        source: str,
        destination: str,
    ) -> str:

        shutil.move(
            source,
            destination,
        )

        return destination

    # ==========================================================================
    # Exists
    # ==========================================================================

    @staticmethod
    def exists(path: str) -> bool:
        return Path(path).exists()

    # ==========================================================================
    # List Directory
    # ==========================================================================

    @staticmethod
    def list_directory(
        path: str,
    ) -> list[str]:

        return sorted(
            str(item)
            for item in Path(path).iterdir()
        )