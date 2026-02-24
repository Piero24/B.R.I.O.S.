<div align="center">

# 🥐 B.R.I.O.S.

**Bluetooth Reactive Intelligent Operator for Croissant Safety**

Enterprise-grade proximity monitoring for macOS — automatically lock your Mac when your iPhone, Apple Watch, or Bluetooth device moves out of range.

[![GitHub release](https://img.shields.io/github/v/release/Piero24/B.R.I.O.S.?include_prereleases&style=flat-square&color=blue)](https://github.com/Piero24/B.R.I.O.S./releases)
[![PyPI version](https://img.shields.io/pypi/v/brios?style=flat-square&color=blue)](https://pypi.org/project/brios/)
[![License: MIT](https://img.shields.io/github/license/Piero24/B.R.I.O.S.?style=flat-square&color=green)](LICENSE)
[![Python](https://img.shields.io/badge/python-≥3.9-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Platform](https://img.shields.io/badge/platform-macOS-000000?style=flat-square&logo=apple&logoColor=white)](https://www.apple.com/macos)
[![Homebrew](https://img.shields.io/badge/homebrew-tap-FBB040?style=flat-square&logo=homebrew&logoColor=white)](https://github.com/Piero24/B.R.I.O.S./blob/main/Formula/brios.rb)
[![GitHub Downloads](https://img.shields.io/github/downloads/Piero24/B.R.I.O.S./total?style=flat-square&label=downloads&color=purple)](https://github.com/Piero24/B.R.I.O.S./releases)
[![GitHub stars](https://img.shields.io/github/stars/Piero24/B.R.I.O.S.?style=flat-square&color=yellow)](https://github.com/Piero24/B.R.I.O.S./stargazers)
[![Docs](https://img.shields.io/badge/docs-online-blue?style=flat-square&logo=readthedocs&logoColor=white)](https://piero24.github.io/B.R.I.O.S./)

</div>

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

# Configure your device (edit with your MAC address)
cat > ~/.brios.env << 'EOF'
TARGET_DEVICE_MAC_ADDRESS=AA:BB:CC:DD:EE:FF
TARGET_DEVICE_NAME=My iPhone
TARGET_DEVICE_TYPE=phone
DISTANCE_THRESHOLD_M=2.0
TX_POWER_AT_1M=-59
PATH_LOSS_EXPONENT=2.8
SAMPLE_WINDOW=12
EOF

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

