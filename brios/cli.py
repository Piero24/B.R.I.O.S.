import os
import sys
import time
import asyncio
import argparse
from typing import Optional

from brios import __version__
from brios.core.utils import (
    Colors,
    Flags,
    apply_robust_bleak_patch,
    __app_name__,
    __app_full_name__,
    PID_FILE,
    LOG_FILE,
    determine_target_address,
)
from brios.core.config import (
    TARGET_DEVICE_MAC_ADDRESS,
    TARGET_DEVICE_UUID_ADDRESS,
    TARGET_DEVICE_NAME,
    TARGET_DEVICE_TYPE,
    TX_POWER_AT_1M,
    PATH_LOSS_EXPONENT,
    SAMPLE_WINDOW,
    DISTANCE_THRESHOLD_M,
    GRACE_PERIOD_SECONDS,
    LOCK_LOOP_THRESHOLD,
    LOCK_LOOP_WINDOW,
    LOCK_LOOP_PENALTY,
)
from brios.core.scanner import DeviceScanner
from brios.core.monitor import DeviceMonitor
from brios.core.service import ServiceManager


# Apply patch immediately
apply_robust_bleak_patch()


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
            args: The parsed command-line arguments.
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
        target_address = determine_target_address(self.args)
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
        • Python 3.9+ required

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


def main() -> None:
    parser = Application.setup_parser()
    args = parser.parse_args()

    if args.scanner is not None and not (5 <= args.scanner <= 60):
        parser.error("Scanner duration must be between 5 and 60 seconds.")

    is_service_command = (
        args.start or args.stop or args.restart or args.status or args.daemon
    )
    is_mode_command = (
        args.scanner is not None or args.target_mac or args.target_uuid
    )

    # If no mode flags are provided, we check if we can default to monitoring
    if not is_mode_command and not is_service_command:
        parser.error(
            "one of the following arguments is required: "
            "--scanner/-s, --target-mac/-tm, --target-uuid/-tu, "
            "--start, --stop, --restart, --status"
        )
    elif not is_mode_command and is_service_command:
        from .core.utils import determine_target_address

        resolved_address = determine_target_address(args)
        if resolved_address:
            args.target_mac = resolved_address

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


if __name__ == "__main__":
    main()
