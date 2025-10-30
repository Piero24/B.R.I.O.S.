import statistics


def estimate_distance(
    rssi: float, 
    tx_power: int, 
    path_loss_exponent: float
) -> float:
    """Estimates the distance from a device based on RSSI.

    Args:
        rssi (float): The received signal strength indicator in dBm.
        tx_power (int): The transmitted power in dBm at 1 meter.
        path_loss_exponent (float): The path loss exponent, typically 
            between 2 and 4.
    
    Returns:
        float: Estimated distance in meters. Returns -1.0 if RSSI is 0.
    """
    if rssi == 0:
        return -1.0
    return 10 ** ((tx_power - rssi) / (10 * path_loss_exponent))


def smooth_rssi(buffer: list[int]) -> float | None:
    """Calculates the mean of the RSSI values in the buffer.
    Args:
        buffer (list[int]): A list of RSSI values.
    Returns:
        float | None: The mean RSSI value, or None if the buffer is empty.
    """
    if not buffer:
        return None
    return statistics.mean(buffer)