from typing import List

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from .utils import Colors, __app_name__, estimate_distance
from .config import TX_POWER_AT_1M, PATH_LOSS_EXPONENT


class DeviceScanner:
    """Performs a one-time BLE device discovery scan.

    This class uses the BleakScanner to perform a scan for nearby BLE devices
    and prints a formatted list of discovered devices along with their RSSI
    and estimated distances.

    Attributes:
        duration: The scan duration in seconds.
        use_bdaddr: Whether to use BD_ADDR (MAC) for identification.
        verbose: Whether to print detailed output.
    """

    def __init__(self, duration: int, use_bdaddr: bool, verbose: bool) -> None:
        """Initializes the DeviceScanner.

        Args:
            duration: The scan duration in seconds.
            use_bdaddr: Whether to use BD_ADDR (MAC) for identification.
            verbose: Whether to print detailed output.
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
            devices: A list of tuples containing BLEDevice instances and their
                corresponding AdvertisementData.
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
            distance = estimate_distance(rssi)
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
