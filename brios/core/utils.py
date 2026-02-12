import os
import sys
import argparse
import statistics
from dataclasses import dataclass
from typing import Any, Deque, Optional


from .config import (
    TARGET_DEVICE_UUID_ADDRESS,
    TARGET_DEVICE_MAC_ADDRESS,
    PATH_LOSS_EXPONENT,
    TX_POWER_AT_1M,
)

# --- Application Constants ---
__app_name__ = "🥐 B.R.I.O.S."
__app_full_name__ = (
    "Bluetooth Reactive Intelligent Operator for Croissant Safety"
)

SCRIPT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # Point to project root roughly, or user home

# For installed package, we might want to store PID/logs in user home or tmp
# But for now, let's keep it compatible with existing logic or adapt.
# Best practice is ~/.brios/ or similar.
# Let's use user home for logs/pid if installed as package.
HOME_DIR = os.path.expanduser("~/.brios")
if not os.path.exists(HOME_DIR):
    os.makedirs(HOME_DIR, exist_ok=True)

PID_FILE = os.path.join(HOME_DIR, ".ble_monitor.pid")
LOG_FILE = os.path.join(HOME_DIR, ".ble_monitor.log")

# Platform-specific imports
IS_MACOS = sys.platform == "darwin"


# --- Configuration Constants (Defaults) ---
# These are loaded from env in cli.py usually, or we can load here if we want
# global access allowing them to be passed in or set via env vars.
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


def determine_target_address(args: argparse.Namespace) -> Optional[str]:
    """Determines the target address based on command-line arguments.

    Args:
        args: Parsed command-line arguments containing target_mac or target_uuid.

    Returns:
        The target address string if found; otherwise, None.
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


def estimate_distance(
    rssi: float,
    tx_power_at_1m: int = TX_POWER_AT_1M,
    path_loss_exponent: float = PATH_LOSS_EXPONENT,
) -> float:
    """Estimates distance to a device using the Log-Distance Path Loss model.

    Args:
        rssi: The Received Signal Strength Indicator in dBm.
        tx_power_at_1m: The expected RSSI at 1 meter distance (in dBm).
        path_loss_exponent: The path loss exponent, which varies based on the
            environment.

    Returns:
        The estimated distance in meters. Returns -1.0 if the RSSI is 0,
        as this is typically an invalid reading.
    """
    if rssi == 0:
        return -1.0
    return 10 ** ((tx_power_at_1m - rssi) / (10 * path_loss_exponent))


def smooth_rssi(buffer: Deque[int]) -> Optional[float]:
    """Calculates the statistical mean of RSSI values in a buffer.

    This function helps to stabilize the fluctuating RSSI readings by averaging
    a collection of recent samples.

    Args:
        buffer: A deque containing recent RSSI samples (integers).

    Returns:
        The mean RSSI value as a float, or None if the buffer is empty.
    """
    if not buffer:
        return None
    return statistics.mean(buffer)


# --- Monkeypatch for Bleak 1.1.1 Crash ---
# Fixes AttributeError: 'NoneType' object has no attribute 'hex'
def apply_robust_bleak_patch() -> None:
    """Applies a monkeypatch to fix a specific Bleak crash on macOS.

    This function modifies the behavior of `BleakScannerCoreBluetooth.start` to
    handle cases where `retrieveAddressForPeripheral_` returns `None`. This
    commonly occurs on older versions of Bleak (like 1.1.1) or specific macOS
    environments when the system fails to resolve the Bluetooth address of a
    peripheral immediately.

    The patch ensures that instead of raising an `AttributeError` when attempting
    to call `.hex()` on a `NoneType` object, the scanner simply skips that
    detection and continues.

    Returns:
        None
    """
    if not IS_MACOS:
        return

    try:
        from bleak.backends.corebluetooth.scanner import BleakScannerCoreBluetooth
        from bleak.backends.corebluetooth.utils import cb_uuid_to_str
        from bleak.backends.scanner import AdvertisementData
        import logging

        logger = logging.getLogger("bleak.backends.corebluetooth.scanner")

        async def patched_start(self: BleakScannerCoreBluetooth) -> None:
            """Patched replacement for BleakScannerCoreBluetooth.start.

            Initializes device tracking and registers the robust callback with
            the central manager.

            Args:
                self: The BleakScannerCoreBluetooth instance.

            Returns:
                None
            """
            self.seen_devices = {}

            def callback(p: Any, a: Any, r: float) -> None:
                """Robust detection callback for macOS Bluetooth scanning.

                Processes advertisement data and handles cases where the device
                address cannot be retrieved.

                Args:
                    p: The peripheral object (CBPeripheral).
                    a: The advertisement data dictionary (NSDictionary).
                    r: The RSSI value.

                Returns:
                    None
                """
                # --- PATCH START ---
                # This inner callback is where the crash happens.
                # We replicate the logic but add a check for None address.

                service_uuids = [
                    cb_uuid_to_str(u)
                    for u in a.get("kCBAdvDataServiceUUIDs", [])
                ]

                if not self.is_allowed_uuid(service_uuids):
                    return

                # Process service data
                service_data_dict_raw = a.get("kCBAdvDataServiceData", {})
                service_data = {
                    cb_uuid_to_str(k): bytes(v)
                    for k, v in service_data_dict_raw.items()
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
                    address_bytes = self._manager.central_manager.retrieveAddressForPeripheral_(
                        p
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
