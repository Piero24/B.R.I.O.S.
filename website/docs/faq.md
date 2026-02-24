---
id: faq
title: FAQ
sidebar_position: 6
---

# Frequently Asked Questions

---

## General

### What is B.R.I.O.S.?

B.R.I.O.S. (**B**luetooth **R**eactive **I**ntelligent **O**perator for Croissant **S**afety) is a professional proximity monitoring system for macOS that automatically locks your Mac when your Bluetooth device moves out of range.

### Why would I use this?

- **Security** — Automatic Mac locking when you walk away
- **Convenience** — Zero-touch security without manual intervention
- **Peace of mind** — Never forget to lock your Mac again
- **Hot-desking** — Instant workspace security in shared offices

### Does it work with any BLE device?

Yes, any BLE 4.0+ compatible device:

- iPhone, iPad, Apple Watch
- Android phones
- AirTags, Tiles
- BLE beacons, fitness trackers, smart watches

---

## Installation & Setup

### What are the system requirements?

- macOS 10.15 (Catalina) or later
- Python 3.9 or higher
- Built-in Bluetooth adapter (all modern Macs)
- Bluetooth permissions for your terminal app

### How do I find my device's MAC address?

```bash
brios --scanner 15 -m
```

This scans for 15 seconds and displays all nearby BLE devices with addresses, names, and signal strengths.

### Why do I get "Permission Denied" errors?

Your terminal needs Bluetooth permissions:

1. Open **System Settings**
2. Go to **Privacy & Security** → **Bluetooth**
3. Enable Bluetooth for your terminal app (Terminal.app, iTerm2, etc.)

### Can I use this without macOS?

The automatic locking feature is macOS-specific. However, the BLE scanning and distance monitoring code is cross-platform and could be adapted for other operating systems.

---

## Configuration

### How accurate is the distance measurement?

Typical accuracy is ±20–30 cm in controlled environments. Factors affecting accuracy:

- Device orientation
- Physical obstacles (walls, furniture)
- Radio interference
- Environmental multipath propagation

### How do I calibrate for better accuracy?

1. Place your device exactly 1 meter from your Mac.
2. Run `brios --target-mac -v` in verbose mode.
3. Note the average RSSI value over 30–60 seconds.
4. Set `TX_POWER_AT_1M` in your `.env` file to that value.

### What's the best distance threshold?

| Threshold | Behavior | Best For |
|---|---|---|
| 1.0–1.5m | Very close proximity | High security (may false-trigger) |
| **2.0m** | **Recommended default** | Balanced sensitivity |
| 3.0–4.0m | Room-level proximity | Triggers when leaving the room |
| 5.0m+ | Large spaces | Warehouses, labs |

### How do I optimize for my environment?

Adjust `PATH_LOSS_EXPONENT` in `.env`:

| Value | Environment |
|---|---|
| 2.0 | Outdoor, no obstacles |
| 2.5–3.0 | Indoor office with light walls |
| 3.5–4.0 | Indoor with heavy walls/obstacles |

---

## Usage

### How do I run it in the background?

```bash
# Start as background service
brios --target-mac -v -f --start

# Check status
brios --status

# Stop service
brios --stop
```

### Can I monitor multiple devices?

Currently, B.R.I.O.S. monitors one device at a time. Multi-device support is planned for a future release.

### How do I view logs?

```bash
# Real-time logs
tail -f ~/.brios/.ble_monitor.log

# Full log
cat ~/.brios/.ble_monitor.log

# Last 50 lines
tail -n 50 ~/.brios/.ble_monitor.log
```

### What happens if my device battery dies?

The monitor detects the device is out of range (no advertisements received) and locks your Mac according to your threshold settings.

---

## Troubleshooting

### "No devices found" when scanning

**Possible causes:**

1. Bluetooth is disabled on your Mac
2. Target device Bluetooth is off
3. Terminal doesn't have Bluetooth permissions
4. Device is too far away or in sleep mode

**Solutions:**

```bash
# Check Bluetooth status
system_profiler SPBluetoothDataType

# Try scanning longer
brios --scanner 30 -m
```

### Monitor keeps triggering false alerts

**Solution 1:** Increase sample window:
```bash
SAMPLE_WINDOW=20  # Default is 12
```

**Solution 2:** Adjust path loss exponent:
```bash
PATH_LOSS_EXPONENT=3.2  # Increase for indoor environments
```

**Solution 3:** Increase threshold:
```bash
DISTANCE_THRESHOLD_M=3.0  # Increase buffer distance
```

### Service won't start

```bash
# Check if already running
brios --status

# Remove stale PID file if needed
rm ~/.brios/.ble_monitor.pid
brios --start

# Run in foreground to see errors
brios --target-mac -v
```

### Mac doesn't lock

Verify the lock command works:

```bash
pmset displaysleepnow
```

Check System Settings:
1. **Energy Saver** — Ensure "Require password" is enabled
2. **Touch ID & Password** — Set "Require password immediately"

![macOS lock screen settings](/img/macos-lock-screen-settings.png)

### High CPU usage

B.R.I.O.S. should use minimal CPU (&lt;1%). If you see high usage:

```bash
# Check for multiple instances
ps aux | grep brios

# Stop all instances
brios --stop

# Restart single instance
brios --target-mac -v -f --start
```

---

## Advanced

### Can I use UUID instead of MAC address?

Yes. On macOS, some devices use privacy-preserving UUIDs:

```bash
# Discover with UUID
brios --scanner 15  # Don't use -m flag

# Monitor with UUID
brios --target-uuid "XXXXXXXX-XXXX-..." -v
```

:::note
UUIDs may change periodically. MAC addresses (with `-m` flag) are more stable and recommended.
:::

### How does the signal smoothing work?

B.R.I.O.S. maintains a rolling buffer (default: 12 samples) and calculates the statistical mean:

```python
smoothed_rssi = mean([-60, -62, -58, -61, ...])  # ≈ -60.25 dBm
```

This eliminates momentary signal drops and provides stable distance measurements.

### Can I integrate this with other automation?

Yes. You can modify the `lock_macbook()` function in `brios/core/system.py` to trigger custom actions:

```python
def lock_macbook() -> Tuple[bool, str]:
    # Your custom action
    subprocess.run(["your_script.sh"])

    # Then lock
    subprocess.run(["pmset", "displaysleepnow"])
    return True, "Custom action executed"
```

---

## Performance

### How much battery does this use?

Minimal! BLE is designed for low energy consumption:

- **BLE advertisements**: ~1–5% battery per day
- **No active connection**: Passive monitoring only
- **No impact on Mac**: Event-driven architecture

### What's the latency?

**Total latency**: 2–15 seconds

| Component | Latency |
|---|---|
| BLE advertisement interval | 100–1000 ms (device-dependent) |
| Sample buffer fill time | 1–12 seconds (depends on `SAMPLE_WINDOW`) |
| Distance calculation | < 1 ms |
| Mac lock command | 100–500 ms |

### Can I make it faster?

Reduce `SAMPLE_WINDOW`:

```bash
SAMPLE_WINDOW=5   # Faster response, less stable
SAMPLE_WINDOW=12  # Balanced (default)
SAMPLE_WINDOW=20  # Slower response, more stable
```

---

## Security & Privacy

### Is my data sent anywhere?

**No.** B.R.I.O.S.:

- ✅ Runs 100% locally
- ✅ No internet connection required
- ✅ No data collection or telemetry
- ✅ Open source and auditable

### What data is logged?

Only operational data: timestamps, RSSI values, calculated distances, and alert events. **No personal data** is logged.

### Can someone spoof my device?

**Theoretical risk:** Someone could broadcast with your device's MAC address.

**Mitigations:**

1. BLE MAC addresses cycle on modern devices (privacy feature)
2. Distance verification adds extra validation
3. This is a convenience tool, not a security perimeter

**Recommendation:** Use in combination with screen lock timeout, automatic logout, and FileVault disk encryption.

---

## Still Have Questions?

1. Search [existing issues](https://github.com/Piero24/B.R.I.O.S./issues)
2. Open a [new issue](https://github.com/Piero24/B.R.I.O.S./issues/new) with the `question` label
3. Start a [discussion](https://github.com/Piero24/B.R.I.O.S./discussions)
