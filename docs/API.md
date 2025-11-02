# 📖 API Reference

Complete reference documentation for Bleissant's classes, methods, and functions.

## Table of Contents

- [Core Classes](#core-classes)
  - [Application](#application)
  - [DeviceMonitor](#devicemonitor)
  - [DeviceScanner](#devicescanner)
  - [ServiceManager](#servicemanager)
- [Utility Functions](#utility-functions)
- [Data Classes](#data-classes)
- [Constants](#constants)

---

## Core Classes

### Application

Main application orchestrator responsible for parsing command-line arguments and delegating tasks.

#### `__init__(args: argparse.Namespace)`

**Parameters:**
- `args`: Parsed command-line arguments

**Example:**
```python
parser = Application.setup_parser()
args = parser.parse_args()
app = Application(args)
```

#### `async run() -> None`

Parses arguments and delegates to appropriate components (ServiceManager, DeviceScanner, or DeviceMonitor).

**Workflow:**
1. Check for service commands (start/stop/restart/status)
2. Check for scanner mode
3. Default to monitor mode

#### `@staticmethod determine_target_address(args: argparse.Namespace) -> str | None`

Determines the target device address from command-line arguments.

**Returns:**
- Target MAC or UUID address, or None if not specified

#### `@staticmethod setup_parser() -> argparse.ArgumentParser`

Sets up the command-line argument parser with all options.

**Returns:**
- Configured ArgumentParser instance

---

### DeviceMonitor

Manages continuous monitoring sessions for a single BLE device.

#### `__init__(target_address: str, use_bdaddr: bool, flags: Flags)`

**Parameters:**
- `target_address`: MAC or UUID of target device
- `use_bdaddr`: Whether to use BD_ADDR (MAC) for identification  
- `flags`: Configuration flags (daemon_mode, file_logging, verbose)

**Attributes:**
- `rssi_buffer`: Deque[int] - Rolling buffer of RSSI samples
- `alert_triggered`: bool - Current alert state
- `log_file`: TextIO | None - Log file handle if logging enabled
- `scanner`: BleakScanner - Bleak scanner instance

#### `async run() -> None`

Starts the monitoring session.

**Behavior:**
- Sets up file logging if enabled
- Prints startup status (unless daemon mode)
- Starts BLE scanner with detection callback
- Runs indefinitely until interrupted

**Exception Handling:**
- Catches scanner start failures
- Ensures graceful shutdown and cleanup

#### `_detection_callback(device: BLEDevice, adv_data: AdvertisementData) -> None`

Core callback function invoked for each BLE advertisement.

**Parameters:**
- `device`: Discovered BLE device
- `adv_data`: Advertisement data with RSSI

**Logic:**
1. Filter for target device only
2. Extract and validate RSSI
3. Process signal (smoothing + distance calculation)
4. Log current status
5. Trigger alerts if threshold exceeded

#### `_process_signal(current_rssi: int) -> tuple[float | None, float | None]`

Updates RSSI buffer and calculates smoothed distance.

**Returns:**
- Tuple of (smoothed_rssi, distance_m) or (None, None) if buffer not full

#### `_lock_macbook() -> str`

Executes macOS system commands to lock the screen.

**Commands executed:**
```bash
defaults write com.apple.screensaver askForPassword -int 1
defaults write com.apple.screensaver askForPasswordDelay -int 0
pmset displaysleepnow
```

**Returns:**
- Status message indicating success or failure

---

### DeviceScanner

Performs one-time BLE device discovery scans.

#### `__init__(duration: int, use_bdaddr: bool, verbose: bool)`

**Parameters:**
- `duration`: Scan duration in seconds (5-60)
- `use_bdaddr`: Use BD_ADDR (MAC) vs UUID
- `verbose`: Print detailed output

#### `async run() -> None`

Executes device scan and prints formatted results.

**Process:**
1. Print scan configuration summary
2. Run BleakScanner.discover() with timeout
3. Sort devices by address
4. Print formatted results table

**Output includes:**
- Device name (or "Unknown")
- MAC address or UUID
- RSSI value with color coding
- Estimated distance

---

### ServiceManager

Handles application lifecycle as a background service (daemon).

#### `__init__(args: argparse.Namespace)`

**Parameters:**
- `args`: Command-line arguments

#### `start() -> None`

Starts the monitor as a background process.

**Process:**
1. Check if already running (via PID file)
2. Reconstruct command with --daemon flag
3. Spawn detached subprocess
4. Print status confirmation

#### `stop() -> None`

Stops the running background monitor.

**Process:**
1. Read PID from file
2. Send SIGTERM signal
3. Remove PID file
4. Print confirmation

#### `restart() -> None`

Restarts the background monitor (stop + start).

#### `display_status() -> None`

Shows current daemon status with details:
- Process status (running/stopped)
- PID and uptime
- Configuration (target device, threshold, etc.)
- Recent log activity (if available)

#### `_get_pid_status() -> tuple[int | None, bool]`

Checks PID file and verifies process existence.

**Returns:**
- Tuple of (pid, is_running)

#### `_reconstruct_command() -> list[str]`

Rebuilds the command to relaunch as daemon.

**Returns:**
- Command list for subprocess.Popen()

---

## Utility Functions

### `_estimate_distance(rssi: float) -> float`

Estimates distance using Log-Distance Path Loss Model.

**Formula:**
```python
distance = 10 ** ((TX_POWER_AT_1M - rssi) / (10 * PATH_LOSS_EXPONENT))
```

**Parameters:**
- `rssi`: RSSI value in dBm

**Returns:**
- Estimated distance in meters, or -1.0 for invalid RSSI (0)

**Example:**
```python
distance = _estimate_distance(-60)  # Returns ~1.26 meters
```

### `_smooth_rssi(buffer: Deque[int]) -> float | None`

Calculates statistical mean of RSSI buffer.

**Parameters:**
- `buffer`: Deque of recent RSSI samples

**Returns:**
- Mean RSSI value, or None if buffer empty

**Example:**
```python
from collections import deque
buffer = deque([-60, -62, -58], maxlen=12)
smoothed = _smooth_rssi(buffer)  # Returns -60.0
```

---

## Data Classes

### Flags

Configuration flags for monitoring sessions.

**Attributes:**
- `daemon_mode`: bool - Running as background process
- `file_logging`: bool - Output redirected to log file
- `verbose`: bool - Detailed output enabled

**Example:**
```python
flags = Flags(
    daemon_mode=False,
    file_logging=True,
    verbose=True
)
```

### Colors

ANSI color codes for terminal output.

**Constants:**
- `GREEN = "\033[92m"`
- `RED = "\033[91m"`
- `YELLOW = "\033[93m"`
- `BLUE = "\033[94m"`
- `GREY = "\033[90m"`
- `BOLD = "\033[1m"`
- `RESET = "\033[0m"`

---

## Constants

### Configuration Constants (from .env)

```python
TARGET_DEVICE_MAC_ADDRESS: str  # MAC address of target device
TARGET_DEVICE_UUID_ADDRESS: str  # UUID address (macOS)
TARGET_DEVICE_NAME: str  # Display name
TARGET_DEVICE_TYPE: str  # Device type description
TX_POWER_AT_1M: int  # Calibrated RSSI at 1 meter (default: -59)
PATH_LOSS_EXPONENT: float  # Environmental factor (default: 2.8)
SAMPLE_WINDOW: int  # RSSI smoothing window (default: 12)
DISTANCE_THRESHOLD_M: float  # Alert threshold (default: 2.0)
```

### File Path Constants

```python
SCRIPT_DIR: str  # Directory containing main.py
PID_FILE: str  # Path to .ble_monitor.pid
LOG_FILE: str  # Path to .ble_monitor.log
```

---

## Usage Examples

### Basic Monitoring

```python
from main import Application
import argparse
import asyncio

# Create args namespace
args = argparse.Namespace(
    target_mac="AA:BB:CC:DD:EE:FF",
    macos_use_bdaddr=True,
    verbose=True,
    file_logging=False,
    daemon=False,
    scanner=None,
    start=False,
    stop=False,
    restart=False,
    status=False
)

# Run application
app = Application(args)
asyncio.run(app.run())
```

### Device Discovery

```python
from main import DeviceScanner
import asyncio

scanner = DeviceScanner(
    duration=15,
    use_bdaddr=True,
    verbose=True
)

asyncio.run(scanner.run())
```

### Custom Distance Calculation

```python
from main import _estimate_distance

# RSSI at various distances
rssi_values = [-50, -60, -70, -80]
for rssi in rssi_values:
    distance = _estimate_distance(rssi)
    print(f"RSSI {rssi} dBm → Distance: {distance:.2f}m")
```

---

## Type Signatures

All functions include type hints for better IDE support and static analysis:

```python
def _estimate_distance(rssi: float) -> float: ...
def _smooth_rssi(buffer: Deque[int]) -> float | None: ...

class DeviceMonitor:
    def __init__(
        self,
        target_address: str,
        use_bdaddr: bool,
        flags: Flags,
    ) -> None: ...
    
    async def run(self) -> None: ...
    
    def _detection_callback(
        self,
        device: BLEDevice,
        adv_data: AdvertisementData,
    ) -> None: ...
```

---

## Error Handling

### Common Exceptions

**Scanner Failures:**
```python
try:
    await scanner.start()
except Exception as e:
    # Bluetooth adapter not available
    # Permissions not granted
    # Hardware error
```

**Lock Command Failures:**
```python
try:
    subprocess.run(["pmset", "displaysleepnow"], check=True)
except subprocess.CalledProcessError:
    # pmset command failed
except FileNotFoundError:
    # pmset not found (non-macOS system)
```

**PID File Issues:**
```python
try:
    with open(PID_FILE, "r") as f:
        pid = int(f.read().strip())
except (IOError, ValueError):
    # File doesn't exist or is corrupted
```

---

For more information, see:
- [Architecture Documentation](ARCHITECTURE.md)
- [Testing Guide](TESTING.md)
- [Contributing Guide](CONTRIBUTING.md)
