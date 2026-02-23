# 🥐 B.R.I.O.S.

**Bluetooth Reactive Intelligent Operator for Croissant Safety**

Enterprise-grade proximity monitoring for macOS — automatically lock your Mac when your iPhone, Apple Watch, or Bluetooth device moves out of range.

---

## Features

- 🔍 BLE device discovery and identification
- 📡 Real-time proximity tracking with RSSI signal analysis
- 🔒 Automatic macOS screen locking when device leaves range
- ⚙️ Configurable distance thresholds, calibration, and environment tuning
- 🚀 Background daemon with service lifecycle management
- 🛡️ Lock loop protection and automatic scanner recovery

## Quick Start

```bash
# Install via Homebrew
brew tap Piero24/brios https://github.com/Piero24/B.R.I.O.S.
brew install brios

# Discover nearby devices
brios --scanner 15 -m

# Configure your device
echo 'TARGET_DEVICE_MAC_ADDRESS=AA:BB:CC:DD:EE:FF' > ~/.brios.env

# Start monitoring
brios --target-mac -v
```

## Requirements

- macOS 10.15 (Catalina) or later
- Python 3.9+
- Bluetooth Low Energy adapter (built-in on all modern Macs)

## Documentation

**📖 Full documentation is available at the [B.R.I.O.S. Documentation Site](https://piero24.github.io/B.R.I.O.S/).**

The documentation includes:

- [Installation Guide](https://piero24.github.io/B.R.I.O.S./docs/getting-started/installation) — Homebrew and manual setup
- [Quick Start](https://piero24.github.io/B.R.I.O.S./docs/getting-started/quick-start) — Up and running in 5 minutes
- [Configuration Reference](https://piero24.github.io/B.R.I.O.S./docs/guide/configuration) — All environment variables and tuning
- [CLI Usage](https://piero24.github.io/B.R.I.O.S./docs/guide/cli-usage) — Complete command-line reference
- [Architecture & API](https://piero24.github.io/B.R.I.O.S./docs/api/architecture) — System design and module reference
- [Testing Guide](https://piero24.github.io/B.R.I.O.S./docs/development/testing) — Running and writing tests
- [Contributing](https://piero24.github.io/B.R.I.O.S./docs/development/contributing) — How to contribute
- [FAQ](https://piero24.github.io/B.R.I.O.S./docs/faq) — Frequently asked questions

## Development

```bash
# Clone and install
git clone https://github.com/Piero24/B.R.I.O.S..git
cd B.R.I.O.S.
python3 -m venv env && source env/bin/activate
pip install -e .

# Run tests
pytest

# Format code
pyink .
```

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Contact

**Pietrobon Andrea** — [@Piero24](https://github.com/Piero24)

Project Link: [https://github.com/Piero24/B.R.I.O.S.](https://github.com/Piero24/B.R.I.O.S.)

