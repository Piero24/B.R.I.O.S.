import pathlib


def _get_version() -> str:
    """Read version from VERSION file in the root directory.

    Returns:
        str: The version string, or "unknown" if it cannot be determined.
    """
    try:
        # Check for VERSION file relative to this file (in project root)
        version_file = pathlib.Path(__file__).parent.parent / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()

        # Fallback for installed package: use importlib.metadata
        from importlib.metadata import version, PackageNotFoundError

        try:
            return version("brios")
        except PackageNotFoundError:
            return "unknown"
    except Exception:
        return "unknown"


__version__ = _get_version()
