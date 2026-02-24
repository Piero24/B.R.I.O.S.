---
id: core-modules
title: Core Modules
sidebar_position: 2
---

# Core Modules API Reference

This page documents the public interfaces of the core B.R.I.O.S. modules.

---

## `brios.core.config`

Loads environment variables from multiple `.env` file locations and exposes them as module-level constants.

### Constants

```python
TARGET_DEVICE_MAC_ADDRESS: Optional[str]  # MAC address of the target device
TARGET_DEVICE_UUID_ADDRESS: Optional[str] # UUID address (macOS privacy mode)
TARGET_DEVICE_NAME: str                    # Human-readable device name (default: "Unknown Device Name")
TARGET_DEVICE_TYPE: str                    # Device type (default: "Unknown Device")

TX_POWER_AT_1M: int       # RSSI at 1 meter (default: -59)
PATH_LOSS_EXPONENT: float  # Environment factor (default: 2.8)
SAMPLE_WINDOW: int         # RSSI buffer size (default: 12)
DISTANCE_THRESHOLD_M: float # Lock distance in meters (default: 2.0)

GRACE_PERIOD_SECONDS: int  # Post-unlock grace period (default: 30)
LOCK_LOOP_THRESHOLD: int   # Lock events before pause (default: 3)
LOCK_LOOP_WINDOW: int      # Lock loop time window (default: 60)
LOCK_LOOP_PENALTY: int     # Pause duration on lock loop (default: 120)
```

---

## `brios.core.utils`

Shared utility functions for signal processing and application helpers.

### `estimate_distance(rssi, tx_power_at_1m, path_loss_exponent) → float`

Estimates the physical distance to a BLE device using the Log-Distance Path Loss model.

**Parameters:**

| Name | Type | Default | Description |
|---|---|---|---|
| `rssi` | `float` | — | Received Signal Strength Indicator (dBm) |
| `tx_power_at_1m` | `int` | `TX_POWER_AT_1M` | Expected RSSI at 1 meter |
| `path_loss_exponent` | `float` | `PATH_LOSS_EXPONENT` | Environment path loss exponent |

**Returns:** `float` — Estimated distance in meters. Returns `-1.0` if RSSI is `0` (invalid reading).

**Formula:**

```
distance = 10 ^ ((tx_power_at_1m − rssi) / (10 × path_loss_exponent))
```

**Example:**

```python
from brios.core.utils import estimate_distance

estimate_distance(-59)   # ≈ 1.0m (at calibration point)
estimate_distance(-40)   # < 1.0m (very close)
estimate_distance(-80)   # > 1.0m (far away)
estimate_distance(0)     # -1.0 (invalid)
```

---

### `smooth_rssi(buffer) → Optional[float]`

Calculates the statistical mean of RSSI values in a buffer to stabilize fluctuating readings.

**Parameters:**

| Name | Type | Description |
|---|---|---|
| `buffer` | `Deque[int]` | A deque containing recent RSSI samples |

**Returns:** `Optional[float]` — The mean RSSI value, or `None` if the buffer is empty.

**Example:**

```python
from collections import deque
from brios.core.utils import smooth_rssi

buffer = deque([-60, -62, -58, -61], maxlen=12)
smooth_rssi(buffer)  # -60.25

smooth_rssi(deque())  # None
```

---

### `determine_target_address(args) → Optional[str]`

Resolves the target device address from CLI arguments and environment configuration.

**Resolution order:**
1. Explicit `--target-mac` or `--target-uuid` argument value
2. Default MAC/UUID from `.env` configuration
3. Returns `None` if no address can be determined

---

### `apply_robust_bleak_patch() → None`

Applies a runtime monkeypatch to fix a Bleak crash on macOS where `retrieveAddressForPeripheral_` returns `None`. Called automatically at startup.

---

### `Colors`

ANSI color code constants for terminal output:

```python
Colors.GREEN   # \033[92m
Colors.RED     # \033[91m
Colors.YELLOW  # \033[93m
Colors.BLUE    # \033[94m
Colors.GREY    # \033[90m
Colors.BOLD    # \033[1m
Colors.RESET   # \033[0m
```

---

### `Flags`

A dataclass holding runtime boolean flags:

```python
@dataclass
class Flags:
    daemon_mode: bool   # Running as background process
    file_logging: bool  # Output to log file
    verbose: bool       # Detailed terminal output
```

---

## `brios.core.scanner`

### `DeviceScanner`

Performs a one-time BLE device discovery scan and prints formatted results.

```python
class DeviceScanner:
    def __init__(self, duration: int, use_bdaddr: bool, verbose: bool) -> None: ...
    async def run(self) -> None: ...
```

**Constructor Parameters:**

| Name | Type | Description |
|---|---|---|
| `duration` | `int` | Scan duration in seconds (5–60) |
| `use_bdaddr` | `bool` | Use real MAC addresses on macOS |
| `verbose` | `bool` | Enable detailed output |

---

## `brios.core.monitor`

### `DeviceMonitor`

Manages a continuous BLE monitoring session for a single target device.

```python
class DeviceMonitor:
    def __init__(self, target_address: str, use_bdaddr: bool, flags: Flags) -> None: ...
    async def run(self) -> None: ...
```

**Constructor Parameters:**

| Name | Type | Description |
|---|---|---|
| `target_address` | `str` | MAC or UUID of the target device |
| `use_bdaddr` | `bool` | Use BD_ADDR (MAC) for identification |
| `flags` | `Flags` | Runtime configuration flags |

**Key Attributes:**

| Attribute | Type | Description |
|---|---|---|
| `rssi_buffer` | `Deque[int]` | Rolling buffer of RSSI samples |
| `alert_triggered` | `bool` | Whether an out-of-range alert is currently active |
| `is_handling_lock` | `bool` | Whether the lock handling coroutine is running |
| `resume_time` | `float` | Monotonic timestamp of last monitoring resumption |
| `lock_history` | `Deque[float]` | Timestamps of recent lock events |

**Key Methods:**

| Method | Description |
|---|---|
| `run()` | Starts the monitoring session (blocking) |
| `_detection_callback()` | Core BLE advertisement handler |
| `_process_signal()` | RSSI buffering and smoothing |
| `_handle_screen_lock()` | Pauses scanner, waits for unlock, reconnects |
| `_watchdog_loop()` | Background health monitor |

---

## `brios.core.service`

### `ServiceManager`

Handles the B.R.I.O.S. lifecycle as a background daemon.

```python
class ServiceManager:
    def __init__(self, args: argparse.Namespace) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def restart(self) -> None: ...
    def display_status(self) -> None: ...
```

| Method | Description |
|---|---|
| `start()` | Launches the monitor as a detached background process |
| `stop()` | Sends `SIGTERM` to the running daemon |
| `restart()` | Stops and restarts the daemon |
| `display_status()` | Prints PID, uptime, target, and recent log entries |

---

## `brios.core.system`

Platform-specific macOS system integration functions.

### `is_screen_locked() → bool`

Checks whether the macOS screen is currently locked using CoreGraphics via `ctypes`.

**Implementation:** Reads the `CGSSessionScreenIsLocked` key from the CoreGraphics session dictionary.

**Returns:** `True` if the screen is locked, `False` otherwise or if not running on macOS.

---

### `lock_macbook() → Tuple[bool, str]`

Locks the macOS screen by:

1. Setting `askForPassword` and `askForPasswordDelay` via `defaults write`.
2. Executing `pmset displaysleepnow` to put the display to sleep.

**Returns:** A tuple of `(success: bool, status_message: str)`.
