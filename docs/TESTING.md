# 🧪 Testing Guide

Complete guide to testing Bleissant, running tests, and writing new tests.

## Overview

Bleissant maintains **100% test coverage** with a comprehensive pytest-based test suite that includes:
- ✅ Unit tests for individual functions
- ✅ Integration tests for class interactions
- ✅ End-to-end tests for complete workflows
- ✅ Async test support with pytest-asyncio
- ✅ Mocking with pytest-mock
- ✅ CI/CD integration with GitHub Actions

---

## Quick Start

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_ble_monitor.py::test_estimate_distance -v

# Run in watch mode (requires pytest-watch)
ptw
```

---

## Test Structure

### File Organization

```
tests/
├── conftest.py              # Pytest configuration and fixtures
└── test_ble_monitor.py      # All tests for main.py
    ├── Mock Classes         # Test doubles for BLE components
    ├── Fixtures             # Reusable test setup
    ├── Unit Tests           # Function-level tests
    ├── Integration Tests    # Component interaction tests
    └── E2E Tests            # Full application flow tests
```

### Test Categories

#### 1. Unit Tests

Test individual functions in isolation:

```python
def test_estimate_distance(reloaded_main_new):
    """Test the distance estimation logic."""
    assert reloaded_main_new._estimate_distance(-59) == pytest.approx(1.0)
    assert reloaded_main_new._estimate_distance(-40) < 1.0
    assert reloaded_main_new._estimate_distance(-80) > 1.0
    assert reloaded_main_new._estimate_distance(0) == -1.0

def test_smooth_rssi(reloaded_main_new):
    """Test the RSSI smoothing logic."""
    from collections import deque
    buffer = deque([-60, -62, -58], maxlen=3)
    assert reloaded_main_new._smooth_rssi(buffer) == pytest.approx(-60.0)
    assert reloaded_main_new._smooth_rssi(deque()) is None
```

#### 2. Integration Tests

Test component interactions:

```python
@pytest.mark.asyncio
async def test_device_scanner_run(mocker, capsys, reloaded_main_new):
    """Test the DeviceScanner functionality and output."""
    mock_devices = {
        "AA:BB:CC:11:22:33": (
            MockBLEDevice("AA:BB:CC:11:22:33", "Device A"),
            MockAdvertisementData(-50),
        ),
    }
    
    async def mock_discover(*args, **kwargs):
        return mock_devices
    
    mocker.patch("bleak.BleakScanner.discover", side_effect=mock_discover)
    
    scanner = reloaded_main_new.DeviceScanner(
        duration=5, use_bdaddr=True, verbose=True
    )
    await scanner.run()
    
    captured = capsys.readouterr()
    assert "Scan Results" in captured.out
    assert "Device A" in captured.out
```

#### 3. End-to-End Tests

Test complete workflows:

```python
@pytest.mark.asyncio
async def test_application_cli_dispatch(mocker, mock_args, reloaded_main_new):
    """Test that the Application class calls the right components based on CLI args."""
    mock_sm = mocker.patch.object(reloaded_main_new, "ServiceManager")
    mock_ds = mocker.patch.object(reloaded_main_new, "DeviceScanner")
    
    # Test Service Start Command
    mock_args.start = True
    app = reloaded_main_new.Application(mock_args)
    await app.run()
    mock_sm.return_value.start.assert_called_once()
```

---

## Test Fixtures

### `conftest.py` Setup

```python
"""Pytest configuration file to set up the test environment."""

import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

### `reloaded_main_new` Fixture

Reloads the main module with mocked environment variables:

```python
@pytest.fixture(scope="function")
def reloaded_main_new(monkeypatch):
    """Set mock environment variables and reload main module."""
    monkeypatch.setenv("TARGET_DEVICE_MAC_ADDRESS", "AA:BB:CC:DD:EE:FF")
    monkeypatch.setenv("TARGET_DEVICE_UUID_ADDRESS", "12345678-1234-5678-1234-567812345678")
    monkeypatch.setenv("TARGET_DEVICE_NAME", "Test Beacon")
    monkeypatch.setenv("TX_POWER_AT_1M", "-59")
    monkeypatch.setenv("PATH_LOSS_EXPONENT", "2.8")
    monkeypatch.setenv("SAMPLE_WINDOW", "3")  # Smaller for testing
    monkeypatch.setenv("DISTANCE_THRESHOLD_M", "2.0")
    
    importlib.reload(main)
    return main
```

### `mock_args` Fixture

Creates a mock argparse.Namespace:

```python
@pytest.fixture
def mock_args(mocker):
    """Fixture to create a mock of argparse.Namespace."""
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

Mock Bleak before importing main module:

```python
# Mock bleak before it is imported by the main script
mock_bleak = MagicMock()
sys.modules["bleak"] = mock_bleak
sys.modules["bleak.backends"] = MagicMock()
sys.modules["bleak.backends.device"] = MagicMock()
sys.modules["bleak.backends.scanner"] = MagicMock()

# Now safe to import
import main
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
def test_service_manager_start_stop(mocker, tmp_path, reloaded_main_new):
    mock_popen = mocker.patch("subprocess.Popen")
    mock_os_kill = mocker.patch("os.kill")
    mocker.patch("time.sleep")  # Speed up tests
    
    # Test start
    manager.start()
    mock_popen.assert_called_with(...)
```

---

## Running Tests

### Local Development

```bash
# Basic test run
pytest

# With verbose output
pytest -v

# With short traceback
pytest --tb=short

# Stop on first failure
pytest -x

# Run specific test file
pytest tests/test_ble_monitor.py

# Run specific test
pytest tests/test_ble_monitor.py::test_estimate_distance

# Run tests matching pattern
pytest -k "scanner"

# Show print statements
pytest -s
```

### Coverage Reports

```bash
# Terminal coverage
pytest --cov=. --cov-report=term-missing

# HTML coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html

# XML coverage (for CI)
pytest --cov=. --cov-report=xml
```

### CI/CD Pipeline

Tests run automatically on GitHub Actions:

```yaml
- name: Run pytest
  run: |
    pytest -v --tb=short
```

View results at: `https://github.com/Piero24/Bleissant/actions`

---

## Writing New Tests

### Test Template

```python
@pytest.mark.asyncio  # For async tests
async def test_new_feature(mocker, reloaded_main_new):
    """Test description explaining what this verifies."""
    # Arrange - Set up test data and mocks
    mock_obj = mocker.patch("module.function")
    test_data = {...}
    
    # Act - Execute the code being tested
    result = await some_async_function(test_data)
    
    # Assert - Verify the results
    assert result == expected_value
    mock_obj.assert_called_once_with(expected_args)
```

### Best Practices

1. **AAA Pattern**: Arrange, Act, Assert
2. **Descriptive Names**: `test_scanner_discovers_multiple_devices`
3. **One Concept Per Test**: Test one thing at a time
4. **Use Fixtures**: Reuse setup code with fixtures
5. **Mock External Dependencies**: Don't make real BLE calls
6. **Test Edge Cases**: Empty buffers, invalid RSSI, etc.

### Example: Testing New Feature

```python
def test_new_distance_threshold(reloaded_main_new, mocker):
    """Test that custom distance thresholds trigger alerts correctly."""
    # Arrange
    target_address = "AA:BB:CC:DD:EE:FF"
    custom_threshold = 5.0  # 5 meters
    
    # Temporarily override threshold
    original_threshold = reloaded_main_new.DISTANCE_THRESHOLD_M
    reloaded_main_new.DISTANCE_THRESHOLD_M = custom_threshold
    
    flags = reloaded_main_new.Flags(
        daemon_mode=False,
        file_logging=False,
        verbose=False
    )
    monitor = reloaded_main_new.DeviceMonitor(
        target_address, use_bdaddr=True, flags=flags
    )
    
    mock_lock = mocker.patch.object(monitor, "_lock_macbook")
    
    # Act - Simulate RSSI that gives ~6m distance
    device = MockBLEDevice(target_address, "Test Device")
    for rssi in [-85, -85, -85]:  # ~6m distance
        adv_data = MockAdvertisementData(rssi)
        monitor._detection_callback(device, adv_data)
    
    # Assert
    mock_lock.assert_called_once()
    assert monitor.alert_triggered is True
    
    # Cleanup
    reloaded_main_new.DISTANCE_THRESHOLD_M = original_threshold
```

---

## Test Data

### Useful RSSI Values for Testing

| RSSI (dBm) | Approx Distance | Use Case |
|------------|----------------|----------|
| -40 | 0.3m | Very close proximity |
| -59 | 1.0m | Calibration reference |
| -70 | 2.0m | Threshold testing |
| -80 | 4.0m | Out of range |
| -90 | 8.0m | Far away |

### Formula for Test RSSI

```python
# Calculate RSSI for desired distance
TX_POWER = -59
PATH_LOSS = 2.8
distance = 3.0  # meters

rssi = TX_POWER - 10 * PATH_LOSS * math.log10(distance)
# Result: -73.4 dBm for 3 meters
```

---

## Debugging Tests

### Print Debug Information

```python
def test_with_debug(reloaded_main_new, capsys):
    result = some_function()
    
    # Capture print output
    captured = capsys.readouterr()
    print(f"Debug: result={result}")
    print(f"Captured output: {captured.out}")
    
    assert result == expected
```

### Use Pytest Debugger

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger immediately
pytest --trace
```

### Verbose Mocking

```python
# See all mock calls
mock_obj = mocker.Mock()
mock_obj.some_method()
print(mock_obj.mock_calls)  # [call.some_method()]
```

---

## Common Testing Patterns

### Testing Async Code

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

### Testing Exceptions

```python
def test_invalid_rssi():
    with pytest.raises(ValueError):
        invalid_operation()
```

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

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Unit Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12.6'
      
      - name: Install dependencies
        run: pip install -r requirements/ci.txt
      
      - name: Run tests
        run: pytest -v --tb=short
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
EOF

pre-commit install
```

---

## Test Metrics

### Current Coverage

```
Name                    Stmts   Miss  Cover
-------------------------------------------
main.py                   450      0   100%
tests/test_ble_monitor    280      0   100%
-------------------------------------------
TOTAL                     730      0   100%
```

### Performance

| Test Suite | Duration |
|------------|----------|
| Unit Tests | < 0.01s |
| Integration Tests | < 0.1s |
| Full Suite | < 0.5s |

---

For more information, see:
- [API Reference](API.md)
- [Architecture Documentation](ARCHITECTURE.md)
- [Contributing Guide](CONTRIBUTING.md)
