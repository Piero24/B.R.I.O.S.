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
# Install from your tap (replace with your tap name)
brew install pietrobon/homebrew-brios/brios
```

# Clone and setup
git clone https://github.com/Piero24/B.R.I.O.S..git && cd B.R.I.O.S.
python3 -m venv env && source env/bin/activate
pip install -r requirements/dev.txt

# Discover your device
python3 main.py --scanner 15 -m

# Configure and start monitoring
cp .env.example .env  # Edit with your device MAC
python3 main.py --target-mac -v
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

- **[Complete Documentation](.github/README.md)** - Full project documentation
- **[Testing Guide](docs/TESTING.md)** - Running and writing tests
- **[Contributing Guide](docs/CONTRIBUTING.md)** - How to contribute
- **[FAQ](docs/FAQ.md)** - Frequently asked questions
- **[Changelog](CHANGELOG.md)** - Version history

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
    Create a `.env` file in your project root or home directory:
    ```bash
    cp .env.example .env
    # Edit .env with your device MAC address
    ```

3.  **Start Monitoring**:
    ```bash
    brios --target-mac -v
    ```

---

## ⚙️ Configuration

B.R.I.O.S. uses environment variables for configuration. You can set these in a `.env` file:

| Parameter | Description | Default |
| :--- | :--- | :--- |
| `TARGET_DEVICE_MAC_ADDRESS` | MAC address of the device to track | Required |
| `DISTANCE_THRESHOLD_M` | Distance in meters to trigger lock | `2.0` |
| `GRACE_PERIOD_SECONDS` | Delay before re-locking after unlock | `15` |
| `TX_POWER_AT_1M` | RSSI measured at 1 meter | `-59` |
| `PATH_LOSS_EXPONENT` | Environment factor (2.0-4.0) | `2.8` |

---

## 🚀 Usage

### Command Line Interface
Once installed, the `brios` command is available globally.

- **Scan for devices**: `brios --scanner`
- **Monitor with MAC**: `brios --target-mac "AA:BB:CC..."`
- **Monitor with UUID**: `brios --target-uuid "XXXXXXXX..."`
- **Verbose output**: Add `-v` to any monitor command.

### Background Daemon (macOS)
You can run B.R.I.O.S. as a background service:

**Using Homebrew (Loads on startup):**
```bash
brew services start brios    # Start and enable at login
brew services stop brios     # Stop the service
```

**Using Internal Service Manager:**
```bash
brios --start    # Start background process
brios --status   # Check status and PID
brios --stop     # Stop background process
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
- [PyObjC](https://github.com/ronaldoussoren/pyobjc) - macOS native integration
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
