import os
import shutil
import hashlib
from datetime import datetime


def file_hash(path, algo: str = "sha256") -> str:
    """Calculate hash of a file."""
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def _remove_if_exists(path: str) -> None:
    """Remove file if it exists."""
    if os.path.exists(path):
        os.remove(path)


def save_wallpaper(wp_folderpath: str):
    """Save the current TranscodedWallpaper to wp_folderpath.

    Returns tuple: (success: bool, message: str, new_file_path: str|None)
    """
    if not os.path.exists(wp_folderpath):
        return False, "destination path does not exist", None

    main_path = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Themes")
    btemp_name = "TranscodedWallpaper-BeratTemp"
    btemp_main_path = os.path.join(main_path, btemp_name)
    btemp_wp_path = os.path.join(wp_folderpath, btemp_name)

    _remove_if_exists(btemp_main_path)

    try:
        shutil.copy(os.path.join(main_path, "TranscodedWallpaper"), btemp_main_path)
    except Exception as e:
        return False, f"failed to copy TranscodedWallpaper: {e}", None

    try:
        src_hash = file_hash(btemp_main_path)
    except Exception as e:
        _remove_if_exists(btemp_main_path)
        return False, f"failed to hash wallpaper: {e}", None

    # Check if same image already exists in destination
    try:
        for file in os.listdir(wp_folderpath):
            if file.startswith("wp-") and file.endswith(".png"):
                existing_path = os.path.join(wp_folderpath, file)
                if file_hash(existing_path) == src_hash:
                    _remove_if_exists(btemp_wp_path)
                    _remove_if_exists(btemp_main_path)
                    return False, f"image already exists as: {file}", None
    except Exception as e:
        _remove_if_exists(btemp_main_path)
        return False, f"error scanning destination: {e}", None

    _remove_if_exists(btemp_wp_path)
    try:
        shutil.move(btemp_main_path, wp_folderpath)
    except Exception as e:
        _remove_if_exists(btemp_main_path)
        return False, f"failed to move temp file: {e}", None

    _remove_if_exists(btemp_main_path)

    now = datetime.now()
    datestr = now.strftime("%y-%m-%d-%f")
    new_file_name = os.path.join(wp_folderpath, f"wp-{datestr}.png")
    try:
        os.rename(os.path.join(wp_folderpath, btemp_name), new_file_name)
    except Exception as e:
        return False, f"failed to rename file: {e}", None

    return True, "process complete", new_file_name
