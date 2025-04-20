"""File handling utilities."""

from pathlib import Path
from typing import Union


def ensure_directory(directory_path: Union[str, Path]) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: The directory path to ensure exists
        
    Returns:
        The Path object for the directory
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path
