# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation suite (API, Architecture, Testing, Contributing)
- Enhanced README with professional formatting and detailed sections
- GitHub Actions CI/CD pipeline integration badges

### Changed
- Reorganized requirements files into `requirements/` folder structure
- Improved test imports with `conftest.py` for better maintainability

## [1.0.0] - 2024-11-02

### Added
- Initial release of Bleissant
- BLE device discovery scanner
- Real-time proximity monitoring
- Automatic macOS locking on proximity loss
- Background service/daemon mode
- RSSI signal smoothing with configurable buffer
- Log-Distance Path Loss Model for accurate distance estimation
- Verbose output mode with detailed RSSI and distance metrics
- File logging support
- Service management commands (start/stop/restart/status)
- Comprehensive test suite with 100% coverage
- CI/CD pipeline with GitHub Actions
  - Code formatting checks (Black/Pyink)
  - Type checking (MyPy)
  - Unit tests (Pytest)
  - Security audit (pip-audit)
- Makefile for developer workflow automation
- `.env` configuration file support
- macOS native integration via PyObjC

### Features
- **Discovery Mode**: Scan for nearby BLE devices with RSSI and distance
- **Monitor Mode**: Continuous proximity tracking with configurable threshold
- **Alert System**: Automatic Mac locking when device moves out of range
- **Signal Processing**: Statistical RSSI smoothing to eliminate false positives
- **Daemon Support**: Background service with PID management
- **Logging**: Optional file logging for audit and debugging

### Technical
- Python 3.8+ support
- Async/await with asyncio
- Type hints with MyPy validation
- Cross-platform BLE via Bleak library
- Comprehensive docstrings
- Professional code architecture

---

## Release Notes

### v1.0.0 - Initial Release

🥐 B.R.I.O.S. is now production-ready with enterprise-grade features:

**🔍 Smart Device Tracking**
- Automatic BLE device discovery
- Real-time RSSI monitoring
- Accurate distance estimation (±20-30cm in controlled environments)

**🔒 Automated Security**
- Instant Mac locking on proximity loss
- Configurable distance thresholds
- Reconnection detection and alerts

**⚙️ Professional Features**
- Background daemon mode
- Comprehensive logging
- Service management interface
- Extensive configuration options

**🧪 Quality Assurance**
- 100% test coverage
- CI/CD with GitHub Actions
- Type-safe codebase
- Security auditing

**📚 Documentation**
- Complete API reference
- Architecture documentation
- Testing guide
- Contributing guidelines

---

<!-- ## Migration Guides

### From Pre-1.0 to 1.0

If you were using pre-release versions:

1. **Requirements Files**: Update import paths
   ```bash
   # Old
   pip install -r requirements.txt
   
   # New
   pip install -r requirements/dev.txt
   ```

2. **Test Imports**: Tests now use `conftest.py` for path setup
   - No manual `sys.path` manipulation needed in test files

3. **Environment Variables**: No changes needed
   - `.env` file format remains compatible -->

---

## Versioning

🥐 B.R.I.O.S. follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality (backwards-compatible)
- **PATCH** version: Bug fixes (backwards-compatible)

---

[Unreleased]: https://github.com/Piero24/Bleissant/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Piero24/Bleissant/releases/tag/v1.0.0
