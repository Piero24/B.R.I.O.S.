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

import statistics
from dotenv import load_dotenv
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

# Load environment variables from a .env file automatically
load_dotenv(".env")

# --- Configuration Constants ---
TARGET_DEVICE_MAC_ADDRESS = os.getenv('TARGET_DEVICE_MAC_ADDRESS')
TARGET_DEVICE_UUID_ADDRESS = os.getenv('TARGET_DEVICE_UUID_ADDRESS')
TARGET_DEVICE_NAME = os.getenv('TARGET_DEVICE_NAME', "Unknown Device Name")
TARGET_DEVICE_TYPE = os.getenv('TARGET_DEVICE_TYPE', 'Unknown Device')

# --- Physics & Monitoring Constants ---
TX_POWER_AT_1M = int(os.getenv('TX_POWER_AT_1M', '-59'))
PATH_LOSS_EXPONENT = float(os.getenv('PATH_LOSS_EXPONENT', '2.8'))
SAMPLE_WINDOW = int(os.getenv('SAMPLE_WINDOW', '12'))
DISTANCE_THRESHOLD_M = float(os.getenv('DISTANCE_THRESHOLD_M', '2.0'))

# --- Daemon/Service Control ---
# The PID file stores the process ID of the running monitor.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(SCRIPT_DIR, ".ble_monitor.pid")
LOG_FILE = os.path.join(SCRIPT_DIR, ".ble_monitor.log")
# -----------------------------

# --- ANSI Color Codes ---
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
# -------------------------

@dataclass
class Flags:
    daemon_mode: bool
    file_logging: bool
    verbose: bool


def _estimate_distance(rssi: float) -> float:
    """Estimates the distance from a device based on RSSI. Uses the 
        Log-Distance Path Loss Model to estimate distance in meters.
        d = 10 ^ ((𝑃ₜₓ - 𝑃ᵣₓ) / (10 * n))

    Args:
        rssi (float): The received signal strength indicator in dBm.

    Returns:
        float: Estimated distance in meters. Returns -1.0 if RSSI is 0.
    """
    if rssi == 0:
        return -1.0
    return 10 ** ((TX_POWER_AT_1M - rssi) / (10 * PATH_LOSS_EXPONENT))


def _smooth_rssi(buffer: list[int]) -> float | None:
    """Calculates the mean of the RSSI values in the buffer.

    Args:
        buffer (list[int]): List of RSSI values.

    Returns:
        float | None: Mean RSSI value, or None if buffer is empty.
    """
    if not buffer:
        return None
    return statistics.mean(buffer)


def _summary_scanner_mode(
    duration: int = -1, 
    use_bdaddr: bool = False, 
    verbose: bool = False,
) -> None:
    """Prints the initial summary of the monitoring configuration.

    Args:
        duration (int): Duration to scan in seconds.
        use_bdaddr (bool): Whether to use BD_ADDR (MAC) or UUIDs on macOS.
        verbose (bool): Whether to show detailed RSSI and distance info.
    """
    print(f"\n{Colors.BOLD}BLE Device Scanner{Colors.RESET}")
    print("─" * 70)
    print(f"Duration:   {duration} seconds")
    _bd_addr = (
        "BD_ADDR (MAC addresses)" 
        if use_bdaddr 
        else "UUIDs (macOS privacy mode)"
    )
    print(f"Mode:       {_bd_addr}")
    print(f"Verbose:    Enabled (showing RSSI and distance estimates)")
    print(f"TX Power:   {TX_POWER_AT_1M} dBm @ 1m (for distance calculation)")
    print(f"Path Loss:  {PATH_LOSS_EXPONENT} (environmental factor)")
    print("─" * 70)
    print(f"\n{Colors.GREEN}●{Colors.RESET} Scanning...\n")


def device_list_generator(devices: dict, sort: bool = False) -> list[BLEDevice]:
    """Generates a sorted list of BLEDevice objects from a dictionary.

    Args:
        devices (dict): Dictionary of devices with addresses as keys.
        sort (bool): Whether to sort the devices by address. Defaults to False.

    Returns:
        list[BLEDevice]: Sorted list of BLEDevice objects.
    """
    device_items = devices.items()
    devices_list = [
        (device, adv_data) for address, (device, adv_data) in device_items
    ]
    
    if sort:
        devices_list.sort(
            key=lambda x: x[0].address 
            if hasattr(x[0], 'address') 
            else str(x[0])
        )
    return devices_list


async def run_scanner_mode(
    duration: int, 
    use_bdaddr: bool, 
    verbose: bool
) -> None:
    """Scans for BLE devices for a specified duration and prints them.

    Args:
        duration (int): Duration to scan in seconds.
        use_bdaddr (bool): Whether to use BD_ADDR (MAC) or UUIDs on macOS.
        verbose (bool): Whether to show detailed RSSI and distance info.
    """
    _summary_scanner_mode(duration, use_bdaddr, verbose)
    # The `cb` dictionary is used to pass backend-specific arguments.
    # Here, we tell the macOS backend (CoreBluetooth) whether to use BD_ADDR.
    scanner_kwargs = {"cb": {"use_bdaddr": use_bdaddr}}
    
    # Always get devices with RSSI info (needed for both modes)
    # return_adv=True returns dict where values are tuples of (BLEDevice, 
    # AdvertisementData)
    devices_and_adv = await BleakScanner.discover(
        timeout=duration, 
        return_adv=True, 
        **scanner_kwargs
    )
    
    devices_list = device_list_generator(devices_and_adv, sort=True)
    
    print(
        f"\n{Colors.BOLD}Scan Results{Colors.RESET} ({len(devices_list)} "
        f"device{'s' if len(devices_list) != 1 else ''} found)"
    )
    print("─" * 70)
    
    if not devices_list:
        print(f"{Colors.YELLOW}No devices found{Colors.RESET}")
        return

    for i, (device, adv_data) in enumerate(devices_list, 1):
        address = device.address if hasattr(device, 'address') else str(device)
        device_name = device.name if hasattr(device, 'name') else None
        name_display = (
            device_name if device_name 
            else f"{Colors.YELLOW}(Unknown){Colors.RESET}"
        )
        
        # Ensure proper alignment
        visible_length = len(device_name) if device_name else 9
        padding = 30 - visible_length
        
        # Get RSSI and calculate distance
        rssi = adv_data.rssi if hasattr(adv_data, 'rssi') else -100
        distance = _estimate_distance(rssi)
        signal_color = (
            Colors.GREEN 
            if rssi > -50 else Colors.YELLOW 
            if rssi > -70 else Colors.RED
        )
        
        print(
            f"{i:2d}. {name_display}{' ' * padding} │ {address} │ "
            f"{signal_color}{rssi:4d} dBm{Colors.RESET} │ ~{distance:5.2f}m"
        )


def _summary_monitor_mode(
    flags: Flags,
    use_bdaddr: bool = False,
    target_address: str = ""
) -> None:
    """
    """
    if flags.daemon_mode:
        return
    
    print(f"\n{Colors.BOLD}Starting BLE Monitor{Colors.RESET}")
    print("─" * 50)
    print(f"Target:     {TARGET_DEVICE_NAME} ({TARGET_DEVICE_TYPE})")
    print(f"Address:    {target_address}")
    print(f"Threshold:  {DISTANCE_THRESHOLD_M}m")
    print(f"TX Power:   {TX_POWER_AT_1M} dBm @ 1m")
    print(f"Path Loss:  {PATH_LOSS_EXPONENT}")
    print(f"Samples:    {SAMPLE_WINDOW} readings")
    if use_bdaddr: 
        print(f"Mode:       {Colors.BLUE}BD_ADDR (MAC){Colors.RESET}")
    print("─" * 50)
    
    if flags.verbose and flags.file_logging:
        print(f"Output:     {Colors.GREEN}Terminal + File{Colors.RESET}")
        print(f"Log file:   {LOG_FILE}")
    elif flags.verbose:
        print(f"Output:     {Colors.GREEN}Terminal only{Colors.RESET}")
    elif flags.file_logging:
        print(f"Output:     {Colors.GREEN}File only{Colors.RESET}")
        print(f"Log file:   {LOG_FILE}")
    
    print(
        f"\n{Colors.GREEN}●{Colors.RESET} Monitoring active - "
        f"Press Ctrl+C to stop\n"
    )


def get_pid_status() -> tuple[int | None, bool]:
    """Checks for the PID file and if the process is running.

    Returns:
        tuple[int | None, bool]: (PID, is_running)
    """
    if not os.path.exists(PID_FILE): return None, False
    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
    except (IOError, ValueError): return None, False
    try:
        os.kill(pid, 0)
        return pid, True
    except OSError: return pid, False


def handle_stop() -> None:
    """Stops the monitor if it is running and cleans up PID file."""
    pid, is_running = get_pid_status()
    if not is_running:
        print(f"{Colors.YELLOW}●{Colors.RESET} Monitor is not running")
        if os.path.exists(PID_FILE): os.remove(PID_FILE)
        return
    
    print(f"Stopping monitor process (PID {pid})...")

    try:
        os.kill(pid, signal.SIGTERM)
        print(f"{Colors.GREEN}✓{Colors.RESET} Monitor stopped successfully")
    except OSError: 
        print(f"{Colors.YELLOW}!{Colors.RESET} Process {pid} already stopped")
    finally:
        if os.path.exists(PID_FILE): os.remove(PID_FILE)
        # if os.path.exists(LOG_FILE): os.remove(LOG_FILE)


def _add_flags_to_command(args: argparse.Namespace) -> list[str]:
    """Adds flags to the command list based on the argparse Namespace.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        list[str]: List of command-line flags.
    """
    command = []

    if args.macos_use_bdaddr:
        command.append("-m")
    if args.verbose:
        command.append("-v")
    if args.file_logging:
        command.append("-f")

    return command


def _command_from_args(args: argparse.Namespace) -> list[str]:
    """Reconstructs the command-line invocation from the argparse Namespace.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        list[str]: List of command-line arguments.
    """
    command = [sys.executable, sys.argv[0]]
    
    if args.target_mac:
        if args.target_mac == "USE_DEFAULT":
            command.append("-tm")
        else:
            command.extend(["--target-mac", args.target_mac])
    elif args.target_uuid:
        if args.target_uuid == "USE_DEFAULT":
            command.append("-tu")
        else:
            command.extend(["--target-uuid", args.target_uuid])
    elif args.scanner is not None:
        command.extend(["--scanner", str(args.scanner)])
    
    _flags = _add_flags_to_command(args)
    return command + _flags + ['--daemon']


def _output_redirect(command : list[str], need_logs: bool) -> None:
    """Redirect stdout and stderr to a log file only if file_logging is enabled.
    
    Args:
        command (list[str]): The command to execute as a list of arguments.
        need_logs (bool): Whether file logging is enabled.
    """
    # Discard output if file logging is not enabled
    if not need_logs:
        subprocess.Popen(
            command, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL, 
            start_new_session=True
        )
        return 
    
    with open(LOG_FILE, 'wb') as log:
        # Use unbuffered output for Python
        subprocess.Popen(
            command, 
            stdout=log, 
            stderr=subprocess.STDOUT, 
            start_new_session=True,
            env={**os.environ, 'PYTHONUNBUFFERED': '1'}
            )


def _print_start_status(target_address: str | None) -> None:
    """Prints the status after attempting to start the monitor.

    Args:
        target_address (str | None): The target device address.
    """
    pid, is_running = get_pid_status()

    if not is_running:
        print(f"{Colors.RED}✗{Colors.RESET} Failed to start monitor")
        print(f"Log file:   {LOG_FILE}")
        print("─" * 50 + "\n")
        return 
    
    print(f"{Colors.GREEN}✓{Colors.RESET} Monitor started successfully")
    print(f"PID:        {pid}")
    print("─" * 50)
    print(f"Target:     {TARGET_DEVICE_NAME} ({TARGET_DEVICE_TYPE})")

    if target_address:
        print(f"Address:    {target_address}")
    print(f"Threshold:  {DISTANCE_THRESHOLD_M}m")
    print(f"TX Power:   {TX_POWER_AT_1M} dBm @ 1m")
    print(f"Path Loss:  {PATH_LOSS_EXPONENT}")
    print(f"Samples:    {SAMPLE_WINDOW} readings")

    if args.macos_use_bdaddr:
        print(f"Mode:       {Colors.BLUE}BD_ADDR (MAC){Colors.RESET}")
    else:
        print(f"Mode:       UUID (Privacy Mode)")
    print("─" * 50)

    if args.file_logging:
        print(f"Log file:   {LOG_FILE} {Colors.GREEN}(enabled){Colors.RESET}")
    else:
        print(f"Logging:    Disabled (use -f to enable)")

    print(f"\n{Colors.GREEN}●{Colors.RESET} Monitor running in background")
    print(
        f"Use '{Colors.BOLD}python3 {sys.argv[0]} "
        f"--status{Colors.RESET}' to check status"
    )
    print(
        f"Use '{Colors.BOLD}python3 {sys.argv[0]} "
        f"--stop{Colors.RESET}' to stop\n"
    )


def _determine_target_address(args: argparse.Namespace) -> str | None:
    """Determines the target address based on command-line arguments.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        str | None: The target address or None if not specified.
    """
    target_address = None
    if args.target_mac:
        target_address = (
            TARGET_DEVICE_MAC_ADDRESS if args.target_mac == "USE_DEFAULT" 
            else args.target_mac
        )
        if not args.macos_use_bdaddr:
            args.macos_use_bdaddr = True
    elif args.target_uuid:
        target_address = (
            TARGET_DEVICE_UUID_ADDRESS if args.target_uuid == "USE_DEFAULT" 
            else args.target_uuid
        )
    return target_address
          

def handle_start(args: argparse.Namespace) -> None:
    """Starts the monitor in the background.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    pid, is_running = get_pid_status()
    if is_running:
        print(
            f"{Colors.YELLOW}!{Colors.RESET} "
            f"Monitor is already running (PID {pid})"
        )
        return
    
    command = _command_from_args(args)
    target_address = _determine_target_address(args)
    
    print(f"\n{Colors.BOLD}Starting Background Monitor{Colors.RESET}")
    print("─" * 50)
    if args.verbose:
        print(f"{Colors.BLUE}Command:{Colors.RESET} {' '.join(command)}")
        print("─" * 50)
    
    _output_redirect(command, args.file_logging)
    time.sleep(0.5)
    _print_start_status(target_address)


def _attribute_hex_error() -> None:
    """Handles the specific AttributeError for malformed packets.
        Catch the specific "NoneType has no attribute 'hex'" error.
    """
    print(
        f"\n{Colors.YELLOW}{'─' * 60}{Colors.RESET}\n{Colors.YELLOW}DEBUG: "
        f"Malformed Packet Ignored{Colors.RESET}\n{Colors.GREY}   └─> Cause: "
        f"This is expected when the host Mac is locked or sleeping."
        f"{Colors.RESET}\n{Colors.YELLOW}{'─' * 60}{Colors.RESET}\n"
    )


def _extra_exception_error() -> None:
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


def _process_signal(
    rssi_buffer: list[int], 
    current_rssi: int
) -> tuple[float | None, float | None]:
        """Updates the signal buffer and calculates smoothed RSSI and distance.
        
        This function encapsulates the core signal processing logic.

        Args:
            rssi_buffer (list[int]): The buffer storing recent RSSI values.
            current_rssi (int): The latest RSSI reading.

        Returns:
            A tuple containing (smoothed_rssi, distance_in_meters).
            Returns (None, None) if the buffer is not yet full.
        """
        rssi_buffer.append(current_rssi)
        if len(rssi_buffer) < SAMPLE_WINDOW:
            return None, None
            
        smoothed_rssi = _smooth_rssi(rssi_buffer)
        if smoothed_rssi is None:
            return None, None
            
        distance_m = _estimate_distance(smoothed_rssi)
        return smoothed_rssi, distance_m





def _lock_macbook() -> str:
    """Executes system commands to immediately lock the macOS screen.

    Returns:
        A status string indicating success or failure.
    """
    try:
        # First, ensure password is required immediately after sleep
        subprocess.run([
            'defaults', 'write', 'com.apple.screensaver', 
            'askForPassword', '-int', '1'
        ], check=True, capture_output=True)

        subprocess.run([
            'defaults', 'write', 'com.apple.screensaver', 
            'askForPasswordDelay', '-int', '0'
        ], check=True, capture_output=True)
        
        # Now lock the screen by putting display to sleep
        subprocess.run(
            ['pmset', 'displaysleepnow'], 
            check=True, capture_output=True
        )
        return "🔒 MacBook locked (password required)"
    
    except Exception as e:
        return f"⚠️  Failed to lock MacBook: {e}"
        





















class DeviceMonitor:
    """
    """
    def __init__(self, target_address: str, use_bdaddr: bool, flags: 'Flags'):
        # Configuration
        self.target_address = target_address
        self.use_bdaddr = use_bdaddr
        self.flags = flags

        # State
        self.rssi_buffer: deque[int] = deque(maxlen=SAMPLE_WINDOW)
        self.alert_triggered: bool = False
        self.log_file = None

        # Components
        self.scanner = BleakScanner(
            detection_callback=self._detection_callback,
            cb={"use_bdaddr": self.use_bdaddr}
        )
    

    def _log_status(
        self,
        current_rssi: int, 
        smoothed_rssi: float, 
        distance_m: float
    ) -> None:
        """
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
                signal_strength = "Strong" if smoothed_rssi > -50 else "Medium" if smoothed_rssi > -70 else "Weak"
                signal_color = Colors.GREEN if smoothed_rssi > -50 else Colors.YELLOW if smoothed_rssi > -70 else Colors.RED
                print(
                    f"{Colors.BLUE}[{timestamp}]{Colors.RESET} RSSI: {current_rssi:4d} dBm → "
                    f"Smoothed: {smoothed_rssi:5.1f} dBm │ "
                    f"Distance: {Colors.BOLD}{distance_m:5.2f}m{Colors.RESET} │ "
                    f"Signal: {signal_color}{signal_strength}{Colors.RESET}"
                )
            
            # Write to log file if file_logging is enabled (regardless of verbose)
            if self.flags.file_logging and self.log_file:
                self.log_file.write(log_message + "\n")
                self.log_file.flush()
    

    def _trigger_out_of_range_alert(self, distance_m: float) -> bool:
        """
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        lock_status = _lock_macbook()
        alert_msg = f"⚠️  ALERT: Device '{TARGET_DEVICE_NAME}' is far away! (~{distance_m:.2f} m) - {lock_status}"
        
        if self.flags.daemon_mode:
            print(alert_msg)
            sys.stdout.flush()  # Force write to file immediately
        else:
            print(
                f"\n{Colors.RED}{'─' * 50}{Colors.RESET}\n"
                f"{Colors.RED}⚠{Colors.RESET}  {Colors.BOLD}ALERT: Device moved out of range{Colors.RESET}\n"
                f"   Device:    {TARGET_DEVICE_NAME}\n"
                f"   Distance:  ~{distance_m:.2f}m (threshold: {DISTANCE_THRESHOLD_M}m)\n"
                f"   Time:      {timestamp}\n"
                f"   Action:    {lock_status}\n"
                f"{Colors.RED}{'─' * 50}{Colors.RESET}\n"
            )
            # Write to log file if enabled
            if self.flags.file_logging and self.log_file:
                self.log_file.write(f"[{timestamp}] {alert_msg}\n")
                self.log_file.flush()
        return True


    def _trigger_in_range_alert(self, distance_m: float) -> bool:
        """
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        back_msg_plain = f"STATUS: Device '{TARGET_DEVICE_NAME}' is back in range. (~{distance_m:.2f} m)"

        if self.flags.daemon_mode:
            print(f"[{timestamp}] {back_msg_plain}")
            sys.stdout.flush()
        else:
            back_msg_rich = (
                f"\n{Colors.GREEN}{'─' * 60}{Colors.RESET}\n"
                f"{Colors.GREEN}✓{Colors.RESET}  {Colors.BOLD}Device Back in Range{Colors.RESET}\n"
                f"   Device:    {TARGET_DEVICE_NAME}\n"
                f"   Distance:  ~{distance_m:.2f}m (Threshold: {DISTANCE_THRESHOLD_M}m)\n"
                f"   Time:      {timestamp}\n"
                f"   Status:    🔓 Ready to unlock MacBook\n"
                f"{Colors.GREEN}{'─' * 60}{Colors.RESET}\n"
            )
            print(back_msg_rich)

            if self.flags.file_logging and self.log_file:
                self.log_file.write(f"[{timestamp}] {back_msg_plain}\n")
                self.log_file.flush()

        return False
    

    def _detection_callback(self, device: BLEDevice, adv_data: AdvertisementData) -> None:
        """
        """
        try:
            if device.address != self.target_address:
                return
            
            current_rssi = int(adv_data.rssi)

        except (AttributeError, TypeError):
            if self.flags.verbose: _attribute_hex_error()
            return
        
        except Exception as e:
            if self.flags.verbose: _extra_exception_error(e)
            return

        smoothed_rssi, distance_m = _process_signal(self.rssi_buffer, current_rssi)
        if distance_m is None or smoothed_rssi is None:
            return

        self._log_status(current_rssi, smoothed_rssi, distance_m)

        if distance_m > DISTANCE_THRESHOLD_M and not self.alert_triggered:
            self.alert_triggered = self._trigger_out_of_range_alert(distance_m)
        elif distance_m <= DISTANCE_THRESHOLD_M and self.alert_triggered:
            self.alert_triggered = self._trigger_in_range_alert(distance_m)

    def _setup_logging(self) -> None:
        """
        """
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
        """
        """
        self._setup_logging()
        _summary_monitor_mode(self.flags, self.use_bdaddr, self.target_address)
        
        try:
            await self.scanner.start()
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
                print(f"{Colors.GREEN}✓{Colors.RESET} Monitoring stopped.\n")


async def run_monitor_mode(
    target_address: str, 
    use_bdaddr: bool, 
    verbose: bool, 
    daemon_mode: bool,
    file_logging: bool = False
) -> None:
    """
    """
    flags = Flags(daemon_mode, file_logging, verbose)

    if flags.daemon_mode:
        # --- Daemon Setup ---
        # This logic is specific to the application environment, not the monitor itself.
        try:
            with open(PID_FILE, "w") as f:
                f.write(str(os.getpid()))
        except IOError as e:
            sys.exit(
                f"DAEMON ERROR: Could not write PID file to {PID_FILE}. "
                f"Error: {e}"
            )

    # --- Create and Run the Monitor ---
    monitor = DeviceMonitor(target_address, use_bdaddr, flags)
    try:
        await monitor.run()
    finally:
        # --- Daemon Teardown ---
        if flags.daemon_mode and os.path.exists(PID_FILE):
            os.remove(PID_FILE)
            

async def main(args: argparse.Namespace) -> None:
    """Main function to route to the correct mode based on arguments."""
    target_address = _determine_target_address(args)

    if args.stop:
        handle_stop()
        return
    
    if args.restart:
        print(f"\n{Colors.BOLD}Restarting monitor...{Colors.RESET}")
        handle_stop()
        await asyncio.sleep(1)
        handle_start(args)
        return
    
    if args.status:
        pid, is_running = get_pid_status()
        print(f"\n{Colors.BOLD}BLE Monitor Status{Colors.RESET}")
        print("─" * 50)
        
        if is_running:
            print(f"Status:     {Colors.GREEN}● RUNNING{Colors.RESET}")
            print(f"PID:        {pid}")
            
            # Get process uptime
            try:
                import subprocess as sp
                result = sp.run(['ps', '-p', str(pid), '-o', 'etime='], 
                              capture_output=True, text=True)
                uptime = result.stdout.strip()
                if uptime:
                    print(f"Uptime:     {uptime}")
            except: pass
            
            # Show target device info
            print(f"Target:     {TARGET_DEVICE_NAME}")
            print(f"Address:    {TARGET_DEVICE_MAC_ADDRESS}")
            print(f"Threshold:  {DISTANCE_THRESHOLD_M}m")
            
            # Check if log file exists and show last few lines
            if os.path.exists(LOG_FILE):
                print(f"\nLog file:   {LOG_FILE}")
                try:
                    with open(LOG_FILE, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            recent = lines[-3:] if len(lines) >= 3 else lines
                            print(f"\nRecent activity:")
                            for line in recent:
                                print(f"  {line.rstrip()}")
                except: pass
        else:
            print(f"Status:     {Colors.RED}● STOPPED{Colors.RESET}")
            print(f"PID:        N/A")
        
        print("─" * 50 + "\n")
        return
    
    if args.scanner is not None:
        duration = args.scanner
        await run_scanner_mode(duration, args.macos_use_bdaddr, args.verbose)
        return

    # Target address was already set at the beginning of main()
    if target_address:
        if args.start:
            handle_start(args)
        else:
            # Use daemon_mode=True if --daemon flag is set (for background processes)
            await run_monitor_mode(
                target_address, 
                args.macos_use_bdaddr, 
                args.verbose, 
                daemon_mode=args.daemon,
                file_logging=args.file_logging
            )
        return

    print(f"{Colors.RED}✗{Colors.RESET} No operating mode selected")
    print(f"Run '{sys.argv[0]} --help' for usage information")






if __name__ == "__main__":
    help_epilog = """
DESCRIPTION:
  A professional BLE (Bluetooth Low Energy) monitoring tool that provides 
  real-time device tracking and proximity alerts based on RSSI signal strength.

OPERATING MODES:
  Scanner Mode    Discover nearby BLE devices and display their addresses
  Monitor Mode    Track a specific device and alert on distance changes
  Service Mode    Run monitor as a background daemon process

EXAMPLES:
  Discover devices (recommended for macOS):
    $ python3 main.py --scanner 10 -m

  Monitor device in foreground with verbose output:
    $ python3 main.py --target-mac -v

  Start monitoring as background service with file logging:
    $ python3 main.py --target-mac -v -f --start
    $ python3 main.py --status
    $ python3 main.py --stop

  Monitor specific device by MAC address:
    $ python3 main.py --target-mac "XX:XX:XX:XX:XX:XX" -m -v

NOTES:
  • On macOS, use -m flag to see real MAC addresses instead of UUIDs
  • Use -f flag to enable logging to .ble_monitor.log in project directory
  • Use -v flag for verbose RSSI/distance output
  • Default distance threshold is 2.0 meters
  • Requires Bluetooth to be enabled

For more information, visit: https://github.com/Piero24/Bleissant
"""
    parser = argparse.ArgumentParser(
        description="BLE device proximity monitor with distance-based alerting",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=help_epilog
    )


    # --- Service Control Group ---
    service_group = parser.add_argument_group("Service Control")
    service_exclusive = service_group.add_mutually_exclusive_group()
    service_exclusive.add_argument(
        "--start", 
        action="store_true", 
        help="start monitor as background daemon"
    )
    service_exclusive.add_argument(
        "--stop", 
        action="store_true", 
        help="stop background daemon"
    )
    service_exclusive.add_argument(
        "--restart", 
        action="store_true", 
        help="restart background daemon"
    )
    service_exclusive.add_argument(
        "--status", 
        action="store_true", 
        help="show daemon status and statistics"
    )
    
    # --- Operating Modes ---
    mode_group = parser.add_argument_group("Operating Modes")
    mode_exclusive = mode_group.add_mutually_exclusive_group(required=False)

    mode_exclusive.add_argument(
        "--scanner", "-s",
        nargs="?",
        const=15,
        type=int,
        metavar="SECONDS",
        help="discover nearby BLE devices (default: 15s, range: 5-60s)"
    )
    mode_exclusive.add_argument(
        "--target-mac", "-tm",
        nargs="?",
        const="USE_DEFAULT",
        type=str,
        metavar="ADDRESS",
        help="monitor device by MAC address (recommended)"
    )
    mode_exclusive.add_argument(
        "--target-uuid", "-tu",
        nargs="?",
        const="USE_DEFAULT",
        type=str,
        metavar="UUID",
        help="monitor device by UUID (macOS privacy mode)"
    )

    # --- Options ---
    options_group = parser.add_argument_group("Options")
    options_group.add_argument(
        "--macos-use-bdaddr", "-m",
        action="store_true",
        help="use real MAC addresses on macOS (recommended)"
    )
    options_group.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="enable verbose output with RSSI and distance details"
    )
    options_group.add_argument(
        "--file-logging", "-f",
        action="store_true",
        help="enable logging to file (only with --start or --daemon)"
    )
    options_group.add_argument(
        "--daemon",
        action="store_true",
        help=argparse.SUPPRESS  # Internal flag
    )

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
        asyncio.run(main(args))
    except KeyboardInterrupt:
        if not (args.start or args.restart):
            print(
                f"\n{Colors.YELLOW}{'─' * 50}{Colors.RESET}\n"
                f"{Colors.YELLOW}⚠{Colors.RESET}  {Colors.BOLD}Monitoring Interrupted{Colors.RESET}\n"
                f"   Reason:    User requested stop (Ctrl+C)\n"
                f"   Status:    {Colors.GREEN}✓{Colors.RESET} Gracefully terminated\n"
                f"{Colors.YELLOW}{'─' * 50}{Colors.RESET}\n"
            )
            sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.RESET} Fatal error: {e}")
        sys.exit(1)