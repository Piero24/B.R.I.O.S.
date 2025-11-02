# test_ble_monitor.py

import sys
import pytest
import asyncio
import importlib
from unittest.mock import MagicMock, patch, call, ANY

# Mock bleak before it is imported by the main script
# This is crucial for tests to run without a real Bluetooth adapter
mock_bleak = MagicMock()
sys.modules["bleak"] = mock_bleak
sys.modules["bleak.backends"] = MagicMock()
sys.modules["bleak.backends.device"] = MagicMock()
sys.modules["bleak.backends.scanner"] = MagicMock()

# Now, import the script to be tested.
import main


# --- Mock Data Classes ---
class MockBLEDevice:

    def __init__(self, address, name):
        self.address = address
        self.name = name


class MockAdvertisementData:

    def __init__(self, rssi):
        self.rssi = rssi


# --- Fixtures ---
@pytest.fixture
def mock_args(mocker):
    """Fixture to create a mock of argparse.Namespace."""
    args = mocker.MagicMock()
    args.start = False
    args.stop = False
    args.restart = False
    args.status = False
    args.scanner = None
    args.target_mac = None
    args.target_uuid = None
    args.macos_use_bdaddr = False
    args.verbose = False
    args.file_logging = False
    args.daemon = False
    return args


@pytest.fixture(scope="function")
def reloaded_main_new(monkeypatch):
    """
    Fixture to set mock environment variables and then RELOAD the main_new
    module. This ensures that module-level constants are updated with
    the patched environment variables before tests run.
    """
    monkeypatch.setenv("TARGET_DEVICE_MAC_ADDRESS", "AA:BB:CC:DD:EE:FF")
    monkeypatch.setenv(
        "TARGET_DEVICE_UUID_ADDRESS", "12345678-1234-5678-1234-567812345678"
    )
    monkeypatch.setenv("TARGET_DEVICE_NAME", "Test Beacon")
    monkeypatch.setenv("TX_POWER_AT_1M", "-59")
    monkeypatch.setenv("PATH_LOSS_EXPONENT", "2.8")
    monkeypatch.setenv("SAMPLE_WINDOW", "3")  # Use a smaller window for testing
    monkeypatch.setenv("DISTANCE_THRESHOLD_M", "2.0")

    # Reload the module to apply the new env vars
    importlib.reload(main)
    return main


# --- Unit Tests ---


def test_estimate_distance(reloaded_main_new):
    """Test the distance estimation logic."""
    assert reloaded_main_new._estimate_distance(-59) == pytest.approx(1.0)
    assert reloaded_main_new._estimate_distance(-40) < 1.0
    assert reloaded_main_new._estimate_distance(-80) > 1.0
    assert reloaded_main_new._estimate_distance(0) == -1.0


def test_smooth_rssi(reloaded_main_new):
    """Test the RSSI smoothing logic."""
    from collections import deque

    buffer = deque([-60, -62, -58], maxlen=3)
    assert reloaded_main_new._smooth_rssi(buffer) == pytest.approx(-60.0)
    assert reloaded_main_new._smooth_rssi(deque()) is None


@pytest.mark.asyncio
async def test_device_scanner_run(mocker, capsys, reloaded_main_new):
    """Test the DeviceScanner functionality and output."""
    # Arrange
    mock_devices = {
        "AA:BB:CC:11:22:33": (
            MockBLEDevice("AA:BB:CC:11:22:33", "Device A"),
            MockAdvertisementData(-50),
        ),
        "DD:EE:FF:44:55:66": (
            MockBLEDevice("DD:EE:FF:44:55:66", "Device B"),
            MockAdvertisementData(-75),
        ),
    }

    # Mock the async function to be awaitable - create an async mock
    async def mock_discover(*args, **kwargs):
        return mock_devices

    mocker.patch("bleak.BleakScanner.discover", side_effect=mock_discover)

    scanner = reloaded_main_new.DeviceScanner(
        duration=5, use_bdaddr=True, verbose=True
    )

    # Act
    await scanner.run()

    # Assert
    captured = capsys.readouterr()
    assert (
        "Scan Results" in captured.out and "(2 devices found)" in captured.out
    )
    assert "Device A" in captured.out and "AA:BB:CC:11:22:33" in captured.out
    assert "Device B" in captured.out and "DD:EE:FF:44:55:66" in captured.out


@pytest.mark.asyncio
async def test_device_monitor_alerts(mocker, reloaded_main_new):
    """Test the DeviceMonitor's alert triggering logic."""
    # Arrange
    target_address = "AA:BB:CC:DD:EE:FF"
    flags = reloaded_main_new.Flags(
        daemon_mode=False, file_logging=False, verbose=False
    )
    monitor = reloaded_main_new.DeviceMonitor(
        target_address, use_bdaddr=True, flags=flags
    )

    mock_lock = mocker.patch.object(
        monitor, "_lock_macbook", return_value="🔒 MacBook locked"
    )
    mocker.patch("builtins.print")

    # --- Test 1: Trigger out-of-range alert ---
    # With TX=-59, n=2.8, RSSI of -75 gives ~3.7m distance, which is > 2.0m threshold
    device = MockBLEDevice(target_address, "Test Beacon")
    # The buffer size (SAMPLE_WINDOW) is 3 from the fixture. We must fill it.
    for rssi in [-74, -75, -76]:
        adv_data = MockAdvertisementData(rssi)
        monitor._detection_callback(device, adv_data)

    # Assert: The alert logic runs on the 3rd callback when the buffer is full.
    mock_lock.assert_called_once()
    assert monitor.alert_triggered is True

    # --- Test 2: Trigger back-in-range alert ---
    mock_lock.reset_mock()
    # RSSI of -50 gives ~0.5m distance
    for rssi in [-50, -51, -49]:
        adv_data = MockAdvertisementData(rssi)
        monitor._detection_callback(device, adv_data)

    mock_lock.assert_not_called()
    assert monitor.alert_triggered is False


def test_service_manager_status(mocker, tmp_path, reloaded_main_new):
    """Test the ServiceManager's status checking."""
    # Arrange
    pid_file = tmp_path / ".ble_monitor.pid"
    reloaded_main_new.PID_FILE = str(pid_file)
    mock_os_kill = mocker.patch("os.kill")
    args = MagicMock()
    manager = reloaded_main_new.ServiceManager(args)

    # Test running
    pid_file.write_text("12345")
    mock_os_kill.return_value = True
    pid, is_running = manager._get_pid_status()
    assert pid == 12345 and is_running is True

    # Test not running (stale PID)
    mock_os_kill.side_effect = OSError
    pid, is_running = manager._get_pid_status()
    assert pid == 12345 and is_running is False


def test_service_manager_start_stop(mocker, tmp_path, reloaded_main_new):
    """Test starting and stopping the service."""
    # Arrange
    pid_file = tmp_path / ".ble_monitor.pid"
    reloaded_main_new.PID_FILE = str(pid_file)
    mock_popen = mocker.patch("subprocess.Popen")
    mock_os_kill = mocker.patch("os.kill")
    mocker.patch("time.sleep")  # Patch sleep to speed up the test

    # --- Test Start (without file logging) ---
    args_no_log = MagicMock(
        target_mac="USE_DEFAULT",
        macos_use_bdaddr=False,
        verbose=False,
        file_logging=False,
    )
    manager = reloaded_main_new.ServiceManager(args_no_log)
    mocker.patch.object(manager, "_get_pid_status", return_value=(None, False))

    manager.start()

    # Assert: The `env` kwarg should NOT be present
    expected_command = [sys.executable, sys.argv[0], "-tm", "--daemon"]
    mock_popen.assert_called_with(
        expected_command, stdout=ANY, stderr=ANY, start_new_session=True
    )

    # --- Test Stop ---
    # Create the PID file to simulate a running process
    pid_file.write_text("12345")
    mocker.patch.object(manager, "_get_pid_status", return_value=(12345, True))
    mock_remove = mocker.patch("os.remove")
    manager.stop()
    mock_os_kill.assert_called_with(12345, reloaded_main_new.signal.SIGTERM)
    mock_remove.assert_called_with(str(pid_file))


@pytest.mark.asyncio
async def test_application_cli_dispatch(mocker, mock_args, reloaded_main_new):
    """Test that the Application class calls the right components based on CLI args."""
    # Patch the classes in the reloaded module using the module object
    mock_sm = mocker.patch.object(reloaded_main_new, "ServiceManager")
    mock_ds = mocker.patch.object(reloaded_main_new, "DeviceScanner")
    mock_dm = mocker.patch.object(reloaded_main_new, "DeviceMonitor")

    # Make the run methods async
    async def async_run_mock():
        pass

    mock_ds.return_value.run = mocker.AsyncMock(side_effect=async_run_mock)
    mock_dm.return_value.run = mocker.AsyncMock(side_effect=async_run_mock)

    # --- Test Service Start Command ---
    mock_args.start = True
    app = reloaded_main_new.Application(mock_args)
    await app.run()
    mock_sm.return_value.start.assert_called_once()
    mock_args.start = False

    # --- Test Scanner Mode ---
    mock_args.scanner = 10
    app = reloaded_main_new.Application(mock_args)
    await app.run()
    mock_ds.assert_called_with(10, ANY, ANY)
    mock_ds.return_value.run.assert_awaited_once()
    mock_args.scanner = None

    # --- Test Monitor Mode ---
    mock_args.target_mac = "USE_DEFAULT"
    app = reloaded_main_new.Application(mock_args)
    await app.run()
    expected_address = "AA:BB:CC:DD:EE:FF"
    mock_dm.assert_called_with(expected_address, True, ANY)
    mock_dm.return_value.run.assert_awaited_once()
