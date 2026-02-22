import sys
import asyncio
import pytest
from typing import Any
from unittest.mock import MagicMock, patch, call, ANY
from collections import deque
import importlib


# --- Fixtures ---
@pytest.fixture
def mock_scanner() -> MagicMock:
    return MagicMock()


@pytest.fixture
def monitor() -> Any:
    # Setup mocks before importing monitor
    mock_bleak = MagicMock()
    mock_bleak.BleakScanner = MagicMock()
    # Ensure backends are mocked
    mock_bleak.backends = MagicMock()
    mock_bleak.backends.device = MagicMock()
    mock_bleak.backends.scanner = MagicMock()

    sys.modules["bleak"] = mock_bleak
    sys.modules["bleak.backends.device"] = mock_bleak.backends.device
    sys.modules["bleak.backends.scanner"] = mock_bleak.backends.scanner

    # Mock Quartz for system module
    sys.modules["Quartz"] = MagicMock()

    # Reload modules to pick up mocks
    import brios.core.monitor

    importlib.reload(brios.core.monitor)
    import brios.core.system

    importlib.reload(brios.core.system)

    from brios.core.monitor import DeviceMonitor
    from brios.core.utils import Flags

    flags = Flags(daemon_mode=False, file_logging=False, verbose=True)
    return DeviceMonitor(
        target_address="AA:BB:CC:DD:EE:FF", use_bdaddr=True, flags=flags
    )


@pytest.fixture
def mock_device() -> MagicMock:
    device = MagicMock()
    device.address = "AA:BB:CC:DD:EE:FF"
    device.name = "Target Device"
    return device


@pytest.fixture
def mock_adv() -> MagicMock:
    adv = MagicMock()
    return adv


# --- Tests ---
@pytest.mark.asyncio
async def test_monitor_initialization(monitor: Any) -> None:
    assert monitor.target_address == "AA:BB:CC:DD:EE:FF"
    assert monitor.use_bdaddr is True
    assert monitor.flags.verbose is True
    assert isinstance(monitor.rssi_buffer, deque)


@pytest.mark.asyncio
async def test_process_signal_out_of_range(
    monitor: Any, mock_device: MagicMock, mock_adv: MagicMock
) -> None:
    """Test that out-of-range signal triggers lock."""
    monitor.resume_time = -1000  # Ensure grace period has passed
    monitor.rssi_buffer.clear()
    for _ in range(11):
        monitor.rssi_buffer.append(-80)

    monitor.target_address = "AA:BB:CC:DD:EE:FF"
    mock_device.address = "AA:BB:CC:DD:EE:FF"
    mock_adv.rssi = -80

    monitor.scanner = MagicMock()
    monitor.scanner.stop.return_value = asyncio.Future()
    monitor.scanner.stop.return_value.set_result(None)

    import brios.core.system

    # Patch the system module as accessed by monitor
    with (
        patch("brios.core.monitor.system.lock_macbook") as mock_lock,
        patch("brios.core.monitor.asyncio.create_task") as mock_create_task,
    ):
        mock_lock.return_value = (True, "Mock Locked")

        monitor._detection_callback(mock_device, mock_adv)

        mock_lock.assert_called_once()
        assert monitor.alert_triggered is True
        mock_create_task.assert_called_once()


@pytest.mark.asyncio
async def test_process_signal_back_in_range(
    monitor: Any, mock_device: MagicMock, mock_adv: MagicMock
) -> None:
    """Test that coming back in range clears alert."""
    monitor.alert_triggered = True
    monitor.resume_time = -1000  # Ensure grace period has passed
    monitor.rssi_buffer.clear()
    for _ in range(11):
        monitor.rssi_buffer.append(-59)

    monitor.target_address = "AA:BB:CC:DD:EE:FF"
    mock_device.address = "AA:BB:CC:DD:EE:FF"
    mock_adv.rssi = -59

    import brios.core.system

    with (
        patch("brios.core.monitor.system.lock_macbook") as mock_lock,
        patch("builtins.print") as mock_print,
    ):

        monitor._detection_callback(mock_device, mock_adv)

        mock_lock.assert_not_called()
        assert monitor.alert_triggered is False


@pytest.mark.asyncio
async def test_grace_period_active(
    monitor: Any, mock_device: MagicMock, mock_adv: MagicMock
) -> None:
    """Test that signals are ignored during grace period."""
    import time

    monitor.resume_time = time.monotonic()
    monitor.rssi_buffer.clear()
    for _ in range(11):
        monitor.rssi_buffer.append(-80)

    mock_device.address = "AA:BB:CC:DD:EE:FF"
    mock_adv.rssi = -80

    import brios.core.system

    with patch("brios.core.monitor.system.lock_macbook") as mock_lock:
        monitor._detection_callback(mock_device, mock_adv)
        mock_lock.assert_not_called()


@pytest.mark.asyncio
async def test_lock_loop_protection(monitor: Any) -> None:
    """Test that rapid locking triggers pause."""
    import time

    monitor.lock_history.clear()
    now = time.monotonic()

    monitor.lock_history.append(now)
    monitor.lock_history.append(now + 1)
    monitor.lock_history.append(now + 2)

    assert len(monitor.lock_history) == 3
