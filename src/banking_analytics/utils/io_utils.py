"""Safe file I/O helpers for CSV, JSON, and artifact persistence."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict
import pandas as pd


def compute_file_checksum(filepath: str) -> str:
    """Computes MD5 checksum of a file.

    Args:
        filepath: Path to the target file.

    Returns:
        str: Hexadecimal MD5 hash digest.
    """
    path = Path(filepath)
    if not path.is_file():
        return ""
    md5 = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            md5.update(chunk)
    return md5.hexdigest()


def read_csv_safe(filepath: str, **kwargs: Any) -> pd.DataFrame:
    """Safely reads a CSV file into a pandas DataFrame.

    Args:
        filepath: Path to CSV file.
        **kwargs: Additional parameters passed to pd.read_csv.

    Returns:
        pd.DataFrame: Loaded DataFrame.
    """
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found at: {filepath}")
    return pd.read_csv(filepath, **kwargs)


def write_csv_safe(df: pd.DataFrame, filepath: str, index: bool = False, **kwargs: Any) -> Path:
    """Safely writes a pandas DataFrame to CSV, ensuring parent directories exist.

    Args:
        df: DataFrame to write.
        filepath: Destination path.
        index: Whether to include index column. Defaults to False.
        **kwargs: Additional parameters passed to df.to_csv.

    Returns:
        Path: Path object of the saved file.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=index, **kwargs)
    return path


def read_json_safe(filepath: str) -> Dict[str, Any]:
    """Safely reads a JSON file into a Python dictionary.

    Args:
        filepath: Path to JSON file.

    Returns:
        Dict[str, Any]: Parsed JSON data.
    """
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"JSON file not found at: {filepath}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json_safe(data: Any, filepath: str, indent: int = 2) -> Path:
    """Safely writes serializable data to a formatted JSON file.

    Args:
        data: Python object to serialize.
        filepath: Destination path.
        indent: Indentation level for pretty-printing.

    Returns:
        Path: Path object of the saved file.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str)
    return path
