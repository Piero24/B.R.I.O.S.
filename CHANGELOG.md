# Changelog

All notable changes to 🥐 B.R.I.O.S. (Bluetooth Reactive Intelligent Operator for Croissant Safety) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2026-03-10

### Added
- **Seamless Scanner Recycling**: Refactored the watchdog scanner recycling logic to retain the historical distance buffer. This eliminates the 7-second "blind spot" when the scanner restarts, allowing for instant locking if a device moves out of range during a flush.
- **0.5s Max-Aggregation Window**: Introduced a packet rate-limiter that absorbs Bluetooth burst anomalies within a half-second window, picking only the strongest signal. This prevents false locks from instantaneous interference and makes a Debounce of `1` perfectly viable.
- **Automated Log Rotation**: The background daemon will now automatically search for and clean `.ble_monitor.log` files every 24 hours, deleting all entries older than 30 days to prevent excessive file bloat.

### Changed
- **Log Formatting**: Standardized all logs (file and terminal) to use full date timestamps `[YYYY-MM-DD HH:MM:SS]`.
- **Log Verbosity Limits**: Background file logs are now strictly rate-limited. Routine distance monitoring will only output to the `.log` file if 30 seconds have passed or the physical distance has shifted by ≥ 0.5 meters.
- **Single-Line Alerts**: Condensed the verbose multi-line lock/unlock alerts into clean single lines for better file readability.

## [1.0.3] - 2026-03-07

### Added
- Out-of-range debounce counter (`OUT_OF_RANGE_DEBOUNCE_COUNT`) to prevent false positive locking from momentary signal drops
- RSSI smoothing method configuration (`SMOOTHING_METHOD`) supporting `median` and `mean` algorithms for better outlier rejection

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
- `--update` / `-up` command for self-updating B.R.I.O.S. in place
- Automatic version check on launch with update notification (24-hour cache)
- Auto-detection of install method (Homebrew vs pip) for seamless updates
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
