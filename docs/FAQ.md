# ❓ Frequently Asked Questions

Quick answers to common questions about 🥐 B.R.I.O.S. (Bluetooth Reactive Intelligent Operator for Croissant Safety).

---

## General

### What is B.R.I.O.S.?

B.R.I.O.S. (Bluetooth Reactive Intelligent Operator for Croissant Safety) is a professional proximity monitoring system for macOS that automatically locks your Mac when your iPhone, Apple Watch, or other Bluetooth device moves out of range.

### Why would I use this?

- **Security**: Automatic Mac locking when you walk away
- **Convenience**: Zero-touch security without manual intervention
- **Peace of Mind**: Never forget to lock your Mac again
- **Hot-desking**: Instant workspace security in shared offices

### Does it work with any BLE device?

Yes! Any BLE 4.0+ compatible device:
- iPhone, iPad, Apple Watch
- Android phones
- AirTags, Tiles
- BLE beacons
- Fitness trackers
- Smart watches

---

## Installation & Setup

### What are the system requirements?

- macOS 10.15 (Catalina) or later
- Python 3.9 or higher
- Built-in Bluetooth adapter (all modern Macs have this)
- Bluetooth permissions for your terminal app

### How do I find my device's MAC address?

```bash
# Use the built-in scanner
python3 main.py --scanner 15 -m
```

This will show all nearby BLE devices with their addresses, names, and signal strengths.

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

Typical accuracy is ±20-30cm in controlled environments. Factors affecting accuracy:
- Device orientation
- Physical obstacles (walls, furniture)
- Radio interference
- Environmental multipath propagation

### How do I calibrate for better accuracy?

1. Place your device exactly 1 meter from your Mac
2. Run monitor in verbose mode: `python3 main.py --target-mac -v`
3. Note the average RSSI value over 30-60 seconds
4. Update `TX_POWER_AT_1M` in your `.env` file with this value

### What's the best distance threshold?

Depends on your needs:
- **1.0-1.5m**: Very close proximity (high security, may trigger if you lean away)
- **2.0m**: Recommended default (balanced)
- **3.0-4.0m**: Room-level proximity (leaving the room)
- **5.0m+**: Large spaces

### How do I optimize for my environment?

Adjust `PATH_LOSS_EXPONENT` in `.env`:
- **2.0**: Outdoor, no obstacles
- **2.5-3.0**: Indoor office with light walls
- **3.5-4.0**: Indoor with heavy walls/obstacles

---

## Usage

### How do I run it in the background?

```bash
# Start as background service
python3 main.py --target-mac -v -f --start

# Check status
python3 main.py --status

# Stop service
python3 main.py --stop
```

### Can I monitor multiple devices?

Currently, B.R.I.O.S. monitors one device at a time. Multi-device support is planned for a future release.

### How do I view logs?

```bash
# Real-time logs (if service is running with -f flag)
tail -f .ble_monitor.log

# View full log
cat .ble_monitor.log

# View last 50 lines
tail -n 50 .ble_monitor.log
```

### What happens if my device battery dies?

The monitor will detect the device is out of range (no advertisements received) and lock your Mac according to your threshold settings.

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

# Ensure permissions are granted
# System Settings → Privacy & Security → Bluetooth

# Try scanning longer
python3 main.py --scanner 30 -m
```

### Monitor keeps triggering false alerts

**Solution 1: Increase sample window**
```bash
# In .env file
SAMPLE_WINDOW=20  # Default is 12
```

**Solution 2: Adjust path loss exponent**
```bash
# In .env file
PATH_LOSS_EXPONENT=3.2  # Increase if indoors
```

**Solution 3: Increase threshold**
```bash
# In .env file
DISTANCE_THRESHOLD_M=3.0  # Increase buffer distance
```

### Service won't start

**Check if already running:**
```bash
python3 main.py --status
```

**If stale PID file exists:**
```bash
rm .ble_monitor.pid
python3 main.py --start
```

**Check for errors:**
```bash
python3 main.py --target-mac -v  # Run in foreground to see errors
```

### Mac doesn't lock

**Verify lock command works:**
```bash
pmset displaysleepnow
```

**Check System Settings:**
1. **Energy Saver**: Ensure "Require password" is enabled
2. **Touch ID & Password**: Set "Require password immediately"

### High CPU usage

This is unexpected. B.R.I.O.S. should use minimal CPU (<1%).

**Diagnose:**
```bash
# Check if multiple instances running
ps aux | grep main.py

# Stop all instances
python3 main.py --stop
killall python3  # If needed

# Restart single instance
python3 main.py --target-mac -v -f --start
```

---

## Advanced

### Can I use UUID instead of MAC address?

Yes! macOS uses privacy-preserving UUIDs for some devices:

```bash
# Discover with UUID
python3 main.py --scanner 15  # Don't use -m flag

# Monitor with UUID
python3 main.py --target-uuid "XXXXXXXX-XXXX..." -v
```

**Note**: UUIDs may change periodically. MAC addresses (with `-m` flag) are more stable.

### How does the signal smoothing work?

B.R.I.O.S. maintains a rolling buffer (default: 12 samples) and calculates the statistical mean:

```python
smoothed_rssi = mean([-60, -62, -58, -61, ...])  # ≈ -60.25 dBm
```

This eliminates momentary signal drops and provides stable distance measurements.

### Can I integrate this with other automation?

Yes! You can modify `_lock_macbook()` method to trigger custom actions:

```python
def _lock_macbook(self) -> str:
    # Your custom action
    subprocess.run(["your_script.sh"])
    
    # Then lock
    subprocess.run(["pmset", "displaysleepnow"])
    return "Custom action executed"
```

### How can I contribute?

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines on:
- Reporting bugs
- Suggesting features
- Submitting code
- Running tests

---

## Performance

### How much battery does this use on my device?

Minimal! BLE is designed for low energy consumption:
- **BLE advertisements**: ~1-5% battery per day
- **No active connection**: Passive monitoring only
- **No impact on Mac**: Event-driven architecture

### What's the latency for alerts?

**Total latency**: 2-15 seconds
- **BLE advertisement interval**: 100-1000ms (device-dependent)
- **Sample buffer fill time**: 1-12 seconds (depends on SAMPLE_WINDOW)
- **Distance calculation**: <1ms
- **Mac lock command**: 100-500ms

### Can I make it faster?

Yes, reduce `SAMPLE_WINDOW`:

```bash
# In .env
SAMPLE_WINDOW=5  # Faster response, less stable

# Default
SAMPLE_WINDOW=12  # Balanced

# More stable
SAMPLE_WINDOW=20  # Slower response, more stable
```

---

## Security & Privacy

### Is my data sent anywhere?

**No!** B.R.I.O.S.:
- ✅ Runs 100% locally
- ✅ No internet connection required
- ✅ No data collection
- ✅ No telemetry or analytics
- ✅ Open source and auditable

### What data is logged?

Only operational data:
- Timestamps
- RSSI values
- Calculated distances
- Alert events

**No personal data** is logged.

### Can someone spoof my device to prevent locking?

**Theoretical attack**: Someone could broadcast with your device's MAC address.

**Mitigations**:
1. BLE MAC addresses cycle on modern devices (privacy feature)
2. Distance verification adds extra validation
3. This is a convenience tool, not a security perimeter

**Recommendation**: Use in combination with:
- Screen lock timeout (macOS setting)
- Automatic logout after inactivity
- FileVault disk encryption

---

## Still Have Questions?

1. **Search**: Check [existing issues](https://github.com/Piero24/B.R.I.O.S./issues)
2. **Ask**: Open a [new issue](https://github.com/Piero24/B.R.I.O.S./issues/new) with the `question` label
3. **Discuss**: Start a [discussion](https://github.com/Piero24/B.R.I.O.S./discussions)

---

*Last updated: November 2, 2024*
