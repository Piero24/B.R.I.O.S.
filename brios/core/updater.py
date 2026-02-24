import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Optional, Tuple

from .utils import Colors, HOME_DIR, __app_name__

# GitHub repository coordinates
_GITHUB_OWNER = "Piero24"
_GITHUB_REPO = "B.R.I.O.S."
_RELEASES_URL = f"https://api.github.com/repos/{_GITHUB_OWNER}/{_GITHUB_REPO}/releases/latest"

# Cache settings
_CACHE_FILE = os.path.join(HOME_DIR, ".update_cache.json")
_CACHE_TTL_SECONDS = 86400  # 24 hours

# Network timeout for the GitHub API call
_REQUEST_TIMEOUT_SECONDS = 2


# ---------------------------------------------------------------------------
# Version comparison helpers
# ---------------------------------------------------------------------------


def _parse_version(version_str: str) -> Tuple[int, ...]:
    """Parses a semver string into a tuple of integers for comparison.

    Strips a leading ``v`` if present and ignores any pre-release suffixes
    (e.g. ``-beta.1``).

    Args:
        version_str: A version string such as ``"1.2.3"`` or ``"v1.2.3"``.

    Returns:
        A tuple of integers, e.g. ``(1, 2, 3)``.
    """
    cleaned = version_str.strip().lstrip("v")
    # Drop pre-release / build metadata (e.g. "-beta.1+build")
    cleaned = cleaned.split("-")[0].split("+")[0]
    parts = []
    for segment in cleaned.split("."):
        try:
            parts.append(int(segment))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _is_newer(latest: str, current: str) -> bool:
    """Returns True if *latest* is strictly newer than *current*.

    Args:
        latest: The version string from the remote release.
        current: The local installed version string.

    Returns:
        True if the remote version is newer.
    """
    return _parse_version(latest) > _parse_version(current)


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------


def _read_cache() -> Optional[dict]:
    """Reads the cached update-check result from disk.

    Returns:
        The parsed JSON dict if the cache file exists and is valid;
        otherwise ``None``.
    """
    try:
        if os.path.exists(_CACHE_FILE):
            with open(_CACHE_FILE, "r") as f:
                result: dict = json.load(f)
                return result
    except (json.JSONDecodeError, IOError, OSError):
        pass
    return None


def _write_cache(latest_version: Optional[str]) -> None:
    """Persists the update-check result to disk.

    Args:
        latest_version: The latest version string (or ``None`` if already
            up to date).
    """
    try:
        os.makedirs(os.path.dirname(_CACHE_FILE), exist_ok=True)
        with open(_CACHE_FILE, "w") as f:
            json.dump(
                {
                    "last_check": time.time(),
                    "latest_version": latest_version,
                },
                f,
            )
    except (IOError, OSError):
        pass


# ---------------------------------------------------------------------------
# Core check
# ---------------------------------------------------------------------------


def _fetch_latest_version() -> Optional[str]:
    """Fetches the latest release tag from GitHub.

    Returns:
        The tag name (e.g. ``"v1.2.0"``) or ``None`` on any failure.
    """
    try:
        req = urllib.request.Request(
            _RELEASES_URL,
            headers={"Accept": "application/vnd.github.v3+json"},
        )
        with urllib.request.urlopen(
            req, timeout=_REQUEST_TIMEOUT_SECONDS
        ) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            tag_name: Optional[str] = data.get("tag_name")
            return tag_name
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        json.JSONDecodeError,
        OSError,
        KeyError,
        ValueError,
    ):
        return None


def check_for_update(
    current_version: str,
    *,
    bypass_cache: bool = False,
) -> Optional[str]:
    """Checks whether a newer version of B.R.I.O.S. is available.

    Uses a 24-hour disk cache to avoid hitting the GitHub API on every
    invocation.  Set *bypass_cache* to ``True`` to force a fresh check
    (used by ``--update``).

    Args:
        current_version: The currently installed version string.
        bypass_cache: If ``True``, ignore the cache and query GitHub.

    Returns:
        The newer version string (without ``v`` prefix) if an upgrade is
        available, or ``None`` if already up to date (or on any error).
    """
    # --- Try cache first ---
    if not bypass_cache:
        cache = _read_cache()
        if cache:
            last_check = cache.get("last_check", 0)
            if (time.time() - last_check) < _CACHE_TTL_SECONDS:
                cached_version: Optional[str] = cache.get("latest_version")
                if cached_version and _is_newer(
                    cached_version, current_version
                ):
                    return str(cached_version.lstrip("v"))
                return None

    # --- Fetch from GitHub ---
    tag = _fetch_latest_version()
    if tag is None:
        # Network error — don't overwrite a valid cache entry
        return None

    latest = tag.lstrip("v")
    _write_cache(latest)

    if _is_newer(latest, current_version):
        return latest
    return None


# ---------------------------------------------------------------------------
# Install-method detection
# ---------------------------------------------------------------------------


def _detect_install_method() -> str:
    """Detects how B.R.I.O.S. was installed.

    Returns:
        ``"homebrew"`` if the Homebrew formula is installed, otherwise
        ``"pip"``.
    """
    if shutil.which("brew") is None:
        return "pip"
    try:
        result = subprocess.run(
            ["brew", "list", "brios"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return "homebrew"
    except (subprocess.TimeoutExpired, OSError):
        pass
    return "pip"


# ---------------------------------------------------------------------------
# Perform update
# ---------------------------------------------------------------------------


def perform_update(current_version: str) -> None:
    """Checks for a new version and upgrades in-place.

    The function auto-detects whether B.R.I.O.S. was installed via Homebrew
    or pip and runs the corresponding upgrade command.

    Args:
        current_version: The currently installed version string.
    """
    print(f"\n{Colors.BOLD}Checking for updates…{Colors.RESET}")

    latest = check_for_update(current_version, bypass_cache=True)

    if latest is None:
        print(
            f"{Colors.GREEN}✓{Colors.RESET} {__app_name__} is already "
            f"up to date ({Colors.BOLD}v{current_version}{Colors.RESET})\n"
        )
        return

    print(
        f"{Colors.YELLOW}⚠{Colors.RESET}  Update available: "
        f"{Colors.BOLD}v{current_version}{Colors.RESET} → "
        f"{Colors.GREEN}{Colors.BOLD}v{latest}{Colors.RESET}\n"
    )

    method = _detect_install_method()

    if method == "homebrew":
        _update_via_homebrew()
    else:
        _update_via_pip(latest)


def _update_via_homebrew() -> None:
    """Runs ``brew upgrade brios`` (preceded by ``brew update``).

    Prints live output so the user can follow progress.
    """
    print(f"{Colors.BLUE}▸{Colors.RESET} Detected install method: Homebrew")
    print(f"{Colors.BLUE}▸{Colors.RESET} Updating Homebrew tap…\n")

    try:
        subprocess.run(
            ["brew", "update"],
            check=True,
        )
    except subprocess.CalledProcessError:
        print(
            f"\n{Colors.RED}✗{Colors.RESET} "
            f"'brew update' failed. Please try manually:\n"
            f"  brew update && brew upgrade brios\n"
        )
        return

    print(f"\n{Colors.BLUE}▸{Colors.RESET} Upgrading brios…\n")

    try:
        subprocess.run(
            ["brew", "upgrade", "brios"],
            check=True,
        )
        print(
            f"\n{Colors.GREEN}✓{Colors.RESET} {__app_name__} upgraded "
            f"successfully via Homebrew.\n"
            f"  Run {Colors.BOLD}brios --version{Colors.RESET} to confirm.\n"
        )
    except subprocess.CalledProcessError:
        print(
            f"\n{Colors.RED}✗{Colors.RESET} "
            f"'brew upgrade brios' failed. Please try manually:\n"
            f"  brew upgrade brios\n"
        )


def _update_via_pip(latest_version: str) -> None:
    """Upgrades via pip using the GitHub release tarball.

    Args:
        latest_version: The target version string (without ``v`` prefix).
    """
    print(f"{Colors.BLUE}▸{Colors.RESET} Detected install method: pip")
    print(f"{Colors.BLUE}▸{Colors.RESET} Upgrading to v{latest_version}…\n")

    install_url = (
        f"https://github.com/{_GITHUB_OWNER}/{_GITHUB_REPO}/"
        f"archive/refs/tags/v{latest_version}.tar.gz"
    )

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", install_url],
            check=True,
        )
        print(
            f"\n{Colors.GREEN}✓{Colors.RESET} {__app_name__} upgraded "
            f"to v{latest_version} via pip.\n"
            f"  Run {Colors.BOLD}brios --version{Colors.RESET} to confirm.\n"
        )
    except subprocess.CalledProcessError:
        print(
            f"\n{Colors.RED}✗{Colors.RESET} "
            f"pip upgrade failed. Please try manually:\n"
            f"  pip install --upgrade {install_url}\n"
        )
