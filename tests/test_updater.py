import json
import os
import time
import pytest
from unittest.mock import MagicMock, patch, mock_open

from brios.core.updater import (
    _parse_version,
    _is_newer,
    _read_cache,
    _write_cache,
    _detect_install_method,
    check_for_update,
    perform_update,
    _CACHE_TTL_SECONDS,
)


# ---------------------------------------------------------------------------
# Version parsing and comparison
# ---------------------------------------------------------------------------


class TestParseVersion:
    """Tests for _parse_version()."""

    def test_simple_version(self) -> None:
        """Verifies parsing of a simple three-part version string."""
        assert _parse_version("1.2.3") == (1, 2, 3)

    def test_strips_v_prefix(self) -> None:
        """Verifies that a leading 'v' is stripped from the version."""
        assert _parse_version("v1.2.3") == (1, 2, 3)

    def test_two_part_version(self) -> None:
        """Verifies parsing of a two-part version string."""
        assert _parse_version("1.0") == (1, 0)

    def test_single_number(self) -> None:
        """Verifies parsing of a single-number version string."""
        assert _parse_version("5") == (5,)

    def test_whitespace_stripped(self) -> None:
        """Verifies that surrounding whitespace is stripped."""
        assert _parse_version("  v2.0.1  ") == (2, 0, 1)

    def test_prerelease_ignored(self) -> None:
        """Verifies that pre-release suffixes are ignored."""
        assert _parse_version("1.2.3-beta.1") == (1, 2, 3)

    def test_build_metadata_ignored(self) -> None:
        """Verifies that build metadata suffixes are ignored."""
        assert _parse_version("1.2.3+build.42") == (1, 2, 3)

    def test_prerelease_and_build(self) -> None:
        """Verifies that both pre-release and build metadata are ignored."""
        assert _parse_version("v2.0.0-rc.1+20260101") == (2, 0, 0)

    def test_non_numeric_segment_becomes_zero(self) -> None:
        """Verifies that non-numeric segments default to zero."""
        assert _parse_version("1.abc.3") == (1, 0, 3)


class TestIsNewer:
    """Tests for _is_newer()."""

    def test_newer_patch(self) -> None:
        """Verifies that a newer patch version is detected."""
        assert _is_newer("1.0.1", "1.0.0") is True

    def test_newer_minor(self) -> None:
        """Verifies that a newer minor version is detected."""
        assert _is_newer("1.1.0", "1.0.9") is True

    def test_newer_major(self) -> None:
        """Verifies that a newer major version is detected."""
        assert _is_newer("2.0.0", "1.9.9") is True

    def test_same_version(self) -> None:
        """Verifies that equal versions return False."""
        assert _is_newer("1.0.0", "1.0.0") is False

    def test_older_version(self) -> None:
        """Verifies that an older version returns False."""
        assert _is_newer("1.0.0", "1.0.1") is False

    def test_with_v_prefix(self) -> None:
        """Verifies comparison works with 'v' prefixed versions."""
        assert _is_newer("v1.1.0", "v1.0.0") is True

    def test_different_length(self) -> None:
        """Verifies comparison across different tuple lengths."""
        # (1, 1) > (1, 0, 0) because tuple comparison is element-by-element
        assert _is_newer("1.1", "1.0.0") is True


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------


class TestCache:
    """Tests for _read_cache() and _write_cache()."""

    @patch("brios.core.updater.os.path.exists", return_value=False)
    def test_read_cache_missing_file(self, _mock_exists: MagicMock) -> None:
        """Verifies that a missing cache file returns None.

        Args:
            _mock_exists: Mocked os.path.exists returning False.
        """
        assert _read_cache() is None

    @patch(
        "builtins.open",
        mock_open(read_data='{"last_check": 100, "latest_version": "1.0.0"}'),
    )
    @patch("brios.core.updater.os.path.exists", return_value=True)
    def test_read_cache_valid(self, _mock_exists: MagicMock) -> None:
        """Verifies that a valid cache file is read and parsed correctly.

        Args:
            _mock_exists: Mocked os.path.exists returning True.
        """
        result = _read_cache()
        assert result is not None
        assert result["latest_version"] == "1.0.0"
        assert result["last_check"] == 100

    @patch("builtins.open", mock_open(read_data="NOT JSON"))
    @patch("brios.core.updater.os.path.exists", return_value=True)
    def test_read_cache_corrupt(self, _mock_exists: MagicMock) -> None:
        """Verifies that a corrupt cache file returns None.

        Args:
            _mock_exists: Mocked os.path.exists returning True.
        """
        assert _read_cache() is None

    @patch("brios.core.updater.os.makedirs")
    @patch("builtins.open", mock_open())
    def test_write_cache(self, _mock_makedirs: MagicMock) -> None:
        """_write_cache should not raise on success."""
        _write_cache("1.2.0")  # Should not raise

    @patch("brios.core.updater.os.makedirs", side_effect=OSError("no perms"))
    def test_write_cache_error_suppressed(
        self, _mock_makedirs: MagicMock
    ) -> None:
        """_write_cache should silently handle OS errors."""
        _write_cache("1.0.0")  # Should not raise


# ---------------------------------------------------------------------------
# Install method detection
# ---------------------------------------------------------------------------


class TestDetectInstallMethod:
    """Tests for _detect_install_method()."""

    @patch("shutil.which", return_value=None)
    def test_no_brew(self, _mock_which: MagicMock) -> None:
        """Verifies pip is returned when brew is not installed.

        Args:
            _mock_which: Mocked shutil.which returning None.
        """
        assert _detect_install_method() == "pip"

    @patch("subprocess.run")
    @patch("shutil.which", return_value="/opt/homebrew/bin/brew")
    def test_brew_has_brios(
        self, _mock_which: MagicMock, mock_run: MagicMock
    ) -> None:
        """Verifies homebrew is returned when brios formula exists.

        Args:
            _mock_which: Mocked shutil.which returning brew path.
            mock_run: Mocked subprocess.run with returncode 0.
        """
        mock_run.return_value.returncode = 0
        assert _detect_install_method() == "homebrew"

    @patch("subprocess.run")
    @patch("shutil.which", return_value="/opt/homebrew/bin/brew")
    def test_brew_no_brios(
        self, _mock_which: MagicMock, mock_run: MagicMock
    ) -> None:
        """Verifies pip is returned when brios formula is not installed.

        Args:
            _mock_which: Mocked shutil.which returning brew path.
            mock_run: Mocked subprocess.run with returncode 1.
        """
        mock_run.return_value.returncode = 1
        assert _detect_install_method() == "pip"

    @patch("subprocess.run", side_effect=OSError("no brew"))
    @patch("shutil.which", return_value="/opt/homebrew/bin/brew")
    def test_brew_oserror(
        self, _mock_which: MagicMock, _mock_run: MagicMock
    ) -> None:
        """Verifies pip is returned when brew command raises OSError.

        Args:
            _mock_which: Mocked shutil.which returning brew path.
            _mock_run: Mocked subprocess.run raising OSError.
        """
        assert _detect_install_method() == "pip"


# ---------------------------------------------------------------------------
# check_for_update
# ---------------------------------------------------------------------------


class TestCheckForUpdate:
    """Tests for check_for_update()."""

    @patch("brios.core.updater._fetch_latest_version", return_value="v2.0.0")
    @patch("brios.core.updater._write_cache")
    def test_update_available(
        self, _mock_write: MagicMock, _mock_fetch: MagicMock
    ) -> None:
        """Verifies that a newer remote version is returned.

        Args:
            _mock_write: Mocked _write_cache.
            _mock_fetch: Mocked _fetch_latest_version returning v2.0.0.
        """
        result = check_for_update("1.0.0", bypass_cache=True)
        assert result == "2.0.0"

    @patch("brios.core.updater._fetch_latest_version", return_value="v1.0.0")
    @patch("brios.core.updater._write_cache")
    def test_already_up_to_date(
        self, _mock_write: MagicMock, _mock_fetch: MagicMock
    ) -> None:
        """Verifies None is returned when already on the latest version.

        Args:
            _mock_write: Mocked _write_cache.
            _mock_fetch: Mocked _fetch_latest_version returning v1.0.0.
        """
        result = check_for_update("1.0.0", bypass_cache=True)
        assert result is None

    @patch("brios.core.updater._fetch_latest_version", return_value=None)
    def test_network_error(self, _mock_fetch: MagicMock) -> None:
        """Verifies None is returned on a network error.

        Args:
            _mock_fetch: Mocked _fetch_latest_version returning None.
        """
        result = check_for_update("1.0.0", bypass_cache=True)
        assert result is None

    @patch("brios.core.updater._read_cache")
    def test_cache_hit_newer(self, mock_read: MagicMock) -> None:
        """Verifies a fresh cache with a newer version is returned.

        Args:
            mock_read: Mocked _read_cache with fresh newer version.
        """
        mock_read.return_value = {
            "last_check": time.time(),  # Fresh cache
            "latest_version": "2.0.0",
        }
        result = check_for_update("1.0.0", bypass_cache=False)
        assert result == "2.0.0"

    @patch("brios.core.updater._read_cache")
    def test_cache_hit_same(self, mock_read: MagicMock) -> None:
        """Verifies None is returned when cached version matches current.

        Args:
            mock_read: Mocked _read_cache with same version.
        """
        mock_read.return_value = {
            "last_check": time.time(),
            "latest_version": "1.0.0",
        }
        result = check_for_update("1.0.0", bypass_cache=False)
        assert result is None

    @patch("brios.core.updater._fetch_latest_version", return_value="v3.0.0")
    @patch("brios.core.updater._write_cache")
    @patch("brios.core.updater._read_cache")
    def test_cache_expired(
        self,
        mock_read: MagicMock,
        _mock_write: MagicMock,
        _mock_fetch: MagicMock,
    ) -> None:
        """Verifies that an expired cache triggers a fresh fetch.

        Args:
            mock_read: Mocked _read_cache with expired timestamp.
            _mock_write: Mocked _write_cache.
            _mock_fetch: Mocked _fetch_latest_version returning v3.0.0.
        """
        mock_read.return_value = {
            "last_check": time.time() - _CACHE_TTL_SECONDS - 1,
            "latest_version": "1.0.0",
        }
        result = check_for_update("1.0.0", bypass_cache=False)
        assert result == "3.0.0"

    @patch("brios.core.updater._fetch_latest_version", return_value="v2.0.0")
    @patch("brios.core.updater._write_cache")
    @patch("brios.core.updater._read_cache")
    def test_bypass_cache_skips_cache(
        self,
        mock_read: MagicMock,
        _mock_write: MagicMock,
        _mock_fetch: MagicMock,
    ) -> None:
        """Verifies that bypass_cache skips the disk cache entirely.

        Args:
            mock_read: Mocked _read_cache (should not be called).
            _mock_write: Mocked _write_cache.
            _mock_fetch: Mocked _fetch_latest_version returning v2.0.0.
        """
        # Even if _read_cache returns data, bypass_cache=True skips it
        mock_read.return_value = {
            "last_check": time.time(),
            "latest_version": "1.0.0",
        }
        result = check_for_update("1.0.0", bypass_cache=True)
        assert result == "2.0.0"
        mock_read.assert_not_called()


# ---------------------------------------------------------------------------
# perform_update
# ---------------------------------------------------------------------------


class TestPerformUpdate:
    """Tests for perform_update()."""

    @patch("brios.core.updater.check_for_update", return_value=None)
    def test_already_up_to_date(
        self, _mock_check: MagicMock, capsys: pytest.CaptureFixture
    ) -> None:
        """Verifies that no upgrade is triggered when already current.

        Args:
            _mock_check: Mocked check_for_update returning None.
            capsys: Pytest capture fixture for stdout.
        """
        perform_update("1.0.0")
        captured = capsys.readouterr()
        assert "up to date" in captured.out

    @patch("brios.core.updater._update_via_homebrew")
    @patch("brios.core.updater._detect_install_method", return_value="homebrew")
    @patch("brios.core.updater.check_for_update", return_value="2.0.0")
    def test_update_homebrew(
        self,
        _mock_check: MagicMock,
        _mock_detect: MagicMock,
        mock_brew: MagicMock,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Verifies that the Homebrew upgrade path is invoked.

        Args:
            _mock_check: Mocked check_for_update returning 2.0.0.
            _mock_detect: Mocked _detect_install_method returning homebrew.
            mock_brew: Mocked _update_via_homebrew.
            capsys: Pytest capture fixture for stdout.
        """
        perform_update("1.0.0")
        mock_brew.assert_called_once()

    @patch("brios.core.updater._update_via_pip")
    @patch("brios.core.updater._detect_install_method", return_value="pip")
    @patch("brios.core.updater.check_for_update", return_value="2.0.0")
    def test_update_pip(
        self,
        _mock_check: MagicMock,
        _mock_detect: MagicMock,
        mock_pip: MagicMock,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Verifies that the pip upgrade path is invoked.

        Args:
            _mock_check: Mocked check_for_update returning 2.0.0.
            _mock_detect: Mocked _detect_install_method returning pip.
            mock_pip: Mocked _update_via_pip.
            capsys: Pytest capture fixture for stdout.
        """
        perform_update("1.0.0")
        mock_pip.assert_called_once_with("2.0.0")
