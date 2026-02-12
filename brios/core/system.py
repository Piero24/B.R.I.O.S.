import sys
import subprocess
from typing import Tuple

# Platform-specific imports
IS_MACOS = sys.platform == "darwin"
try:
    import Quartz

    HAS_QUARTZ = True
except ImportError:
    HAS_QUARTZ = False


def is_screen_locked() -> bool:
    """Checks if the macOS screen is currently locked using Quartz.

    Returns:
        True if the screen is locked, False otherwise or if Quartz is unavailable.
    """
    if not HAS_QUARTZ:
        return False
    try:
        # Use Quartz (PyObjC) to check if screen is locked
        session_dict = Quartz.CGSessionCopyCurrentDictionary()
        if session_dict is None:
            return False
        return bool(session_dict.get("CGSSessionScreenIsLocked", False))
    except Exception:
        return False


def lock_macbook() -> Tuple[bool, str]:
    """Executes system commands to immediately lock the macOS screen.

    Returns:
        A tuple of (success, status_message).
    """
    if not IS_MACOS:
        return False, "Not macOS system"

    try:
        # First, ensure password is required immediately after sleep
        subprocess.run(
            [
                "defaults",
                "write",
                "com.apple.screensaver",
                "askForPassword",
                "-int",
                "1",
            ],
            check=True,
            capture_output=True,
        )

        subprocess.run(
            [
                "defaults",
                "write",
                "com.apple.screensaver",
                "askForPasswordDelay",
                "-int",
                "0",
            ],
            check=True,
            capture_output=True,
        )

        # Now lock the screen by putting display to sleep
        subprocess.run(
            ["pmset", "displaysleepnow"], check=True, capture_output=True
        )
        return True, "🔒 MacBook locked (password required)"

    except Exception as e:
        return False, f"⚠️  Failed to lock MacBook: {e}"
