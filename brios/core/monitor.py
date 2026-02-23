import os
import sys
import time
import asyncio
import subprocess
from datetime import datetime
from collections import deque
from typing import Optional, TextIO, Deque, Tuple

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from .utils import (
    Colors,
    __app_name__,
    estimate_distance,
    smooth_rssi,
    LOG_FILE,
)
from . import system

from .config import (
    DISTANCE_THRESHOLD_M,
    GRACE_PERIOD_SECONDS,
    LOCK_LOOP_THRESHOLD,
    LOCK_LOOP_WINDOW,
    LOCK_LOOP_PENALTY,
    TARGET_DEVICE_NAME,
    TARGET_DEVICE_TYPE,
    SAMPLE_WINDOW,
    TX_POWER_AT_1M,
    PATH_LOSS_EXPONENT,
)
from .utils import Flags


class DeviceMonitor:
    """Manages a continuous monitoring session for a single BLE device.

    This class sets up a long-running scan that invokes a callback for each
    advertisement received. It processes the signal strength, calculates
    distance, and triggers alerts based on a defined threshold.

    Attributes:
        target_address: The MAC or UUID address of the target device.
        use_bdaddr: Whether to use BD_ADDR (MAC) for identification.
        flags: Configuration flags for the monitoring session.
        rssi_buffer: A buffer to hold recent RSSI samples (dBm).
        alert_triggered: Indicates if an out-of-range alert is active.
        log_file: The file object for logging output, if any.
        scanner: The Bleak scanner instance for BLE scanning.
        is_handling_lock: True if currently handling a screen lock state.
        last_packet_time: Monotonic timestamp of the last packet received.
        lock_handling_start_time: Timestamp when lock handling began.
        resume_time: Timestamp when monitoring was last resumed.
        lock_history: History of recent lock events to detect loops.
    """

    def __init__(
        self,
        target_address: str,
        use_bdaddr: bool,
        flags: Flags,
    ) -> None:
        """Initializes the DeviceMonitor.

        Args:
            target_address: The MAC or UUID address of the target device.
            use_bdaddr: Whether to use BD_ADDR (MAC) for identification.
            flags: Configuration flags for the monitoring session.
        """
        # Normalize address to uppercase for case-insensitive matching.
        # Different pyobjc / macOS versions can return UUIDs in different
        # cases, causing silent comparison failures.
        self.target_address = target_address.upper()
        self.use_bdaddr = use_bdaddr
        self.flags = flags

        self.rssi_buffer: Deque[int] = deque(maxlen=SAMPLE_WINDOW)
        self.alert_triggered: bool = False
        self.log_file: Optional[TextIO] = None
        self.is_handling_lock: bool = False
        self.last_packet_time: float = time.monotonic()
        self.lock_handling_start_time: float = 0

        # Diagnostic counters for daemon debugging
        self._target_matched: bool = False
        self._callback_count: int = 0
        self._match_count: int = 0
        self._error_count: int = 0

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

        In daemon mode, a plain-text version is written to the log file.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.flags.daemon_mode:
            # In daemon mode, only write to self.log_file (not stdout)
            # to avoid duplicate entries.
            if self.log_file:
                lines = [
                    f"[{timestamp}] ══════════════════════════════════════════",
                    f"[{timestamp}] {__app_name__} Daemon Started",
                    f"[{timestamp}] ──────────────────────────────────────────",
                    f"[{timestamp}] Target:     {TARGET_DEVICE_NAME} ({TARGET_DEVICE_TYPE})",
                    f"[{timestamp}] Address:    {self.target_address}",
                    f"[{timestamp}] Threshold:  {DISTANCE_THRESHOLD_M}m",
                    f"[{timestamp}] TX Power:   {TX_POWER_AT_1M} dBm @ 1m",
                    f"[{timestamp}] Path Loss:  {PATH_LOSS_EXPONENT}",
                    f"[{timestamp}] Samples:    {SAMPLE_WINDOW} readings",
                    f"[{timestamp}] Mode:       {'BD_ADDR (MAC)' if self.use_bdaddr else 'UUID'}",
                    f"[{timestamp}] Log file:   {LOG_FILE}",
                    f"[{timestamp}] PID:        {os.getpid()}",
                    f"[{timestamp}] ──────────────────────────────────────────",
                    f"[{timestamp}] Monitoring active - waiting for device...",
                    f"[{timestamp}] ══════════════════════════════════════════",
                ]
                for line in lines:
                    self.log_file.write(line + "\n")
                self.log_file.flush()
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
        self._callback_count += 1
        is_locked = False

        try:
            # Normalize to uppercase for case-insensitive matching.
            device_addr = device.address.upper() if device.address else ""
            if device_addr != self.target_address:
                return
            current_rssi = int(adv_data.rssi)

        except (AttributeError, TypeError) as exc:
            self._error_count += 1
            self._handle_bleak_error(exc)
            return
        except Exception as e:
            self._error_count += 1
            self._handle_generic_error(e)
            return

        # Log first-time match for daemon diagnostics
        if not self._target_matched:
            self._target_matched = True
            if self.flags.daemon_mode and self.log_file:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.log_file.write(
                    f"[{timestamp}] Target device FOUND - "
                    f"address={device_addr}, rssi={current_rssi}\n"
                )
                self.log_file.flush()
        self._match_count += 1

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
                    print(
                        f"{Colors.YELLOW}Warning: Scanner stop timed out{Colors.RESET}"
                    )
            except Exception as e:
                if self.flags.verbose:
                    print(
                        f"{Colors.YELLOW}Warning: Scanner stop failed: {e}{Colors.RESET}"
                    )

            timestamp = datetime.now().strftime("%H:%M:%S")

            if self.flags.daemon_mode:
                msg = f"[{timestamp}] Screen locked - Scanner paused"
                if self.log_file:
                    self.log_file.write(msg + "\n")
                    self.log_file.flush()
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
            while system.is_screen_locked():
                loop_count += 1

                if not is_waiting:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    is_waiting = True

                    if self.flags.daemon_mode:
                        if self.log_file:
                            self.log_file.write(
                                f"[{timestamp}] "
                                f"Screen still locked - Waiting for unlock\n"
                            )
                            self.log_file.flush()
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
                if self.log_file:
                    self.log_file.write(
                        f"[{timestamp}] Screen unlocked - "
                        f"Reconnecting scanner (locked for {total_time}s)\n"
                    )
                    self.log_file.flush()
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
                        if self.log_file:
                            self.log_file.write(f"[{timestamp}] {msg}\n")
                            self.log_file.flush()
                    else:
                        print(
                            f"\n{Colors.RED}{Colors.BOLD}{msg}{Colors.RESET}\n"
                        )

                    if self.flags.file_logging and self.log_file:
                        self.log_file.write(f"[{timestamp}] {msg}\n")
                        self.log_file.flush()

                    await asyncio.sleep(LOCK_LOOP_PENALTY)
                    self.lock_history.clear()

            # Retry logic for scanner reconnection
            # Recreate scanner instance to ensure fresh connection
            if self.flags.verbose:
                print(
                    f"{Colors.GREY}[Debug] Recreating BleakScanner instance...{Colors.RESET}"
                )

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
                        if self.log_file:
                            self.log_file.write(f"{msg}\n")
                            self.log_file.flush()
                    elif self.flags.verbose:
                        print(f"{Colors.YELLOW}{msg}{Colors.RESET}")

                    if self.flags.file_logging and self.log_file:
                        self.log_file.write(f"{msg}\n")
                        self.log_file.flush()

                    await asyncio.sleep(wait_time)

            timestamp = datetime.now().strftime("%H:%M:%S")
            if self.flags.daemon_mode:
                msg = f"[{timestamp}] Scanner reconnected - Monitoring resumed"
                if self.log_file:
                    self.log_file.write(msg + "\n")
                    self.log_file.flush()
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
                if self.log_file:
                    self.log_file.write(
                        f"[{timestamp}] ERROR: Failed to reconnect scanner - {e}\n"
                    )
                    self.log_file.flush()
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

        smoothed_rssi = smooth_rssi(self.rssi_buffer)
        if smoothed_rssi is None:
            return None, None

        distance_m = estimate_distance(smoothed_rssi)
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
            if self.log_file:
                self.log_file.write(log_message + "\n")
                self.log_file.flush()
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

    def _trigger_out_of_range_alert(self, distance_m: float) -> bool:
        """Handles the out-of-range alert logic.

        Args:
            distance_m (float): The estimated distance in meters.

        Returns:
            bool: True if the MacBook was locked, False otherwise.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        success, lock_status = system.lock_macbook()
        is_locked = success

        alert_msg = (
            f"⚠️  ALERT: Device '{TARGET_DEVICE_NAME}' is far away! "
            f"(~{distance_m:.2f} m) - {lock_status}"
        )

        if self.flags.daemon_mode:
            msg = f"[{timestamp}] {alert_msg}"
            if self.log_file:
                self.log_file.write(msg + "\n")
                self.log_file.flush()

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
            msg = f"[{timestamp}] {back_msg_plain}"
            if self.log_file:
                self.log_file.write(msg + "\n")
                self.log_file.flush()

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

    def _handle_bleak_error(self, exc: Optional[Exception] = None) -> None:
        """Handles the specific AttributeError for malformed packets.
        Catch the specific "NoneType has no attribute 'hex'" error.
        """
        if self.flags.daemon_mode:
            # In daemon mode, stdout is /dev/null. Write to log file.
            if self.log_file:
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.log_file.write(
                    f"[{timestamp}] DEBUG: Malformed packet ignored"
                    f"{f' ({exc})' if exc else ''}\n"
                )
                self.log_file.flush()
        elif self.flags.verbose:
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
        if self.flags.daemon_mode:
            # In daemon mode, stdout is /dev/null. Write to log file.
            if self.log_file:
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.log_file.write(f"[{timestamp}] CALLBACK ERROR: {e}\n")
                self.log_file.flush()
        elif self.flags.verbose:
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

            if self.flags.daemon_mode:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                msg = f"[{timestamp}] Scanner started successfully - listening for BLE advertisements"
                if self.log_file:
                    self.log_file.write(msg + "\n")
                    self.log_file.flush()

            asyncio.create_task(self._watchdog_loop())

            while True:
                await asyncio.sleep(1.0)
        except Exception as e:
            # Handle scanner start failure
            if self.flags.daemon_mode:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                msg = (
                    f"[{timestamp}] DAEMON ERROR: Failed to start scanner: {e}"
                )
                if self.log_file:
                    self.log_file.write(msg + "\n")
                    self.log_file.flush()
                sys.exit(msg)
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
                print(
                    f"{Colors.GREEN}✓{Colors.RESET} {__app_name__} stopped.\n"
                )

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
                    time_since_packet = int(
                        current_time - self.last_packet_time
                    )
                    timestamp = datetime.now().strftime("%H:%M:%S")

                    if self.flags.daemon_mode:
                        msg = (
                            f"[{timestamp}] [Watchdog] Active - "
                            f"Last packet: {time_since_packet}s ago | "
                            f"Callbacks: {self._callback_count} | "
                            f"Target matches: {self._match_count} | "
                            f"Errors: {self._error_count}"
                        )
                        if self.log_file:
                            self.log_file.write(msg + "\n")
                            self.log_file.flush()
                    else:
                        print(
                            f"{Colors.GREY}[{timestamp}] [Watchdog] Active - Last packet: {time_since_packet}s ago{Colors.RESET}"
                        )
                    last_log_time = current_time

                if system.is_screen_locked() and not self.is_handling_lock:
                    # Spawn handler as a task so watchdog keeps running
                    asyncio.create_task(self._handle_screen_lock())

                # Heartbeat check: Restart scanner if no packets received for 120s
                if (
                    current_time - self.last_packet_time > 120
                    and not self.is_handling_lock
                ):
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    msg = "Watchdog: Scanner frozen (no data for 120s) -> Restarting..."
                    if self.flags.daemon_mode:
                        if self.log_file:
                            self.log_file.write(f"[{timestamp}] {msg}\n")
                            self.log_file.flush()
                    elif self.flags.verbose:
                        print(f"{Colors.YELLOW}{msg}{Colors.RESET}")
                    # Spawn handler as a task
                    asyncio.create_task(self._handle_screen_lock())

                # Stuck handler check: If handling lock takes > 60s, force reset
                if self.is_handling_lock and self.lock_handling_start_time > 0:
                    if current_time - self.lock_handling_start_time > 60:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        msg = "Watchdog: Lock handler stuck for >60s -> Forcing reset"
                        if self.flags.daemon_mode:
                            if self.log_file:
                                self.log_file.write(f"[{timestamp}] {msg}\n")
                                self.log_file.flush()
                        elif self.flags.verbose:
                            print(f"{Colors.RED}{msg}{Colors.RESET}")
                        self.is_handling_lock = False
                        self.lock_handling_start_time = 0
                        # We don't call _handle_screen_lock immediately to avoid recursion loop
                        # The next watchdog tick will trigger it if needed (via heartbeat or lock check)

                await asyncio.sleep(2.0)
            except Exception as e:
                if self.flags.daemon_mode:
                    if self.log_file:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        self.log_file.write(
                            f"[{timestamp}] Watchdog error: {e}\n"
                        )
                        self.log_file.flush()
                elif self.flags.verbose:
                    print(f"{Colors.YELLOW}Watchdog error: {e}{Colors.RESET}")
                await asyncio.sleep(5.0)
