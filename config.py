"""Configuration management for Save Windows Wallpaper."""

import os
import json

WP_DEFAULT = "X:\\Files\\Wallpapers\\n1\\x\\"
CONFIG_FILE = os.path.join(
    os.path.expanduser("~"), "AppData", "Local", "BRT-SaveWallpaper", "config.json"
)


def _ensure_config_dir():
    """Ensure config directory exists."""
    config_dir = os.path.dirname(CONFIG_FILE)
    os.makedirs(config_dir, exist_ok=True)


def get_default_folder():
    """Load default folder from config, or return WP_DEFAULT if not set."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return config.get("default_folder", WP_DEFAULT)
    except Exception:
        pass
    return WP_DEFAULT


def set_default_folder(folder_path: str):
    """Save default folder to config file."""
    _ensure_config_dir()
    try:
        config = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
        config["default_folder"] = folder_path
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False
