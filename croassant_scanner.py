import asyncio
import argparse
import statistics

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from devices import (
    TARGET_DEVICES,
    PATH_LOSS_EXPONENT,
    SAMPLE_WINDOW,
    DISTANCE_THRESHOLD_M,
)

# https://github.com/hbldh/bleak
# pip install bleak

# Global buffer to store recent RSSI values for our single target device
rssi_buffer: list[int] = []
# Global flag to track the alert state for our single target device
alert_triggered = False

def estimate_distance(
    rssi: float, 
    tx_power: int, 
    path_loss_exponent: float
) -> float:
    """Estimates the distance from a device based on RSSI."""
    if rssi == 0:
        return -1.0
    return 10 ** ((tx_power - rssi) / (10 * path_loss_exponent))

def smooth_rssi(buffer: list[int]) -> float | None:
    """Calculates the mean of the RSSI values in the buffer."""
    if not buffer:
        return None
    return statistics.mean(buffer)

async def main(args: argparse.Namespace) -> None:
    """
    Main function to set up and run the BLE scanner for distance monitoring.
    """
    global alert_triggered, rssi_buffer

    print("--- DISTANCE MONITOR INITIALIZING ---")
    print(f"Targeting specific devices:")
    for device in TARGET_DEVICES:
        print(
            f" - {device['name']} ({device['device_type']}): "
            f"{device['mac']} | UUID: {device['uuid']} | "
            f"TX Power: {device['tx_power']} dBm"
        )
    print(f"Distance Threshold: {DISTANCE_THRESHOLD_M} m")
    print("Press Ctrl+C to stop.")
    print("-------------------------------------\n")

    def detection_callback(
        device: BLEDevice, 
        adv_data: AdvertisementData, 
        uuid: bool = False
    ) -> None:
        """
        Callback function executed for each received BLE advertisement.
        TODO: The UUID one
        """
        global alert_triggered, rssi_buffer

        address = [
            target["uuid"] 
            if target.get("uuid") else target["mac"] 
            for target in TARGET_DEVICES
        ]

        if device.address not in address:
            return

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

    # TODO: Add parse scanner
    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("\nINFO: Program interrupted by user (Ctrl+C).")