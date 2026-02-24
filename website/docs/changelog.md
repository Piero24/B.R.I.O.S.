---
id: changelog
title: Changelog
sidebar_position: 7
---

# Changelog

All notable changes to 🥐 B.R.I.O.S. (Bluetooth Reactive Intelligent Operator for Croissant Safety) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-23

Initial release of 🥐 B.R.I.O.S. — a BLE proximity monitor for macOS that
automatically locks your Mac when a trusted Bluetooth device moves out of range.

### Added
- BLE device discovery scanner with RSSI and estimated distance
- Real-time proximity monitoring with configurable threshold
- Automatic macOS screen locking on proximity loss
- Background daemon mode with PID management (`-f` flag)
- RSSI signal smoothing with configurable buffer size
- Log-Distance Path Loss Model for accurate distance estimation
- Verbose output mode with detailed RSSI and distance metrics (`-v` flag)
- File logging support (`-l` flag)
- Service management commands: start / stop / restart / status
- Watchdog loop for scanner health monitoring and automatic recovery
- Lock loop protection to prevent excessive locking cycles
- Grace period to suppress false triggers after unlock/resume
- Scanner reconnection with retry and exponential backoff
- Bleak monkeypatch for macOS CoreBluetooth `None` address handling
- Modular `brios/` installable package with CLI entry point (`brios` command)
- Multi-location config loading (`.env`, `~/.brios.env`, `~/.config/brios/config`)
- `--version` argument to display version information
- Homebrew formula for easy installation (`brew install brios`)
- Makefile for developer workflow automation
- macOS native integration via ctypes (CoreGraphics)
- Comprehensive help documentation with all parameters and examples
- CI/CD pipeline with GitHub Actions
  - Code formatting checks (Pyink)
  - Type checking (MyPy)
  - Unit tests (Pytest)
  - Security audit (pip-audit)
  - Automated release on push to main

---

## Versioning

🥐 B.R.I.O.S. follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality (backwards-compatible)
- **PATCH** version: Bug fixes (backwards-compatible)

---

[1.0.0]: https://github.com/Piero24/B.R.I.O.S./releases/tag/v1.0.0
