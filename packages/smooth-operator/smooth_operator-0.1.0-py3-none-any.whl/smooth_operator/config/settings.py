import os
import yaml
import shutil
from typing import Any, Dict, Optional
from pathlib import Path
from ..utils.logging import get_logger

logger = get_logger("config")

# Default configuration
DEFAULT_CONFIG = {
    "terminus": {
        "binary": "terminus",
        "terminus_path": None,  # Path to external Terminus executable
        "use_lando": True,  # Whether to use Lando for Terminus commands
    },
    "lando": {
        "sites_path": "~/pantheon",
    },
    "gitlab": {
        "api_url": "https://gitlab.example.com/api/v4",
        "token": "",
    },
    "logging": {
        "level": "INFO",
        "file": None,
    },
    "parallel": {
        "default": False,
        "max_workers": 5,
    }
}


def get_config_path() -> Path:
    """
    Get the path to the configuration file.

    Returns:
        Path to the configuration file
    """
    # Check for config in environment variable
    if "SMOOTH_OPERATOR_CONFIG" in os.environ:
        return Path(os.environ["SMOOTH_OPERATOR_CONFIG"])

    # Check in user's home directory
    home_config_dir = Path.home() / ".smooth_operator"
    if not home_config_dir.exists():
        home_config_dir.mkdir(exist_ok=True)

    home_config = home_config_dir / "config.yml"
    if home_config.exists():
        return home_config

    # Check for legacy config in home directory
    legacy_home_config = Path.home() / ".smooth_operator.yml"
    if legacy_home_config.exists():
        # Migrate to new location
        shutil.copy(legacy_home_config, home_config)
        return home_config

    # Check in current directory
    local_config = Path(".smooth_operator.yml")
    if local_config.exists():
        return local_config

    # No config found, return default location
    return home_config


def load_config() -> Dict[str, Any]:
    """
    Load configuration from file.

    Returns:
        Configuration dictionary
    """
    config_path = get_config_path()
    config = DEFAULT_CONFIG.copy()

    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                user_config = yaml.safe_load(f)

            if user_config and isinstance(user_config, dict):
                # Merge user config with defaults
                for section, values in user_config.items():
                    if section in config and isinstance(values, dict):
                        config[section].update(values)
                    else:
                        config[section] = values

            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {str(e)}")
    else:
        logger.info(f"No configuration file found at {config_path}, using defaults")

    return config


def save_config(config: Dict[str, Any]) -> bool:
    """
    Save configuration to file.

    Args:
        config: Configuration dictionary

    Returns:
        True if successful, False otherwise
    """
    config_path = get_config_path()

    try:
        # Create parent directories if they don't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

        logger.info(f"Saved configuration to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving config to {config_path}: {str(e)}")
        return False


def get_setting(section: str, key: str, default: Any = None) -> Any:
    """
    Get a specific setting from the configuration.

    Args:
        section: Configuration section
        key: Setting key
        default: Default value if not found

    Returns:
        Setting value
    """
    config = load_config()

    try:
        return config.get(section, {}).get(key, default)
    except (KeyError, AttributeError):
        return default