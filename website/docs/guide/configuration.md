---
id: configuration
title: Configuration
sidebar_position: 1
---

# Configuration

B.R.I.O.S. is configured through environment variables, typically set in a `.env` file. This page documents every available parameter.

---

## Configuration File Locations

B.R.I.O.S. loads environment variables from the following locations, in order (later files do **not** override earlier ones):

| Priority | Location | Description |
|---|---|---|
| 1 | `.env` | Current working directory |
| 2 | `~/.brios.env` | Home directory file |
| 3 | `~/.brios/config` | Dedicated config directory |
| 4 | `~/.brios/.env` | Dedicated config directory (alternate) |
| 5 | `~/.config/brios/config` | XDG-compliant config path |

### Quick Setup

**Homebrew installation:**

```bash
# Create a config file in your home directory (recommended)
cp $(brew --prefix brios)/share/brios/.env.example ~/.brios.env
```

**Manual installation:**

```bash
cp .env.example ~/.brios.env
```

---

## Parameter Reference

:::warning Personalize for Your Environment
The default values listed below are **baseline approximations** for a typical indoor office setup. For reliable results, you **must calibrate** the signal parameters (`TX_POWER_AT_1M`, `PATH_LOSS_EXPONENT`, `DISTANCE_THRESHOLD_M`) for your **specific environment** — your office layout, physical obstacles, device model, and even device case can significantly affect RSSI readings.

See the [Calibrating TX Power](#calibrating-tx-power) and [Path Loss Exponent Guide](#path-loss-exponent-guide) sections below for step-by-step instructions.
:::

### Target Device

| Parameter | Type | Default | Description |
|---|---|---|---|
| `TARGET_DEVICE_MAC_ADDRESS` | `string` | *Required* | MAC address of the Bluetooth device to track (e.g., `AA:BB:CC:DD:EE:FF`) |
| `TARGET_DEVICE_UUID_ADDRESS` | `string` | — | UUID address for macOS privacy mode (e.g., `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`) |
| `TARGET_DEVICE_NAME` | `string` | `"Unknown Device Name"` | Human-readable name for the device, used in logs and alerts |
| `TARGET_DEVICE_TYPE` | `string` | `"Unknown Device"` | Device type descriptor (e.g., `"phone"`, `"watch"`, `"tablet"`) |

### Distance & Signal

| Parameter | Type | Default | Description |
|---|---|---|---|
| `DISTANCE_THRESHOLD_M` | `float` | `2.0` | Distance in meters beyond which the device is considered "out of range" and the Mac will be locked |
| `TX_POWER_AT_1M` | `int` | `-59` | RSSI value (in dBm) measured at exactly 1 meter from the device. Critical for accurate distance estimation |
| `PATH_LOSS_EXPONENT` | `float` | `2.8` | Environment factor for the path loss model. Ranges from `2.0` (open space) to `4.0` (heavy obstacles) |
| `SAMPLE_WINDOW` | `int` | `12` | Number of RSSI samples to average for signal smoothing. Higher values = more stable but slower response |

### Safety & Reliability

| Parameter | Type | Default | Description |
|---|---|---|---|
| `GRACE_PERIOD_SECONDS` | `int` | `30` | Seconds to ignore out-of-range signals after unlocking/resuming. Prevents immediate re-locking while the signal stabilizes |
| `LOCK_LOOP_THRESHOLD` | `int` | `3` | Number of lock events within `LOCK_LOOP_WINDOW` that trigger the lock loop protection |
| `LOCK_LOOP_WINDOW` | `int` | `60` | Time window (seconds) for detecting lock loops |
| `LOCK_LOOP_PENALTY` | `int` | `120` | Pause duration (seconds) when a lock loop is detected |

---

## Calibrating TX Power

For the most accurate distance measurements, calibrate `TX_POWER_AT_1M` for your specific device:

1. Place your target device exactly **1 meter** from your Mac.
2. Run the monitor in verbose mode:
   ```bash
   brios --target-mac -v
   ```
3. Observe the RSSI readings for 30–60 seconds and note the **average value**.
4. Set `TX_POWER_AT_1M` to that value in your `.env` file.

:::tip Typical TX Power Values
- **iPhone**: −55 to −62 dBm
- **Android phones**: −50 to −65 dBm
- **Apple Watch**: −55 to −60 dBm
- **AirTags / Tiles**: −58 to −65 dBm
:::

---

## Path Loss Exponent Guide

The `PATH_LOSS_EXPONENT` models how quickly the signal attenuates in your environment:

| Value | Environment | Use Case |
|---|---|---|
| `2.0` | Free space / outdoors | Open-plan outdoor desks |
| `2.5` | Light indoor, no walls | Open-plan office |
| `2.8` | Indoor office (default) | Standard office with cubicles |
| `3.0–3.5` | Indoor with light walls | Home office, apartments |
| `3.5–4.0` | Indoor with heavy walls | Concrete/brick buildings |

---

## Distance Threshold Recommendations

| Threshold | Behavior | Best For |
|---|---|---|
| `1.0–1.5m` | Very close proximity | High-security environments (may trigger if you lean back) |
| `2.0m` | **Recommended default** | Balanced sensitivity for typical desks |
| `3.0–4.0m` | Room-level proximity | Triggers when you leave the room |
| `5.0m+` | Large-space monitoring | Warehouses, labs, open floors |

---

## Example Configuration

```bash
# Target Device
TARGET_DEVICE_MAC_ADDRESS=AA:BB:CC:DD:EE:FF
TARGET_DEVICE_NAME=My iPhone
TARGET_DEVICE_TYPE=phone

# Distance & Signal
DISTANCE_THRESHOLD_M=2.0
TX_POWER_AT_1M=-59
PATH_LOSS_EXPONENT=2.8
SAMPLE_WINDOW=12

# Safety
GRACE_PERIOD_SECONDS=30
LOCK_LOOP_THRESHOLD=3
LOCK_LOOP_WINDOW=60
LOCK_LOOP_PENALTY=120
```
