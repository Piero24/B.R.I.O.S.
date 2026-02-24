---
id: cli-usage
title: CLI Usage
sidebar_position: 2
---

# Command-Line Interface

Once installed, B.R.I.O.S. provides the `brios` command (also runnable via `python -m brios`). This page documents all available commands and flags.

---

## Synopsis

```bash
brios [SERVICE_COMMAND] [OPERATING_MODE] [OPTIONS]
```

---

## Service Control

Manage the B.R.I.O.S. background daemon:

| Command | Description |
|---|---|
| `brios --start` | Start B.R.I.O.S. as a background daemon |
| `brios --stop` | Stop the background daemon |
| `brios --restart` | Restart the background daemon |
| `brios --status` | Display daemon status, PID, uptime, and recent activity |

These commands are mutually exclusive — only one can be used per invocation.

:::tip Auto-resolve from .env
If your `.env` file contains a configured target address (`TARGET_DEVICE_MAC_ADDRESS` or `TARGET_DEVICE_UUID_ADDRESS`), you can run `brios --start` **without** specifying `--target-mac` or `--target-uuid`. B.R.I.O.S. will automatically resolve the target device from your configuration.
:::

---

## Operating Modes

### Scanner Mode

Discover nearby BLE devices:

```bash
# Default 15-second scan
brios --scanner

# Custom duration (5–60 seconds)
brios --scanner 30

# Short alias
brios -s 20

# With real MAC addresses (recommended on macOS)
brios --scanner 15 -m
```

### Monitor Mode — MAC Address

Track a device by its MAC address:

```bash
# Use the MAC from .env configuration
brios --target-mac

# Specify MAC directly on the command line
brios --target-mac "AA:BB:CC:DD:EE:FF"

# Short alias
brios -tm
```

### Monitor Mode — UUID

Track a device by its UUID (macOS privacy mode):

```bash
# Use the UUID from .env configuration
brios --target-uuid

# Specify UUID directly
brios --target-uuid "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"

# Short alias
brios -tu
```

:::info MAC vs UUID
On macOS, Bluetooth devices are assigned privacy-preserving UUIDs by default. Use the `-m` flag with scanner and monitor commands to see and use **real MAC addresses** instead. MAC addresses are more stable and recommended.
:::

---

## Options

| Flag | Alias | Description |
|---|---|---|
| `--macos-use-bdaddr` | `-m` | Use real MAC addresses on macOS instead of UUIDs (recommended) |
| `--verbose` | `-v` | Enable verbose output with RSSI, smoothed signal, and distance details |
| `--file-logging` | `-f` | Enable logging to `~/.brios/.ble_monitor.log` |
| `--version` | — | Show version information and exit |
| `--help` | `-h` | Show help message and exit |

---

## Usage Examples

### Basic Workflow

```bash
# 1. Discover devices
brios --scanner 15 -m

# 2. Start monitoring (MAC from .env)
brios --target-mac -v

# 3. Start as background service
brios --target-mac -v -f --start

# 4. Check status
brios --status

# 5. Stop the service
brios --stop
```

### Advanced Examples

```bash
# Monitor a specific device by MAC with verbose output
brios --target-mac "AA:BB:CC:DD:EE:FF" -m -v

# Monitor by UUID in macOS privacy mode
brios --target-uuid "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"

# Start daemon with file logging and verbose output
brios --target-mac -v -f --start

# Restart the background daemon
brios --restart
```

---

## Files

| File | Description |
|---|---|
| `~/.brios/.ble_monitor.pid` | PID file for the background daemon |
| `~/.brios/.ble_monitor.log` | Log file (when file logging is enabled) |
| `.env` / `~/.brios.env` | Configuration file with device settings |

---

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Normal exit |
| `1` | Fatal error |
| `130` | Interrupted by user (Ctrl+C) |
