import configparser
import os
from pathlib import Path

# Resolve project root relative to this file: src/utils/config.py
# src/utils/config.py -> src/utils -> src -> project_root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_config(config_path: str = "config.ini") -> configparser.ConfigParser:
    """
    Load the project configuration from config.ini.

    Args:
        config_path (str): Relative path to config file from project root.
                           Defaults to 'config.ini'.

    Returns:
        configparser.ConfigParser: The loaded configuration object.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    config_file = PROJECT_ROOT / config_path

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found at {config_file}")

    config = configparser.ConfigParser()
    config.read(config_file)
    return config
