# Bleissant

<p align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/3145/3145073.png" width="100">
</p>

<p align="center">
  <strong>Enterprise-grade BLE proximity monitoring for macOS security automation</strong>
  <br/>
  Automatically lock your Mac when your iPhone, Apple Watch, or BLE device moves out of range
</p>

<p align="center">
  <a href="https://github.com/Piero24/Bleissant/blob/main/.github/README.md"><strong>📖 Full Documentation »</strong></a>
  <br/>
  <br/>
  <a href=".github/README.md#quick-start">Quick Start</a>
  •
  <a href="docs/FAQ.md">FAQ</a>
  •
  <a href="https://github.com/Piero24/Bleissant/issues">Report Bug</a>
  •
  <a href="https://github.com/Piero24/Bleissant/issues">Request Feature</a>
</p>

---

## ⚡ Quick Start

```bash
# Clone and setup
git clone https://github.com/Piero24/Bleissant.git && cd Bleissant
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
> - **Python Version**: 3.12.6 (should work on Python 3.8+)
> - **OS**: macOS (Bluetooth stack specific to macOS)
> 
> **Critical Device Requirements:**
> - ⚠️ **Different Apple ID Pairing**: If your Mac and iPhone/device use **different Apple IDs**, you **must pair them first** in **System Settings → Bluetooth**. Otherwise, Apple hides the MAC address and the device won't be discoverable.
> - ⚠️ **Android devices** should work without pairing requirements.
> - ⚠️ **Apple Watch**: Currently **not discoverable from Mac** due to Apple's BLE restrictions.
> 
> If you encounter issues on other configurations, please [report them](https://github.com/Piero24/Bleissant/issues).

**System Requirements:**

- macOS 10.15 (Catalina) or later
- Python 3.8+
- Bluetooth Low Energy adapter (built-in on all modern Macs)

## 📦 Installation

```bash
# 1. Clone repository
git clone https://github.com/Piero24/Bleissant.git
cd Bleissant

# 2. Create virtual environment
python3 -m venv env
source env/bin/activate

# 3. Install dependencies
pip install -r requirements/dev.txt

# 4. Configure
cp .env.example .env
# Edit .env with your device information
```

## 🚀 Usage

### Discovery Mode
```bash
python3 main.py --scanner 15 -m
```

### Monitor Mode (Foreground)
```bash
python3 main.py --target-mac -v
```

### Background Service
```bash
python3 main.py --target-mac -v -f --start
python3 main.py --status
python3 main.py --stop
```

## 🏗️ Architecture

```
Application → [ServiceManager | DeviceScanner | DeviceMonitor]
                                                      ↓
                                              Signal Processing
                                                      ↓
                                              Distance Calculation
                                                      ↓
                                              Alert & Mac Lock
```

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=. --cov-report=term-missing
```

**Current Coverage**: 100%

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Bleak](https://github.com/hbldh/bleak) - Cross-platform BLE library
- [PyObjC](https://github.com/ronaldoussoren/pyobjc) - macOS native integration
- [Pytest](https://pytest.org/) - Testing framework

## 📬 Contact

**Pietrobon Andrea** - [@Piero24](https://github.com/Piero24)

Project Link: [https://github.com/Piero24/Bleissant](https://github.com/Piero24/Bleissant)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/Piero24">Pietrobon Andrea</a>
  <br/>
  <sub>Copyright © 2024 - Released: November 2, 2024</sub>
</p>
