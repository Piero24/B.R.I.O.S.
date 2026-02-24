---
id: testing
title: Testing Guide
sidebar_position: 1
---

# Testing Guide

B.R.I.O.S. maintains **100% test coverage** with a comprehensive `pytest`-based test suite. This guide covers running tests, writing new tests, and understanding the testing strategy.

---

## Quick Start

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# With coverage report
pytest --cov=brios --cov-report=term-missing

# HTML coverage report
pytest --cov=brios --cov-report=html
open htmlcov/index.html

# Run a specific test file
pytest tests/test_monitor.py

# Run a specific test
pytest tests/test_monitor.py::test_out_of_range_triggers_lock -v

# Run tests matching a pattern
pytest -k "scanner"

# Stop on first failure
pytest -x
```

---

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and path setup
├── test_monitor.py          # Tests for DeviceMonitor (alerts, grace period, lock loop)
└── test_utils_system.py     # Tests for utility functions and system calls
    ├── estimate_distance    # Path-loss distance calculation
    ├── smooth_rssi          # RSSI buffer smoothing
    ├── determine_target     # Target address resolution
    ├── is_screen_locked     # macOS screen lock detection
    └── lock_macbook         # macOS lock command
```

### Test Categories

| Category | File | Coverage |
|---|---|---|
| Unit Tests | `test_utils_system.py` | Individual functions: `estimate_distance`, `smooth_rssi`, `determine_target_address` |
| Integration Tests | `test_monitor.py` | Component interactions: `DeviceMonitor`, `DeviceScanner` |
| End-to-End Tests | `test_monitor.py` | Full workflows: CLI dispatch, service management |

---

## Fixtures

### `conftest.py`

Sets up the Python path so tests can import the `brios` package:

```python
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

### `reloaded_main_new`

Reloads the main module with mocked environment variables for each test:

```python
@pytest.fixture(scope="function")
def reloaded_main_new(monkeypatch):
    monkeypatch.setenv("TARGET_DEVICE_MAC_ADDRESS", "AA:BB:CC:DD:EE:FF")
    monkeypatch.setenv("TARGET_DEVICE_UUID_ADDRESS", "12345678-...")
    monkeypatch.setenv("TARGET_DEVICE_NAME", "Test Beacon")
    monkeypatch.setenv("TX_POWER_AT_1M", "-59")
    monkeypatch.setenv("PATH_LOSS_EXPONENT", "2.8")
    monkeypatch.setenv("SAMPLE_WINDOW", "3")
    monkeypatch.setenv("DISTANCE_THRESHOLD_M", "2.0")
    importlib.reload(main)
    return main
```

### `mock_args`

Creates a mock `argparse.Namespace` with default values:

```python
@pytest.fixture
def mock_args(mocker):
    args = mocker.MagicMock()
    args.start = False
    args.stop = False
    args.scanner = None
    args.target_mac = None
    args.verbose = False
    return args
```

---

## Mocking Strategy

### BLE Components

Bleak is imported at the module level, so it must be mocked **before** importing `brios.core` modules:

```python
from unittest.mock import MagicMock
import sys

mock_bleak = MagicMock()
sys.modules["bleak"] = mock_bleak
sys.modules["bleak.backends"] = MagicMock()
sys.modules["bleak.backends.device"] = MagicMock()
sys.modules["bleak.backends.scanner"] = MagicMock()

from brios.core.monitor import DeviceMonitor
```

### Mock Data Classes

```python
class MockBLEDevice:
    def __init__(self, address, name):
        self.address = address
        self.name = name

class MockAdvertisementData:
    def __init__(self, rssi):
        self.rssi = rssi
```

### System Commands

```python
def test_service_manager(mocker, tmp_path, reloaded_main_new):
    mock_popen = mocker.patch("subprocess.Popen")
    mock_os_kill = mocker.patch("os.kill")
    mocker.patch("time.sleep")
    manager.start()
    mock_popen.assert_called_with(...)
```

---

## Writing New Tests

### Template

```python
@pytest.mark.asyncio
async def test_new_feature(mocker, reloaded_main_new):
    """Test description explaining what this verifies."""
    # Arrange
    mock_obj = mocker.patch("module.function")
    test_data = {...}

    # Act
    result = await some_async_function(test_data)

    # Assert
    assert result == expected_value
    mock_obj.assert_called_once_with(expected_args)
```

### Best Practices

1. **AAA Pattern** — Arrange, Act, Assert
2. **Descriptive names** — `test_scanner_discovers_multiple_devices`
3. **One concept per test** — Test one behavior at a time
4. **Use fixtures** — Reuse setup code
5. **Mock external dependencies** — Never make real BLE or system calls
6. **Test edge cases** — Empty buffers, invalid RSSI values, `None` returns

### Parametrized Tests

```python
@pytest.mark.parametrize("rssi,expected_distance", [
    (-59, 1.0),
    (-70, 2.0),
    (-80, 4.0),
])
def test_distance_estimation(rssi, expected_distance, reloaded_main_new):
    distance = reloaded_main_new._estimate_distance(rssi)
    assert distance == pytest.approx(expected_distance, rel=0.1)
```

---

## RSSI Test Data

| RSSI (dBm) | Approx Distance | Use Case |
|---|---|---|
| −40 | 0.3m | Very close proximity |
| −59 | 1.0m | Calibration reference |
| −70 | 2.0m | Threshold testing |
| −80 | 4.0m | Out of range |
| −90 | 8.0m | Far away |

### Computing RSSI for a Target Distance

```python
import math

TX_POWER = -59
PATH_LOSS = 2.8
distance = 3.0  # meters

rssi = TX_POWER - 10 * PATH_LOSS * math.log10(distance)
# Result: ≈ −72.4 dBm
```

---

## CI/CD Integration

Tests run automatically on every push and pull request via GitHub Actions:

```yaml
- name: Run pytest
  run: pytest -v --tb=short
```

View results at: [GitHub Actions](https://github.com/Piero24/B.R.I.O.S./actions)

---

## Coverage Metrics

B.R.I.O.S. targets **100% test coverage** across all modules:

```
brios/__init__.py         100%
brios/cli.py              100%
brios/core/config.py      100%
brios/core/monitor.py     100%
brios/core/scanner.py     100%
brios/core/service.py     100%
brios/core/system.py      100%
brios/core/utils.py       100%
```
