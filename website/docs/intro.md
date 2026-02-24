---
id: intro
title: Introduction
sidebar_position: 1
---

# 🥐 B.R.I.O.S.

**Bluetooth Reactive Intelligent Operator for Croissant Safety**

> Enterprise-grade proximity monitoring for macOS security automation.
> Automatically lock your Mac when your iPhone, Apple Watch, or any Bluetooth device moves out of range.

---

## What is B.R.I.O.S.?

B.R.I.O.S. is a professional BLE (Bluetooth Low Energy) proximity monitoring system for macOS. It continuously tracks the distance between your Mac and a trusted Bluetooth device — such as an iPhone, Apple Watch, or Android phone — and **automatically locks your Mac** the moment the device moves beyond a configurable distance threshold.

Think of it as a smart, zero-touch security layer: walk away from your desk, and your Mac locks itself. Return, and monitoring resumes seamlessly.

---

## Key Features

| Feature | Description |
|---|---|
| 🔍 **BLE Device Discovery** | Scan and identify nearby Bluetooth Low Energy devices |
| 📡 **Real-Time Monitoring** | Continuous proximity tracking with RSSI signal analysis |
| 🔒 **Automatic Locking** | Instant macOS screen lock when the device leaves range |
| ⚙️ **Highly Configurable** | Custom distance thresholds, calibration, and environment tuning |
| 🚀 **Background Service** | Daemon mode with full service lifecycle management |
| 📊 **Verbose Logging** | Detailed RSSI, smoothed signal, and distance metrics |
| 🛡️ **Lock Loop Protection** | Intelligent safeguards against excessive lock/unlock cycles |
| 🔄 **Automatic Recovery** | Watchdog and scanner reconnection with exponential backoff |
| 🧪 **100% Test Coverage** | Comprehensive pytest-based test suite |
| 🔄 **CI/CD Ready** | GitHub Actions pipeline with formatting, type checks, and security audits |

---

## How It Works

B.R.I.O.S. uses the **Log-Distance Path Loss Model** to estimate the physical distance between your Mac and the target device based on the received Bluetooth signal strength (RSSI):

```
distance = 10 ^ ((TX_POWER − RSSI) / (10 × PATH_LOSS_EXPONENT))
```

1. **Scan**: The BLE scanner listens for advertisement packets from the target device.
2. **Smooth**: Raw RSSI samples are collected into a rolling buffer and averaged to eliminate noise.
3. **Estimate**: The smoothed RSSI is converted to a distance estimate using the path loss model.
4. **Act**: If the estimated distance exceeds the configured threshold, macOS locks the screen immediately.
5. **Recover**: After the screen is unlocked, B.R.I.O.S. automatically resumes monitoring with a grace period to prevent false re-triggers.

---

## System Requirements

- **macOS** 10.15 (Catalina) or later
- **Bluetooth Low Energy** adapter (built-in on all modern Macs)
- **Python** 3.9+ (installed automatically via Homebrew, only needed manually for source installs)

---

## Quick Links

- [Installation](./getting-started/installation) — Get B.R.I.O.S. installed via Homebrew or from source
- [Quick Start](./getting-started/quick-start) — Start monitoring in under 5 minutes
- [Configuration](./guide/configuration) — Full reference for all environment variables
- [CLI Usage](./guide/cli-usage) — Complete command-line interface reference
- [FAQ](./faq) — Answers to common questions

---

## Compatibility Notice

:::caution Testing & Compatibility
This project has been tested on:
- **Hardware**: MacBook Pro M3 Pro with iPhone
- **Python**: 3.12.6 (should work on Python 3.9+)
- **OS**: macOS (Bluetooth stack is macOS-specific)

**Device pairing requirements:**
- If your Mac and iPhone/device use **different Apple IDs**, you **must pair them first** in **System Settings → Bluetooth**. Otherwise, Apple hides the MAC address and the device won't be discoverable.
- **Android devices** should work without pairing requirements.
- **Apple Watch** is currently **not discoverable from Mac** due to Apple's BLE restrictions.

![Bluetooth pairing in System Settings](/img/paring.png)

If you encounter issues on other configurations, please [report them](https://github.com/Piero24/B.R.I.O.S./issues).
:::
