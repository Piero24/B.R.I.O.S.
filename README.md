# 🥐 B.R.I.O.S.

<p align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/3145/3145073.png" width="100">
</p>

<p align="center">
  <strong>🥐 Bluetooth Reactive Intelligent Operator for Croissant Safety</strong>
  <br/>
  <sub>Version 1.0.0</sub>
  <br/>
  <br/>
  Enterprise-grade proximity monitoring for macOS security automation
  <br/>
  Automatically lock your Mac when your iPhone, Apple Watch, or device moves out of range
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a>
  •
  <a href="docs/FAQ.md">FAQ</a>
  •
  <a href="https://github.com/Piero24/B.R.I.O.S./issues">Report Bug</a>
  •
  <a href="https://github.com/Piero24/B.R.I.O.S./issues">Request Feature</a>
</p>

---

## 📦 Installation

### Option 1: Homebrew (Recommended)
The easiest way to install B.R.I.O.S. on macOS.

```bash
# Tap the repository
brew tap Piero24/brios https://github.com/Piero24/B.R.I.O.S.

# Install brios
brew install brios
```

## ✨ Key Features

- 🔍 **BLE Device Discovery** - Find and identify nearby Bluetooth devices
- 📡 **Real-time Monitoring** - Continuous proximity tracking with RSSI analysis
- 🔒 **Automatic Locking** - Instant Mac security when device moves away
- ⚙️ **Highly Configurable** - Custom thresholds, calibration, and tuning
- 🚀 **Background Service** - Daemon mode with service management
- 📊 **Verbose Logging** - Detailed RSSI, distance, and signal metrics
- 🧪 **100% Test Coverage** - Comprehensive pytest test suite
- 🔄 **CI/CD Ready** - GitHub Actions workflow included

## 📚 Documentation

**📖 Full documentation is available at the [B.R.I.O.S. Documentation Site](https://piero24.github.io/B.R.I.O.S/).**

- **[Installation Guide](https://piero24.github.io/B.R.I.O.S./docs/getting-started/installation)** — Homebrew and manual setup
- **[Quick Start](https://piero24.github.io/B.R.I.O.S./docs/getting-started/quick-start)** — Up and running in 5 minutes
- **[Configuration Reference](https://piero24.github.io/B.R.I.O.S./docs/guide/configuration)** — All environment variables and tuning
- **[CLI Usage](https://piero24.github.io/B.R.I.O.S./docs/guide/cli-usage)** — Complete command-line reference
- **[Architecture & API](https://piero24.github.io/B.R.I.O.S./docs/api/architecture)** — System design and module reference
- **[Testing Guide](https://piero24.github.io/B.R.I.O.S./docs/development/testing)** — Running and writing tests
- **[Contributing](https://piero24.github.io/B.R.I.O.S./docs/development/contributing)** — How to contribute
- **[FAQ](https://piero24.github.io/B.R.I.O.S./docs/faq)** — Frequently asked questions

## 🛠️ Requirements

> [!IMPORTANT]
> **Testing & Compatibility Notice**
> 
> This project has been tested **only** on:
> - **Hardware**: MacBook Pro M3 Pro with iPhone
> - **Python Version**: 3.12.6 (should work on Python 3.9+)
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
- Python 3.9+
- Bluetooth Low Energy adapter (built-in on all modern Macs)

## 📦 Installation

### Option 2: Manual Installation (Development)

```bash
# 1. Clone repository
git clone https://github.com/Piero24/B.R.I.O.S..git
cd B.R.I.O.S.

# 2. Create virtual environment
python3 -m venv env
source env/bin/activate

# 3. Install in editable mode
pip install -e .
```

---

## 🚀 Quick Start

1.  **Discover your device**:
    ```bash
    brios --scanner 15 -m
    ```
    *Note the MAC address of your device from the output.*

2.  **Configure**:
    Create a `.env` file in one of these locations (loaded in order):
    - `.env` (project root / current directory)
    - `~/.brios.env`
    - `~/.config/brios/config`

    Add your device's MAC address:
    ```bash
    echo 'TARGET_DEVICE_MAC_ADDRESS=AA:BB:CC:DD:EE:FF' > .env
    ```

3.  **Start Monitoring**:
    ```bash
    brios --target-mac -v
    ```

---

## ⚙️ Configuration

B.R.I.O.S. uses environment variables for configuration. You can set these in a `.env` file or across your system in the following locations (loaded in order):

1.  **Local:** `.env` (in the directory where you run the command)
2.  **Home File:** `~/.brios.env`
3.  **Home Folder:** `~/.brios/config` or `~/.brios/.env`
4.  **XDG Config:** `~/.config/brios/config`

### Quick Setup

If you installed via Homebrew, you can copy the example configuration to your home folder:

```bash
# Recommended: Create a hidden file in your home directory
cp $(brew --prefix brios)/share/brios/.env.example ~/.brios.env

# Alternative: Create a config folder
mkdir -p ~/.brios
cp $(brew --prefix brios)/share/brios/.env.example ~/.brios/config
```

If you installed manually from source:

```bash
cp .env.example ~/.brios.env
```

| Parameter | Description | Default |
| :--- | :--- | :--- |
| `TARGET_DEVICE_MAC_ADDRESS` | MAC address of the device to track | Required |
| `TARGET_DEVICE_UUID_ADDRESS` | UUID address (macOS privacy mode) | — |
| `TARGET_DEVICE_NAME` | Human-readable device name | `"Unknown Device Name"` |
| `TARGET_DEVICE_TYPE` | Device type (e.g., "phone", "watch") | `"Unknown Device"` |
| `DISTANCE_THRESHOLD_M` | Distance in meters to trigger lock | `2.0` |
| `GRACE_PERIOD_SECONDS` | Delay before re-triggering after unlock | `30` |
| `TX_POWER_AT_1M` | RSSI measured at 1 meter (dBm) | `-59` |
| `PATH_LOSS_EXPONENT` | Environment factor (2.0-4.0) | `2.8` |
| `SAMPLE_WINDOW` | Number of RSSI samples for smoothing | `12` |
| `SMOOTHING_METHOD` | Statistical method to smooth RSSI values ('median' or 'mean') | `median` |
| `OUT_OF_RANGE_DEBOUNCE_COUNT` | Consecutive checks to confirm out of range (1-9) | `3` |
| `LOCK_LOOP_THRESHOLD` | Lock events within window to trigger pause | `3` |
| `LOCK_LOOP_WINDOW` | Time window (seconds) for lock loop detection | `60` |
| `LOCK_LOOP_PENALTY` | Pause duration (seconds) on lock loop | `120` |

---

## 🚀 Usage

### Command Line Interface
Once installed, the `brios` command is available globally (also runnable via `python -m brios`).

- **Scan for devices**: `brios --scanner` or `brios -s [SECONDS]`
- **Monitor with MAC**: `brios --target-mac "AA:BB:CC..."` or `brios -tm`
- **Monitor with UUID**: `brios --target-uuid "XXXXXXXX..."` or `brios -tu`
- **Use real MAC addresses (macOS)**: Add `-m` to scanner/monitor commands
- **Verbose output**: Add `-v` to any monitor command
- **File logging**: Add `-f` to enable logging to file
- **Restart daemon**: `brios --restart`

### Background Daemon (macOS)
You can run B.R.I.O.S. as a background service:

**Using Homebrew (Loads on startup):**
```bash
brew services start brios    # Start and enable at login
brew services stop brios     # Stop the service
```

**Using Internal Service Manager:**
```bash
brios --start        # Start background process
brios --status       # Check status and PID
brios --stop         # Stop background process
brios --stop <1-24>  # Pause for 1 to 24 hours (e.g. brios --stop 2)
brios --stop -d      # Pause background process for 1 day
brios --stop -w      # Pause background process for 1 week
```

---

## 🧪 Development

### Running Tests
We use `pytest` for unit testing.
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=brios --cov-report=term-missing
```

### Code Formatting
We use `pyink` (Google's fork of Black) to maintain code style.
```bash
# Check formatting
pyink --check .

# Apply formatting
pyink .
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Bleak](https://github.com/hbldh/bleak) - Cross-platform BLE library
- [Pytest](https://pytest.org/) - Testing framework

## 📬 Contact

**Pietrobon Andrea** - [@Piero24](https://github.com/Piero24)

Project Link: [https://github.com/Piero24/B.R.I.O.S.](https://github.com/Piero24/B.R.I.O.S.)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/Piero24">Pietrobon Andrea</a>
  <br/>
  <sub>Copyright © 2024 - Released: November 2, 2024</sub>
</p>
