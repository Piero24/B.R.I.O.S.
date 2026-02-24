---
id: architecture
title: Architecture Overview
sidebar_position: 1
---

# Architecture Overview

B.R.I.O.S. is organized as a modular Python package with clearly separated concerns. This page describes the high-level architecture and how the components interact.

---

## Package Structure

```
brios/
├── __init__.py          # Version resolution
├── __main__.py          # Entry point for `python -m brios`
├── cli.py               # CLI argument parsing and Application orchestrator
└── core/
    ├── config.py         # Environment variable loading and constants
    ├── monitor.py        # Real-time BLE device monitoring
    ├── scanner.py        # One-time BLE device discovery
    ├── service.py        # Background daemon lifecycle management
    ├── system.py         # macOS system integration (lock, screen state)
    └── utils.py          # Shared utilities, colors, signal processing
```

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLI (cli.py)                               │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Application                                │  │
│  │  • Parses command-line arguments                              │  │
│  │  • Delegates to ServiceManager, DeviceScanner, or Monitor     │  │
│  └──────────┬──────────────────┬──────────────────┬──────────────┘  │
│             │                  │                  │                  │
│    ┌────────▼──────┐  ┌───────▼────────┐  ┌──────▼───────────┐    │
│    │ ServiceManager│  │ DeviceScanner  │  │ DeviceMonitor    │    │
│    │ (service.py)  │  │ (scanner.py)   │  │ (monitor.py)     │    │
│    │               │  │                │  │                  │    │
│    │ • start/stop  │  │ • BLE scan     │  │ • RSSI tracking  │    │
│    │ • restart     │  │ • Device list  │  │ • Distance calc  │    │
│    │ • status      │  │ • Distance est │  │ • Alert logic    │    │
│    │ • PID mgmt    │  │                │  │ • Lock handling  │    │
│    └───────────────┘  └────────────────┘  │ • Watchdog       │    │
│                                           └──────┬───────────┘    │
│                                                  │                 │
│                              ┌───────────────────┼────────────┐    │
│                              │                   │            │    │
│                     ┌────────▼──────┐   ┌────────▼──────┐     │    │
│                     │ system.py     │   │ utils.py      │     │    │
│                     │               │   │               │     │    │
│                     │ • lock_macbook│   │ • estimate_   │     │    │
│                     │ • is_screen_  │   │   distance    │     │    │
│                     │   locked      │   │ • smooth_rssi │     │    │
│                     └───────────────┘   │ • Colors      │     │    │
│                                         │ • Flags       │     │    │
│                                         └───────────────┘     │    │
│                              └────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                              ┌─────▼─────┐
                              │ config.py  │
                              │            │
                              │ • .env     │
                              │   loading  │
                              │ • Constants│
                              └────────────┘
```

---

## Data Flow

### Monitoring Flow

1. **`Application.run()`** resolves the operating mode from CLI arguments.
2. **`DeviceMonitor`** initializes a `BleakScanner` with a detection callback.
3. For each BLE advertisement received:
   - `_detection_callback()` filters for the target device.
   - `_process_signal()` appends the RSSI to a rolling buffer and computes a smoothed value.
   - `estimate_distance()` converts the smoothed RSSI to a distance estimate using the Log-Distance Path Loss model.
   - If the distance exceeds the threshold, `_trigger_out_of_range_alert()` calls `system.lock_macbook()`.
4. The **watchdog loop** runs concurrently, monitoring for external screen locks and scanner health.
5. After a lock event, `_handle_screen_lock()` pauses the scanner, waits for unlock, and reconnects with retry logic.

### Scanner Flow

1. **`DeviceScanner.run()`** calls `BleakScanner.discover()` with the configured timeout.
2. Discovered devices are sorted and formatted with RSSI and distance estimates.
3. Results are printed to the terminal.

---

## Key Design Decisions

### Signal Smoothing
Raw RSSI values fluctuate significantly due to multipath propagation, reflections, and environmental interference. B.R.I.O.S. uses a **rolling mean** over a configurable window (`SAMPLE_WINDOW`) to stabilize readings before distance calculations.

### Grace Period
After the screen is unlocked (either by the user or because the device returned), a **grace period** (`GRACE_PERIOD_SECONDS`) suppresses re-triggering. This prevents rapid lock/unlock cycles when the device is near the threshold boundary.

### Lock Loop Protection
If the system detects `LOCK_LOOP_THRESHOLD` lock events within `LOCK_LOOP_WINDOW` seconds, it pauses monitoring for `LOCK_LOOP_PENALTY` seconds. This prevents pathological behavior at the threshold boundary.

### Bleak Monkeypatch
On macOS, the `retrieveAddressForPeripheral_` CoreBluetooth API can return `None` for some peripherals, causing Bleak to crash with an `AttributeError`. B.R.I.O.S. applies a runtime patch to handle this gracefully.
