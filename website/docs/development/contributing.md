---
id: contributing
title: Contributing
sidebar_position: 2
---

# Contributing to B.R.I.O.S.

Thank you for considering contributing to B.R.I.O.S.! This guide provides everything you need to get started.

---

## How Can I Contribute?

### Reporting Bugs

**Before submitting a bug report:**

1. Check the [existing issues](https://github.com/Piero24/B.R.I.O.S./issues).
2. Verify the bug exists in the latest version.
3. Collect information about your environment.

**When submitting a bug report, include:**

- Clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Screenshots if applicable
- Environment details (macOS version, Python version, etc.)
- Log files from `~/.brios/.ble_monitor.log` if available

### Suggesting Enhancements

1. Check if the enhancement has already been suggested.
2. Determine which part of the project your suggestion relates to.
3. Consider whether it fits the project's scope and goals.

### Code Contributions

We welcome contributions in:

- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test coverage expansion
- Code refactoring

---

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/B.R.I.O.S..git
cd B.R.I.O.S.
```

### 2. Create Virtual Environment

```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install Development Dependencies

```bash
pip install -r requirements/dev.txt
```

### 4. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

---

## Coding Standards

### Python Style

B.R.I.O.S. follows **PEP 8** with Google-style modifications via [Pyink](https://github.com/google/pyink):

```bash
# Format all code
pyink .

# Or use the Makefile
make format
```

### Rules

| Rule | Value |
|---|---|
| Line length | 80 characters |
| Indentation | 4 spaces (no tabs) |
| Imports | Organized: stdlib → third-party → local |
| Docstrings | Google-style for all public functions/classes |
| Type hints | Required for all function signatures |

### Example

```python
def calculate_distance(rssi: float, tx_power: int, path_loss: float) -> float:
    """Calculates distance using Log-Distance Path Loss Model.

    Args:
        rssi: Received Signal Strength Indicator in dBm.
        tx_power: Calibrated signal strength at 1 meter.
        path_loss: Environmental path loss exponent.

    Returns:
        Estimated distance in meters. Returns -1.0 for invalid RSSI.
    """
    if rssi == 0:
        return -1.0
    return 10 ** ((tx_power - rssi) / (10 * path_loss))
```

### Type Checking

```bash
mypy brios/
```

---

## Testing Requirements

- **Minimum coverage**: 90%
- **Target coverage**: 100%
- All new code must include tests

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=brios --cov-report=term-missing
```

See the [Testing Guide](./testing) for detailed information.

---

## Pull Request Process

### Before Submitting

- [ ] Update your branch with latest `main`
- [ ] Run all tests (`pytest`)
- [ ] Format code (`pyink .`)
- [ ] Run type checking (`mypy brios/`)
- [ ] Update documentation if needed
- [ ] Add tests for new features

### Creating a Pull Request

1. Push your branch: `git push origin feature/your-feature-name`
2. Open a PR on GitHub with a clear title and description
3. Link related issues using `Fixes #123` or `Closes #456`

### Review Process

1. **Automated checks** must pass (formatting, type checking, tests, security audit)
2. **Code review** — At least one maintainer approval required
3. **Revisions** — Address review feedback promptly

---

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>
```

### Types

| Type | Description |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code style (formatting, no logic change) |
| `refactor` | Code restructuring |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |

### Examples

```bash
git commit -m "feat(monitor): add multi-device support"
git commit -m "fix(scanner): handle empty device names correctly"
git commit -m "docs(readme): update installation instructions"
```

---

## Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/awesome-feature

# 2. Make changes and test
pytest
pyink .
mypy brios/

# 3. Commit
git add .
git commit -m "feat: add awesome feature"

# 4. Push and open PR
git push origin feature/awesome-feature
```

### Makefile Commands

```bash
make format                        # Format code with Pyink
make run ARGS="--scanner 15 -m"    # Run with arguments
make ble-run ARGS="--target-mac -v" # Format + run
make check                         # Run MyPy type checking
```

---

## Questions?

- Check [existing issues](https://github.com/Piero24/B.R.I.O.S./issues)
- Open a [new issue](https://github.com/Piero24/B.R.I.O.S./issues/new) with the `question` label
- Start a [discussion](https://github.com/Piero24/B.R.I.O.S./discussions)
