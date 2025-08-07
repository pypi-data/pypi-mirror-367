"""mysharelib utils directory."""
import os
from typing import Tuple
from openbb_core.app.utils import get_user_cache_directory

project_name = "mysharelib"

def get_project_name() -> str:
    """
    Get the project name.

    Returns:
        str: The project name.
    """
    import tomllib

    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)

    project_name = data["project"]["name"]
    return project_name

def get_log_path() -> str:
    """
    Get the path for Tushare log file.

    Returns:
        str: The path to the Tushare log file.
    """
    project_name = get_project_name()
    log_dir = f"{get_user_cache_directory()}/{project_name}"
    log_path = f"{log_dir}/{project_name}.log"

    os.makedirs(log_dir, exist_ok=True)

    return log_path

def get_cache_path() -> str:
    """
    Get the path for Tushare cache database.

    Returns:
        str: The path to the Tushare cache database.
    """
    db_dir = f"{get_user_cache_directory()}/{project_name}"
    db_path = f"{db_dir}/equity.db"

    os.makedirs(db_dir, exist_ok=True)

    return db_path