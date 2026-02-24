---
id: background-service
title: Background Service
sidebar_position: 3
---

# Background Service

B.R.I.O.S. can run as a persistent background daemon on macOS, automatically monitoring your device and locking your Mac when you walk away.

---

## Starting the Service

### Using Homebrew Services

If you installed B.R.I.O.S. via Homebrew, you can use `brew services` for automatic startup at login:

```bash
# Start and enable at login
brew services start brios

# Stop the service
brew services stop brios
```

### Using the Built-In Service Manager

B.R.I.O.S. includes its own service manager for finer control:

```bash
# Start the background monitor
brios --target-mac -v -f --start

# Check status, PID, and recent activity
brios --status

# Stop the background monitor
brios --stop

# Restart the background monitor
brios --restart
```

When started with `--start`, B.R.I.O.S. automatically enables:
- **File logging** (`-f`) — All output is written to `~/.brios/.ble_monitor.log`
- **Verbose mode** (`-v`) — Detailed RSSI and distance data is captured

---

## Service Status

The `--status` command displays:

```
🥐 B.R.I.O.S. Monitor Status
──────────────────────────────────────────────────────
Status:     ● RUNNING
PID:        12345
Uptime:     01:23:45
Target:     iPhone
Address:    AA:BB:CC:DD:EE:FF
Threshold:  2.0m

Log file:   /Users/you/.brios/.ble_monitor.log

Recent activity:
  [14:30:01] RSSI: -52 dBm → Smoothed: -53.2 dBm │ Distance:  0.85m
  [14:30:02] RSSI: -55 dBm → Smoothed: -53.8 dBm │ Distance:  0.92m
  [14:30:03] RSSI: -54 dBm → Smoothed: -53.5 dBm │ Distance:  0.88m
──────────────────────────────────────────────────────
```

---

## Log File

When file logging is enabled, all output is written to:

```
~/.brios/.ble_monitor.log
```

### Viewing Logs

```bash
# Real-time log tail
tail -f ~/.brios/.ble_monitor.log

# View the full log
cat ~/.brios/.ble_monitor.log

# View the last 50 lines
tail -n 50 ~/.brios/.ble_monitor.log
```

### Log Format

```
[2026-02-23 14:30:01] RSSI: -52 dBm → Smoothed: -53.2 dBm │ Distance:  0.85m
[2026-02-23 14:30:15] ⚠️ ALERT: Device 'iPhone' is far away! (~3.45 m) - 🔒 MacBook locked
[2026-02-23 14:30:16] Screen locked - Scanner paused
[2026-02-23 14:31:20] Screen unlocked - Reconnecting scanner (locked for 64s)
[2026-02-23 14:31:21] Scanner reconnected - Monitoring resumed
```

---

## PID Management

The background process writes its PID to `~/.brios/.ble_monitor.pid`. This file is used by the service manager to track the running instance.

### Stale PID File

If B.R.I.O.S. crashes or is killed externally, the PID file may become stale. The service manager detects this automatically, but you can also clean up manually:

```bash
rm ~/.brios/.ble_monitor.pid
brios --start
```

---

## Watchdog

The background daemon includes a built-in watchdog that:

1. **Monitors scanner health** — Restarts the BLE scanner if no packets are received for 120 seconds.
2. **Detects external screen locks** — Pauses the scanner when the screen is locked (e.g., via keyboard shortcut) and resumes on unlock.
3. **Handles stuck lock handlers** — Forces a reset if the lock handling logic is stuck for more than 60 seconds.
4. **Lock loop protection** — If the Mac locks too many times within a short window, monitoring pauses temporarily to prevent excessive cycling.
