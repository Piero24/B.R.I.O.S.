# import asyncio
# from bleak import BleakScanner

# async def run():
#     devices = await BleakScanner.discover()
#     for d in devices:
#         print(d)

# loop = asyncio.get_event_loop()
# loop.run_until_complete(run()) 


# import argparse
# import asyncio

# from bleak import BleakScanner


# class Args(argparse.Namespace):
#     macos_use_bdaddr: bool
#     services: list[str]


# async def main(args: Args):
#     print("scanning for 5 seconds, please wait...")

#     devices = await BleakScanner.discover(
#         return_adv=True,
#         service_uuids=args.services,
#         cb={"use_bdaddr": args.macos_use_bdaddr},
#     )

#     for d, a in devices.values():
#         # print()
#         # print(d)
#         # print("-" * len(str(d)))
#         # print(a)
#         if "XX" in str(d):
#             print(a)


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()

#     parser.add_argument(
#         "--services",
#         metavar="<uuid>",
#         nargs="*",
#         help="UUIDs of one or more services to filter for",
#     )

#     parser.add_argument(
#         "--macos-use-bdaddr",
#         action="store_true",
#         help="when true use Bluetooth address instead of UUID on macOS",
#     )

#     args = parser.parse_args(namespace=Args())

#     asyncio.run(main(args))
import argparse
import asyncio
import statistics
from bleak import BleakScanner
from bleak.backends.device import BLEDevice # Correct import is already here
from bleak.backends.scanner import AdvertisementData
from typing import List

# --- Configuration Constants ---
# This should be the real, non-randomized MAC address of your iPhone.
TARGET_DEVICE_ADDRESS = ""

# TX Power at 1 meter. This value is crucial for accurate distance estimation.
TX_POWER_AT_1M = -59

# Path-loss exponent. Varies depending on the environment.
PATH_LOSS_EXPONENT = 2.8

# The number of recent RSSI samples to average for smoothing.
SAMPLE_WINDOW = 12

# The distance in meters beyond which an alert will be triggered.
DISTANCE_THRESHOLD_M = 2.0
# -----------------------------

# Global buffer to store recent RSSI values for our single target device
rssi_buffer: List[int] = []
# Global flag to track the alert state for our single target device
alert_triggered = False

def estimate_distance(rssi: float, tx_power: int, path_loss_exponent: float) -> float:
    """Estimates the distance from a device based on RSSI."""
    if rssi == 0:
        return -1.0
    return 10 ** ((tx_power - rssi) / (10 * path_loss_exponent))

def smooth_rssi(buffer: List[int]) -> float | None:
    """Calculates the mean of the RSSI values in the buffer."""
    if not buffer:
        return None
    return statistics.mean(buffer)

async def main(args: argparse.Namespace):
    """
    Main function to set up and run the BLE scanner for distance monitoring.
    """
    global alert_triggered, rssi_buffer

    print("--- DISTANCE MONITOR INITIALIZING ---")
    print(f"Targeting specific device: {TARGET_DEVICE_ADDRESS}")
    print(f"Distance Threshold: {DISTANCE_THRESHOLD_M} m")
    print("Press Ctrl+C to stop.")
    print("-------------------------------------\n")

    # FIXED TYPO HERE: Corrected "BLEDEvice" to "BLEDevice"
    def detection_callback(device: BLEDevice, adv_data: AdvertisementData):
        """
        Callback function executed for each received BLE advertisement.
        """
        global alert_triggered, rssi_buffer

        # Only proceed if the advertisement is from our specific target device
        if device.address == TARGET_DEVICE_ADDRESS:

            # CRASH FIX: Immediately cast the RSSI value to a standard Python integer.
            current_rssi = int(adv_data.rssi)

            print(f"DEBUG: >> Target device FOUND: {device.address} | RSSI: {current_rssi}")

            # Add the new RSSI value to the buffer
            rssi_buffer.append(current_rssi)
            if len(rssi_buffer) > SAMPLE_WINDOW:
                rssi_buffer.pop(0)

            # Get the smoothed RSSI value
            smoothed_rssi = smooth_rssi(rssi_buffer)
            if smoothed_rssi is not None:
                distance_m = estimate_distance(smoothed_rssi, TX_POWER_AT_1M, PATH_LOSS_EXPONENT)

                print(f"INFO: Smoothed RSSI: {smoothed_rssi:.1f} | Distance: {distance_m:.2f} m")

                # Check if the distance threshold is exceeded
                if distance_m > DISTANCE_THRESHOLD_M and not alert_triggered:
                    print(f"⚠️  ALERT: Device {device.address} is far away! (~{distance_m:.2f} m)")
                    alert_triggered = True
                # Check if the device has returned within the threshold
                elif distance_m <= DISTANCE_THRESHOLD_M and alert_triggered:
                    print(f"✅  Device {device.address} is back in range. (~{distance_m:.2f} m)")
                    alert_triggered = False

    scanner = BleakScanner(
        detection_callback=detection_callback,
        service_uuids=getattr(args, 'services', []),
        cb={"use_bdaddr": getattr(args, 'macos_use_bdaddr', False)}
    )

    try:
        print("DEBUG: Attempting to start the scanner...")
        await scanner.start()
        print("DEBUG: Scanner started successfully. Listening for advertisements...")
        while True:
            await asyncio.sleep(5.0)
    except Exception as e:
        print(f"ERROR: Failed to start the scanner. Please ensure your Bluetooth adapter is enabled. Details: {e}")
    finally:
        print("\nDEBUG: Stopping scanner...")
        if await scanner.is_scanning():
            await scanner.stop()
        print("INFO: Scanner stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Continuously monitor the distance of a specific BLE device."
    )
    parser.add_argument(
        "--services",
        metavar="<uuid>",
        nargs="*",
        help="UUIDs of one or more services to filter for.",
    )
    parser.add_argument(
        "--macos-use-bdaddr",
        action="store_true",
        help="Use Bluetooth address instead of UUID on macOS. Recommended.",
    )
    args = parser.parse_args()
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("\nINFO: Program interrupted by user (Ctrl+C).")