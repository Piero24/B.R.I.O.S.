import os
import sys
import signal
import asyncio
import argparse
import subprocess
from datetime import datetime

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


def estimate_distance(rssi: float) -> float:
    """Estimates the distance from a device based on RSSI."""
    if rssi == 0:
        return -1.0
    return 10 ** ((TX_POWER_AT_1M - rssi) / (10 * PATH_LOSS_EXPONENT))


def smooth_rssi(buffer: list[int]) -> float | None:
    """Calculates the mean of the RSSI values in the buffer."""
    if not buffer:
        return None
    return statistics.mean(buffer)


async def run_scanner_mode(
    duration: int, 
    use_bdaddr: bool, 
    verbose: bool
) -> None:
    """
    Scans for BLE devices for a specified duration and prints them.
    """
    print(f"\n{Colors.BOLD}BLE Device Scanner{Colors.RESET}")
    print("─" * 70)
    print(f"Duration:   {duration} seconds")
    print(f"Mode:       {'BD_ADDR (MAC addresses)' if use_bdaddr else 'UUIDs (macOS privacy mode)'}")
    print(f"Verbose:    Enabled (showing RSSI and distance estimates)")
    print(f"TX Power:   {TX_POWER_AT_1M} dBm @ 1m (for distance calculation)")
    print(f"Path Loss:  {PATH_LOSS_EXPONENT} (environmental factor)")
    print("─" * 70)
    print(f"\n{Colors.GREEN}●{Colors.RESET} Scanning...\n")

    # The `cb` dictionary is used to pass backend-specific arguments.
    # Here, we tell the macOS backend (CoreBluetooth) whether to use BD_ADDR.
    scanner_kwargs = {"cb": {"use_bdaddr": use_bdaddr}}
    
    # Always get devices with RSSI info (needed for both modes)
    # return_adv=True returns dict where values are tuples of (BLEDevice, AdvertisementData)
    devices_and_adv = await BleakScanner.discover(timeout=duration, return_adv=True, **scanner_kwargs)
    
    # Convert to list and sort
    devices_list = []
    for address, (device, adv_data) in devices_and_adv.items():
        devices_list.append((device, adv_data))
    
    # Sort by address
    devices_list.sort(key=lambda x: x[0].address if hasattr(x[0], 'address') else str(x[0]))

    print(f"\n{Colors.BOLD}Scan Results{Colors.RESET} ({len(devices_list)} device{'s' if len(devices_list) != 1 else ''} found)")
    print("─" * 70)
    
    if not devices_list:
        print(f"{Colors.YELLOW}No devices found{Colors.RESET}")
    else:
        for i, (device, adv_data) in enumerate(devices_list, 1):
            # Get device info
            address = device.address if hasattr(device, 'address') else str(device)
            device_name = device.name if hasattr(device, 'name') else None
            name_display = device_name if device_name else f"{Colors.YELLOW}(Unknown){Colors.RESET}"
            
            # Ensure proper alignment
            visible_length = len(device_name) if device_name else 9
            padding = 30 - visible_length
            
            # Get RSSI and calculate distance
            rssi = adv_data.rssi if hasattr(adv_data, 'rssi') else -100
            distance = estimate_distance(rssi)
            signal_color = Colors.GREEN if rssi > -50 else Colors.YELLOW if rssi > -70 else Colors.RED
            
            print(
                f"{i:2d}. {name_display}{' ' * padding} │ {address} │ "
                f"{signal_color}{rssi:4d} dBm{Colors.RESET} │ ~{distance:5.2f}m"
            )


async def run_monitor_mode(
    target_address: str, 
    use_bdaddr: bool, 
    verbose: bool, 
    daemon_mode: bool,
    file_logging: bool = False
) -> None:
    """Continuously monitors a single target device for distance."""
    if daemon_mode:
        try:
            with open(PID_FILE, "w") as f:
                f.write(str(os.getpid()))
        except IOError as e:
            sys.exit(f"DAEMON ERROR: Could not write PID file to {PID_FILE}. Error: {e}")
            return

    # Open log file if file logging is enabled
    log_file = None
    if file_logging:
        try:
            log_file = open(LOG_FILE, "a")  # Append mode
        except IOError as e:
            print(f"{Colors.YELLOW}Warning:{Colors.RESET} Could not open log file: {e}")
            file_logging = False

    rssi_buffer: list[int] = []
    alert_triggered = False

    if not daemon_mode:
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
        
        # Show logging configuration
        if verbose and file_logging:
            print(f"Output:     {Colors.GREEN}Terminal + File{Colors.RESET}")
            print(f"Log file:   {LOG_FILE}")
        elif verbose:
            print(f"Output:     {Colors.GREEN}Terminal only{Colors.RESET}")
        elif file_logging:
            print(f"Output:     {Colors.GREEN}File only{Colors.RESET}")
            print(f"Log file:   {LOG_FILE}")
        
        print(f"\n{Colors.GREEN}●{Colors.RESET} Monitoring active - Press Ctrl+C to stop\n")

    def detection_callback(
        device: BLEDevice, 
        adv_data: AdvertisementData
    ) -> None:
        
        nonlocal alert_triggered, rssi_buffer, log_file

        if device.address != target_address:
            return
        
        try:
            current_rssi = int(adv_data.rssi)
            
            # Always get timestamp for logging and alerts
            timestamp = datetime.now().strftime("%H:%M:%S")
                
            rssi_buffer.append(current_rssi)
            if len(rssi_buffer) > SAMPLE_WINDOW:
                rssi_buffer.pop(0)

            smoothed_rssi = smooth_rssi(rssi_buffer)
            if smoothed_rssi is None:
                return 
            
            distance_m = estimate_distance(smoothed_rssi)

            # Log details based on verbose and file_logging flags
            # -v only: terminal output
            # -f only: file output
            # -v -f: both terminal and file
            if verbose or file_logging:
                log_message = f"[{timestamp}] RSSI: {current_rssi:4d} dBm → Smoothed: {smoothed_rssi:5.1f} dBm │ Distance: {distance_m:5.2f}m"
                
                if daemon_mode:
                    # In daemon mode, only print if file_logging is enabled (goes to log file via stdout redirect)
                    if file_logging:
                        print(log_message)
                        sys.stdout.flush()  # Force write to file immediately
                else:
                    # In foreground mode
                    if verbose:
                        # Show fancy colored output to console
                        signal_strength = "Strong" if smoothed_rssi > -50 else "Medium" if smoothed_rssi > -70 else "Weak"
                        signal_color = Colors.GREEN if smoothed_rssi > -50 else Colors.YELLOW if smoothed_rssi > -70 else Colors.RED
                        print(
                            f"{Colors.BLUE}[{timestamp}]{Colors.RESET} RSSI: {current_rssi:4d} dBm → "
                            f"Smoothed: {smoothed_rssi:5.1f} dBm │ "
                            f"Distance: {Colors.BOLD}{distance_m:5.2f}m{Colors.RESET} │ "
                            f"Signal: {signal_color}{signal_strength}{Colors.RESET}"
                        )
                    
                    # Write to log file if file_logging is enabled (regardless of verbose)
                    if file_logging and log_file:
                        log_file.write(log_message + "\n")
                        log_file.flush()

            if distance_m > DISTANCE_THRESHOLD_M and not alert_triggered:
                # Lock the MacBook when device is too far - requires password to unlock
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
                    subprocess.run(['pmset', 'displaysleepnow'], check=True, capture_output=True)
                    lock_status = "🔒 MacBook locked (password required)"
                except Exception as e:
                    lock_status = f"⚠️  Failed to lock MacBook: {e}"
                
                alert_msg = f"⚠️  ALERT: Device '{TARGET_DEVICE_NAME}' is far away! (~{distance_m:.2f} m) - {lock_status}"
                
                if daemon_mode:
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
                    if file_logging and log_file:
                        log_file.write(f"[{timestamp}] {alert_msg}\n")
                        log_file.flush()
                alert_triggered = True

            elif distance_m <= DISTANCE_THRESHOLD_M and alert_triggered:
                back_msg = f"✅  Device '{TARGET_DEVICE_NAME}' is back in range. (~{distance_m:.2f} m)"
                
                if daemon_mode:
                    print(back_msg)
                    sys.stdout.flush()  # Force write to file immediately
                else:
                    print(
                        f"\n{Colors.GREEN}{'─' * 50}{Colors.RESET}\n"
                        f"{Colors.GREEN}✓{Colors.RESET}  {Colors.BOLD}Device back in range{Colors.RESET}\n"
                        f"   Device:    {TARGET_DEVICE_NAME}\n"
                        f"   Distance:  ~{distance_m:.2f}m (threshold: {DISTANCE_THRESHOLD_M}m)\n"
                        f"   Time:      {timestamp}\n"
                        f"   Status:    🔓 Ready to unlock MacBook\n"
                        f"{Colors.GREEN}{'─' * 50}{Colors.RESET}\n"
                    )
                    # Write to log file if enabled
                    if file_logging and log_file:
                        log_file.write(f"[{timestamp}] {back_msg}\n")
                        log_file.flush()
                alert_triggered = False

        except AttributeError:
            # This will catch the specific "NoneType has no attribute 'hex'" error.
            if verbose:
                print(
                    f"\n{Colors.YELLOW}{'─' * 60}{Colors.RESET}\n"
                    f"{Colors.YELLOW}DEBUG: Malformed Packet Ignored{Colors.RESET}\n"
                    f"{Colors.GREY}   └─> Cause: This is expected when the host Mac is locked or sleeping.{Colors.RESET}\n"
                    f"{Colors.YELLOW}{'─' * 60}{Colors.RESET}\n"
                )
        except Exception as e:
            # Catch any other unexpected errors to keep the scanner alive.
            if verbose:
                print(
                    f"\n{Colors.RED}{'─' * 60}{Colors.RESET}\n"
                    f"{Colors.RED}CRITICAL: Unexpected Callback Error{Colors.RESET}\n"
                    f"{Colors.GREY}   An error was caught, but the scanner will continue to run.{Colors.RESET}\n"
                    f"   └─> {Colors.BOLD}Error Details:{Colors.RESET} {e}\n"
                    f"{Colors.RED}{'─' * 60}{Colors.RESET}\n"
                )

    scanner = BleakScanner(
        detection_callback=detection_callback, 
        cb={"use_bdaddr": use_bdaddr}
    )
    
    try:
        await scanner.start()
        while True:
            await asyncio.sleep(1.0)
    except Exception as e:
        if daemon_mode:
            print(f"ERROR: Failed to start the scanner. Details: {e}")
        else:
            print(
                f"\n{Colors.RED}✗{Colors.RESET} {Colors.BOLD}Error:{Colors.RESET} "
                f"Failed to start the scanner.\n"
                f"  Please ensure your Bluetooth adapter is enabled.\n"
                f"  Details: {e}\n"
            )
    finally:
        if verbose and not daemon_mode: 
            print(f"\n{Colors.YELLOW}Stopping scanner...{Colors.RESET}")
        await scanner.stop()
        
        # Close log file if it was opened
        if file_logging and log_file:
            log_file.close()
            
        if daemon_mode and os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        if not daemon_mode:
            print(f"{Colors.GREEN}✓{Colors.RESET} Monitoring stopped.\n")


def get_pid_status() -> tuple[int | None, bool]:
    """Checks for the PID file and if the process is running."""
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
    """Stops the monitor if it is running."""
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

def handle_start(args) -> None:
    """Starts the monitor in the background."""
    pid, is_running = get_pid_status()
    if is_running:
        print(f"{Colors.YELLOW}!{Colors.RESET} Monitor is already running (PID {pid})")
        return

    # Reconstruct command from args object to ensure all flags are preserved
    command = [sys.executable, sys.argv[0]]
    
    # Add target mode
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
    
    # Add flags
    if args.macos_use_bdaddr:
        command.append("-m")
    if args.verbose:
        command.append("-v")
    if args.file_logging:
        command.append("-f")
    
    # Add the --daemon flag to tell the subprocess it's running in daemon mode
    command.append('--daemon')
    
    # Determine target address for display
    target_address = None
    if args.target_mac:
        target_address = (
            TARGET_DEVICE_MAC_ADDRESS if args.target_mac == "USE_DEFAULT" 
            else args.target_mac
        )
    elif args.target_uuid:
        target_address = (
            TARGET_DEVICE_UUID_ADDRESS if args.target_uuid == "USE_DEFAULT" 
            else args.target_uuid
        )
    
    print(f"\n{Colors.BOLD}Starting Background Monitor{Colors.RESET}")
    print("─" * 50)
    if args.verbose:
        print(f"{Colors.BLUE}Command:{Colors.RESET} {' '.join(command)}")
        print("─" * 50)
    
    # Redirect stdout and stderr to a log file only if file_logging is enabled
    if args.file_logging:
        with open(LOG_FILE, 'wb') as log:
            # Use unbuffered output for Python
            subprocess.Popen(
                command, 
                stdout=log, 
                stderr=subprocess.STDOUT, 
                start_new_session=True,
                env={**os.environ, 'PYTHONUNBUFFERED': '1'}
            )
    else:
        # Discard output if file logging is not enabled
        subprocess.Popen(
            command, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL, 
            start_new_session=True
        )
    
    # Give it a moment to start and create PID file
    import time
    time.sleep(0.5)
    
    pid, is_running = get_pid_status()
    if is_running:
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
        print(f"Use '{Colors.BOLD}python3 {sys.argv[0]} --status{Colors.RESET}' to check status")
        print(f"Use '{Colors.BOLD}python3 {sys.argv[0]} --stop{Colors.RESET}' to stop\n")
    else:
        print(f"{Colors.RED}✗{Colors.RESET} Failed to start monitor")
        print(f"Log file:   {LOG_FILE}")
        print("─" * 50 + "\n")


async def main(args: argparse.Namespace) -> None:
    """Main function to route to the correct mode based on arguments."""

    # Process target address and set flags FIRST, before handling service commands
    # This ensures --start and --restart have correct configuration
    target_address = None
    if args.target_mac:
        target_address = (
            TARGET_DEVICE_MAC_ADDRESS if args.target_mac == "USE_DEFAULT" 
            else args.target_mac
        )
        # Automatically enable BD_ADDR mode when using MAC address
        if not args.macos_use_bdaddr:
            args.macos_use_bdaddr = True
    elif args.target_uuid:
        target_address = (
            TARGET_DEVICE_UUID_ADDRESS if args.target_uuid == "USE_DEFAULT" 
            else args.target_uuid
        )

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