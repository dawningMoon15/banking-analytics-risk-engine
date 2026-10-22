"""Configuration loader with environment variable interpolation."""

import os
import re
from pathlib import Path
from typing import Any, Dict
import yaml

from banking_analytics.utils.exceptions import PipelineConfigError


def _interpolate_env_vars(obj: Any) -> Any:
    """Recursively replaces ${VAR_NAME} with the environment variable value."""
    if isinstance(obj, dict):
        return {k: _interpolate_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_interpolate_env_vars(item) for item in obj]
    elif isinstance(obj, str):
        pattern = re.compile(r"\$\{([^}]+)\}")
        matches = pattern.findall(obj)
        for var in matches:
            val = os.environ.get(var, "")
            obj = obj.replace(f"${{{var}}}", val)
        return obj
    return obj


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """Loads and validates the YAML configuration file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Dict[str, Any]: Parsed configuration dictionary with environment variables resolved.

    Raises:
        PipelineConfigError: If config file is missing, cannot be parsed, or missing required keys.
    """
    path = Path(config_path)
    if not path.is_file():
        raise PipelineConfigError(
            f"Configuration file not found at: {config_path}",
            module="config_loader",
            action=f"Ensure {config_path} exists and is readable.",
        )

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise PipelineConfigError(
            f"Failed to parse YAML configuration: {exc}",
            module="config_loader",
            action="Check config/config.yaml for YAML syntax errors.",
        ) from exc

    if not isinstance(raw_config, dict):
        raise PipelineConfigError(
            "Configuration root must be a dictionary.",
            module="config_loader",
            action="Ensure config/config.yaml has top-level key-value mappings.",
        )

    # Validate essential sections
    required_sections = ["project", "data", "ml", "database", "visualization", "logging"]
    missing = [sec for sec in required_sections if sec not in raw_config]
    if missing:
        raise PipelineConfigError(
            f"Missing required configuration sections: {missing}",
            module="config_loader",
            action=f"Add missing sections {missing} to {config_path}.",
        )

    return _interpolate_env_vars(raw_config)
