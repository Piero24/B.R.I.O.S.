from typing import Any

class Device:
    """Class representing a BLE device with relevant attributes."""

    def __init__(
        self,
        name: str,
        mac: str,
        uuid: str,
        device_type: str,
        tx_power: int,
        rssi_buffer: list[int] = None,
        distance_m: float = None,
        current_rssi: int = None,
        alert_triggered: bool = False,
        *args: Any, **kwargs: Any
    ) -> None:
        """
        """
        self.mac = mac
        self.uuid = uuid
        self.name = name
        self.device_type = device_type
        self.tx_power = tx_power
    
    def __repr__(self) -> str:
        pass

    def to_dict(self) -> dict[str, Any]:
        pass

    # build the object from a dictionary in input
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Device":
        pass

    def update_rssi(self, rssi: int) -> None:
        pass

    def calculate_distance(self) -> float:
        pass