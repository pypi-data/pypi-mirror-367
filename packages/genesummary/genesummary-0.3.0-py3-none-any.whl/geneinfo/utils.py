"""
# Author: Chunjie Liu
# Contact: chunjie.sam.liu.at.gmail.com
# Date: 2025-08-07
# Description: Utility functions for environment management and API key handling
# Version: 0.1

Utility functions for environment management and API key handling.
"""

import os
from pathlib import Path
from typing import Optional, Union

from dotenv import load_dotenv

# Sentinel value to distinguish between "not provided" and "explicitly None"
_NOT_PROVIDED = object()


def load_environment() -> None:
    """Load environment variables from .env file if it exists."""
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)


def get_api_key(
    key_name: str, cli_value: Union[str, None, object] = _NOT_PROVIDED
) -> Optional[str]:
    """
    Get API key from CLI argument, environment variable, or return None.

    Priority order:
    1. CLI argument (if provided)
    2. Environment variable (if no CLI argument provided)
    3. None

    Args:
        key_name: Name of the environment variable (e.g., "OMIM_API_KEY")
        cli_value: Value provided via CLI argument

    Returns:
        API key string or None if not found
    """
    # Check CLI value first - if explicitly passed, use it (even if None)
    if cli_value is not _NOT_PROVIDED:
        if cli_value and isinstance(cli_value, str) and cli_value.strip():
            return cli_value.strip()
        else:
            return None

    # Load environment variables only if no CLI value was provided
    load_environment()

    # Check environment variable
    env_value = os.getenv(key_name)
    if env_value and env_value.strip():
        return env_value.strip()

    return None


def get_email(
    cli_email: Union[str, None, object] = _NOT_PROVIDED,
) -> Optional[str]:
    """
    Get email from CLI argument or environment variable.

    Args:
        cli_email: Email provided via CLI argument

    Returns:
        Email string or None if not found
    """
    return get_api_key("ENTREZ_EMAIL", cli_email)


def validate_required_keys(*required_keys: str) -> bool:
    """
    Validate that all required API keys are available.

    Args:
        required_keys: List of required environment variable names

    Returns:
        True if all keys are available, False otherwise
    """
    load_environment()

    for key in required_keys:
        if not os.getenv(key):
            return False
    return True
