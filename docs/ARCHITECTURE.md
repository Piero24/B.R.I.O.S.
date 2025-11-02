# 🏗️ Architecture Overview

Comprehensive guide to Bleissant's system design, code organization, and architectural decisions.

## Table of Contents

- [System Architecture](#system-architecture)
- [Module Organization](#module-organization)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)
- [Class Hierarchy](#class-hierarchy)
- [State Management](#state-management)
- [Error Handling Strategy](#error-handling-strategy)
- [Performance Considerations](#performance-considerations)

---

## System Architecture

Bleissant follows a clean, modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Interface                          │
│                    (ArgumentParser)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
┌─────────▼─────────┐  ┌────────▼────────┐
│   Application     │  │ ServiceManager  │
│   Orchestrator    │  │  (Daemon Ctrl)  │
└─────────┬─────────┘  └─────────────────┘
          │
    ┌─────┴─────┐
    │           │
┌───▼────┐  ┌──▼──────────┐
│Scanner │  │   Monitor   │
│ Mode   │  │    Mode     │
└────────┘  └──┬──────────┘
               │
      ┌────────┴────────┐
      │                 │
┌─────▼─────┐  ┌───────▼────────┐
│  Signal   │  │   Distance     │
│Processing │  │  Estimation    │
└───────────┘  └────────────────┘
      │                 │
      └────────┬────────┘
               │
     ┌─────────▼──────────┐
     │  Alert & Action    │
     │  (macOS Lock)      │
     └────────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **Application** | CLI parsing, component orchestration, mode selection |
| **ServiceManager** | Daemon lifecycle (start/stop/restart/status) |
| **DeviceScanner** | BLE device discovery and listing |
| **DeviceMonitor** | Continuous proximity monitoring and alerts |
| **Signal Processing** | RSSI smoothing and noise filtering |
| **Distance Estimation** | Log-Distance Path Loss Model calculations |

---

## Module Organization

### File Structure

```
Bleissant/
├── main.py                    # Main application entry point
├── .env.example               # Configuration template
├── requirements/              # Dependency management
│   ├── base.txt              # Core runtime dependencies
│   ├── dev.txt               # Development tools
│   └── ci.txt                # CI/CD dependencies
├── tests/                     # Test suite
│   ├── conftest.py           # Pytest configuration
│   └── test_ble_monitor.py   # Comprehensive tests
├── docs/                      # Documentation
│   ├── API.md                # API reference
│   ├── ARCHITECTURE.md       # This file
│   ├── CONTRIBUTING.md       # Contribution guidelines
│   └── TESTING.md            # Testing documentation
└── .github/
    ├── workflows/            # CI/CD pipelines
    └── README.md             # Project documentation
```

### Code Organization in main.py

```python
# 1. Imports & Environment Setup
import os, sys, asyncio, ...
load_dotenv(".env")

# 2. Constants Configuration
TARGET_DEVICE_MAC_ADDRESS = os.getenv(...)
TX_POWER_AT_1M = int(os.getenv(...))
...

# 3. Utility Classes & Functions
class Colors: ...
@dataclass class Flags: ...
def _estimate_distance(...): ...
def _smooth_rssi(...): ...

# 4. Service Management
class ServiceManager:
    - start(), stop(), restart()
    - display_status()
    - _get_pid_status(), _reconstruct_command()

# 5. Device Scanner
class DeviceScanner:
    - run()
    - _print_summary(), _print_results()

# 6. Device Monitor
class DeviceMonitor:
    - run()
    - _detection_callback()
    - _process_signal()
    - _log_status()
    - _trigger_out_of_range_alert()
    - _trigger_in_range_alert()
    - _lock_macbook()

# 7. Application Orchestrator
class Application:
    - run()
    - _run_monitor_foreground()
    - @staticmethod determine_target_address()
    - @staticmethod setup_parser()

# 8. Entry Point
if __name__ == "__main__":
    # Parse args and run
```

---

## Data Flow

### Discovery Mode Flow

```
User Input (--scanner 15 -m)
    ↓
Application.run()
    ↓
DeviceScanner(duration=15, use_bdaddr=True)
    ↓
BleakScanner.discover(timeout=15)
    ↓
Device List Processing
    ↓
Formatted Output (name, MAC, RSSI, distance)
```

### Monitor Mode Flow

```
User Input (--target-mac -v)
    ↓
Application._run_monitor_foreground()
    ↓
DeviceMonitor(target, use_bdaddr, flags)
    ↓
┌─────── BleakScanner.start() ──────┐
│                                    │
│  ┌─ _detection_callback() ◄───────┤
│  │                                 │
│  │  1. Filter target device        │
│  │  2. Extract RSSI                │
│  │  3. Add to buffer               │
│  │  4. Calculate smoothed RSSI     │
│  │  5. Estimate distance           │
│  │  6. Log status                  │
│  │  7. Check threshold             │
│  │  │                               │
│  │  ├─ Distance > Threshold?       │
│  │  │  YES ↓                        │
│  │  │  _trigger_out_of_range_alert() │
│  │  │  └─ _lock_macbook()          │
│  │  │                               │
│  │  └─ Distance <= Threshold?      │
│  │     YES ↓                        │
│  │     _trigger_in_range_alert()   │
│  │                                  │
│  └──────────────┬───────────────────┤
│                 ↓                   │
│           (Loop Forever)            │
└─────────────────────────────────────┘
```

### Service Mode Flow

```
User Input (--start)
    ↓
ServiceManager.start()
    ↓
_reconstruct_command()
    ↓
subprocess.Popen(command, daemon=True)
    ↓
Write PID to file
    ↓
Background Process Running
    │
    ├─ --status → display_status()
    ├─ --stop   → stop() → SIGTERM
    └─ --restart → stop() + start()
```

---

## Design Patterns

### 1. **Strategy Pattern** - Distance Calculation

Different path loss exponents can be configured for different environments:

```python
# Indoor office
PATH_LOSS_EXPONENT = 2.8

# Open outdoor space
PATH_LOSS_EXPONENT = 2.0

# Heavy obstruction
PATH_LOSS_EXPONENT = 3.5
```

### 2. **Observer Pattern** - BLE Callbacks

The monitor registers a callback that's invoked for each BLE advertisement:

```python
self.scanner = BleakScanner(
    detection_callback=self._detection_callback,
    cb={"use_bdaddr": self.use_bdaddr}
)
```

### 3. **Facade Pattern** - Application Class

Simplifies complex subsystem interactions:

```python
app = Application(args)
await app.run()  # Hides ServiceManager, Scanner, Monitor complexity
```

### 4. **State Pattern** - Alert Management

Monitor maintains state to prevent duplicate alerts:

```python
self.alert_triggered: bool = False

# Out of range
if distance > threshold and not self.alert_triggered:
    self._trigger_out_of_range_alert()
    self.alert_triggered = True

# Back in range
if distance <= threshold and self.alert_triggered:
    self._trigger_in_range_alert()
    self.alert_triggered = False
```

### 5. **Template Method** - Service Lifecycle

ServiceManager defines the skeleton of daemon operations:

```python
def start(self):
    pid, is_running = self._get_pid_status()  # Check current state
    if is_running:
        return  # Already running
    
    command = self._reconstruct_command()  # Prepare command
    subprocess.Popen(command, ...)  # Execute
    self._print_start_status()  # Feedback
```

---

## Class Hierarchy

```
┌─────────────────────┐
│    Application      │  ← Main Orchestrator
└──────────┬──────────┘
           │
           ├─── ServiceManager    ← Daemon Lifecycle
           │
           ├─── DeviceScanner     ← BLE Discovery
           │
           └─── DeviceMonitor     ← Proximity Tracking
                     │
                     ├─ BleakScanner (composition)
                     ├─ rssi_buffer (deque)
                     └─ log_file (TextIO)

┌─────────────────────┐
│       Flags         │  ← Data Class
│  (daemon_mode,      │
│   file_logging,     │
│   verbose)          │
└─────────────────────┘

┌─────────────────────┐
│      Colors         │  ← Utility Class
│  (ANSI codes)       │
└─────────────────────┘
```

### Inheritance

Bleissant uses **composition over inheritance**. No classes inherit from each other; instead, they are composed:

```python
class Application:
    def __init__(self, args):
        self.args = args
        self.service_manager = ServiceManager(args)  # Composition

class DeviceMonitor:
    def __init__(self, target_address, use_bdaddr, flags):
        self.scanner = BleakScanner(...)  # Composition
        self.rssi_buffer = deque(maxlen=SAMPLE_WINDOW)  # Composition
```

---

## State Management

### Monitor State

```python
class DeviceMonitor:
    # Persistent State
    rssi_buffer: Deque[int]         # Rolling RSSI history
    alert_triggered: bool            # Current alert state
    log_file: TextIO | None         # Log file handle
    
    # Configuration (immutable after init)
    target_address: str
    use_bdaddr: bool
    flags: Flags
```

### Service State

```python
# File-based state
PID_FILE = ".ble_monitor.pid"    # Contains process ID
LOG_FILE = ".ble_monitor.log"    # Contains activity log

# State transitions
[Not Running] --start--> [Running] --stop--> [Not Running]
              <-restart--          --restart-->
```

### State Diagram

```
                    ┌──────────────┐
         ┌─────────►│  Monitoring  │◄─────────┐
         │          │  (No Alert)  │          │
         │          └──────┬───────┘          │
         │                 │                  │
         │        Distance > Threshold        │
         │                 │                  │
         │          ┌──────▼───────┐          │
         │          │  Out of      │          │
Device   │          │  Range       │          │ Distance <=
Returns  │          │  (Alert ON)  │          │ Threshold
         │          └──────┬───────┘          │
         │                 │                  │
         │       System Lock Executed         │
         │                 │                  │
         └─────────────────┘──────────────────┘
```

---

## Error Handling Strategy

### Graceful Degradation

```python
def _detection_callback(self, device, adv_data):
    try:
        # Main processing logic
        ...
    except (AttributeError, TypeError):
        # Malformed packets (expected during Mac sleep)
        if self.flags.verbose:
            self._handle_bleak_error()
        return  # Continue monitoring
    except Exception as e:
        # Unexpected errors
        if self.flags.verbose:
            self._handle_generic_error(e)
        return  # Keep scanner alive
```

### Exception Hierarchy

```
Exception
├── OSError
│   └── Used for: PID file operations, process signals
├── subprocess.CalledProcessError
│   └── Used for: Mac lock command failures
├── IOError / ValueError
│   └── Used for: Configuration file errors
└── BleakError (from bleak library)
    └── Used for: BLE scanner failures
```

### Error Recovery

1. **Scanner Failures**: Print error, exit gracefully
2. **Callback Errors**: Log and continue monitoring
3. **Lock Command Failures**: Report failure but continue monitoring
4. **PID File Issues**: Clean up and continue

---

## Performance Considerations

### Memory Management

```python
# Fixed-size buffer prevents memory growth
self.rssi_buffer: Deque[int] = deque(maxlen=SAMPLE_WINDOW)

# Log file is kept open for append (no repeated open/close)
self.log_file = open(LOG_FILE, "a")

# Scanner uses callbacks (event-driven, not polling)
self.scanner = BleakScanner(detection_callback=...)
```

### CPU Efficiency

- **Event-driven architecture**: No busy waiting or polling
- **Statistical smoothing**: O(n) where n = SAMPLE_WINDOW (typically 12)
- **Distance calculation**: O(1) mathematical operation
- **Async/await**: Non-blocking I/O operations

### Network Efficiency

- **BLE is low-energy**: Minimal battery impact on target device
- **Advertisement-based**: No active connections required
- **Passive scanning**: Monitor only, no pairing needed

### Latency Considerations

| Operation | Typical Latency |
|-----------|----------------|
| BLE Advertisement | 100-1000ms |
| RSSI Buffer Fill | 1.2-12 seconds (depends on SAMPLE_WINDOW) |
| Distance Calculation | < 1ms |
| macOS Lock Command | 100-500ms |
| **Total Alert Latency** | **~2-15 seconds** |

---

## Scalability

### Single Device Limitation

Current design monitors **one device at a time** for security focus:

```python
def _detection_callback(self, device, adv_data):
    if device.address != self.target_address:
        return  # Ignore other devices
```

### Potential Multi-Device Extension

To support multiple devices:

```python
class MultiDeviceMonitor:
    def __init__(self, target_addresses: list[str], ...):
        self.monitors = {
            addr: DeviceState(buffer=deque(...), alert=False)
            for addr in target_addresses
        }
    
    def _detection_callback(self, device, adv_data):
        if device.address in self.monitors:
            # Process this device
            ...
```

---

## Testing Architecture

### Test Organization

```
tests/
├── conftest.py              # Pytest fixtures and configuration
└── test_ble_monitor.py      # Comprehensive test suite
    ├── Mock Classes         # MockBLEDevice, MockAdvertisementData
    ├── Fixtures             # mock_args, reloaded_main_new
    ├── Unit Tests           # Function-level tests
    │   ├── test_estimate_distance()
    │   └── test_smooth_rssi()
    ├── Integration Tests    # Component interaction
    │   ├── test_device_scanner_run()
    │   ├── test_device_monitor_alerts()
    │   └── test_service_manager_*()
    └── E2E Tests            # Full application flow
        └── test_application_cli_dispatch()
```

### Mocking Strategy

```python
# Mock Bleak before main import
mock_bleak = MagicMock()
sys.modules["bleak"] = mock_bleak
sys.modules["bleak.backends.device"] = MagicMock()
...

# Now safe to import
import main
```

---

## Security Considerations

### Privilege Requirements

- **Bluetooth Access**: macOS Bluetooth permissions required
- **Lock Commands**: No elevated privileges needed (user-level)
- **File I/O**: Writes to project directory only

### Attack Surface

| Vector | Risk | Mitigation |
|--------|------|------------|
| BLE Spoofing | Medium | MAC address filtering, distance verification |
| PID File Tampering | Low | File permissions, PID validation |
| Log Injection | Low | Controlled log format, no user input in logs |
| Denial of Service | Low | Graceful error handling, automatic restart |

### Privacy

- **No data transmission**: All processing is local
- **No cloud dependencies**: Fully offline operation
- **Log files**: Contain only timestamps, RSSI, distance (no personal data)

---

## Future Architecture Enhancements

### Potential Improvements

1. **Plugin System**: Extensible action triggers (not just lock)
2. **Multi-Device Support**: Monitor multiple devices simultaneously
3. **Machine Learning**: Adaptive path loss calibration
4. **REST API**: Remote monitoring and control
5. **WebUI**: Browser-based dashboard
6. **Database**: SQLite for historical data analysis

### Backward Compatibility

Any future changes will maintain:
- ✅ CLI interface compatibility
- ✅ .env configuration format
- ✅ Core monitoring functionality
- ✅ Service management commands

---

For more details, see:
- [API Reference](API.md)
- [Testing Guide](TESTING.md)
- [Contributing Guide](CONTRIBUTING.md)
