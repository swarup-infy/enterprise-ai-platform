"""
File Utilities.

Common file operations used across the Enterprise AI Platform.
"""

from __future__ import annotations

import hashlib
import mimetypes
import shutil
from pathlib import Path


# ==============================================================================
# Directories
# ==============================================================================


def ensure_directory(path: str | Path) -> Path:
    """
    Create directory if it doesn't exist.
    """

    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)

    return directory


# ==============================================================================
# File Hash
# ==============================================================================


def sha256(path: str | Path) -> str:
    """
    Calculate SHA256 hash.
    """

    file = Path(path)

    digest = hashlib.sha256()

    with file.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            digest.update(chunk)

    return digest.hexdigest()


# ==============================================================================
# File Size
# ==============================================================================


def file_size(path: str | Path) -> int:
    """
    Return file size in bytes.
    """

    return Path(path).stat().st_size


# ==============================================================================
# MIME Type
# ==============================================================================


def mime_type(path: str | Path) -> str:
    """
    Detect MIME type.
    """

    mime, _ = mimetypes.guess_type(str(path))

    return mime or "application/octet-stream"


# ==============================================================================
# Copy
# ==============================================================================


def copy_file(
    source: str | Path,
    destination: str | Path,
) -> Path:
    """
    Copy file.
    """

    destination = Path(destination)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(source, destination)

    return destination


# ==============================================================================
# Move
# ==============================================================================


def move_file(
    source: str | Path,
    destination: str | Path,
) -> Path:
    """
    Move file.
    """

    destination = Path(destination)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.move(str(source), str(destination))

    return destination


# ==============================================================================
# Delete
# ==============================================================================


def delete_file(path: str | Path) -> bool:
    """
    Delete file.
    """

    file = Path(path)

    if file.exists():
        file.unlink()

    return True


# ==============================================================================
# Exists
# ==============================================================================


def file_exists(path: str | Path) -> bool:
    """
    Check whether file exists.
    """

    return Path(path).exists()


# ==============================================================================
# Read
# ==============================================================================


def read_text(
    path: str | Path,
    encoding: str = "utf-8",
) -> str:
    """
    Read text file.
    """

    return Path(path).read_text(
        encoding=encoding,
        errors="ignore",
    )


# ==============================================================================
# Write
# ==============================================================================


def write_text(
    path: str | Path,
    content: str,
    encoding: str = "utf-8",
) -> Path:
    """
    Write text file.
    """

    file = Path(path)

    file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file.write_text(
        content,
        encoding=encoding,
    )

    return file