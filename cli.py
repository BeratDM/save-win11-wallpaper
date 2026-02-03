"""Command-line interface for Save Windows Wallpaper."""

import os
import sys
from config import get_default_folder, set_default_folder
from getwallpaper import save_wallpaper


def cli_help():
    """Print CLI usage information."""
    print(
        """
Save Windows Wallpaper - CLI Commands

Usage: gui.exe [command] [options]

Commands:
  config get              Show current default folder
  config set <path>       Set new default folder
  save [path]             Save wallpaper to path (uses default if not specified)

Examples:
  gui.exe config get
  gui.exe config set "C:\\Users\\YourName\\Pictures"
  gui.exe save "C:\\MyWallpapers"
  gui.exe                 (launches GUI)
"""
    )


def handle_cli():
    """Process CLI arguments. Returns True if CLI was handled, False to launch GUI."""
    if len(sys.argv) < 2:
        return False  # No CLI args, launch GUI

    command = sys.argv[1].lower()

    if command == "config":
        if len(sys.argv) < 3:
            print("Error: config requires subcommand 'get' or 'set'")
            cli_help()
            return True

        subcommand = sys.argv[2].lower()

        if subcommand == "get":
            folder = get_default_folder()
            print(f"Default folder: {folder}")
            return True

        elif subcommand == "set":
            if len(sys.argv) < 4:
                print("Error: config set requires a path")
                cli_help()
                return True

            path = sys.argv[3]
            if not os.path.exists(path):
                print(f"Error: Path does not exist: {path}")
                return True

            if set_default_folder(path):
                print(f"✓ Default folder set to: {path}")
                return True
            else:
                print("✗ Failed to save config")
                return True

    elif command == "save":
        path = sys.argv[2] if len(sys.argv) > 2 else get_default_folder()
        if not os.path.exists(path):
            print(f"Error: Path does not exist: {path}")
            return True

        success, msg, new_file = save_wallpaper(path)
        if success:
            print(f"✓ Wallpaper saved: {new_file}")
        else:
            print(f"✗ {msg}")
        return True

    elif command == "help" or command == "--help" or command == "-h":
        cli_help()
        return True

    else:
        print(f"Unknown command: {command}")
        cli_help()
        return True
