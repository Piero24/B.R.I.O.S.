import os
import sys
import time
import signal
import argparse
import subprocess
from typing import Optional, Tuple, List

from .utils import PID_FILE, LOG_FILE, Colors, Flags, __app_name__, determine_target_address
from .config import (
    TARGET_DEVICE_NAME,
    TARGET_DEVICE_MAC_ADDRESS,
    TARGET_DEVICE_TYPE,
    DISTANCE_THRESHOLD_M,
    SAMPLE_WINDOW,
    TX_POWER_AT_1M,
    PATH_LOSS_EXPONENT,
)


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
            args: The parsed command-line arguments.
        """
        self.args = args

    def _get_pid_status(self) -> Tuple[Optional[int], bool]:
        """Checks for the PID file and determines if the process is running.

        Reads the PID from the PID file and checks if a process with that PID
        is currently active.

        Returns:
            A tuple containing (pid, is_running). The pid is None if the file
            does not exist.
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
        if sys.argv[0].endswith("brios"):
            # If running via 'brios' entry point, use it directly
            command = [sys.argv[0]]
        else:
            # Fallback to python + script path
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
        target_address = determine_target_address(self.args)

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
