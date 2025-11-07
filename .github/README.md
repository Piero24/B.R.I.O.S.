<div id="top"></div>
<br/>
<br/>

<p align="center">
  <img src="https://em-content.zobj.net/source/apple/237/croissant_1f950.png" width="105" height="100">
</p>
<h1 align="center">
    <!-- 
    <a href="https://github.com/Piero24/B.R.I.O.S.">🥐 B.R.I.O.S.</a>
     -->
    <a href="https://github.com/Piero24/B.R.I.O.S.">B.R.I.O.S.</a>
</h1>
<p align="center">
    <!-- BADGE -->
    <a href="https://github.com/Piero24/B.R.I.O.S./commits/main">
    <img src="https://img.shields.io/github/last-commit/piero24/B.R.I.O.S.">
    </a>
    <a href="https://github.com/Piero24/B.R.I.O.S.">
    <img src="https://img.shields.io/badge/Maintained-yes-green.svg">
    </a>
    <a href="https://github.com/Piero24/B.R.I.O.S./issues">
    <img src="https://img.shields.io/github/issues/piero24/B.R.I.O.S.">
    </a>
    <a href="https://github.com/Piero24/B.R.I.O.S./blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/piero24/B.R.I.O.S.">
    </a>
    <a href="https://github.com/Piero24/B.R.I.O.S./actions">
    <img src="https://img.shields.io/github/actions/workflow/status/piero24/B.R.I.O.S./02-unit-tests.yml?branch=main&label=tests">
    </a>
    <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg">
    </a>
    <a href="https://www.apple.com/macos/">
    <img src="https://img.shields.io/badge/Platform-macOS-lightgrey.svg">
    </a>
    <a href="https://github.com/Piero24/B.R.I.O.S./releases">
    <img src="https://img.shields.io/badge/Version-1.0.0-blue.svg">
    </a>
</p>
<p align="center">
    <strong>🥐 Bluetooth Reactive Intelligent Operator for Croissant Safety 🥐</strong>
    <br/>
    <br/>
    <em>Enterprise-grade proximity monitoring for macOS security automation</em>
    <br/>
    Automatically lock your Mac when your iPhone, Apple Watch, or BLE device moves out of range
    <br/>
    <br/>
    <a href="#quick-start"><strong>Quick Start</strong></a>
    •
    <a href="#documentation"><strong>Documentation</strong></a>
    •
    <a href="docs/FAQ.md"><strong>FAQ</strong></a>
    •
    <a href="#prerequisites"><strong>Requirements</strong></a>
    •
    <a href="https://github.com/Piero24/B.R.I.O.S./issues"><strong>Report Bug</strong></a>
    •
    <a href="https://github.com/Piero24/B.R.I.O.S./issues"><strong>Request Feature</strong></a>
</p>


---

<br/>

## 📑 Table of Contents

- [Introduction](#introduction)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Quick Start](#quick-start)
- [Built With](#made-in)
- [Documentation](#documentation)
- [Prerequisites](#prerequisites)
- [Installation](#how-to-start)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Architecture](#architecture)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Contributing](#contributing)
- [Roadmap & Future Improvements](#roadmap)
- [Responsible Disclosure](#responsible-disclosure)
- [Bug Reports & Features](#report-a-bug)
- [License](#license)
- [Third Party Licenses](#third-party-licenses)

---


<br/><br/>
<h2 id="introduction">📔  Introduction</h2>

<p align="left">
    <strong>🥐 B.R.I.O.S.</strong> (Bluetooth Reactive Intelligent Operator for Croissant Safety) is an enterprise-grade proximity monitoring system designed specifically for macOS. It provides automated security by continuously tracking the distance to a designated Bluetooth device (iPhone, Apple Watch, AirTag, or any BLE beacon) and automatically locking your Mac when the device moves beyond a configurable threshold.
</p>

<p align="left">
    Built with production-ready code architecture, comprehensive test coverage, and CI/CD integration, B.R.I.O.S. employs sophisticated signal processing algorithms to deliver accurate distance estimation and reliable proximity detection. The system uses the <strong>Log-Distance Path Loss Model</strong> combined with statistical RSSI smoothing to filter environmental noise and provide stable, actionable proximity alerts.

<br/>

> [!NOTE]
> **Why B.R.I.O.S.?**: At my company, we must lock our computers when leaving our desks. If a colleague finds your computer unlocked, they can post a croissant emoji (🥐) in the company Slack channel. This alerts everyone that you forgot to lock your computer, and the next day you have to bring croissants for your colleagues to enjoy together. I think it's a fun way to remind people about security! However, especially at the end of the day, it's easy to forget to lock your PC when grabbing water or rushing to a meeting. For this reason, I developed this extra layer of security that has your back in case you forget to lock your computer. It instantly locks your Mac and prevents your colleagues from getting those delicious croissants. Sorry, guys! 🥐

> [!WARNING]
> **Distance Accuracy**: Since Apple has not released a MacBook with an Ultra-Wideband (UWB) chip at the time of development, it's quite difficult to achieve very precise distance measurements between your smartphone and computer. This system relies on RSSI (Received Signal Strength Indicator), which is inherently noisy and subject to environmental interference (walls, furniture, people moving around, etc.). The current implementation using the Log-Distance Path Loss Model can provide distance estimates with an accuracy of approximately ±20-30cm in controlled environments. However, real-world accuracy may vary significantly based on factors such as device orientation, obstacles, and environmental conditions. For critical security applications, we recommend calibrating the TX_POWER_AT_1M parameter for your specific device and environment to improve accuracy. Remember that RSSI is not a precise distance measurement method, and results should be interpreted with caution. Unfortunately, I can't install a UWB chip in my MacBook or use multiple devices for triangulation, so this is the best solution available at the moment.

### 🎯 Key Use Cases

- **🔐 Automatic Security**: Walk away from your desk, and your Mac locks automatically
- **👨‍💻 Hot-desking Environments**: Instant workspace security in shared office spaces  
- **🏢 Corporate Security**: Enforce physical proximity requirements for sensitive workstations
- **🏠 Home Office**: Ensure your Mac is never left unlocked when you leave
- **⚡ Zero-Touch Workflow**: Seamless security without manual intervention

<p align="right"><a href="#top">⇧</a></p>

---

<br/>
<h2 id="key-features">✨  Key Features</h2>

<table>
<tr>
<td width="50%">

### 🔍 **Discovery & Monitoring**
- **Device Scanner**: Find all nearby BLE devices with RSSI and distance metrics
- **Real-time Monitoring**: Continuous proximity tracking with sub-second latency
- **Multi-device Support**: Track any BLE 4.0+ compatible device
- **Signal Smoothing**: Statistical analysis eliminates false positives

</td>
<td width="50%">

### ⚙️ **Advanced Configuration**
- **Customizable Thresholds**: Set your own distance limits (meters)
- **TX Power Calibration**: Fine-tune for your specific device
- **Path Loss Tuning**: Optimize for your environment (indoor/outdoor)
- **Sample Window Control**: Adjust smoothing sensitivity

</td>
</tr>
<tr>
<td width="50%">

### 🚀 **Deployment Options**
- **Foreground Mode**: Real-time terminal output with detailed metrics
- **Background Service**: Daemon mode with service management
- **File Logging**: Comprehensive activity logs for auditing
- **Make Commands**: Developer-friendly automation

</td>
<td width="50%">

### 🔒 **Security & Reliability**
- **Automatic Mac Locking**: Instant security on proximity loss
- **Reconnection Detection**: Smart alerts when device returns
- **Type-Safe Code**: MyPy static type checking
- **100% Test Coverage**: Comprehensive pytest test suite

</td>
</tr>
<tr>
<td width="50%">

### 📊 **Monitoring & Insights**
- **Verbose Output**: Real-time RSSI, distance, and signal strength
- **Service Status**: Check daemon health and uptime
- **Activity Logs**: Review historical proximity events
- **Debug Mode**: Detailed troubleshooting information

</td>
<td width="50%">

### 🔧 **Developer Experience**
- **Clean Architecture**: Well-documented, modular codebase
- **CI/CD Ready**: GitHub Actions workflow included
- **Easy Setup**: Virtual environment with dependency management
- **Cross-platform BLE**: Bleak library for BLE abstraction

</td>
</tr>
</table>

<p align="right"><a href="#top">⇧</a></p>

---

<br/>
<h2 id="how-it-works">🔬  How It Works</h2>
<br/>
<h2 id="how-it-works">🔬  How It Works</h2>

<p>
    B.R.I.O.S. implements a sophisticated four-stage pipeline for accurate proximity detection and automated security enforcement:
</p>

### 1️⃣ **Signal Collection & Processing**

The application continuously scans for BLE advertisements from your target device and extracts RSSI (Received Signal Strength Indicator) values. Each advertisement provides real-time signal strength data that forms the foundation for distance calculation.

```
BLE Device → Advertisement → RSSI Extraction → Signal Buffer
```

### 2️⃣ **Statistical Smoothing**

Raw RSSI values are inherently noisy due to environmental factors (walls, interference, multipath propagation). B.R.I.O.S. maintains a configurable rolling buffer (default: 12 samples) and calculates the statistical mean to eliminate transient fluctuations:

```python
smoothed_rssi = statistics.mean(rssi_buffer)
```

This ensures stable distance measurements and prevents false-positive alerts from momentary signal drops.

### 3️⃣ **Distance Estimation**

Using the **Log-Distance Path Loss Model**, B.R.I.O.S. converts smoothed RSSI values into accurate distance measurements:

```python
distance = 10 ** ((TX_POWER_AT_1M - smoothed_rssi) / (10 * PATH_LOSS_EXPONENT))
```

**Parameters:**
- **TX_POWER_AT_1M**: Calibrated signal strength at 1 meter (default: -59 dBm)
- **PATH_LOSS_EXPONENT** (n): Environmental attenuation factor (default: 2.8)
  - **2.0**: Free space (outdoor, no obstacles)
  - **2.5-3.0**: Indoor with light walls
  - **3.5-4.0**: Indoor with heavy walls/obstacles

### 4️⃣ **Proximity Alerting & Action**

When the calculated distance exceeds your configured threshold (default: 2.0m), B.R.I.O.S. triggers an automated security response:

1. **System Lock**: Executes macOS native commands to lock the screen immediately
2. **Alert Logging**: Records the event with timestamp, distance, and device info
3. **Password Enforcement**: Ensures password is required on wake
4. **Reconnection Detection**: Monitors for device return and logs the event

<br/>
<div align="center">
    <img src="https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=800&auto=format&fit=crop" style="width: 100%;" width="100%">
    <p><em>Bluetooth proximity monitoring for enhanced security</em></p>
</div>
<br/>

> [!NOTE]
> **Distance Accuracy**: The Log-Distance Path Loss Model provides ±20-30cm accuracy in controlled environments. Accuracy may vary based on device orientation, obstacles, and environmental factors. For critical applications, we recommend calibrating TX_POWER_AT_1M for your specific device.

<p align="right"><a href="#top">⇧</a></p>

---

<br/>
<h2 id="quick-start">⚡  Quick Start</h2>

Get B.R.I.O.S. running in less than 2 minutes:

```bash
# 1. Clone and navigate
git clone https://github.com/Piero24/B.R.I.O.S..git && cd B.R.I.O.S.

# 2. Set up Python environment
python3 -m venv env && source env/bin/activate

# 3. Install dependencies
pip install -r requirements/dev.txt

# 4. Discover your device
python3 main.py --scanner 15 -m

# 5. Configure (edit .env with your device MAC)
cp .env.example .env && nano .env

# 6. Start monitoring
python3 main.py --target-mac -v
```

**That's it!** Your Mac will now lock automatically when your device moves out of range.

For production deployment with background service:
```bash
python3 main.py --target-mac -v -f --start
python3 main.py --status  # Check service status
```

<p align="right"><a href="#top">⇧</a></p>

---

<br/><br/>
<h2 id="made-in">�  Built With</h2>
<p>
    B.R.I.O.S. is built entirely in Python using industry-standard libraries for cross-platform Bluetooth communication, native macOS integration, and enterprise-grade testing infrastructure.
</p>

### Core Technologies

<table>
<tr>
<td align="center" width="25%">
<img src="https://www.python.org/static/community_logos/python-logo-generic.svg" width="80"><br/>
<strong>Python 3.8+</strong><br/>
<sub>Core Language</sub>
</td>
<td align="center" width="25%">
<img src="https://raw.githubusercontent.com/hbldh/bleak/develop/docs/source/_static/logo.png" width="80"><br/>
<strong>Bleak</strong><br/>
<sub>BLE Communication</sub>
</td>
<td align="center" width="25%">
<img src="https://raw.githubusercontent.com/pyobjc/pyobjc/master/docs/_static/pyobjc.png" width="80"><br/>
<strong>PyObjC</strong><br/>
<sub>macOS Integration</sub>
</td>
<td align="center" width="25%">
<img src="https://docs.pytest.org/en/stable/_static/pytest_logo_curves.svg" width="80"><br/>
<strong>Pytest</strong><br/>
<sub>Testing Framework</sub>
</td>
</tr>
</table>

### Development Stack

- **Configuration**: python-dotenv for environment management
- **Code Quality**: Black + Pyink for formatting, MyPy for type checking
- **Testing**: pytest, pytest-asyncio, pytest-mock with comprehensive coverage
- **CI/CD**: GitHub Actions for automated testing and quality checks
- **Documentation**: Markdown with comprehensive inline code documentation

<p align="right"><a href="#top">⇧</a></p>

<br/><br/>
<h2 id="documentation">📚  Documentation</h2>

B.R.I.O.S. provides comprehensive documentation for all skill levels:

### 📖 **User Documentation**

- **[Installation Guide](#how-to-start)** - Step-by-step setup instructions
- **[Configuration Reference](#configuration)** - Complete `.env` parameter guide  
- **[Usage Examples](#usage-examples)** - Common use cases and command patterns
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### 🔧 **Developer Documentation**

- **[Contributing Guide](docs/CONTRIBUTING.md)** - How to contribute to the project
- **[Testing Guide](docs/TESTING.md)** - Running and writing tests
- **[FAQ](docs/FAQ.md)** - Frequently asked questions
- **[Code of Conduct](docs/CODE_OF_CONDUCT.md)** - Community guidelines

### 📋 **Additional Resources**

- **[CI/CD Pipeline](docs/CICD.md)** - GitHub Actions workflow documentation
- **[Changelog](CHANGELOG.md)** - Version history and release notes
- **[FAQ](docs/FAQ.md)** - Frequently asked questions

> [!TIP]
> **First Time Using BLE?** Start with the [Quick Start](#quick-start) guide above, then explore the scanner mode to understand BLE device discovery: `python3 main.py --scanner 15 -m`

> [!WARNING]  
> **macOS Lock Screen Settings**: Ensure The password is required immediately after sleep or screen saver begins in *System Settings → Lock Screen*. Without this setting, B.R.I.O.S. cannot enforce security upon proximity loss. (See image below)

<img src="./images/macos-lock-screen-settings.png" alt="macOS Lock Screen Settings" style="width: 100%;" width="600">

<p align="right"><a href="#top">⇧</a></p>


<h2 id="prerequisites"><br/>🧰  Prerequisites</h2>
<p>
    The only prerequisites for running this project are Python 3.8 or higher and the required Python packages. All dependencies are organized in the `requirements/` folder and can be installed with pip.
</p>

> [!IMPORTANT]
> **Testing & Compatibility Notice**
> 
> This project has been tested **only** on:
> - **Hardware**: MacBook Pro M3 Pro with iPhone
> - **Python Version**: 3.12.6 (should work on Python 3.8+)
> - **OS**: macOS (Bluetooth stack specific to macOS)
> 
> **Critical Device Requirements:**
> - ⚠️ **Different Apple ID Pairing**: If your Mac and iPhone/device use **different Apple IDs**, you **must pair them first** in **System Settings → Bluetooth**. Otherwise, Apple hides the MAC address and the device won't be discoverable.
> - ⚠️ **Android devices** should work without pairing requirements.
> - ⚠️ **Apple Watch**: Currently **not discoverable from Mac** due to Apple's BLE restrictions.
> 
> If you encounter issues on other configurations, please [report them](https://github.com/Piero24/B.R.I.O.S./issues).

**System Requirements:**

- macOS 10.15 (Catalina) or later
- Python 3.8+ (tested on 3.12.6)
- Bluetooth Low Energy adapter (built-in on all modern Macs)

**Python Dependencies:**

- `bleak` - Cross-platform BLE library
- `python-dotenv` - Configuration file management
- `pyobjc-framework-CoreBluetooth` - macOS Bluetooth support
- `pyobjc-framework-Cocoa` - macOS system integration

<br/>

Install all dependencies with:

```sh
pip install -r requirements/dev.txt
```

<p align="right"><a href="#top">⇧</a></p>


<h2 id="how-to-start"><br/>⚙️  How to Start</h2>
<p>
    Depending on whether you want to discover devices, monitor in the foreground, or run as a background service, you have different parameters available. The following guide covers all operating modes.
</p>
<br/>

1. Clone the repo
  
```sh
git clone https://github.com/Piero24/B.R.I.O.S..git
cd B.R.I.O.S.
```

2. Create and activate a virtual environment

```sh
python3 -m venv env
source env/bin/activate
```

3. Install dependencies
  
```sh
pip install -r requirements/dev.txt
```

4. Configure your target device

    4.1 First, discover nearby BLE devices to find your target device's address:
  
    ```sh
    python3 main.py --scanner 15 -m
    ```
    
    This will scan for 15 seconds and display all discovered devices with their MAC addresses, names, RSSI values, and estimated distances.

    4.2 Copy the example configuration file and edit it:
  
    ```sh
    cp .env.example .env
    nano .env  # or use your preferred editor
    ```
    
    4.3 Update the `.env` file with your device information:
    
    ```bash
    TARGET_DEVICE_MAC_ADDRESS=XX:XX:XX:XX:XX:XX  # Your device's MAC
    TARGET_DEVICE_NAME=My iPhone                  # Device name
    TARGET_DEVICE_TYPE=iPhone 15 Pro             # Device type
    DISTANCE_THRESHOLD_M=2.0                     # Lock distance
    ```

5. Now depending on your desired operating mode, use the appropriate command:

    5.1 **Discovery Mode** - Scan for nearby BLE devices:
  
    ```sh
    # Scan for 15 seconds using MAC addresses (recommended for macOS)
    python3 main.py --scanner 15 -m
    
    # Scan for 30 seconds using UUIDs
    python3 main.py --scanner 30
    ```

    5.2 **Monitor Mode (Foreground)** - Real-time monitoring with terminal output:
  
    ```sh
    # Monitor using default MAC from .env with verbose output
    python3 main.py --target-mac -v
    
    # Monitor specific device with file logging
    python3 main.py --target-mac "A1:B2:C3:D4:E5:F6" -m -v -f
    
    # Monitor using UUID (macOS privacy mode)
    python3 main.py --target-uuid -v
    ```

    5.3 **Background Service Mode** - Run as a daemon:
  
    ```sh
    # Start the background monitor
    python3 main.py --target-mac -v -f --start
    
    # Check service status
    python3 main.py --status
    
    # Stop the service
    python3 main.py --stop
    
    # Restart the service
    python3 main.py --restart
    ```

> [!NOTE] 
> 1. When running in background mode with file logging (`-f`), all output is written to `.ble_monitor.log` in the project directory.
> 2. The PID of the background process is stored in `.ble_monitor.pid`.
> 3. Always use `-m` flag on macOS for better device tracking reliability.

<br/>

**Command-Line Arguments:**

| Argument | Short | Description |
|----------|-------|-------------|
| `--scanner SECONDS` | `-s` | Discover BLE devices for specified duration (5-60s) |
| `--target-mac [ADDRESS]` | `-tm` | Monitor by MAC address (use default from .env if no address provided) |
| `--target-uuid [UUID]` | `-tu` | Monitor by UUID (macOS privacy mode) |
| `--macos-use-bdaddr` | `-m` | Force MAC address mode on macOS (recommended) |
| `--verbose` | `-v` | Enable detailed RSSI and distance output |
| `--file-logging` | `-f` | Enable logging to file |
| `--start` | | Start as background daemon |
| `--stop` | | Stop background daemon |
| `--restart` | | Restart background daemon |
| `--status` | | Show daemon status and recent activity |

<br/>

**Example Output (Monitor Mode):**

```
Starting 🥐 B.R.I.O.S.
──────────────────────────────────────────────────
Target:     Pietro's iPhone (iPhone 15 Pro)
Address:    A1:B2:C3:D4:E5:F6
Threshold:  2.0m
TX Power:   -59 dBm @ 1m
Path Loss:  2.8
Samples:    12 readings
Mode:       BD_ADDR (MAC)
──────────────────────────────────────────────────

● Monitoring active - Press Ctrl+C to stop

[14:32:15] RSSI:  -52 dBm → Smoothed:  -51.3 dBm │ Distance:  0.56m │ Signal: Strong
[14:32:16] RSSI:  -54 dBm → Smoothed:  -52.1 dBm │ Distance:  0.61m │ Signal: Strong
[14:32:17] RSSI:  -75 dBm → Smoothed:  -69.1 dBm │ Distance:  2.81m │ Signal: Weak

──────────────────────────────────────────────────
⚠  ALERT: Device moved out of range
   Device:    Pietro's iPhone
   Distance:  ~2.81m (threshold: 2.0m)
   Time:      14:32:17
   Action:    🔒 MacBook locked (password required)
──────────────────────────────────────────────────
```

<br/>
<p align="right"><a href="#top">⇧</a></p>

---

<br/>
<h2 id="configuration">🔧  Configuration</h2>

B.R.I.O.S. is highly configurable via the `.env` file. All settings are documented below.

### Configuration File Reference

```bash
# ============================================
# TARGET DEVICE SETTINGS
# ============================================

# MAC Address (recommended for stability)
TARGET_DEVICE_MAC_ADDRESS=XX:XX:XX:XX:XX:XX

# UUID Address (macOS privacy mode - may change periodically)
TARGET_DEVICE_UUID_ADDRESS=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX

# Human-readable device name (for logs and alerts)
TARGET_DEVICE_NAME=My iPhone

# Device type description
TARGET_DEVICE_TYPE=iPhone 15 Pro

# ============================================
# DISTANCE CALCULATION PARAMETERS
# ============================================

# TX Power: RSSI measured at exactly 1 meter distance
# Default: -59 dBm (typical for smartphones)
# Calibration: Place device 1m away, run with -v, note average RSSI
TX_POWER_AT_1M=-59

# Path Loss Exponent: Environmental signal attenuation factor
# 2.0  = Free space (outdoor, no obstacles)
# 2.5  = Typical indoor environment
# 2.8  = Office with walls and furniture (recommended default)
# 3.5  = Dense indoor environment with many obstacles
# 4.0  = Very obstructed environment
PATH_LOSS_EXPONENT=2.8

# Sample Window: Number of RSSI readings to average
# Lower = Faster response, less stable
# Higher = Slower response, more stable
# Recommended: 12 readings (provides good balance)
SAMPLE_WINDOW=12

# Distance Threshold: Maximum distance before alert (in meters)
# 1.0-1.5m  = Very close proximity (may trigger if you lean away)
# 2.0m      = Recommended default (walking away from desk)
# 3.0-4.0m  = Room-level proximity
# 5.0m+     = Large spaces
DISTANCE_THRESHOLD_M=2.0
```

### Environment Presets

**🏢 Office Environment (Default)**
```bash
PATH_LOSS_EXPONENT=2.8
SAMPLE_WINDOW=12
DISTANCE_THRESHOLD_M=2.0
```

**🏠 Home (Open Space)**
```bash
PATH_LOSS_EXPONENT=2.3
SAMPLE_WINDOW=10
DISTANCE_THRESHOLD_M=2.5
```

**🏗️ Dense Environment (Many Obstacles)**
```bash
PATH_LOSS_EXPONENT=3.5
SAMPLE_WINDOW=15
DISTANCE_THRESHOLD_M=1.5
```

**⚡ Fast Response (Less Stable)**
```bash
PATH_LOSS_EXPONENT=2.8
SAMPLE_WINDOW=5
DISTANCE_THRESHOLD_M=2.0
```

**🎯 High Precision (More Stable)**
```bash
PATH_LOSS_EXPONENT=2.8
SAMPLE_WINDOW=20
DISTANCE_THRESHOLD_M=2.0
```

<p align="right"><a href="#top">⇧</a></p>

---

<br/>
<h2 id="usage-examples">📋  Usage Examples</h2>

### Discovery Mode

Find nearby BLE devices and their information:

```bash
# Basic scan (15 seconds, UUIDs on macOS)
python3 main.py --scanner 15

# Recommended: Scan with real MAC addresses (macOS)
python3 main.py --scanner 15 -m

# Long scan (60 seconds max)
python3 main.py --scanner 60 -m

# Quick scan (5 seconds min)
python3 main.py --scanner 5 -m
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

Scan Results (3 devices found)
──────────────────────────────────────────────────────────────────────
 1. Pietro's iPhone                │ A1:B2:C3:D4:E5:F6 │  -52 dBm │ ~ 0.58m
 2. Apple Watch                    │ B2:C3:D4:E5:F6:A1 │  -65 dBm │ ~ 1.75m
 3. (Unknown)                      │ C3:D4:E5:F6:A1:B2 │  -80 dBm │ ~ 4.24m
```

### Monitor Mode (Foreground)

Run monitoring with real-time terminal output:

```bash
# Basic monitoring (default device from .env)
python3 main.py --target-mac

# With verbose RSSI and distance output
python3 main.py --target-mac -v

# Monitor specific MAC address
python3 main.py --target-mac "A1:B2:C3:D4:E5:F6" -m -v

# Monitor with file logging
python3 main.py --target-mac -v -f

# Monitor using UUID (privacy mode)
python3 main.py --target-uuid -v

# Monitor specific UUID
python3 main.py --target-uuid "12345678-1234-5678-1234-567812345678" -v
```

### Background Service Mode

Run as a daemon for continuous monitoring:

```bash
# Start service with verbose logging to file
python3 main.py --target-mac -v -f --start

# Check service status
python3 main.py --status

# View live logs
tail -f .ble_monitor.log

# Stop service
python3 main.py --stop

# Restart service (stop + start)
python3 main.py --restart
```

**Service Status Output:**
```
🥐 B.R.I.O.S. Status
──────────────────────────────────────────────────
Status:     ● RUNNING
PID:        12345
Uptime:     2:34:56
Target:     Pietro's iPhone
Address:    A1:B2:C3:D4:E5:F6
Threshold:  2.0m

Log file:   /path/to/.ble_monitor.log

Recent activity:
  [14:30:15] RSSI:  -55 dBm → Smoothed:  -54.2 dBm │ Distance:  0.68m
  [14:30:16] RSSI:  -57 dBm → Smoothed:  -55.8 dBm │ Distance:  0.76m
  [14:30:17] RSSI:  -58 dBm → Smoothed:  -56.7 dBm │ Distance:  0.82m
──────────────────────────────────────────────────
```

### Using Make Commands

Convenient development workflow automation:

```bash
# Format code with Pyink
make format

# Run application
make run ARGS="--scanner 15 -m"

# Format and run in one command
make ble:run ARGS="--target-mac -v"

# Examples
make run ARGS="--status"
make run ARGS="--target-mac -v -f --start"
make run ARGS="--stop"
```

### Real-World Scenarios

#### Scenario 1: Daily Office Use

```bash
# Morning: Start background service
python3 main.py --target-mac -v -f --start

# During day: Check if still running
python3 main.py --status

# Evening: Stop service before leaving
python3 main.py --stop
```

#### Scenario 2: Shared Workspace

```bash
# Quick setup at hot-desk
python3 main.py --target-mac -v

# Walk away for coffee → Mac locks automatically
# Return to desk → Notification logged
```

#### Scenario 3: Home Office

```bash
# Start monitoring in background on system startup
# (Add to login items or use launchd)
python3 main.py --target-mac -f --start

# Mac stays locked whenever you're not in the room
```

#### Scenario 4: Conference Room

```bash
# Temporary monitoring for presentation
python3 main.py --target-mac -v

# Ctrl+C when done
```

<p align="right"><a href="#top">⇧</a></p>

---

<br/>
<h2 id="architecture">🏗️  Architecture</h2>

B.R.I.O.S. follows a clean, modular architecture for maintainability and extensibility.

### System Components

```
┌─────────────────────────────────┐
│      Application (CLI)          │  Main orchestrator
└───────────┬─────────────────────┘
            │
    ┌───────┴────────┐
    │                │
┌───▼────┐     ┌────▼────────┐
│Scanner │     │  Monitor    │
│  Mode  │     │    Mode     │
└────────┘     └──────┬──────┘
                      │
            ┌─────────┴────────┐
            │                  │
    ┌───────▼────────┐  ┌─────▼──────┐
    │  Signal        │  │  Distance  │
    │  Processing    │  │  Calc      │
    └───────┬────────┘  └─────┬──────┘
            │                 │
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │  Alert & Lock   │
            └─────────────────┘
```

### Key Classes

- **`Application`**: CLI interface and component orchestration
- **`ServiceManager`**: Daemon lifecycle management (start/stop/restart/status)
- **`DeviceScanner`**: BLE device discovery and listing
- **`DeviceMonitor`**: Continuous proximity monitoring with callbacks
- **`Flags`**: Configuration data class (daemon_mode, file_logging, verbose)
- **`Colors`**: Terminal output formatting utilities

<p align="right"><a href="#top">⇧</a></p>

---


<p align="right"><a href="#top">⇧</a></p>

---

<br/>
<h2 id="roadmap">🗺️  Roadmap & Future Improvements</h2>

### 🎯 Next Steps

**High Priority:**
- ⚡ **Performance Optimization** - Reduce latency, optimize RSSI processing, minimize CPU usage
- 🎯 **Kalman Filter** - Improve accuracy to ±10-15cm (vs current ±20-30cm) with better noise filtering

**Planned Features:**
- 📱 Multi-device monitoring with priority and fallback logic
- 🎨 Custom actions (scripts, webhooks, Shortcuts.app)
- 🔧 Visual calibration tool and environment presets
- 🧠 ML-based adaptive calibration and anomaly detection
- 🔌 Plugin system for extensibility
- 💻 Cross-platform support (Windows, Linux, Docker)

**Technical Improvements:**
- Code refactoring, enhanced error handling
- Expanded test coverage and performance benchmarks
- Mock BLE hardware for CI/CD testing

### 🤝 Contributing

We welcome contributions for any of these features! See our [Contributing Guide](docs/CONTRIBUTING.md) to get started.

**Priority areas for community contributions:**
1. Kalman filter implementation (Python expertise needed)
2. Cross-platform support (Windows/Linux developers)
4. Documentation improvements
5. Performance testing and optimization

<p align="right"><a href="#top">⇧</a></p>

---

<br/>
<h2 id="testing">🧪  Testing</h2>

B.R.I.O.S. maintains 100% test coverage with comprehensive pytest-based tests.

### Running Tests

```bash
# Run all tests
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=. --cov-report=term-missing

# Run specific test
pytest tests/test_ble_monitor.py::test_estimate_distance -v
```

### Test Categories

- ✅ **Unit Tests**: Individual function validation
- ✅ **Integration Tests**: Component interaction verification
- ✅ **End-to-End Tests**: Complete workflow testing
- ✅ **Async Tests**: pytest-asyncio for async code
- ✅ **Mocking**: pytest-mock for BLE components

### Test Coverage

```
Name                    Stmts   Miss  Cover
-------------------------------------------
main.py                   450      0   100%
tests/test_ble_monitor    280      0   100%
-------------------------------------------
TOTAL                     730      0   100%
```

For detailed testing documentation, see [docs/TESTING.md](docs/TESTING.md).

<p align="right"><a href="#top">⇧</a></p>

---

<br/>
<h2 id="cicd-pipeline">�  CI/CD Pipeline</h2>

Automated quality assurance via GitHub Actions.

### Workflow Stages

1. **Code Formatting** (`01-style-check.yml`)
   - Validates Black/Pyink formatting
   - Ensures consistent code style

2. **Unit Tests** (`02-unit-tests.yml`)
   - Runs complete test suite
   - Validates all functionality

3. **Type Checking** (`03-type-check.yml`)
   - MyPy static type analysis
   - Catches type errors

4. **Security Audit** (`04-security-audit.yml`)
   - pip-audit for vulnerabilities
   - Dependency security scanning

### Viewing Results

Check workflow status:
- **Badge**: See README header for status
- **Actions Tab**: https://github.com/Piero24/B.R.I.O.S./actions
- **Pull Requests**: Automatic checks on PRs

All workflows must pass before merging to `main`.

<p align="right"><a href="#top">⇧</a></p>

---

<br/>
<h2 id="contributing">🤝  Contributing</h2>

Contributions are welcome! We value:
- 🐛 Bug reports and fixes
- ✨ Feature suggestions and implementations
- 📚 Documentation improvements
- 🧪 Test coverage expansion
- 🎨 Code quality enhancements

### Quick Contribution Guide

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/B.R.I.O.S..git`
3. **Branch**: `git checkout -b feature/your-feature-name`
4. **Develop**: Make your changes with tests
5. **Test**: `pytest` and `pyink .`
6. **Commit**: `git commit -m "feat: add awesome feature"`
7. **Push**: `git push origin feature/your-feature-name`
8. **PR**: Open a Pull Request on GitHub

For detailed guidelines, see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

<p align="right"><a href="#top">⇧</a></p>

---

<br/>
<h2 id="responsible-disclosure">⚠️  Responsible Disclosure</h2>

We assume no responsibility for an improper use of this code and everything related to it. We do not assume any responsibility for damage caused to people and/or objects in the use of the code.

**By using this code even in a small part, the developers are declined from any responsibility.**

It is possible to have more information by viewing the following links: [Code of Conduct](docs/CODE_OF_CONDUCT.md) • [License](#license)

<p align="right"><a href="#top">⇧</a></p>

---

<br/>
<h2 id="report-a-bug">🐛  Bug Reports & Features</h2>

To **report a bug** or to request the implementation of **new features**, it is strongly recommended to use the [**ISSUES tool from Github »**](https://github.com/Piero24/B.R.I.O.S./issues)

Here you may already find the answer to the problem you have encountered, in case it has already happened to other people. Otherwise you can report the bugs found.

**ATTENTION:** To speed up the resolution of problems, it is recommended to answer all the questions present in the request phase in an exhaustive manner.

(Even in the phase of requests for the implementation of new functions, we ask you to better specify the reasons for the request and what final result you want to obtain).

<p align="right"><a href="#top">⇧</a></p>
  
---

<br/>
<h2 id="license">🔍  License</h2>

**MIT LICENSE**

*Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including...*

[**License Documentation »**](https://github.com/Piero24/B.R.I.O.S./blob/main/LICENSE)

<p align="right"><a href="#top">⇧</a></p>

---

<br/>
<h2 id="third-party-licenses">📌  Third Party Licenses</h2>

In the event that the software uses third-party components for its operation, the individual licenses are indicated in the following section.

**Software list:**

<table>
  <tr  align="center">
    <th>Software</th>
    <th>License owner</th> 
    <th>License type</th> 
    <th>Link</th>
  </tr>
  <tr  align="center">
    <td>Bleak</td>
    <td><a href="https://github.com/hbldh/bleak">hbldh</a></td>
    <td>MIT</td>
    <td><a href="https://github.com/hbldh/bleak">here</a></td>
  </tr>
  <tr  align="center">
    <td>python-dotenv</td> 
    <td><a href="https://github.com/theskumar">theskumar</a></td>
    <td>BSD-3-Clause</td>
    <td><a href="https://github.com/theskumar/python-dotenv">here</a></td>
  </tr>
  <tr  align="center">
    <td>PyObjC</td>
    <td><a href="https://github.com/ronaldoussoren/pyobjc">PyObjC Team</a></td>
    <td>MIT</td>
    <td><a href="https://github.com/ronaldoussoren/pyobjc">here</a></td>
  </tr>
</table>

<p align="right"><a href="#top">⇧</a></p>

---

<br/>

## 🌟 Project Status

**🥐 B.R.I.O.S. is production-ready** with enterprise-grade features:

- ✅ 100% test coverage
- ✅ CI/CD pipeline with automated checks
- ✅ Comprehensive documentation
- ✅ Active maintenance
- ✅ Type-safe codebase
- ✅ Security audited

### Versioning

B.R.I.O.S. follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New features (backwards-compatible)
- **PATCH**: Bug fixes (backwards-compatible)

Current version: **1.0.0** - [Changelog](CHANGELOG.md)

---

<br/>

## 📬 Contact & Support

### Get Help

- 📖 **Documentation**: [docs/](docs/) folder
- ❓ **FAQ**: [docs/FAQ.md](docs/FAQ.md)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Piero24/B.R.I.O.S./discussions)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/Piero24/B.R.I.O.S./issues)

### Stay Updated

- ⭐ **Star** this repository to show support
- 👀 **Watch** for new releases and updates
- 🔔 **Subscribe** to [release notifications](https://github.com/Piero24/B.R.I.O.S./releases)

### Connect

- **Author**: Pietrobon Andrea
- **GitHub**: [@Piero24](https://github.com/Piero24)
- **Email**: pietrobon.andrea24@gmail.com

---

<br/>

## 🙏 Acknowledgments

Special thanks to:

- **[Bleak Team](https://github.com/hbldh/bleak)** - Excellent cross-platform BLE library
- **[PyObjC Contributors](https://github.com/ronaldoussoren/pyobjc)** - macOS native integration
- **Open Source Community** - For inspiration and support

---

## 📄 License & Copyright

**Copyright © 2024 Pietrobon Andrea**

---
> *<p align="center"> Copyright (C) by Pietrobon Andrea <br/> Released date: 07-11-2025*
