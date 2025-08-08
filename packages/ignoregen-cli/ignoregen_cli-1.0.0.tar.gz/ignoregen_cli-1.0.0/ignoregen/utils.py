"""Utility functions for IgnoreGen."""

import os
from pathlib import Path
from typing import List, Set


def find_files_with_extensions(directory: Path, extensions: Set[str]) -> List[Path]:
    """Find all files with given extensions in directory."""
    files = []
    try:
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix in extensions:
                files.append(file_path)
    except PermissionError:
        pass
    return files


def has_any_file(directory: Path, filenames: List[str]) -> bool:
    """Check if directory contains any of the specified files."""
    try:
        for filename in filenames:
            if (directory / filename).exists():
                return True
    except PermissionError:
        pass
    return False


def get_project_name(directory: Path) -> str:
    """Get project name from directory."""
    return directory.name