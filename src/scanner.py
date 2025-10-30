import asyncio
import argparse
from typing import Any

import structlog
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from calculations.distance_estimation import estimate_distance, smooth_rssi
from settings.devices import (
    TARGET_DEVICES,
    PATH_LOSS_EXPONENT,
    SAMPLE_WINDOW,
    DISTANCE_THRESHOLD_M,
)


log = structlog.get_logger()

# Global buffer to store recent RSSI values for our single target device
rssi_buffer: dict[str, list[int]] = {}
# Global flag to track the alert state for our single target device
alert_triggered = False

async def _log_device_info(
    target_devices: list[dict[str, any]], 
    uuid: bool = False
) -> None:
    """
    """
    log.info("--- DISTANCE MONITOR INITIALIZING ---")
    log.info("Targeting specific devices:")

    for device in target_devices:
        log.info(
            f" - {device['name']} ({device['device_type']}): "
            f"{device['mac']} | UUID: {device['uuid']} | "
            f"TX Power: {device['tx_power']} dBm"
        )

    log.info(f"Distance Threshold: {DISTANCE_THRESHOLD_M} m")

    _searched_by = "UUID" if uuid else "MAC Address"
    log.info(f"Search by: {_searched_by} m")

    log.info("Press Ctrl+C to stop.")
    log.info("-------------------------------------\n")


def _address_found(
    target_devices: list[dict[str, Any]],
    uuid: bool = False
) -> dict[str, dict[str, Any]]:
    """
    Build a dictionary mapping each device's MAC or UUID to its remaining info.
    """
    address = {}
    for target in target_devices:
        _device_copy = target.copy()
        if uuid and _device_copy.get("uuid"):
            _address_key = _device_copy.pop("uuid")
        else:
            _address_key = _device_copy.pop("mac")
        address[_address_key] = _device_copy
    return address



















def _create_detection_callback(uuid: bool = False):
    """
    Factory function to create a detection callback with the specified uuid parameter.
    """
    def detection_callback(
        device: BLEDevice, 
        adv_data: AdvertisementData
    ) -> None:
        """
        Callback function executed for each received BLE advertisement.
        """
        global alert_triggered, rssi_buffer
        
        address = _address_found(TARGET_DEVICES, uuid)

        address_keys = address.keys()
        # TODO: What if not found for too much time?
        if device.address not in address_keys:
            return
        
        _curr_rssi_buffer = rssi_buffer.get(device.address, [])

        current_rssi = int(adv_data.rssi)

        log.debug(
            f"Target device FOUND: {device.address} | RSSI: {current_rssi}"
        )

        _curr_rssi_buffer.append(current_rssi)
        if len(_curr_rssi_buffer) > SAMPLE_WINDOW:
            _curr_rssi_buffer.pop(0)

        # Get the smoothed RSSI value
        smoothed_rssi = smooth_rssi(_curr_rssi_buffer)

        address_tx_power = address[device.address].get("tx_power")
        rssi_buffer[device.address] = _curr_rssi_buffer

        if smoothed_rssi is None:
            return 
        
        distance_m = estimate_distance(
            smoothed_rssi, 
            address_tx_power, 
            PATH_LOSS_EXPONENT
        )

        log.debug(
            f"Smoothed RSSI: {smoothed_rssi:.1f} | Distance: {distance_m:.2f} m"
        )

        # Check if the distance threshold is exceeded
        if distance_m > DISTANCE_THRESHOLD_M and not alert_triggered:
            log.info(
                f"ALERT: Device {address[device.address]["name"]}, {device.address} is far away! "
                f"(~{distance_m:.2f} m)"
            )
            alert_triggered = True
        # Check if the device has returned within the threshold
        elif distance_m <= DISTANCE_THRESHOLD_M and alert_triggered:
            log.info(
                f"Device {address[device.address]["name"]}, {device.address} is back in range "
                f"(~{distance_m:.2f} m)"
            )
            alert_triggered = False
    
    return detection_callback


















async def start_scanner(args: argparse.Namespace) -> None:
    """Main function to set up and run the BLE scanner for distance monitoring.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    uuid = getattr(args, 'uuid', False)
    await _log_device_info(TARGET_DEVICES, uuid)
    
    detection_callback = _create_detection_callback(uuid)
    
    scanner = BleakScanner(
        detection_callback=detection_callback,
        service_uuids=getattr(args, 'services', []),
        cb={"use_bdaddr": getattr(args, 'macos_use_bdaddr', False)},
    )

    try:
        log.debug("Attempting to start the scanner...")
        await scanner.start()
        log.debug(
            "Scanner started successfully. Listening for advertisements..."
        )
        while True:
            await asyncio.sleep(5.0)
    except Exception as e:
        log.error(
            f"Failed to start the scanner. Please ensure your Bluetooth "
            f"is enabled. Details: {e}"
        )
    finally:
        log.debug("Stopping scanner...")
        if await scanner.is_scanning():
            await scanner.stop()
        log.debug("Scanner stopped.")


