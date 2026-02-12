import sys
import pytest
from unittest.mock import MagicMock, patch
from collections import deque
import importlib


# --- Utils Tests ---
def test_estimate_distance():
    from brios.core.utils import estimate_distance

    """Test the Log-Distance Path Loss calculation."""
    # Test with default constants (TX=-59, N=2.8)
    # If RSSI == TX_POWER, distance should be 1.0m
    assert estimate_distance(-59) == pytest.approx(1.0)

    # If RSSI is weaker (-80), distance should be > 1.0m
    assert estimate_distance(-80) > 1.0

    # If RSSI is stronger (-40), distance should be < 1.0m
    assert estimate_distance(-40) < 1.0

    # Test 0 RSSI handling
    assert estimate_distance(0) == -1.0

    # Test custom parameters
    # TX=-50, N=2.0, RSSI=-70 -> delta=20. 20/(10*2) = 1. 10^1 = 10m
    assert estimate_distance(
        -70, tx_power_at_1m=-50, path_loss_exponent=2.0
    ) == pytest.approx(10.0)


def test_smooth_rssi():
    from brios.core.utils import smooth_rssi

    """Test RSSI averaging."""
    buffer = deque([-60, -60, -60])
    assert smooth_rssi(buffer) == -60.0

    buffer = deque([-50, -60, -70])
    assert smooth_rssi(buffer) == -60.0

    assert smooth_rssi(deque()) is None


def test_determine_target_address():
    from brios.core.utils import determine_target_address

    """Test logic for picking MAC vs UUID."""
    args = MagicMock()

    # Case 1: Target MAC provided
    args.target_mac = "11:22:33:44:55:66"
    args.target_uuid = None
    assert determine_target_address(args) == "11:22:33:44:55:66"

    # Case 2: Target UUID provided
    args.target_mac = None
    args.target_uuid = "UUID-1234"
    assert determine_target_address(args) == "UUID-1234"

    # Case 3: USE_DEFAULT
    args.target_mac = "USE_DEFAULT"
    with patch("brios.core.utils.TARGET_DEVICE_MAC_ADDRESS", "DEFAULT_MAC"):
        assert determine_target_address(args) == "DEFAULT_MAC"

    args.target_mac = None
    args.target_uuid = "USE_DEFAULT"
    with patch("brios.core.utils.TARGET_DEVICE_UUID_ADDRESS", "DEFAULT_UUID"):
        assert determine_target_address(args) == "DEFAULT_UUID"


# --- System Tests ---
def test_is_screen_locked_true():
    """Test screen lock detection when locked."""
    # Mock Quartz before import
    mock_quartz = MagicMock()
    sys.modules["Quartz"] = mock_quartz

    # Reload system module to pick up the mock
    import brios.core.system

    importlib.reload(brios.core.system)

    mock_quartz.CGSessionCopyCurrentDictionary.return_value = {
        "CGSSessionScreenIsLocked": 1
    }

    # Re-import function from reloaded module
    from brios.core.system import is_screen_locked

    assert is_screen_locked() is True


def test_is_screen_locked_false():
    """Test screen lock detection when unlocked."""
    mock_quartz = MagicMock()
    sys.modules["Quartz"] = mock_quartz

    import brios.core.system

    importlib.reload(brios.core.system)

    mock_quartz.CGSessionCopyCurrentDictionary.return_value = {
        "CGSSessionScreenIsLocked": 0
    }

    from brios.core.system import is_screen_locked

    assert is_screen_locked() is False


def test_is_screen_locked_no_quartz():
    """Test screen lock detection on non-macOS."""
    import brios.core.system

    # Patch the constant
    with patch("brios.core.system.HAS_QUARTZ", False):
        from brios.core.system import is_screen_locked

        assert is_screen_locked() is False


@patch("subprocess.run")
def test_lock_macbook_success(mock_run):
    """Test locking command execution on macOS."""
    # Force generic reload to ensure consistent state
    import brios.core.system
    # Manually set IS_MACOS for test
    with patch("brios.core.system.IS_MACOS", True):
        mock_run.return_value.returncode = 0
        from brios.core.system import lock_macbook

        success, msg = lock_macbook()
        assert success is True
        assert "locked" in msg
        assert mock_run.call_count >= 1


def test_lock_macbook_non_macos():
    """Test locking on non-macOS."""
    import brios.core.system

    with patch("brios.core.system.IS_MACOS", False):
        from brios.core.system import lock_macbook

        success, msg = lock_macbook()
        assert success is False
        assert "Not macOS" in msg
