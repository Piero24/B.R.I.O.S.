<div id="top"></div>
<br/>
<br/>

<p align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/3145/3145073.png" width="105" height="100">
</p>
<h1 align="center">
    <a href="https://github.com/Piero24/B.R.I.O.S.">B.R.I.O.S.</a>
</h1>
<p align="center">
    <!-- BADGE -->
    <!--
        *** You can make other badges here
        *** [shields.io](https://shields.io/)
        *** or here
        *** [CircleCI](https://circleci.com/)
    -->
    <a href="https://github.com/Piero24/B.R.I.O.S./commits/main">
    <img src="https://img.shields.io/github/last-commit/piero24/B.R.I.O.S.">
    </a>
    <a href="https://github.com/Piero24/B.R.I.O.S.">
    <img src="https://img.shields.io/badge/Maintained-yes-green.svg">
    </a>
    <!--<a href="https://github.com/Piero24/B.R.I.O.S.">
    <img src="https://img.shields.io/badge/Maintained%3F-no-red.svg">
    </a> -->
    <a href="https://github.com/Piero24/B.R.I.O.S./issues">
    <img src="https://img.shields.io/github/issues/piero24/B.R.I.O.S.">
    </a>
    <a href="https://github.com/Piero24/B.R.I.O.S./blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/piero24/B.R.I.O.S.">
    </a>
</p>
<p align="center">
    A professional BLE proximity monitor that automatically locks your Mac when your device moves out of range
    <br/>
    <br/>
    <a href="#prerequisites">Requirements</a>
    •
    <a href="https://github.com/Piero24/B.R.I.O.S./issues">Report Bug</a>
    •
    <a href="https://github.com/Piero24/B.R.I.O.S./issues">Request Feature</a>
</p>


---


---

<br/>

## 📖 Table of Contents

- [Introduction](#introduction)
- [How It Works](#how-it-works)
- [Features](#features)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Discovery Mode](#discovery-mode)
  - [Monitor Mode](#monitor-mode)
  - [Background Service](#background-service)
- [Configuration](#configuration)
- [Example Output](#example-output)
- [Technical Details](#technical-details)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

<p align="right"><a href="#top">⇧</a></p>

---

<br/>

<h2 id="introduction">📔 Introduction</h2>

**B.R.I.O.S.** is a professional-grade Bluetooth Low Energy (BLE) proximity monitoring tool designed specifically for macOS. It continuously tracks the distance to a designated BLE device (such as your iPhone, Apple Watch, or any BLE beacon) and automatically **locks your Mac** when the device moves beyond a configurable distance threshold.

<br/>

### Why B.R.I.O.S.?

- **Security Enhancement**: Automatically lock your Mac when you walk away with your phone
- **Seamless Experience**: Works silently in the background without interrupting your workflow
- **Smart Detection**: Uses advanced RSSI signal smoothing for accurate distance estimation
- **Privacy-Focused**: All processing happens locally on your Mac
- **Highly Configurable**: Customize thresholds, calibration parameters, and monitoring behavior

<br/>

<div align="center">
  <img src="https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=800&auto=format&fit=crop" width="80%">
  <p><i>Keep your Mac secure by monitoring your device's proximity</i></p>
</div>

<p align="right"><a href="#top">⇧</a></p>

---

<br/>

<h2 id="how-it-works">⚙️ How It Works</h2>

B.R.I.O.S. employs a sophisticated distance estimation algorithm based on the **Log-Distance Path Loss Model**, which calculates the distance between your Mac and the target BLE device using signal strength (RSSI).

<br/>

### The Process

1. **📡 Signal Monitoring**
   - Continuously scans for BLE advertisements from your target device
   - Collects RSSI (Received Signal Strength Indicator) values in real-time

2. **📊 Signal Smoothing**
   - Maintains a rolling buffer of recent RSSI samples (default: 12 readings)
   - Calculates statistical mean to filter out momentary fluctuations
   - Provides stable, reliable distance measurements

3. **📏 Distance Calculation**
   - Applies the Log-Distance Path Loss formula:
   
   $$d = 10^{\frac{TX_{power} - RSSI}{10 \cdot n}}$$
   
   Where:
   - $d$ = estimated distance in meters
   - $TX_{power}$ = calibrated signal strength at 1 meter
   - $RSSI$ = smoothed signal strength reading
   - $n$ = path loss exponent (environment-dependent)

4. **🚨 Proximity Alert**
   - Compares calculated distance against configured threshold
   - Triggers MacBook lock when device moves out of range
   - Sends notification when device returns to range

<br/>

<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Signal_strength_vs_distance.svg/800px-Signal_strength_vs_distance.svg.png" width="60%">
  <p><i>Signal strength decreases logarithmically with distance</i></p>
</div>

<p align="right"><a href="#top">⇧</a></p>

---

<br/>

<h2 id="features">✨ Features</h2>

### Core Functionality

- ✅ **Real-time BLE Device Monitoring** - Continuous tracking of device proximity
- ✅ **Automatic Mac Locking** - Instant lock when device moves out of range  
- ✅ **Distance Estimation** - Accurate distance calculation using RSSI signal analysis
- ✅ **Signal Smoothing** - Configurable rolling average to eliminate false positives

### Operating Modes

- 🔍 **Discovery Scanner** - Find nearby BLE devices and their addresses
- 👁️ **Monitor Mode** - Real-time foreground monitoring with verbose output
- 🔄 **Background Service** - Run as a daemon with full service management

### Advanced Features

- 📝 **File Logging** - Optional persistent logging to disk
- 🔧 **Highly Configurable** - Customize all parameters via `.env` file
- 🍎 **macOS-Optimized** - Native support for both UUID and BD_ADDR modes
- 📊 **Verbose Output** - Detailed RSSI, distance, and signal strength reporting
- 🧪 **Fully Tested** - Comprehensive test suite with pytest

<p align="right"><a href="#top">⇧</a></p>

---

<br/>

<h2 id="requirements">🧰 Requirements</h2>

### System Requirements

- **macOS** 10.15 (Catalina) or later
- **Python** 3.9 or higher
- **Bluetooth** Low Energy compatible adapter (built-in on all modern Macs)

### Python Dependencies

The project uses the following main libraries:

- **`bleak`** - Cross-platform BLE library for Python
- **`python-dotenv`** - Environment configuration management
- **`pyobjc-framework-CoreBluetooth`** - macOS CoreBluetooth bindings

All dependencies are listed in `requirements.txt`.

<p align="right"><a href="#top">⇧</a></p>

---

<br/>

<h2 id="quick-start">🚀 Quick Start</h2>

Get up and running in 5 minutes!

<br/>

### 1. Clone the Repository

```bash
git clone https://github.com/Piero24/B.R.I.O.S..git
cd B.R.I.O.S.
```

<br/>

### 2. Create a Virtual Environment

```bash
python3 -m venv env
source env/bin/activate  # On macOS/Linux
```

<br/>

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

<br/>

### 4. Configure Your Device

First, discover your device's BLE address:

```bash
python3 main.py --scanner 15 -m
```

This will scan for 15 seconds and display all nearby BLE devices with their MAC addresses.

<br/>

### 5. Set Up Configuration

Copy the example configuration file and edit it with your device details:

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Update the following values:

```bash
TARGET_DEVICE_MAC_ADDRESS=XX:XX:XX:XX:XX:XX  # Your device's MAC address
TARGET_DEVICE_NAME=My iPhone                   # Human-readable name
TARGET_DEVICE_TYPE=iPhone 15 Pro              # Device type
DISTANCE_THRESHOLD_M=2.0                      # Lock distance in meters
```

<br/>

### 6. Test the Monitor

Run in foreground mode to test:

```bash
python3 main.py --target-mac -v
```

You should see real-time RSSI and distance updates!

<br/>

### 7. Start as Background Service

Once everything works, start the monitor as a background service:

```bash
python3 main.py --target-mac -v -f --start
```

Check the status:

```bash
python3 main.py --status
```

<p align="right"><a href="#top">⇧</a></p>

---

<br/>

<h2 id="usage">📚 Usage</h2>

B.R.I.O.S. supports three primary operating modes:

<br/>

<h3 id="discovery-mode">🔍 Discovery Mode</h3>

Scan for nearby BLE devices to find your target device's address:

```bash
# Scan for 15 seconds (default) using MAC addresses
python3 main.py --scanner 15 -m

# Scan for 30 seconds in UUID mode (macOS privacy)
python3 main.py --scanner 30

# Scan with verbose output
python3 main.py --scanner 10 -m -v
```

**Example Output:**

```
BLE Device Scanner
──────────────────────────────────────────────────────────────────────
Duration:   15 seconds
Mode:       BD_ADDR (MAC addresses)
Verbose:    Enabled (showing RSSI and distance estimates)
──────────────────────────────────────────────────────────────────────

● Scanning...

Scan Results (5 devices found)
──────────────────────────────────────────────────────────────────────
 1. Pietro's iPhone            │ A1:B2:C3:D4:E5:F6 │  -45 dBm │ ~ 0.32m
 2. Apple Watch                │ B2:C3:D4:E5:F6:A1 │  -58 dBm │ ~ 0.95m
 3. AirPods Pro                │ C3:D4:E5:F6:A1:B2 │  -72 dBm │ ~ 3.45m
 4. (Unknown)                  │ D4:E5:F6:A1:B2:C3 │  -85 dBm │ ~10.23m
 5. Smart Lock                 │ E5:F6:A1:B2:C3:D4 │  -91 dBm │ ~18.67m
```

<br/>

<h3 id="monitor-mode">👁️ Monitor Mode (Foreground)</h3>

Run the monitor in the foreground with real-time output:

```bash
# Monitor using default MAC address from .env
python3 main.py --target-mac -v

# Monitor specific device by MAC address
python3 main.py --target-mac "A1:B2:C3:D4:E5:F6" -m -v

# Monitor using UUID (macOS privacy mode)
python3 main.py --target-uuid -v

# Monitor with file logging enabled
python3 main.py --target-mac -v -f
```

**Example Output:**

```
Starting BLE Monitor
──────────────────────────────────────────────────────────────────────
Target:     Pietro's iPhone (iPhone 15 Pro)
Address:    A1:B2:C3:D4:E5:F6
Threshold:  2.0m
TX Power:   -59 dBm @ 1m
Path Loss:  2.8
Samples:    12 readings
Mode:       BD_ADDR (MAC)
──────────────────────────────────────────────────────────────────────
Output:     Terminal + File
Log file:   /Users/pietrobon/Desktop/B.R.I.O.S./.ble_monitor.log

● Monitoring active - Press Ctrl+C to stop

[14:32:15] RSSI:  -52 dBm → Smoothed:  -51.3 dBm │ Distance:  0.56m │ Signal: Strong
[14:32:16] RSSI:  -54 dBm → Smoothed:  -52.1 dBm │ Distance:  0.61m │ Signal: Strong
[14:32:17] RSSI:  -56 dBm → Smoothed:  -53.8 dBm │ Distance:  0.71m │ Signal: Strong
[14:32:18] RSSI:  -58 dBm → Smoothed:  -55.2 dBm │ Distance:  0.81m │ Signal: Strong
[14:32:19] RSSI:  -71 dBm → Smoothed:  -64.5 dBm │ Distance:  1.87m │ Signal: Medium

──────────────────────────────────────────────────────────────────────
⚠  ALERT: Device moved out of range
   Device:    Pietro's iPhone
   Distance:  ~3.42m (threshold: 2.0m)
   Time:      14:32:23
   Action:    🔒 MacBook locked (password required)
──────────────────────────────────────────────────────────────────────
```

<br/>

<h3 id="background-service">🔄 Background Service (Daemon Mode)</h3>

Run B.R.I.O.S. as a persistent background service:

<br/>

**Start the service:**

```bash
python3 main.py --target-mac -v -f --start
```

**Check service status:**

```bash
python3 main.py --status
```

**Example Status Output:**

```
BLE Monitor Status
──────────────────────────────────────────────────────────────────────
Status:     ● RUNNING
PID:        42531
Uptime:     2:15:43
Target:     Pietro's iPhone
Address:    A1:B2:C3:D4:E5:F6
Threshold:  2.0m

Log file:   /Users/pietrobon/Desktop/B.R.I.O.S./.ble_monitor.log

Recent activity:
  [16:47:32] RSSI:  -61 dBm → Smoothed:  -60.2 dBm │ Distance:  1.23m
  [16:47:33] RSSI:  -59 dBm → Smoothed:  -59.8 dBm │ Distance:  1.15m
  [16:47:34] RSSI:  -62 dBm → Smoothed:  -60.7 dBm │ Distance:  1.29m
──────────────────────────────────────────────────────────────────────
```

<br/>

**Stop the service:**

```bash
python3 main.py --stop
```

**Restart the service:**

```bash
python3 main.py --restart
```

<br/>

### Command-Line Arguments Reference

| Argument | Short | Description |
|----------|-------|-------------|
| `--scanner SECONDS` | `-s` | Discover BLE devices (5-60s range) |
| `--target-mac [ADDRESS]` | `-tm` | Monitor by MAC address |
| `--target-uuid [UUID]` | `-tu` | Monitor by UUID (macOS privacy) |
| `--macos-use-bdaddr` | `-m` | Force MAC address mode on macOS |
| `--verbose` | `-v` | Enable detailed output |
| `--file-logging` | `-f` | Enable logging to file |
| `--start` | | Start as background daemon |
| `--stop` | | Stop background daemon |
| `--restart` | | Restart background daemon |
| `--status` | | Show daemon status |

<p align="right"><a href="#top">⇧</a></p>

---

<br/>

<h2 id="configuration">⚙️ Configuration</h2>

All configuration is managed via the `.env` file. Copy `.env.example` to `.env` and customize:

<br/>

### Device Configuration

```bash
# Your device's MAC address (use scanner to find it)
TARGET_DEVICE_MAC_ADDRESS=XX:XX:XX:XX:XX:XX

# Your device's UUID (macOS privacy mode)
TARGET_DEVICE_UUID_ADDRESS=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX

# Human-readable device name
TARGET_DEVICE_NAME=My iPhone

# Device type for identification
TARGET_DEVICE_TYPE=iPhone 15 Pro
```

<br/>

### Signal Processing Parameters

```bash
# TX Power: Signal strength (dBm) at 1 meter distance
# This value is device-specific. Calibrate by measuring RSSI at exactly 1m
# Typical values: -59 for most phones, -55 to -65 for wearables
TX_POWER_AT_1M=-59

# Path Loss Exponent: Environmental signal degradation factor
# 2.0 = Free space (outdoor, line of sight)
# 2.5-3.0 = Indoor, minimal obstacles
# 3.0-4.0 = Indoor with walls/furniture
# Recommended: 2.8 for typical indoor environments
PATH_LOSS_EXPONENT=2.8

# Sample Window: Number of RSSI readings to average
# Higher = more stable, but slower response
# Lower = faster response, but more noise
# Recommended: 10-15 for best balance
SAMPLE_WINDOW=12
```

<br/>

### Monitoring Behavior

```bash
# Distance Threshold: Lock trigger distance in meters
# Device must exceed this distance to trigger lock
# Recommended: 2.0-5.0 meters depending on your use case
DISTANCE_THRESHOLD_M=2.0
```

<br/>

### Calibration Tips

For best accuracy, calibrate `TX_POWER_AT_1M` for your specific device:

1. Place your device **exactly 1 meter** from your Mac
2. Run the monitor with verbose mode: `python3 main.py --target-mac -v`
3. Note the average RSSI value after readings stabilize
4. Set `TX_POWER_AT_1M` to this average value in your `.env` file

<p align="right"><a href="#top">⇧</a></p>

---

<br/>

<h2 id="example-output">📸 Example Output</h2>

### Successful Lock Trigger

```
[15:23:45] RSSI:  -58 dBm → Smoothed:  -57.2 dBm │ Distance:  0.95m │ Signal: Strong
[15:23:46] RSSI:  -67 dBm → Smoothed:  -63.8 dBm │ Distance:  1.76m │ Signal: Medium
[15:23:47] RSSI:  -75 dBm → Smoothed:  -69.1 dBm │ Distance:  2.81m │ Signal: Weak

──────────────────────────────────────────────────────────────────────
⚠  ALERT: Device moved out of range
   Device:    Pietro's iPhone
   Distance:  ~2.81m (threshold: 2.0m)
   Time:      15:23:47
   Action:    🔒 MacBook locked (password required)
──────────────────────────────────────────────────────────────────────

[15:24:02] RSSI:  -78 dBm → Smoothed:  -74.3 dBm │ Distance:  3.98m │ Signal: Weak
[15:24:03] RSSI:  -81 dBm → Smoothed:  -77.6 dBm │ Distance:  5.12m │ Signal: Weak
```

<br/>

### Device Returns to Range

```
[15:25:18] RSSI:  -72 dBm → Smoothed:  -70.2 dBm │ Distance:  3.01m │ Signal: Weak
[15:25:19] RSSI:  -65 dBm → Smoothed:  -66.8 dBm │ Distance:  2.15m │ Signal: Medium
[15:25:20] RSSI:  -58 dBm → Smoothed:  -62.1 dBm │ Distance:  1.52m │ Signal: Medium

────────────────────────────────────────────────────────────────────────
✓  Device Back in Range
   Device:    Pietro's iPhone
   Distance:  ~1.52m (Threshold: 2.0m)
   Time:      15:25:20
   Status:    🔓 Ready to unlock MacBook
────────────────────────────────────────────────────────────────────────
```

<p align="right"><a href="#top">⇧</a></p>

---

<br/>

<h2 id="technical-details">🔬 Technical Details</h2>

### Distance Estimation Algorithm

B.R.I.O.S. uses the **Log-Distance Path Loss Model**, which is one of the most widely used models for indoor distance estimation:

$$d = 10^{\frac{TX_{power} - RSSI_{smoothed}}{10 \cdot n}}$$

Where:
- **$d$**: Estimated distance in meters
- **$TX_{power}$**: Reference signal strength at 1 meter (calibrated)
- **$RSSI_{smoothed}$**: Smoothed signal strength reading
- **$n$**: Path loss exponent (environment-dependent)

<br/>

### Signal Smoothing

To minimize false positives from temporary signal fluctuations, B.R.I.O.S. implements a **rolling average filter**:

1. Maintains a circular buffer (deque) of the last $N$ RSSI samples
2. Calculates the statistical mean of these samples
3. Uses the smoothed value for distance calculation

This approach provides:
- **Stability**: Eliminates temporary spikes/drops
- **Responsiveness**: Still reacts to genuine distance changes
- **Accuracy**: Reduces measurement noise

<br/>

### macOS Bluetooth Modes

macOS offers two BLE addressing modes:

| Mode | Address Type | When to Use |
|------|-------------|-------------|
| **UUID** | Random identifier | Default, preserves privacy |
| **BD_ADDR** | Real MAC address | Better reliability, use `-m` flag |

> **Recommendation**: Always use `-m` flag for consistent device tracking

<br/>

### Architecture Overview

```
main.py
├── Application (Main orchestrator)
│   ├── ServiceManager (Daemon lifecycle)
│   │   ├── start()
│   │   ├── stop()
│   │   ├── restart()
│   │   └── display_status()
│   │
│   ├── DeviceScanner (Discovery mode)
│   │   └── run()
│   │
│   └── DeviceMonitor (Proximity tracking)
│       ├── _detection_callback()
│       ├── _process_signal()
│       ├── _estimate_distance()
│       ├── _smooth_rssi()
│       └── _lock_macbook()
│
└── Utility Functions
    ├── _estimate_distance()
    └── _smooth_rssi()
```

<p align="right"><a href="#top">⇧</a></p>

---

<br/>

<h2 id="testing">🧪 Testing</h2>

B.R.I.O.S. includes a comprehensive test suite using `pytest`:

<br/>

### Run All Tests

```bash
# Activate virtual environment first
source env/bin/activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest test_ble_monitor.py -v
```

<br/>

### Run Specific Tests

```bash
# Test distance estimation
pytest test_ble_monitor.py::test_estimate_distance -v

# Test signal smoothing
pytest test_ble_monitor.py::test_smooth_rssi -v

# Test alert triggering
pytest test_ble_monitor.py::test_device_monitor_alerts -v
```

<br/>

### Test Coverage

The test suite covers:
- ✅ Distance calculation accuracy
- ✅ RSSI smoothing algorithm
- ✅ Device scanner discovery
- ✅ Alert triggering logic
- ✅ Service lifecycle management
- ✅ CLI argument parsing

<br/>

### Using Makefile

You can also use the provided `Makefile` for common tasks:

```bash
# Format code with Pyink
make format

# Run the application
make run ARGS="--target-mac -v"

# Format and run
make ble:run ARGS="--scanner 15 -m"
```

<p align="right"><a href="#top">⇧</a></p>

---

<br/>

<h2 id="troubleshooting">🔧 Troubleshooting</h2>

<br/>

### Bluetooth Permission Issues

**Problem**: Scanner fails to start or doesn't find devices

**Solution**:
1. Open **System Preferences** → **Security & Privacy** → **Privacy**
2. Select **Bluetooth** from the left sidebar
3. Ensure **Terminal** (or your terminal app) has Bluetooth permission
4. If using VS Code's integrated terminal, grant VS Code Bluetooth access

<br/>

### Device Not Found

**Problem**: Target device doesn't appear in scanner results

**Solutions**:
- Ensure Bluetooth is enabled on both your Mac and the target device
- Make sure the device is **not** connected to your Mac (disconnect in Bluetooth settings)
- Try scanning for longer duration: `--scanner 30`
- Use `-m` flag to see real MAC addresses: `--scanner 15 -m`
- Ensure the device is advertising (not in sleep mode)

<br/>

### False Positives (Premature Locking)

**Problem**: Mac locks even when device is nearby

**Solutions**:
- **Increase sample window**: Set `SAMPLE_WINDOW=15` or higher in `.env`
- **Recalibrate TX power**: Measure actual RSSI at 1 meter and update `TX_POWER_AT_1M`
- **Adjust path loss exponent**: Increase `PATH_LOSS_EXPONENT` to 3.0-3.5 for obstacle-rich environments
- **Increase threshold**: Set `DISTANCE_THRESHOLD_M=3.0` or higher

<br/>

### Slow Response Time

**Problem**: Delayed lock when walking away

**Solutions**:
- **Decrease sample window**: Set `SAMPLE_WINDOW=8` in `.env` (faster but less stable)
- **Decrease threshold**: Set `DISTANCE_THRESHOLD_M=1.5` for earlier triggering
- Ensure Bluetooth isn't being interfered with by Wi-Fi or other devices

<br/>

### Service Won't Start

**Problem**: `--start` command fails silently

**Solutions**:
```bash
# Check if service is already running
python3 main.py --status

# View log file for errors
cat .ble_monitor.log

# Try running in foreground first to debug
python3 main.py --target-mac -v

# Ensure .env file exists and is configured
ls -la .env
cat .env
```

<br/>

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'bleak'`

**Solution**:
```bash
# Ensure virtual environment is activated
source env/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep bleak
```

<p align="right"><a href="#top">⇧</a></p>

---

<br/>

<h2 id="contributing">🤝 Contributing</h2>

Contributions are welcome and greatly appreciated! Here's how you can help:

<br/>

### Ways to Contribute

- 🐛 **Report bugs** via [GitHub Issues](https://github.com/Piero24/B.R.I.O.S./issues)
- 💡 **Suggest features** or improvements
- 📖 **Improve documentation**
- 🧪 **Add tests** for uncovered scenarios
- 🔧 **Submit pull requests** with bug fixes or new features

<br/>

### Development Setup

```bash
# Clone and set up development environment
git clone https://github.com/Piero24/B.R.I.O.S..git
cd B.R.I.O.S.
python3 -m venv env
source env/bin/activate
pip install -r requirements-dev.txt

# Make your changes, then format code
make format

# Run tests
pytest -v

# Submit a pull request!
```

<p align="right"><a href="#top">⇧</a></p>

---

<br/>

<h2 id="license">📄 License</h2>

**MIT LICENSE**

<br/>

Copyright © 2025 Pietrobon Andrea

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<br/>

<a href="https://github.com/Piero24/B.R.I.O.S./blob/main/LICENSE">
    <strong>Full License Text »</strong>
</a>

<p align="right"><a href="#top">⇧</a></p>

---

<br/>

### 🙏 Acknowledgments

- **[Bleak](https://github.com/hbldh/bleak)** - Excellent cross-platform BLE library
- **Apple** - CoreBluetooth framework and PyObjC bindings
- **Community** - Thanks to all contributors and users

<br/>

### 📮 Responsible Disclosure

We assume no responsibility for improper use of this code. This tool is designed
for personal security enhancement. By using this software, you accept full
responsibility for its use and any consequences.

**The developers disclaim all liability for damage to persons or property.**

<p align="right"><a href="#top">⇧</a></p>

---

<br/>

<p align="center">
  <strong>Made with ❤️ by <a href="https://github.com/Piero24">Pietrobon Andrea</a></strong>
  <br/>
  <sub>Released: November 2, 2025</sub>
</p>

<p align="center">
  <a href="#top">⇧ Back to Top</a>
</p>

<h2 id="made-in"><br/>🛠  Built in</h2>
<p>
    This project is entirely written in C++ and uses the OpenCV for extract the pixels value from the image and nlohmann/json for saving weights and biases in a JSON file.
</p>
<p align="center">
    <a href="https://cplusplus.com">C++</a> • <a href="https://opencv.org">OpenCV</a> • <a href="https://github.com/nlohmann/json">nlohmann/json</a> • <a href="https://cmake.org">cmake</a>
</p>
<p align="right"><a href="#top">⇧</a></p>

<h2 id="documentation"><br/><br/>📚  Documentation</h2>

> [!TIP]
> In the file [mnist_fc128_relu_fc10_log_softmax_weights_biases.json](https://github.com/Piero24/VanillaNet-cpp/blob/main/Resources/output/weights/mnist_fc128_relu_fc10_log_softmax_weights_biases.json) are the weights and biases present in the trained model which allowed to obtain an accuracy of 98%.

<p>
    The neural network is fully customizable. You can define the number of inputs for each neuron, the number of neurons for each layer, the total number of layers, and even the activation function for each layer individually <strong>(ReLU, Sigmoid, Tanh, Softmax)</strong>. This flexibility allows you to tailor the network architecture to suit a wide range of tasks, from simple binary classification to more complex multi-class problems.
</p>
<p>
    Additionally, for the training phase, you have the option to set key hyperparameters such as the number of <strong>epochs</strong>, the <strong>learning rate</strong>, and the <strong>batch size</strong>, giving you full control over the optimization process. If you have an additional dataset, it’s also possible to use it to train the network by making the necessary adjustments to the code, allowing for easy experimentation with different data and configurations.
</p>
<p>
    This customizable approach ensures that the network can be adapted to a variety of use cases, helping to deepen your understanding of how different architectures and training parameters affect performance.
</p>

> [!NOTE]
> If you have a pythorch model and you want to try this project with yourt weights and biases, you can export them from the `.pt` to `.json` by using the script [ptToJson](https://github.com/Piero24/VanillaNet-cpp/blob/main/src/scripts/ptToJson.py).

<p>
    For a broader view it is better to refer the user to the documentation via links: <a href="https://github.com/Piero24/VanillaNet-cpp/blob/main/.github/doc.md">Documentation »</a>
</p>

> [!WARNING]  
> The **softmax activation function** is used only in the output layer. Is not possible to use it in the hidden layers.


<p align="right"><a href="#top">⇧</a></p>


<h2 id="prerequisites"><br/>🧰  Prerequisites</h2>
<p>
    The only prerequisites for running this project are the OpenCV library. There are many ways to install OpenCV, each depending on your operating system. The official OpenCV website provides detailed instructions on how to install the library on various platforms. You can find the installation guide at the following link: <a href="https://opencv.org">OpenCV Installation Guide</a>.
</p>

If you have a mac and `homebrew` installed, you can install OpenCV by running the following command:

```sh
brew install opencv
```

<br/>

Also download the dataset from the following link: [MNIST in CSV](https://www.kaggle.com/datasets/oddrationale/mnist-in-csv).

<p align="right"><a href="#top">⇧</a></p>


<h2 id="how-to-start"><br/>⚙️  How to Start</h2>
<p>
    Depending if you want to train the model or use a pre-trained model, you have different parameters that you can use. For a more detailed list of the parameters, you can refer to the <a href="https://github.com/Piero24/VanillaNet-cpp/blob/main/.github/doc.md">Documentation »</a>.
</p>
<br/>

1. Clone the repo
  
```sh
git clone https://github.com/Piero24/VanillaNet-cpp.git
```

> [!IMPORTANT] 
> The following commands (n° 2) for building the project with `cmake`are only for Unix systems. For Windows, the commands are slightly different. You can easily find the instructions on the official CMake website. (Or just ask to chatGPT for converting the commands 😉).

2. From the folder of the project, run the following commands:

    2.1 Create a build directory
  
    ```sh
    mkdir build
    ```

    2.2 Generate build files in the build directory
  
    ```sh
    cmake -S . -B build
    ```

    2.3 Build the project inside the build directory
  
    ```sh
    make -C build
    ```
3. [ONLY IF YOU WANT TO USE A DATASET COMPRESSED IN A CSV LIKE THE MNIST DATASET] Create a folder inside `./Resources/Dataset/csv/` and put the datasets in csv format inside it.To esxtract the images from the csv file, run the following command:

    ```sh
    ./VanillaNet-cpp -csv ./Resources/Dataset/csv/
    ```

    The images will be saved in the folder `./Resources/Dataset/mnist_test` and `./Resources/Dataset/mnist_train`.

4. Now as described before the parameter that you have to pass deends on if you want to train the model or use a pre-trained model. or make both the training and the testing.

    4.1 If you want ONLY to train the model, run the following command:
  
    ```sh
    ./VanillaNet-cpp -Tr <path_to_training_dataset> -E <number_of_epochs> -LR <learning_rate> -BS <batch_size>
    ```

    4.2 If you want ONLY to test the model, run the following command:
  
    ```sh
    ./VanillaNet-cpp -Te <path_to_testing_dataset> -wb <path_to_weights_and_biases>
    ```

    4.3 Train and test the model:
  
    ```sh
    ./VanillaNet-cpp -Tr <path_to_training_dataset> -E <number_of_epochs> -LR <learning_rate> -BS <batch_size> -Te <path_to_testing_dataset> -wb <path_to_weights_and_biases>
    ```

> [!NOTE] 
> 1. During the training phase, the weights and biases are saved multiple times in the folder `Resources/output/weights/` in order to have a backup of the weights and biases at the end of each epoch.
> 2. If you are using the MNIST dataset, you have to replace the `<path_to_training_dataset>` with the path to the folder `./Resources/Dataset/mnist_train` and `<path_to_testing_dataset>` with the path to the folder `./Resources/Dataset/mnist_test`.

<br/>
<div align="center">
    <img src="https://raw.githubusercontent.com/Piero24/VanillaNet-cpp/main/.github/out.png" style="width: 100%;" width="100%">
</div>
<br/>
<p align="right"><a href="#top">⇧</a></p>


---


<h3 id="responsible-disclosure"><br/>📮  Responsible Disclosure</h3>
<p>
    We assume no responsibility for an improper use of this code and everything related to it. We do not assume any responsibility for damage caused to people and / or objects in the use of the code.
</p>
<strong>
    By using this code even in a small part, the developers are declined from any responsibility.
</strong>
<br/>
<br/>
<p>
    It is possible to have more information by viewing the following links: 
    <a href="#code-of-conduct"><strong>Code of conduct</strong></a>
     • 
    <a href="#license"><strong>License</strong></a>
</p>

<p align="right"><a href="#top">⇧</a></p>


<h3 id="report-a-bug"><br/>🐛  Bug and Feature</h3>
<p>
    To <strong>report a bug</strong> or to request the implementation of <strong>new features</strong>, it is strongly recommended to use the <a href="https://github.com/Piero24/VanillaNet-cpp/issues"><strong>ISSUES tool from Github »</strong></a>
</p>
<br/>
<p>
    Here you may already find the answer to the problem you have encountered, in case it has already happened to other people. Otherwise you can report the bugs found.
</p>
<br/>
<strong>
    ATTENTION: To speed up the resolution of problems, it is recommended to answer all the questions present in the request phase in an exhaustive manner.
</strong>
<br/>
<br/>
<p>
    (Even in the phase of requests for the implementation of new functions, we ask you to better specify the reasons for the request and what final result you want to obtain).
</p>
<br/>

<p align="right"><a href="#top">⇧</a></p>
  
 --- 

<h2 id="license"><br/>🔍  License</h2>
<strong>MIT LICENSE</strong>
<br/>
<br/>
<i>Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including...</i>
<br/>
<br/>
<a href="https://github.com/Piero24/VanillaNet-cpp/blob/main/LICENSE">
    <strong>License Documentation »</strong>
</a>
<br/>
<p align="right"><a href="#top">⇧</a></p>


<h3 id="third-party-licenses"><br/>📌  Third Party Licenses</h3>

In the event that the software uses third-party components for its operation, 
<br/>
the individual licenses are indicated in the following section.
<br/>
<br/>
<strong>Software list:</strong>
<br/>
<table>
  <tr  align="center">
    <th>Software</th>
    <th>License owner</th> 
    <th>License type</th> 
    <th>Link</th>
  </tr>
  <tr  align="center">
    <td>OpenCV</td>
    <td><a href="https://opencv.org">OpenCV</a></td>
    <td>Apache-2.0 license</td>
    <td><a href="https://github.com/opencv/opencv">here</a></td>
  </tr>
  <tr  align="center">
    <td>nlohmann/json</td> 
    <td><a href="https://github.com/nlohmann">nlohmann</a></td>
    <td>MIT</td>
    <td><a href="https://github.com/nlohmann/json">here</a></td>
  </tr>
  <tr  align="center">
    <td>pyTorch</td>
    <td><a href="https://pytorch.org">PyTorch</a></td>
    <td>Multiple</td>
    <td><a href="https://github.com/pytorch/pytorch">here</a></td>
  </tr>
</table>

<p align="right"><a href="#top">⇧</a></p>


---
> *<p align="center"> Copyrright (C) by Pietrobon Andrea <br/> Released date: 15-09-2024*