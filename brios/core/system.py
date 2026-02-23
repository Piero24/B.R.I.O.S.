import sys
import subprocess
import ctypes
import ctypes.util
from typing import Tuple

# Platform-specific imports
IS_MACOS = sys.platform == "darwin"


def is_screen_locked() -> bool:
    """Checks if the macOS screen is currently locked using CoreGraphics via ctypes.

    Returns:
        True if the screen is locked, False otherwise or if unavailable.
    """
    if not IS_MACOS:
        return False

    try:
        core_graphics = ctypes.util.find_library("CoreGraphics")
        if not core_graphics:
            return False
        cg = ctypes.cdll.LoadLibrary(core_graphics)
        cg.CGSessionCopyCurrentDictionary.restype = ctypes.c_void_p
        cg.CGSessionCopyCurrentDictionary.argtypes = []
        dict_ptr = cg.CGSessionCopyCurrentDictionary()
        if not dict_ptr:
            return False

        core_foundation = ctypes.util.find_library("CoreFoundation")
        if not core_foundation:
            return False
        cf = ctypes.cdll.LoadLibrary(core_foundation)
        cf.CFDictionaryGetValue.restype = ctypes.c_void_p
        cf.CFDictionaryGetValue.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        cf.CFStringCreateWithCString.restype = ctypes.c_void_p
        cf.CFStringCreateWithCString.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_uint32,
        ]

        # kCFStringEncodingUTF8 is 0x08000100
        key = cf.CFStringCreateWithCString(
            None, b"CGSSessionScreenIsLocked", 0x08000100
        )
        val_ptr = cf.CFDictionaryGetValue(dict_ptr, key)

        cf.CFRelease.argtypes = [ctypes.c_void_p]
        cf.CFRelease.restype = None

        if not val_ptr:
            cf.CFRelease(key)
            cf.CFRelease(dict_ptr)
            return False

        cf.CFBooleanGetValue.restype = ctypes.c_bool
        cf.CFBooleanGetValue.argtypes = [ctypes.c_void_p]
        is_locked = bool(cf.CFBooleanGetValue(val_ptr))

        cf.CFRelease(key)
        cf.CFRelease(dict_ptr)

        return is_locked
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
