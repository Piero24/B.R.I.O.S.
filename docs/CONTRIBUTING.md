# 🤝 Contributing to 🥐 B.R.I.O.S.

Thank you for considering contributing to B.R.I.O.S. (Bluetooth Reactive Intelligent Operator for Croissant Safety)! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Commit Message Guidelines](#commit-message-guidelines)

---

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behavior includes:**
- Trolling, insulting comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

---

## How Can I Contribute?

### Reporting Bugs

**Before submitting a bug report:**
1. Check the [existing issues](https://github.com/Piero24/B.R.I.O.S./issues)
2. Verify the bug exists in the latest version
3. Collect information about your environment

**When submitting a bug report, include:**
- Clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Screenshots if applicable
- Environment details (macOS version, Python version, etc.)
- Log files from `.ble_monitor.log` if available

### Suggesting Enhancements

**Before suggesting an enhancement:**
1. Check if it's already been suggested
2. Determine which part of the project your suggestion relates to
3. Consider if it fits the project's scope and goals

**When suggesting an enhancement, include:**
- Clear, descriptive title
- Detailed description of the proposed feature
- Why this enhancement would be useful
- Possible implementation approach

### Code Contributions

We welcome code contributions! Areas where you can help:
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
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/B.R.I.O.S..git
cd B.R.I.O.S.
```

### 2. Create Virtual Environment

```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -r requirements/dev.txt
```

### 4. Create Development Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 5. Set Up Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

---

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications via Pyink (Google-style):

```bash
# Format your code before committing
pyink .

# Or use make command
make format
```

### Code Style Rules

- **Line Length**: 80 characters
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Organized (stdlib, third-party, local)
- **Docstrings**: Google style for all public functions/classes
- **Type Hints**: Required for all function signatures

### Example Function

```python
def calculate_distance(rssi: float, tx_power: int, path_loss: float) -> float:
    """Calculates distance using Log-Distance Path Loss Model.
    
    Args:
        rssi: Received Signal Strength Indicator in dBm.
        tx_power: Calibrated signal strength at 1 meter.
        path_loss: Environmental path loss exponent.
    
    Returns:
        Estimated distance in meters. Returns -1.0 for invalid RSSI.
    
    Example:
        >>> calculate_distance(-60, -59, 2.8)
        1.05
    """
    if rssi == 0:
        return -1.0
    return 10 ** ((tx_power - rssi) / (10 * path_loss))
```

### Type Checking

Run MyPy to verify types:

```bash
mypy main.py
```

---

## Testing Requirements

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test
pytest tests/test_ble_monitor.py::test_estimate_distance -v
```

### Test Coverage Requirement

- **Minimum Coverage**: 90%
- **Target Coverage**: 100%
- All new code must include tests

### Writing Tests

```python
def test_new_feature(reloaded_main_new, mocker):
    """Test description following AAA pattern."""
    # Arrange - Set up test data
    mock_obj = mocker.patch("module.function")
    test_input = {...}
    
    # Act - Execute the code
    result = function_under_test(test_input)
    
    # Assert - Verify results
    assert result == expected_output
    mock_obj.assert_called_once()
```

---

## Pull Request Process

### Before Submitting

1. ✅ Update your branch with latest `main`
2. ✅ Run all tests (`pytest`)
3. ✅ Format code (`pyink .`)
4. ✅ Run type checking (`mypy main.py`)
5. ✅ Update documentation if needed
6. ✅ Add tests for new features

### Creating the Pull Request

1. **Push your branch**: `git push origin feature/your-feature-name`
2. **Open PR on GitHub** with clear title and description
3. **Fill out PR template** (if provided)
4. **Link related issues** using `Fixes #123` or `Closes #456`

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review performed
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Review Process

1. **Automated Checks**: CI/CD pipeline must pass
   - Code formatting (Black/Pyink)
   - Type checking (MyPy)
   - Unit tests (Pytest)
   - Security audit (pip-audit)

2. **Code Review**: At least one maintainer approval required

3. **Revisions**: Address review feedback promptly

4. **Merge**: Maintainers will merge once approved

---

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code restructuring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
# Feature
git commit -m "feat(monitor): add multi-device support"

# Bug fix
git commit -m "fix(scanner): handle empty device names correctly"

# Documentation
git commit -m "docs(readme): update installation instructions"

# With body
git commit -m "feat(alert): add email notification support

Add ability to send email notifications when device goes out
of range. Configurable via .env file with SMTP settings.

Closes #42"
```

---

## Development Workflow

### Typical Flow

```bash
# 1. Create feature branch
git checkout -b feature/awesome-feature

# 2. Make changes
# Edit files...

# 3. Test changes
pytest
pyink .
mypy main.py

# 4. Commit
git add .
git commit -m "feat: add awesome feature"

# 5. Push
git push origin feature/awesome-feature

# 6. Create PR on GitHub

# 7. Address review feedback
# Make changes...
git add .
git commit -m "fix: address review comments"
git push origin feature/awesome-feature

# 8. Merge (done by maintainer)
```

### Using Make Commands

```bash
# Format code
make format

# Run application
make run ARGS="--scanner 15 -m"

# Format and run
make ble:run ARGS="--target-mac -v"
```

---

## Questions?

If you have questions about contributing:

1. Check existing [issues](https://github.com/Piero24/B.R.I.O.S./issues)
2. Check [discussions](https://github.com/Piero24/B.R.I.O.S./discussions)
3. Open a new issue with the `question` label

---

## Recognition

Contributors will be recognized in:
- Project README
- Release notes
- GitHub contributors page

Thank you for making B.R.I.O.S. better! 🎉
