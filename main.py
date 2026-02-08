#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🥐 B.R.I.O.S. - Bluetooth Reactive Intelligent Operator for Croissant Safety

A professional proximity monitoring tool for device tracking and automated security.

This script provides a command-line interface to scan for Bluetooth devices
and monitor a specific target device's proximity based on its
Received Signal Strength Indicator (RSSI). It can be run as a foreground
process for immediate monitoring or as a background daemon for continuous
operation.

Key features include:
  - Real-time RSSI signal strength monitoring.
  - Distance estimation using the Log-Distance Path Loss model.
  - Proximity alerts when a device moves beyond a configurable threshold.
  - A discovery scanner to find nearby devices.
  - Service management for starting, stopping, and checking the monitor's
    status as a background process.
"""

# --- Version Information ---
__version__ = "1.0.0"
__app_name__ = "🥐 B.R.I.O.S."
__app_full_name__ = (
    "Bluetooth Reactive Intelligent Operator for Croissant Safety"
)

import os
import sys
import time
import signal
import asyncio
import argparse
import subprocess
from datetime import datetime
from collections import deque
from dataclasses import dataclass
from typing import Optional, TextIO, Deque, Tuple, List

import statistics
from dotenv import load_dotenv
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

# Platform-specific imports
IS_MACOS = sys.platform == "darwin"

try:
    import Quartz

    HAS_QUARTZ = True
except ImportError:
    HAS_QUARTZ = False

# --- Monkeypatch for Bleak 1.1.1 Crash ---
# Fixes AttributeError: 'NoneType' object has no attribute 'hex'
def _apply_robust_bleak_patch() -> None:
    """
    Monkeypatches BleakScannerCoreBluetooth.start to fix a crash when
    retrieveAddressForPeripheral_ returns None.
    """
    if not IS_MACOS:
        return

    try:
        from bleak.backends.corebluetooth.scanner import BleakScannerCoreBluetooth
        from bleak.backends.corebluetooth.utils import cb_uuid_to_str
        from bleak.backends.scanner import AdvertisementData
        import logging

        logger = logging.getLogger("bleak.backends.corebluetooth.scanner")

        async def patched_start(self) -> None:
            self.seen_devices = {}

            def callback(p, a, r) -> None:
                # --- PATCH START ---
                # This inner callback is where the crash happens.
                # We replicate the logic but add a check for None address.
                
                service_uuids = [
                    cb_uuid_to_str(u) for u in a.get("kCBAdvDataServiceUUIDs", [])
                ]

                if not self.is_allowed_uuid(service_uuids):
                    return

                # Process service data
                service_data_dict_raw = a.get("kCBAdvDataServiceData", {})
                service_data = {
                    cb_uuid_to_str(k): bytes(v) for k, v in service_data_dict_raw.items()
                }

                # Process manufacturer data
                manufacturer_binary_data = a.get("kCBAdvDataManufacturerData")
                manufacturer_data = {}
                if manufacturer_binary_data:
                    manufacturer_id = int.from_bytes(
                        manufacturer_binary_data[0:2], byteorder="little"
                    )
                    manufacturer_value = bytes(manufacturer_binary_data[2:])
                    manufacturer_data[manufacturer_id] = manufacturer_value

                # set tx_power data if available
                tx_power = a.get("kCBAdvDataTxPowerLevel")

                advertisement_data = AdvertisementData(
                    local_name=a.get("kCBAdvDataLocalName"),
                    manufacturer_data=manufacturer_data,
                    service_data=service_data,
                    service_uuids=service_uuids,
                    tx_power=tx_power,
                    rssi=r,
                    platform_data=(p, a, r),
                )

                if self._use_bdaddr:
                    # HACK: retrieveAddressForPeripheral_ is undocumented
                    address_bytes = (
                        self._manager.central_manager.retrieveAddressForPeripheral_(p)
                    )
                    if address_bytes is None:
                        # PATCH: Handle None address gracefully
                        # logger.debug("Could not get Bluetooth address...")
                        return
                    address = address_bytes.hex(":").upper()
                else:
                    address = p.identifier().UUIDString()

                device = self.create_or_update_device(
                    p.identifier().UUIDString(),
                    address,
                    p.name(),
                    (p, self._manager.central_manager.delegate()),
                    advertisement_data,
                )

                self.call_detection_callbacks(device, advertisement_data)
                # --- PATCH END ---

            self._manager.callbacks[id(self)] = callback
            await self._manager.start_scan(self._service_uuids)

        BleakScannerCoreBluetooth.start = patched_start
        # print(f"{Colors.GREEN}✓{Colors.RESET} Applied Bleak 1.1.1 crash fix")
        
    except ImportError:
        pass

# Apply patch immediately
_apply_robust_bleak_patch()

# --- Configuration Loader ---
# Load user-defined settings from a .env file for easier configuration.
load_dotenv(".env")

# --- Application Constants ---
# The target device's address. This can be a MAC address (on most platforms)
# or a UUID-based address (common on macOS due to privacy features).
TARGET_DEVICE_MAC_ADDRESS = os.getenv("TARGET_DEVICE_MAC_ADDRESS")
TARGET_DEVICE_UUID_ADDRESS = os.getenv("TARGET_DEVICE_UUID_ADDRESS")

# A human-readable name for the target device, used in logs and alerts.
TARGET_DEVICE_NAME = os.getenv("TARGET_DEVICE_NAME", "Unknown Device Name")
TARGET_DEVICE_TYPE = os.getenv("TARGET_DEVICE_TYPE", "Unknown Device")

# RSSI value (in dBm) of the target device measured at a distance of 1 meter.
# This value is crucial for accurate distance estimation.
TX_POWER_AT_1M = int(os.getenv("TX_POWER_AT_1M", "-59"))

# The path-loss exponent (n) for the environment. This value describes the rate
# at which the signal strength decreases with distance. Common values range
# from 2.0 (free space) to 4.0 (obstructed environments).
PATH_LOSS_EXPONENT = float(os.getenv("PATH_LOSS_EXPONENT", "2.8"))

# The number of recent RSSI samples to average for smoothing out fluctuations.
SAMPLE_WINDOW = int(os.getenv("SAMPLE_WINDOW", "12"))

# The distance (in meters) beyond which a device is considered "out of range."
DISTANCE_THRESHOLD_M = float(os.getenv("DISTANCE_THRESHOLD_M", "2.0"))

# --- Reliability & Safety Constants ---
# Time (in seconds) to ignore "out of range" signals after unlocking/resuming.
# Prevents immediate re-locking while signal stabilizes.
GRACE_PERIOD_SECONDS = int(os.getenv("GRACE_PERIOD_SECONDS", "30"))

# Lock Loop Protection:
# If the Mac locks LOCK_LOOP_THRESHOLD times within LOCK_LOOP_WINDOW seconds,
# the script will pause for LOCK_LOOP_PENALTY seconds.
LOCK_LOOP_THRESHOLD = int(os.getenv("LOCK_LOOP_THRESHOLD", "3"))
LOCK_LOOP_WINDOW = int(os.getenv("LOCK_LOOP_WINDOW", "60"))
LOCK_LOOP_PENALTY = int(os.getenv("LOCK_LOOP_PENALTY", "120"))

# --- File Paths ---
# The PID file stores the process ID of the running monitor.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(SCRIPT_DIR, ".ble_monitor.pid")
LOG_FILE = os.path.join(SCRIPT_DIR, ".ble_monitor.log")


# --- Utility Classes & Functions ---
class Colors:
    """A utility class for ANSI color codes to enhance terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    GREY = "\033[90m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


@dataclass
class Flags:
    """A data class to hold boolean flags derived from command-line arguments.

    Attributes:
        daemon_mode: True if the application is running as a background process.
        file_logging: True if output should be redirected to a log file.
        verbose: True if detailed, non-essential output should be printed.
    """

    daemon_mode: bool
    file_logging: bool
    verbose: bool


def _estimate_distance(rssi: float) -> float:
    """Estimates distance to a device using the Log-Distance Path Loss model.

    Args:
        rssi (float): The Received Signal Strength Indicator in dBm.

    Returns:
        float: The estimated distance in meters. Returns -1.0 if the RSSI is 0,
            as this is typically an invalid reading.
    """
    if rssi == 0:
        return -1.0
    return 10 ** ((TX_POWER_AT_1M - rssi) / (10 * PATH_LOSS_EXPONENT))


def _smooth_rssi(buffer: Deque[int]) -> Optional[float]:
    """Calculates the statistical mean of RSSI values in a buffer.

    This function helps to stabilize the fluctuating RSSI readings by averaging
    a collection of recent samples.

    Args:
        buffer (Deque[int]): A deque containing recent RSSI samples.

    Returns:
        Optional[float]: The mean RSSI value, or None if the buffer is empty.
    """
    if not buffer:
        return None
    return statistics.mean(buffer)


# ==============================================================================
# SERVICE MANAGEMENT CLASS
# ==============================================================================
class ServiceManager:
    """Handles the application's lifecycle as a background service (daemon).

    This class provides methods to start, stop, restart, and check the status
    of the monitoring script as a detached background process. It uses a PID
    file to track the running instance.

    Attributes:
        args: The command-line arguments parsed into a Namespace object.
    """

    def __init__(self, args: argparse.Namespace) -> None:
        """Initializes the ServiceManager.

        Args:
            args (argparse.Namespace): The parsed command-line arguments.
        """
        self.args = args

    def _get_pid_status(self) -> Tuple[Optional[int], bool]:
        """Checks for the PID file and determines if the process is running.

        Reads the PID from the PID file and checks if a process with that PID
        is currently active.

        Returns:
            A tuple containing:
                - The PID (int) if the file exists, otherwise None.
                - A boolean indicating if the process is currently running.
        """
        if not os.path.exists(PID_FILE):
            return None, False
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())

        except (IOError, ValueError):
            # The PID file is corrupt or unreadable.
            return None, False

        try:
            # A signal of 0 tests for the existence of the process without
            # affecting it.
            os.kill(pid, 0)
            return pid, True
        except OSError:
            # The process does not exist.
            return pid, False

    def _reconstruct_command(self) -> List[str]:
        """Reconstructs the original command to relaunch the script as a daemon.

        This ensures that the background process is started with the same
        target and options as the initial command.

        Returns:
            A list of strings representing the command and its arguments.
        """
        command = [sys.executable, sys.argv[0]]

        if self.args.target_mac:
            if self.args.target_mac == "USE_DEFAULT":
                command.append("-tm")
            else:
                command.extend(["--target-mac", self.args.target_mac])
        elif self.args.target_uuid:
            if self.args.target_uuid == "USE_DEFAULT":
                command.append("-tu")
            else:
                command.extend(["--target-uuid", self.args.target_uuid])
        elif self.args.scanner is not None:
            command.extend(["--scanner", str(self.args.scanner)])

        if self.args.macos_use_bdaddr:
            command.append("-m")

        if self.args.verbose:
            command.append("-v")

        if self.args.file_logging:
            command.append("-f")

        # The '--daemon' flag is an internal signal for the new process to
        # run in daemon mode.
        command.append("--daemon")
        return command

    def start(self) -> None:
        """Starts the monitor in the background."""
        pid, is_running = self._get_pid_status()
        if is_running:
            print(
                f"{Colors.YELLOW}!{Colors.RESET} Monitor is already "
                f"running (PID {pid})"
            )
            return

        command = self._reconstruct_command()
        target_address = Application.determine_target_address(self.args)

        print(
            f"\n{Colors.BOLD}Starting {__app_name__} Background Monitor{Colors.RESET}"
        )
        print("─" * 50)

        if self.args.verbose:
            print(f"{Colors.BLUE}Command:{Colors.RESET} {' '.join(command)}")
            print("─" * 50)

        if self.args.file_logging:
            with open(LOG_FILE, "wb") as log:
                subprocess.Popen(
                    command,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                    env={**os.environ, "PYTHONUNBUFFERED": "1"},
                )
        else:
            subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

        time.sleep(0.5)
        self._print_start_status(target_address)

    def stop(self) -> None:
        """Stops the monitor if it is running."""
        pid, is_running = self._get_pid_status()

        if not is_running:
            print(
                f"{Colors.YELLOW}●{Colors.RESET} {__app_name__} is not running"
            )
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
            return

        print(f"Stopping {__app_name__} (PID {pid})...")

        try:
            # Type guard: pid is guaranteed to be int here since is_running is True
            assert (
                pid is not None
            ), "PID should not be None when is_running is True"
            os.kill(pid, signal.SIGTERM)
            print(
                f"{Colors.GREEN}✓{Colors.RESET} {__app_name__} stopped successfully"
            )
        except OSError:
            print(
                f"{Colors.YELLOW}!{Colors.RESET} Process {pid} already stopped"
            )
        finally:
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
            # if os.path.exists(LOG_FILE): os.remove(LOG_FILE)

    def restart(self) -> None:
        """Restarts the background monitor."""
        print(f"\n{Colors.BOLD}Restarting {__app_name__}..{Colors.RESET}")
        self.stop()
        time.sleep(1)
        self.start()

    def display_status(self) -> None:
        """Displays the current status of the background monitor."""
        pid, is_running = self._get_pid_status()

        print(f"\n{Colors.BOLD}{__app_name__} Monitor Status{Colors.RESET}")
        print("─" * 50)

        if is_running:
            print(f"Status:     {Colors.GREEN}● RUNNING{Colors.RESET}")
            print(f"PID:        {pid}")

            try:
                result = subprocess.run(
                    ["ps", "-p", str(pid), "-o", "etime="],
                    capture_output=True,
                    text=True,
                )

                if uptime := result.stdout.strip():
                    print(f"Uptime:     {uptime}")

            except Exception:
                pass

            print(f"Target:     {TARGET_DEVICE_NAME}")
            print(f"Address:    {TARGET_DEVICE_MAC_ADDRESS}")
            print(f"Threshold:  {DISTANCE_THRESHOLD_M}m")

            if os.path.exists(LOG_FILE):
                print(f"\nLog file:   {LOG_FILE}")
                try:
                    with open(LOG_FILE, "r") as f:
                        lines = f.readlines()
                        if lines:
                            recent = lines[-3:] if len(lines) >= 3 else lines
                            print(f"\nRecent activity:")
                            for line in recent:
                                print(f"  {line.rstrip()}")
                except Exception:
                    pass
        else:
            print(f"Status:     {Colors.RED}● STOPPED{Colors.RESET}")
            print(f"PID File:   Not found")

        print("─" * 50 + "\n")

    def _print_start_status(self, target_address: Optional[str]) -> None:
        """Prints a detailed summary after a start attempt.

        Args:
            target_address (Optional[str]): The MAC or UUID address of the
                device being monitored.
        """
        pid, is_running = self._get_pid_status()

        if not is_running:
            print(f"{Colors.RED}✗{Colors.RESET} Failed to start {__app_name__}")
            print(f"Log file:   {LOG_FILE}")
            print("─" * 50 + "\n")
            return

        print(
            f"{Colors.GREEN}✓{Colors.RESET} {__app_name__} started successfully"
        )
        print(f"PID:        {pid}")
        print("─" * 50)
        print(f"Target:     {TARGET_DEVICE_NAME} ({TARGET_DEVICE_TYPE})")

        if target_address:
            print(f"Address:    {target_address}")

        print(f"Threshold:  {DISTANCE_THRESHOLD_M}m")
        print(f"TX Power:   {TX_POWER_AT_1M} dBm @ 1m")
        print(f"Path Loss:  {PATH_LOSS_EXPONENT}")
        print(f"Samples:    {SAMPLE_WINDOW} readings")

        if self.args.macos_use_bdaddr:
            print(f"Mode:       {Colors.BLUE}BD_ADDR (MAC){Colors.RESET}")
        else:
            print(f"Mode:       UUID (Privacy Mode)")
        print("─" * 50)

        if self.args.file_logging:
            print(
                f"Log file:   {LOG_FILE} {Colors.GREEN}(enabled){Colors.RESET}"
            )
        else:
            print(f"Logging:    Disabled (use -f to enable)")

        print(
            f"\n{Colors.GREEN}●{Colors.RESET} {__app_name__} running in background"
        )
        print(
            f"\nUse `{sys.argv[0]} --status` to check status or "
            f"`--stop` to terminate."
        )


# ==============================================================================
# DEVICE SCANNER CLASS
# ==============================================================================
class DeviceScanner:
    """Performs a one-time BLE device discovery scan.

    This class uses the BleakScanner to perform a scan for nearby BLE devices
    and prints a formatted list of discovered devices along with their RSSI
    and estimated distances.

    Attributes:
        duration (int): The scan duration in seconds.
        use_bdaddr (bool): Whether to use BD_ADDR (MAC) for identification.
        verbose (bool): Whether to print detailed output.
    """

    def __init__(self, duration: int, use_bdaddr: bool, verbose: bool) -> None:
        """Initializes the DeviceScanner.

        Args:
            duration (int): The scan duration in seconds.
            use_bdaddr (bool): Whether to use BD_ADDR (MAC) for identification.
            verbose (bool): Whether to print detailed output.
        """
        self.duration = duration
        self.use_bdaddr = use_bdaddr
        self.verbose = verbose

    async def run(self) -> None:
        """Executes the device scan and prints formatted results."""
        self._print_summary()

        # Pass cb parameter directly to satisfy mypy type checking
        devices_and_adv = await BleakScanner.discover(
            timeout=float(self.duration),
            return_adv=True,
            cb={"use_bdaddr": self.use_bdaddr},
        )

        devices = sorted(
            [
                (device, adv_data)
                for _, (device, adv_data) in devices_and_adv.items()
            ],
            key=lambda x: getattr(x[0], "address", str(x[0])),
        )

        self._print_results(devices)

    def _print_summary(self) -> None:
        """Prints a summary of the scanner configuration."""
        print(f"\n{Colors.BOLD}{__app_name__} Device Scanner{Colors.RESET}")
        print("─" * 70)
        print(f"Duration:   {self.duration} seconds")

        mode = (
            "BD_ADDR (MAC addresses)"
            if self.use_bdaddr
            else "UUIDs (macOS privacy)"
        )

        print(f"Mode:       {mode}")
        print(f"Verbose:    Enabled (showing RSSI and distance estimates)")
        print(
            f"TX Power:   {TX_POWER_AT_1M} dBm @ 1m (for distance calculation)"
        )
        print(f"Path Loss:  {PATH_LOSS_EXPONENT} (environmental factor)")
        print("─" * 70)
        print(f"\n{Colors.GREEN}●{Colors.RESET} Scanning...\n")

    def _print_results(
        self,
        devices: List[tuple[BLEDevice, AdvertisementData]],
    ) -> None:
        """Formats and prints the list of discovered devices.

        Args:
            devices (List[tuple[BLEDevice, AdvertisementData]]): A list of
                tuples containing BLEDevice instances and their corresponding
                AdvertisementData.
        """
        print(
            f"\n{Colors.BOLD}Scan Results{Colors.RESET} ({len(devices)} "
            f"device{'s' if len(devices) != 1 else ''} found)"
        )
        print("─" * 70)

        if not devices:
            print(f"{Colors.YELLOW}No devices found{Colors.RESET}")
            return

        for i, (device, adv_data) in enumerate(devices, 1):
            address = (
                device.address if hasattr(device, "address") else str(device)
            )
            device_name = device.name if hasattr(device, "name") else None
            name_display = (
                device_name
                if device_name
                else f"{Colors.YELLOW}(Unknown){Colors.RESET}"
            )

            # Ensure proper alignment
            visible_length = len(device_name) if device_name else 9
            padding = 30 - visible_length

            # Get RSSI and calculate distance
            rssi = adv_data.rssi if hasattr(adv_data, "rssi") else -100
            distance = _estimate_distance(rssi)
            signal_color = (
                Colors.GREEN
                if rssi > -50
                else Colors.YELLOW
                if rssi > -70
                else Colors.RED
            )

            print(
                f"{i:2d}. {name_display}{' ' * padding} │ {address} │ "
                f"{signal_color}{rssi:4d} dBm{Colors.RESET} │ ~{distance:5.2f}m"
            )


# ==============================================================================
# DEVICE MONITOR CLASS
# ==============================================================================
class DeviceMonitor:
    """Manages a continuous monitoring session for a single BLE device.

    This class sets up a long-running scan that invokes a callback for each
    advertisement received. It processes the signal strength, calculates
    distance, and triggers alerts based on a defined threshold.

    Attributes:
        target_address (str): The MAC or UUID address of the target device.
        use_bdaddr (bool): Whether to use BD_ADDR (MAC) for identification.
        flags (Flags): Configuration flags for the monitoring session.
        rssi_buffer (Deque[int]): A buffer to hold recent RSSI samples.
        alert_triggered (bool): Indicates if an out-of-range alert is active.
        log_file (TextIO | None): The file object for logging output, if any.
        scanner (BleakScanner): The Bleak scanner instance for BLE scanning.
    """

    def __init__(
        self,
        target_address: str,
        use_bdaddr: bool,
        flags: Flags,
    ) -> None:
        """Initializes the DeviceMonitor.
        Args:
            target_address (str): The MAC or UUID address of the target device.
            use_bdaddr (bool): Whether to use BD_ADDR (MAC) for identification.
            flags (Flags): Configuration flags for the monitoring session.
            rssi_buffer (Deque[int]): A buffer to hold recent RSSI samples.
            alert_triggered (bool):
                Indicates if an out-of-range alert is active.
            log_file (TextIO | None):
                The file object for logging output, if any.
            scanner (BleakScanner): The Bleak scanner instance for BLE scanning.
        """
        self.target_address = target_address
        self.use_bdaddr = use_bdaddr
        self.flags = flags

        self.rssi_buffer: Deque[int] = deque(maxlen=SAMPLE_WINDOW)
        self.alert_triggered: bool = False
        self.log_file: Optional[TextIO] = None
        self.is_handling_lock: bool = False
        self.last_packet_time: float = time.monotonic()
        self.lock_handling_start_time: float = 0
        
        # Safety state
        self.resume_time: float = 0
        self.lock_history: Deque[float] = deque(maxlen=LOCK_LOOP_THRESHOLD)

        self.scanner = BleakScanner(
            detection_callback=self._detection_callback,
            cb={"use_bdaddr": self.use_bdaddr},
        )

    def _print_start_status(self) -> None:
        """Prints the startup status of the monitoring process.

        This method displays formatted information about the current
            monitor configuration, including target device details, distance
            and power parameters, and output settings. It is primarily used to
            provide user-friendly feedback in the terminal when the monitoring
            process begins.

        The output is suppressed if the monitor is running in daemon mode.
        """
        if self.flags.daemon_mode:
            return

        print(f"\n{Colors.BOLD}Starting {__app_name__} Monitor{Colors.RESET}")
        print("─" * 50)
        print(f"Target:     {TARGET_DEVICE_NAME} ({TARGET_DEVICE_TYPE})")
        print(f"Address:    {self.target_address}")
        print(f"Threshold:  {DISTANCE_THRESHOLD_M}m")
        print(f"TX Power:   {TX_POWER_AT_1M} dBm @ 1m")
        print(f"Path Loss:  {PATH_LOSS_EXPONENT}")
        print(f"Samples:    {SAMPLE_WINDOW} readings")
        if self.use_bdaddr:
            print(f"Mode:       {Colors.BLUE}BD_ADDR (MAC){Colors.RESET}")
        print("─" * 50)

        if self.flags.verbose and self.flags.file_logging:
            print(f"Output:     {Colors.GREEN}Terminal + File{Colors.RESET}")
            print(f"Log file:   {LOG_FILE}")
        elif self.flags.verbose:
            print(f"Output:     {Colors.GREEN}Terminal only{Colors.RESET}")
        elif self.flags.file_logging:
            print(f"Output:     {Colors.GREEN}File only{Colors.RESET}")
            print(f"Log file:   {LOG_FILE}")

        print(
            f"\n{Colors.GREEN}●{Colors.RESET} Monitoring active - "
            f"Press Ctrl+C to stop\n"
        )

    def _detection_callback(
        self,
        device: BLEDevice,
        adv_data: AdvertisementData,
    ) -> None:
        """Processes incoming BLE advertisements.

        This is the core callback function for the BleakScanner. It filters for
        the target device, processes its signal, and manages state.

        Args:
            device: The BLEDevice object discovered by the scanner.
            adv_data: The advertisement data associated with the device.
        """
        self.last_packet_time = time.monotonic()
        is_locked = False

        try:
            if device.address != self.target_address:
                return
            current_rssi = int(adv_data.rssi)

        except (AttributeError, TypeError):
            if self.flags.verbose:
                self._handle_bleak_error()
            return
        except Exception as e:
            if self.flags.verbose:
                self._handle_generic_error(e)
            return

        smoothed_rssi, distance_m = self._process_signal(current_rssi)
        if distance_m is None or smoothed_rssi is None:
            return

        self._log_status(current_rssi, smoothed_rssi, distance_m)

        if distance_m > DISTANCE_THRESHOLD_M and not self.alert_triggered:
            # Check for Grace Period
            time_since_resume = time.monotonic() - self.resume_time
            if time_since_resume < GRACE_PERIOD_SECONDS:
                if self.flags.verbose:
                     print(
                        f"{Colors.GREY}[Grace Period] Ignoring trigger "
                        f"({time_since_resume:.1f}/{GRACE_PERIOD_SECONDS}s){Colors.RESET}"
                    )
                return

            is_locked = self._trigger_out_of_range_alert(distance_m)
        elif distance_m <= DISTANCE_THRESHOLD_M and self.alert_triggered:
            self._trigger_in_range_alert(distance_m)

        if is_locked:
            asyncio.create_task(self._handle_screen_lock())

    async def _handle_screen_lock(self) -> None:
        """Handles the screen lock state by monitoring and re-establishing
            scanner connection.

        This method runs in the background while the screen is locked,
        periodically checking the lock status. When the screen is unlocked, it
        restarts the scanner and clears the RSSI buffer to ensure
        fresh readings.
        """
        if self.is_handling_lock:
            return

        self.is_handling_lock = True
        self.lock_handling_start_time = time.monotonic()
        
        try:
            # Try to stop scanner with timeout
            try:
                await asyncio.wait_for(self.scanner.stop(), timeout=5.0)
            except asyncio.TimeoutError:
                if self.flags.verbose:
                    print(f"{Colors.YELLOW}Warning: Scanner stop timed out{Colors.RESET}")
            except Exception as e:
                if self.flags.verbose:
                    print(f"{Colors.YELLOW}Warning: Scanner stop failed: {e}{Colors.RESET}")

            timestamp = datetime.now().strftime("%H:%M:%S")

            if self.flags.daemon_mode:
                msg = f"[{timestamp}] Screen locked - Scanner paused"
                print(msg)
                sys.stdout.flush()
            elif self.flags.verbose:
                print(
                    f"{Colors.YELLOW}[{timestamp}]{Colors.RESET} Screen locked "
                    f"→ Scanner {Colors.BOLD}{Colors.YELLOW}Paused{Colors.RESET}"
                    f" │ Monitoring: Waiting for unlock"
                )

            if self.flags.file_logging and self.log_file:
                self.log_file.write(
                    f"[{timestamp}] Screen locked - Scanner paused\n"
                )
                self.log_file.flush()

            await asyncio.sleep(2)

            loop_count = 0
            is_waiting = False
            while self._is_screen_locked():
                loop_count += 1

                if not is_waiting:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    is_waiting = True

                    if self.flags.daemon_mode:
                        print(
                            f"[{timestamp}] "
                            f"Screen still locked - Waiting for unlock"
                        )
                        sys.stdout.flush()
                    elif self.flags.verbose:
                        print(
                            f"{Colors.GREY}[{timestamp}]{Colors.RESET} "
                            f"Screen locked → Waiting..."
                        )

                    if self.flags.file_logging and self.log_file:
                        self.log_file.write(
                            f"[{timestamp}] "
                            f"Screen still locked - Waiting for unlock\n"
                        )
                        self.log_file.flush()

                await asyncio.sleep(2)

            timestamp = datetime.now().strftime("%H:%M:%S")
            total_time = loop_count * 2

            self.rssi_buffer.clear()

            if self.flags.daemon_mode:
                print(
                    f"[{timestamp}] Screen unlocked - "
                    f"Reconnecting scanner (locked for {total_time}s)"
                )
                sys.stdout.flush()
            elif self.flags.verbose:
                print(
                    f"{Colors.GREEN}[{timestamp}]{Colors.RESET} Screen unlocked "
                    f"→ Reconnecting │ Locked: {total_time}s │ "
                    f"RSSI buffer: Cleared"
                )

            if self.flags.file_logging and self.log_file:
                self.log_file.write(
                    f"[{timestamp}] Screen unlocked - Reconnecting scanner "
                    f"(locked for {total_time}s)\n"
                )
                self.log_file.flush()

            # --- Lock Loop Protection ---
            now = time.monotonic()
            self.lock_history.append(now)
            
            if len(self.lock_history) == LOCK_LOOP_THRESHOLD:
                # Check if all events happened within window
                if now - self.lock_history[0] < LOCK_LOOP_WINDOW:
                    msg = (
                        f"⚠️  LOCK LOOP DETECTED! ({LOCK_LOOP_THRESHOLD} locks in "
                        f"{int(now - self.lock_history[0])}s) -> "
                        f"PAUSING FOR {LOCK_LOOP_PENALTY}s"
                    )
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    if self.flags.daemon_mode:
                        print(f"[{timestamp}] {msg}")
                        sys.stdout.flush()
                    else:
                        print(f"\n{Colors.RED}{Colors.BOLD}{msg}{Colors.RESET}\n")
                        
                    if self.flags.file_logging and self.log_file:
                        self.log_file.write(f"[{timestamp}] {msg}\n")
                        self.log_file.flush()
                        
                    await asyncio.sleep(LOCK_LOOP_PENALTY)
                    self.lock_history.clear()

            # Retry logic for scanner reconnection
            # Recreate scanner instance to ensure fresh connection
            if self.flags.verbose:
                print(f"{Colors.GREY}[Debug] Recreating BleakScanner instance...{Colors.RESET}")
            
            self.scanner = BleakScanner(
                detection_callback=self._detection_callback,
                cb={"use_bdaddr": self.use_bdaddr},
            )

            max_retries = 5
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    # Try to start scanner with timeout
                    await asyncio.wait_for(self.scanner.start(), timeout=5.0)
                    break  # Success!
                except Exception as e:
                    if attempt >= max_retries - 1:
                        raise e

                    timestamp = datetime.now().strftime("%H:%M:%S")
                    wait_time = retry_delay * (attempt + 1)
                    
                    msg = (
                        f"[{timestamp}] Scanner start failed (Attempt "
                        f"{attempt + 1}/{max_retries}) - Retrying in "
                        f"{wait_time}s... Error: {e}"
                    )
                    
                    if self.flags.daemon_mode:
                        print(msg)
                        sys.stdout.flush()
                    elif self.flags.verbose:
                        print(f"{Colors.YELLOW}{msg}{Colors.RESET}")
                        
                    if self.flags.file_logging and self.log_file:
                        self.log_file.write(f"{msg}\n")
                        self.log_file.flush()
                        
                    await asyncio.sleep(wait_time)
                        

            timestamp = datetime.now().strftime("%H:%M:%S")
            if self.flags.daemon_mode:
                msg = f"[{timestamp}] Scanner reconnected - Monitoring resumed"
                print(msg)
                sys.stdout.flush()
            elif self.flags.verbose:
                print(
                    f"{Colors.GREEN}[{timestamp}]{Colors.RESET} Scanner ready "
                    f"→ Monitoring: {Colors.GREEN}{Colors.BOLD}Active{Colors.RESET}"
                )

            if self.flags.file_logging and self.log_file:
                self.log_file.write(
                    f"[{timestamp}] Scanner reconnected - Monitoring resumed\n"
                )
                self.log_file.flush()

            # Set resume time for Grace Period logic
            self.resume_time = time.monotonic()

        except Exception as e:
            import traceback

            error_detail = traceback.format_exc()
            timestamp = datetime.now().strftime("%H:%M:%S")

            if self.flags.daemon_mode:
                print(f"[{timestamp}] ERROR: Failed to reconnect scanner - {e}")
                sys.stdout.flush()
            else:
                print(
                    f"{Colors.RED}[{timestamp}]{Colors.RESET} Error → "
                    f"Scanner reconnection failed │ {e}"
                )

            if self.flags.file_logging and self.log_file:
                self.log_file.write(
                    f"[{timestamp}] ERROR: Scanner reconnection failed\n"
                    f"{error_detail}\n"
                )
                self.log_file.flush()
        finally:
            self.is_handling_lock = False
            self.lock_handling_start_time = 0

    def _is_screen_locked(self) -> bool:
        """Checks if the macOS screen is currently locked.

        Returns:
            bool: True if the screen is locked, False otherwise.
        """
        if not HAS_QUARTZ:
            # Quartz not available (non-macOS platform)
            return False

        try:
            # Use Quartz (PyObjC) to check if screen is locked
            session_dict = Quartz.CGSessionCopyCurrentDictionary()

            if session_dict is None:
                return False

            is_locked = session_dict.get("CGSSessionScreenIsLocked", False)

            return bool(is_locked)
        except Exception as e:
            if self.flags.file_logging and self.log_file:
                self.log_file.write(
                    f"[{datetime.now().strftime('%H:%M:%S')}] "
                    f"ERROR: Screen lock check failed - {e}\n"
                )
                self.log_file.flush()
            return False

    def _process_signal(
        self,
        current_rssi: int,
    ) -> Tuple[Optional[float], Optional[float]]:
        """Updates the RSSI buffer and calculates the smoothed distance.

        Args:
            current_rssi: The latest raw RSSI value received.

        Returns:
            A tuple containing:
                - The smoothed RSSI value (float), or None if buffer is not full.
                - The estimated distance (float), or None if buffer is not full.
        """
        self.rssi_buffer.append(current_rssi)
        if len(self.rssi_buffer) < SAMPLE_WINDOW:
            return None, None

        smoothed_rssi = _smooth_rssi(self.rssi_buffer)
        if smoothed_rssi is None:
            return None, None

        distance_m = _estimate_distance(smoothed_rssi)
        return smoothed_rssi, distance_m

    def _log_status(
        self,
        current_rssi: int,
        smoothed_rssi: float,
        distance_m: float,
    ) -> None:
        """Logs the current status to console and/or file.

        Args:
            current_rssi (int): The latest raw RSSI value received.
            smoothed_rssi (float): The smoothed RSSI value.
            distance_m (float): The estimated distance in meters.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        if not self.flags.verbose and not self.flags.file_logging:
            return

        log_message = (
            f"[{timestamp}] RSSI: {current_rssi:4d} dBm → "
            f"Smoothed: {smoothed_rssi:5.1f} dBm │ "
            f"Distance: {distance_m:5.2f}m"
        )

        if self.flags.daemon_mode:
            if self.flags.file_logging:
                print(log_message)
                sys.stdout.flush()
        else:
            if self.flags.verbose:
                signal_strength = (
                    "Strong"
                    if smoothed_rssi > -50
                    else "Medium"
                    if smoothed_rssi > -70
                    else "Weak"
                )
                signal_color = (
                    Colors.GREEN
                    if smoothed_rssi > -50
                    else Colors.YELLOW
                    if smoothed_rssi > -70
                    else Colors.RED
                )
                print(
                    f"{Colors.BLUE}[{timestamp}]{Colors.RESET} "
                    f"RSSI: {current_rssi:4d} dBm → "
                    f"Smoothed: {smoothed_rssi:5.1f} dBm │ "
                    f"Distance: {Colors.BOLD}{distance_m:5.2f}m{Colors.RESET} │ "
                    f"Signal: {signal_color}{signal_strength}{Colors.RESET}"
                )

            if self.flags.file_logging and self.log_file:
                self.log_file.write(log_message + "\n")
                self.log_file.flush()

    def _lock_macbook(self) -> str:
        """Executes system commands to immediately lock the macOS screen.

        Returns:
            A status string indicating success or failure.
        """
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
            return "🔒 MacBook locked (password required)"

        except Exception as e:
            return f"⚠️  Failed to lock MacBook: {e}"

    def _trigger_out_of_range_alert(self, distance_m: float) -> bool:
        """Handles the out-of-range alert logic.

        Args:
            distance_m (float): The estimated distance in meters.

        Returns:
            bool: True if the MacBook was locked, False otherwise.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        lock_status = self._lock_macbook()
        is_locked = "Failed" not in lock_status

        alert_msg = (
            f"⚠️  ALERT: Device '{TARGET_DEVICE_NAME}' is far away! "
            f"(~{distance_m:.2f} m) - {lock_status}"
        )

        if self.flags.daemon_mode:
            print(alert_msg)
            sys.stdout.flush()

        else:
            print(
                f"\n{Colors.RED}{'─' * 50}{Colors.RESET}\n"
                f"{Colors.RED}⚠{Colors.RESET}  {Colors.BOLD}"
                f"ALERT: Device moved out of range{Colors.RESET}\n"
                f"   Device:    {TARGET_DEVICE_NAME}\n"
                f"   Distance:  ~{distance_m:.2f}m "
                f"(threshold: {DISTANCE_THRESHOLD_M}m)\n"
                f"   Time:      {timestamp}\n"
                f"   Action:    {lock_status}\n"
                f"{Colors.RED}{'─' * 50}{Colors.RESET}\n"
            )
            # Write to log file if enabled
            if self.flags.file_logging and self.log_file:
                self.log_file.write(f"[{timestamp}] {alert_msg}\n")
                self.log_file.flush()

        self.alert_triggered = True
        return is_locked

    def _trigger_in_range_alert(self, distance_m: float) -> None:
        """Handles the back-in-range alert logic.

        Args:
            distance_m (float): The estimated distance in meters.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        back_msg_plain = (
            f"STATUS: Device '{TARGET_DEVICE_NAME}' is back in range. "
            f"(~{distance_m:.2f} m)"
        )

        if self.flags.daemon_mode:
            print(f"[{timestamp}] {back_msg_plain}")
            sys.stdout.flush()

        else:
            back_msg_rich = (
                f"\n{Colors.GREEN}{'─' * 60}{Colors.RESET}\n"
                f"{Colors.GREEN}✓{Colors.RESET}  {Colors.BOLD}"
                f"Device Back in Range{Colors.RESET}\n"
                f"   Device:    {TARGET_DEVICE_NAME}\n"
                f"   Distance:  ~{distance_m:.2f}m "
                f"(Threshold: {DISTANCE_THRESHOLD_M}m)\n"
                f"   Time:      {timestamp}\n"
                f"   Status:    🔓 Ready to unlock MacBook\n"
                f"{Colors.GREEN}{'─' * 60}{Colors.RESET}\n"
            )
            print(back_msg_rich)

            if self.flags.file_logging and self.log_file:
                self.log_file.write(f"[{timestamp}] {back_msg_plain}\n")
                self.log_file.flush()
        self.alert_triggered = False

    def _handle_bleak_error(self) -> None:
        """Handles the specific AttributeError for malformed packets.
        Catch the specific "NoneType has no attribute 'hex'" error.
        """
        print(
            f"\n{Colors.YELLOW}{'─' * 60}{Colors.RESET}\n{Colors.YELLOW}"
            f"DEBUG: Malformed Packet Ignored{Colors.RESET}\n{Colors.GREY}   "
            f"└─> Cause: This is expected when the host Mac is locked or "
            f"sleeping.{Colors.RESET}\n{Colors.YELLOW}{'─' * 60}"
            f"{Colors.RESET}\n"
        )

    def _handle_generic_error(self, e: Exception) -> None:
        """Handles unexpected exceptions in the callback.
        Catch any other unexpected errors to keep the scanner alive.
        """
        print(
            f"\n{Colors.RED}{'─' * 60}{Colors.RESET}\n{Colors.RED}CRITICAL: "
            f"Unexpected Callback Error{Colors.RESET}\n{Colors.GREY}   "
            f"An error was caught, but the scanner will continue to run."
            f"{Colors.RESET}\n   └─> {Colors.BOLD}Error Details:"
            f"{Colors.RESET} {e}\n{Colors.RED}{'─' * 60}{Colors.RESET}\n"
        )

    def _setup_logging(self) -> None:
        """Sets up file logging if enabled in the flags."""
        if self.flags.file_logging:
            try:
                self.log_file = open(LOG_FILE, "a")
            except IOError as e:
                print(
                    f"{Colors.YELLOW}Warning:{Colors.RESET} "
                    f"Could not open log file: {e}"
                )
                self.flags.file_logging = False

    async def run(self) -> None:
        """Starts the monitoring session."""
        self._setup_logging()
        self._print_start_status()

        try:
            await self.scanner.start()
            asyncio.create_task(self._watchdog_loop())
            
            while True:
                await asyncio.sleep(1.0)
        except Exception as e:
            # Handle scanner start failure
            if self.flags.daemon_mode:
                # In a real daemon, you'd write to the log file here
                sys.exit(f"DAEMON ERROR: Failed to start scanner: {e}")
            else:
                print(
                    f"\n{Colors.RED}✗{Colors.RESET} {Colors.BOLD}"
                    f"Error:{Colors.RESET} Failed to start the scanner.\n"
                    f"  Please ensure your Bluetooth adapter is enabled.\n"
                    f"  Details: {e}\n"
                )
        finally:
            # Graceful shutdown
            if self.flags.verbose and not self.flags.daemon_mode:
                print(f"\n{Colors.YELLOW}Stopping scanner...{Colors.RESET}")

            await self.scanner.stop()

            if self.log_file:
                self.log_file.close()

            if not self.flags.daemon_mode:
                print(f"{Colors.GREEN}✓{Colors.RESET} {__app_name__} stopped.\n")

    async def _watchdog_loop(self) -> None:
        """Background task to monitor for external screen lock events.

        This loop runs concurrently with the scanner and checks if the screen
        is locked. If it detects a lock event that wasn't triggered by the
        script itself, it initiates the lock handling logic to pause the
        scanner and wait for unlock.
        """
        last_log_time = time.monotonic()
        
        while True:
            try:
                current_time = time.monotonic()
                
                # Periodic liveness log (every 60s)
                if self.flags.verbose and current_time - last_log_time > 60:
                    time_since_packet = int(current_time - self.last_packet_time)
                    print(f"{Colors.GREY}[Watchdog] Active - Last packet: {time_since_packet}s ago{Colors.RESET}")
                    last_log_time = current_time

                if self._is_screen_locked() and not self.is_handling_lock:
                    # Spawn handler as a task so watchdog keeps running
                    asyncio.create_task(self._handle_screen_lock())
                
                # Heartbeat check: Restart scanner if no packets received for 120s
                if current_time - self.last_packet_time > 120 and not self.is_handling_lock:
                    if self.flags.verbose:
                        print(f"{Colors.YELLOW}Watchdog: Scanner frozen (no data for 120s) -> Restarting...{Colors.RESET}")
                    # Spawn handler as a task
                    asyncio.create_task(self._handle_screen_lock())

                # Stuck handler check: If handling lock takes > 60s, force reset
                if self.is_handling_lock and self.lock_handling_start_time > 0:
                    if current_time - self.lock_handling_start_time > 60:
                        if self.flags.verbose:
                            print(f"{Colors.RED}Watchdog: Lock handler stuck for >60s -> Forcing reset{Colors.RESET}")
                        self.is_handling_lock = False
                        self.lock_handling_start_time = 0
                        # We don't call _handle_screen_lock immediately to avoid recursion loop
                        # The next watchdog tick will trigger it if needed (via heartbeat or lock check)

                await asyncio.sleep(2.0)
            except Exception as e:
                if self.flags.verbose:
                    print(f"{Colors.YELLOW}Watchdog error: {e}{Colors.RESET}")
                await asyncio.sleep(5.0)


# ==============================================================================
# MAIN APPLICATION CLASS
# ==============================================================================
class Application:
    """The main application orchestrator.

    This class is responsible for parsing command-line arguments and delegating
    the requested tasks to the appropriate component (e.g., ServiceManager,
    DeviceScanner, or DeviceMonitor).

    Attributes:
        args: The command-line arguments parsed into a Namespace object.
        service_manager: An instance of ServiceManager for handling
            daemon tasks.
    """

    def __init__(self, args: argparse.Namespace) -> None:
        """Initializes the Application.

        Args:
            args (argparse.Namespace): The parsed command-line arguments.
        """
        self.args = args
        self.service_manager = ServiceManager(args)

    async def run(self) -> None:
        """Parses arguments and delegates tasks to the appropriate component."""
        if self.args.status:
            self.service_manager.display_status()
        elif self.args.stop:
            self.service_manager.stop()
        elif self.args.restart:
            self.service_manager.restart()
        elif self.args.start:
            self.service_manager.start()
        elif self.args.scanner is not None:
            scanner = DeviceScanner(
                self.args.scanner, self.args.macos_use_bdaddr, self.args.verbose
            )
            await scanner.run()
        else:
            await self._run_monitor_foreground()

    async def _run_monitor_foreground(self) -> None:
        """Configures and runs the device monitor in the foreground."""
        target_address = self.determine_target_address(self.args)
        if not target_address:
            print(f"{Colors.RED}✗{Colors.RESET} No operating mode selected")
            print(f"Run '{sys.argv[0]} --help' for usage information")
            return

        flags = Flags(
            daemon_mode=self.args.daemon,
            file_logging=self.args.file_logging,
            verbose=self.args.verbose,
        )

        use_bdaddr = self.args.macos_use_bdaddr or bool(self.args.target_mac)
        monitor = DeviceMonitor(target_address, use_bdaddr, flags)

        if flags.daemon_mode:
            try:
                with open(PID_FILE, "w") as f:
                    f.write(str(os.getpid()))
            except IOError:
                print(f"{Colors.RED}✗{Colors.RESET} Failed to write PID file")
                sys.exit(1)

        try:
            await monitor.run()
        finally:
            if flags.daemon_mode and os.path.exists(PID_FILE):
                os.remove(PID_FILE)

    @staticmethod
    def determine_target_address(args: argparse.Namespace) -> Optional[str]:
        """Determines the target address based on command-line arguments.

        Args:
            args (argparse.Namespace): Parsed command-line arguments.

        Returns:
            Optional[str]: The target address or None if not specified.
        """
        if args.target_mac:
            return (
                TARGET_DEVICE_MAC_ADDRESS
                if args.target_mac == "USE_DEFAULT"
                else args.target_mac
            )
        if args.target_uuid:
            return (
                TARGET_DEVICE_UUID_ADDRESS
                if args.target_uuid == "USE_DEFAULT"
                else args.target_uuid
            )
        return None

    @staticmethod
    def setup_parser() -> argparse.ArgumentParser:
        """Sets up the command-line argument parser.

        Returns:
            argparse.ArgumentParser: The configured argument parser.
        """
        help_epilog = f"""
        DESCRIPTION:
        {__app_name__} ({__app_full_name__})
        
        A professional proximity monitoring tool that provides real-time device 
        tracking and automated security based on Bluetooth signal strength (RSSI).
        Automatically locks your Mac when your iPhone, Apple Watch, or any Bluetooth 
        device moves beyond a configurable distance threshold.

        OPERATING MODES:
        Scanner Mode    Discover nearby Bluetooth devices and display their information
        Monitor Mode    Track a specific device and trigger alerts on distance changes
        Service Mode    Run as a background daemon with service management

        EXAMPLES:
        Discover nearby devices (recommended for macOS):
            $ python3 main.py --scanner 10 -m

        Quick scan with default 15 seconds:
            $ python3 main.py --scanner

        Monitor device in foreground with verbose output:
            $ python3 main.py --target-mac -v

        Monitor specific device by MAC address:
            $ python3 main.py --target-mac "AA:BB:CC:DD:EE:FF" -m -v

        Monitor device by UUID (macOS privacy mode):
            $ python3 main.py --target-uuid "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"

        Start monitoring as background service with file logging:
            $ python3 main.py --target-mac -v -f --start

        Check background service status:
            $ python3 main.py --status

        Stop background service:
            $ python3 main.py --stop

        Restart background service:
            $ python3 main.py --restart

        COMMAND-LINE OPTIONS:
        Service Control:
          --start               Start {__app_name__} as background daemon
          --stop                Stop background daemon
          --restart             Restart background daemon
          --status              Show daemon status and statistics

        Operating Modes:
          --scanner, -s [SEC]   Discover devices (default: 15s, range: 5-60s)
          --target-mac, -tm     Monitor by MAC address (recommended)
          --target-uuid, -tu    Monitor by UUID (macOS privacy mode)

        Options:
          --macos-use-bdaddr, -m    Use real MAC addresses on macOS (recommended)
          --verbose, -v             Show detailed RSSI and distance output
          --file-logging, -f        Enable logging to .ble_monitor.log

        CONFIGURATION:
        Edit the .env file to customize:
        • TARGET_DEVICE_MAC_ADDRESS    MAC address of your device
        • TARGET_DEVICE_UUID_ADDRESS   UUID address (for macOS)
        • TARGET_DEVICE_NAME           Friendly name for your device
        • TARGET_DEVICE_TYPE           Device type (e.g., "phone", "watch")
        • DISTANCE_THRESHOLD_M         Alert distance in meters (default: 2.0)
        • TX_POWER_AT_1M               RSSI at 1 meter (default: -59 dBm)
        • PATH_LOSS_EXPONENT           Environment factor (default: 2.8)
        • SAMPLE_WINDOW                Signal smoothing samples (default: 12)

        NOTES:
        • On macOS, use -m flag to see real MAC addresses instead of UUIDs
        • Use -f flag to enable logging to .ble_monitor.log in project directory
        • Use -v flag for verbose RSSI/distance output in terminal
        • Background service (--start) automatically enables file logging
        • Bluetooth must be enabled on your Mac
        • Requires macOS 10.15 (Catalina) or later
        • Python 3.8+ required

        FILES:
        .env                  Configuration file with device settings
        .ble_monitor.pid      Process ID file for background service
        .ble_monitor.log      Log file (when file logging is enabled)

        For more information, visit: https://github.com/Piero24/B.R.I.O.S.
        """
        parser = argparse.ArgumentParser(
            description=(
                f"{__app_name__} - {__app_full_name__}\n"
                "Device proximity monitor with distance-based alerting"
            ),
            formatter_class=argparse.RawTextHelpFormatter,
            epilog=help_epilog,
        )

        # --- Version ---
        parser.add_argument(
            "--version",
            action="version",
            version=f"{__app_name__} v{__version__}",
            help="show program's version number and exit",
        )

        # --- Service Control Group ---
        service_group = parser.add_argument_group("Service Control")
        service_exclusive = service_group.add_mutually_exclusive_group()
        service_exclusive.add_argument(
            "--start",
            action="store_true",
            help="start monitor as background daemon",
        )
        service_exclusive.add_argument(
            "--stop", action="store_true", help="stop background daemon"
        )
        service_exclusive.add_argument(
            "--restart", action="store_true", help="restart background daemon"
        )
        service_exclusive.add_argument(
            "--status",
            action="store_true",
            help="show daemon status and statistics",
        )

        # --- Operating Modes ---
        mode_group = parser.add_argument_group("Operating Modes")
        mode_exclusive = mode_group.add_mutually_exclusive_group(required=False)

        mode_exclusive.add_argument(
            "--scanner",
            "-s",
            nargs="?",
            const=15,
            type=int,
            metavar="SECONDS",
            help="discover nearby BLE devices (default: 15s, range: 5-60s)",
        )
        mode_exclusive.add_argument(
            "--target-mac",
            "-tm",
            nargs="?",
            const="USE_DEFAULT",
            type=str,
            metavar="ADDRESS",
            help="monitor device by MAC address (recommended)",
        )
        mode_exclusive.add_argument(
            "--target-uuid",
            "-tu",
            nargs="?",
            const="USE_DEFAULT",
            type=str,
            metavar="UUID",
            help="monitor device by UUID (macOS privacy mode)",
        )

        # --- Options ---
        options_group = parser.add_argument_group("Options")
        options_group.add_argument(
            "--macos-use-bdaddr",
            "-m",
            action="store_true",
            help="use real MAC addresses on macOS (recommended)",
        )
        options_group.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            help="enable verbose output with RSSI and distance details",
        )
        options_group.add_argument(
            "--file-logging",
            "-f",
            action="store_true",
            help="enable logging to file (only with --start or --daemon)",
        )
        options_group.add_argument(
            "--daemon", action="store_true", help=argparse.SUPPRESS
        )
        return parser


# ==============================================================================
# SCRIPT ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    parser = Application.setup_parser()
    args = parser.parse_args()

    if args.scanner is not None and not (5 <= args.scanner <= 60):
        parser.error("Scanner duration must be between 5 and 60 seconds.")

    is_service_command = args.start or args.stop or args.restart or args.status
    is_mode_command = (
        args.scanner is not None or args.target_mac or args.target_uuid
    )

    if not is_service_command and not is_mode_command:
        parser.error(
            "error: one of the following arguments is required: "
            "--scanner/-s, --target-mac/-tm, --target-uuid/-tu, "
            "--start, --stop, --restart, --status"
        )

    try:
        app = Application(args)
        asyncio.run(app.run())
    except KeyboardInterrupt:
        if not (args.start or args.restart):
            print(
                f"\n{Colors.YELLOW}{'─' * 50}{Colors.RESET}\n"
                f"{Colors.YELLOW}⚠{Colors.RESET}  {Colors.BOLD}"
                f"Monitoring Interrupted{Colors.RESET}\n   Reason:    "
                f"User requested stop (Ctrl+C)\n   Status:    "
                f"{Colors.GREEN}✓{Colors.RESET} Gracefully terminated\n"
                f"{Colors.YELLOW}{'─' * 50}{Colors.RESET}\n"
            )
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}✗ FATAL ERROR:{Colors.RESET} {e}")
        sys.exit(1)
