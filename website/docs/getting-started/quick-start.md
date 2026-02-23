---
id: quick-start
title: Quick Start
sidebar_position: 2
---

# Quick Start

Get B.R.I.O.S. up and running in under 5 minutes.

---

## Step 1: Discover Your Device

First, scan for nearby BLE devices to find your target device's MAC address:

```bash
brios --scanner 15 -m
```

- `--scanner 15` scans for 15 seconds (range: 5–60s).
- `-m` uses real MAC addresses instead of macOS privacy UUIDs (recommended).

**Example output:**

```
🥐 B.R.I.O.S. Device Scanner
──────────────────────────────────────────────────────────────────────
Duration:   15 seconds
Mode:       BD_ADDR (MAC addresses)
──────────────────────────────────────────────────────────────────────

● Scanning...

Scan Results (3 devices found)
──────────────────────────────────────────────────────────────────────
 1. iPhone                         │ AA:BB:CC:DD:EE:FF │  -52 dBm │ ~ 0.85m
 2. AirPods Pro                    │ 11:22:33:44:55:66 │  -68 dBm │ ~ 2.10m
 3. (Unknown)                      │ 77:88:99:AA:BB:CC │  -85 dBm │ ~ 6.30m
```

Note the MAC address of your target device from the output.

---

## Step 2: Configure

Create a `.env` configuration file. B.R.I.O.S. loads configuration from these locations (in order):

1. `.env` in the current working directory
2. `~/.brios.env`
3. `~/.brios/config` or `~/.brios/.env`
4. `~/.config/brios/config`

### Minimal Configuration

Set the MAC address of the device to track:

```bash
echo 'TARGET_DEVICE_MAC_ADDRESS=AA:BB:CC:DD:EE:FF' > ~/.brios.env
```

### Using the Example Configuration

If installed via Homebrew:

```bash
cp $(brew --prefix brios)/share/brios/.env.example ~/.brios.env
```

If installed from source:

```bash
cp .env.example ~/.brios.env
```

Then edit `~/.brios.env` with your device's MAC address.

---

## Step 3: Start Monitoring

### Foreground Mode (Interactive)

Run B.R.I.O.S. in the foreground with verbose output:

```bash
brios --target-mac -v
```

You will see real-time RSSI readings, smoothed signal values, and distance estimates:

```
Starting 🥐 B.R.I.O.S. Monitor
──────────────────────────────────────────────────────
Target:     iPhone (phone)
Address:    AA:BB:CC:DD:EE:FF
Threshold:  2.0m
TX Power:   -59 dBm @ 1m
Path Loss:  2.8
Samples:    12 readings
──────────────────────────────────────────────────────

● Monitoring active - Press Ctrl+C to stop

[14:32:01] RSSI:  -52 dBm → Smoothed: -53.2 dBm │ Distance:  0.85m │ Signal: Strong
[14:32:02] RSSI:  -55 dBm → Smoothed: -53.8 dBm │ Distance:  0.92m │ Signal: Strong
```

### Background Mode (Daemon)

Start B.R.I.O.S. as a background service:

```bash
brios --target-mac -v -f --start
```

Check status:

```bash
brios --status
```

Stop the service:

```bash
brios --stop
```

---

## What Happens When You Walk Away

1. **Signal weakens** — RSSI drops as you move away from your Mac.
2. **Distance exceeds threshold** — When the estimated distance surpasses `DISTANCE_THRESHOLD_M` (default: 2.0m), B.R.I.O.S. triggers a lock.
3. **Mac locks** — The screen locks immediately via `pmset displaysleepnow`.
4. **Grace period** — After you unlock, a configurable grace period (default: 30s) prevents immediate re-locking while the signal stabilizes.
5. **Monitoring resumes** — B.R.I.O.S. continues tracking automatically.

---

## Next Steps

- [Configuration Reference](../guide/configuration) — Fine-tune thresholds, calibration, and environment parameters
- [CLI Usage](../guide/cli-usage) — Explore all available commands and flags
- [Background Service](../guide/background-service) — Run B.R.I.O.S. as a persistent daemon
- [FAQ](../faq) — Answers to common questions
