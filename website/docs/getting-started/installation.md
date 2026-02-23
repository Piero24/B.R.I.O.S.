---
id: installation
title: Installation
sidebar_position: 1
---

# Installation

B.R.I.O.S. can be installed via **Homebrew** (recommended) or manually from source for development purposes.

---

## Option 1: Homebrew (Recommended)

The simplest way to install B.R.I.O.S. on macOS:

```bash
# Tap the repository
brew tap Piero24/brios https://github.com/Piero24/B.R.I.O.S.

# Install brios
brew install brios
```

After installation, the `brios` command is available globally in your terminal.

---

## Option 2: Manual Installation (Development)

Use this method if you want to contribute to B.R.I.O.S. or run the latest development version.

### 1. Clone the Repository

```bash
git clone https://github.com/Piero24/B.R.I.O.S..git
cd B.R.I.O.S.
```

### 2. Create a Virtual Environment

```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install in Editable Mode

```bash
pip install -e .
```

This installs B.R.I.O.S. in editable (development) mode, meaning changes to the source code take effect immediately without re-installing.

You can also run B.R.I.O.S. as a Python module:

```bash
python -m brios --help
```

---

## Verifying the Installation

After installing, verify that B.R.I.O.S. is available:

```bash
brios --version
```

You should see output similar to:

```
🥐 B.R.I.O.S. v1.0.5
```

---

## Bluetooth Permissions

On macOS, your terminal application needs Bluetooth permissions to scan for devices:

1. Open **System Settings**
2. Navigate to **Privacy & Security** → **Bluetooth**
3. Enable Bluetooth access for your terminal app (Terminal.app, iTerm2, VS Code terminal, etc.)

:::tip
If you see "Permission Denied" errors when scanning, this is almost always a missing Bluetooth permission for your terminal app.
:::

---

## Dependencies

B.R.I.O.S. depends on the following Python packages (installed automatically):

| Package | Version | Purpose |
|---|---|---|
| [Bleak](https://github.com/hbldh/bleak) | 0.21.1 | Cross-platform BLE communication library |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | ≥1.0.0 | Environment variable loading from `.env` files |

---

## Next Steps

Once installed, proceed to the [Quick Start](./quick-start) guide to configure and start monitoring your device.
