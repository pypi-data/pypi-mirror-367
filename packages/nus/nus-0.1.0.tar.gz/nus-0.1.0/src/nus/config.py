"""Python module for nus configuration and paths."""

from pathlib import Path

ROOT_FOLDER_NAME = ".nus"
DEFAULT_USER_HOME_CACHE_PATH = Path.home() / ROOT_FOLDER_NAME
"""Path to the user home cache path."""

log_file_path: Path = DEFAULT_USER_HOME_CACHE_PATH / "nus.log"
"""Path to the log file."""
