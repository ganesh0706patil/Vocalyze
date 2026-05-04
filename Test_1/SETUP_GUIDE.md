# Vocalyze Testing Infrastructure Setup Guide

Complete guide for setting up and running the Vocalyze testing suite.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running Tests](#running-tests)
6. [Understanding Test Coverage](#understanding-test-coverage)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Overview

The Vocalyze testing suite provides comprehensive test coverage across all major components:

- **320+ Test Cases** across 5 major modules
- **5 Test Files** for different functionality areas
- **78%+ Target Coverage** for production code
- **Pytest-based Framework** for easy integration

### Test Modules

| Module | File | Tests | Scope |
|--------|------|-------|-------|
| Authentication | test_authentication.py | 60+ | User management, passwords, tokens |
| Assessment | test_assessment.py | 50+ | Assessments, questions, scoring |
| Audio | test_audio_processing.py | 60+ | Transcription, fluency, pronunciation |
| Feedback | test_feedback.py | 70+ | Feedback generation and delivery |
| Integration | test_api_integration.py | 80+ | API endpoints, system flows |

## Prerequisites

### Required Software
- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control)

### Recommended
- Virtual environment (venv, conda, or poetry)
- IDE with pytest support (VS Code, PyCharm, etc.)
- 2GB+ RAM for running full test suite

### Check Prerequisites
```bash
python --version        # Should be 3.8+
pip --version          # Should be latest
virtualenv --version   # For virtual environments
```

## Installation

### Step 1: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 2: Install Testing Dependencies

```bash
# Option A: Install individual packages
pip install pytest==7.4.3
pip install pytest-asyncio==0.21.1
pip install pytest-cov==4.1.0
pip install pytest-mock==3.12.0
pip install faker==20.1.0

# Option B: From requirements file (if available)
pip install -r requirements-test.txt

# Option C: Install all common packages
pip install pytest pytest-asyncio pytest-cov pytest-mock faker
```

### Step 3: Verify Installation

```bash
# Check pytest installation
pytest --version

# Run a quick sanity check
pytest TestingFiles/ --collect-only
```

## Configuration

### pytest.ini Setup

The `pytest.ini` file in TestingFiles folder contains configuration:

```ini
[pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers = 
    unit: Unit tests
    integration: Integration tests
    api: API tests
    slow: Slow running tests
    audio: Audio tests
    db: Database tests
```

### Environment Variables

Create a `.env` file in TestingFiles folder (if needed):

```bash
# Testing configuration
TESTING=true
TEST_DB_URL=sqlite:///test.db
GROQ_API_KEY=test_key_for_testing
API_FRONTEND_URL=http://localhost:3000
```

### IDE Configuration

**VS Code:**
```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["TestingFiles"],
    "python.linting.pylintEnabled": true
}
```

**PyCharm:**
- Go to Settings → Tools → Python Integrated Tools
- Select pytest as default test runner

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest TestingFiles/

# Run with verbose output
pytest TestingFiles/ -v

# Run specific test file
pytest TestingFiles/test_authentication.py

# Run specific test class
pytest TestingFiles/test_authentication.py::TestUserLogin

# Run specific test
pytest TestingFiles/test_authentication.py::TestUserLogin::test_login_success
```

### Filter by Markers

```bash
# Run only unit tests
pytest TestingFiles/ -m unit

# Run only integration tests
pytest TestingFiles/ -m integration

# Skip slow tests
pytest TestingFiles/ -m "not slow"

# Run unit OR api tests
pytest TestingFiles/ -m "unit or api"

# Run tests with specific keyword
pytest TestingFiles/ -k "authentication"
pytest TestingFiles/ -k "login"
```

### Generate Reports

```bash
# Terminal coverage report
pytest TestingFiles/ --cov=. --cov-report=term-missing

# HTML coverage report
pytest TestingFiles/ --cov=. --cov-report=html
# Open htmlcov/index.html in browser

# JSON coverage report
pytest TestingFiles/ --cov=. --cov-report=json

# XML coverage report (for CI/CD)
pytest TestingFiles/ --cov=. --cov-report=xml
```

### Debugging

```bash
# Stop on first failure
pytest TestingFiles/ -x

# Drop into pdb debugger on failure
pytest TestingFiles/ --pdb

# Show print statements
pytest TestingFiles/ -s

# Show test durations
pytest TestingFiles/ --durations=10

# Run with more verbose output
pytest TestingFiles/ -vv
```

## Understanding Test Coverage

### Coverage Metrics

Coverage is measured as percentage of code lines executed during tests:

```
Coverage = (Lines executed / Total lines) × 100%
```

### Target Coverage by Module

| Module | Target | Current |
|--------|--------|---------|
| Authentication | 80% | TBD |
| Assessment | 75% | TBD |
| Audio Processing | 85% | TBD |
| Feedback | 80% | TBD |
| API Integration | 70% | TBD |
| **Overall** | **78%** | TBD |

### Interpreting Coverage Reports

```
module.py:45    missed  # Line 45 not covered by tests
module.py:50    covered # Line 50 covered by tests
module.py:51    excluded # Line 51 excluded from coverage
```

## Best Practices

### Writing Tests

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.unit
class TestUserAuthentication:
    """Group related tests in classes."""
    
    def test_login_success(self, sample_user, mock_auth_service):
        """
        Test should have:
        - Descriptive name starting with test_
        - Clear docstring
        - Arrange-Act-Assert pattern
        - Use fixtures for common data
        """
        # Arrange
        credentials = {"email": "user@example.com", "password": "pass"}
        
        # Act
        result = authenticate(credentials)
        
        # Assert
        assert result["success"] is True
        assert "token" in result

    @pytest.mark.slow
    def test_large_dataset_processing(self):
        """Mark slow tests with @pytest.mark.slow"""
        pass

    def test_error_handling(self):
        """Test error scenarios too."""
        with pytest.raises(ValueError):
            invalid_operation()
```

### Using Fixtures

```python
@pytest.fixture
def authenticated_user(sample_user, mock_auth_service):
    """Create fixture for reusable setup."""
    mock_auth_service.authenticate.return_value = sample_user
    return sample_user

def test_with_fixture(authenticated_user):
    """Use fixture as parameter."""
    assert authenticated_user["username"] == "testuser"
```

### Mocking External Services

```python
from unittest.mock import patch, MagicMock

def test_with_mock():
    """Mock external API calls."""
    with patch('audioProcessor.client') as mock_groq:
        mock_groq.transcribe.return_value = "Transcribed text"
        result = transcribe_audio("audio.wav")
        assert result == "Transcribed text"
```

## Test Execution Workflow

### Daily Development

```bash
# 1. Run unit tests (fast feedback)
pytest TestingFiles/ -m unit

# 2. Run relevant tests for your changes
pytest TestingFiles/ -k "auth"

# 3. Before committing, run all tests
pytest TestingFiles/

# 4. Check coverage
pytest TestingFiles/ --cov=.
```

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

pytest TestingFiles/ -m "not slow" || exit 1
```

### Continuous Integration

```bash
# Run in CI/CD pipeline
pytest TestingFiles/ \
    --cov=. \
    --cov-report=xml \
    --junitxml=report.xml \
    -v
```

## Troubleshooting

### Common Issues

**Issue: "ModuleNotFoundError: No module named 'pytest'"**
```bash
# Solution: Install pytest
pip install pytest
```

**Issue: Tests not discovered**
```bash
# Solution: Check test file naming
# Files must be named test_*.py
# Methods must start with test_
# Classes must start with Test

pytest TestingFiles/ --collect-only  # See what's discovered
```

**Issue: Fixtures not found**
```bash
# Solution: Check conftest.py location
# conftest.py should be in TestingFiles/
ls TestingFiles/conftest.py

# Verify fixture name matches parameter
pytest TestingFiles/ -v  # See fixture names
```

**Issue: Tests timeout**
```bash
# Solution: Install pytest-timeout
pip install pytest-timeout

# Run with increased timeout
pytest TestingFiles/ --timeout=600
```

**Issue: Mock not working**
```python
# Common mistake: Wrong patch path
# WRONG: patch('module') 
# RIGHT: patch('package.module.ClassName.method')

# Find correct path:
import package.module
print(package.module.ClassName.method)  # Shows actual location
```

**Issue: Import errors**
```bash
# Solution: Set PYTHONPATH
# Windows
set PYTHONPATH=%PYTHONPATH%;%cd%

# macOS/Linux
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run tests
pytest TestingFiles/
```

## Performance Optimization

### Run Tests in Parallel

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run with parallel workers
pytest TestingFiles/ -n auto
```

### Run Only Fast Tests

```bash
# Skip slow tests
pytest TestingFiles/ -m "not slow"

# Run last failed tests first
pytest TestingFiles/ --ff

# Run last modified tests
pytest TestingFiles/ --lf
```

## Integration with Tools

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements-test.txt
      - run: pytest TestingFiles/ --cov --cov-report=xml
```

### Pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest TestingFiles/
        language: system
        pass_filenames: false
        stages: [commit]
```

## Additional Resources

### Documentation
- [Pytest Official Docs](https://docs.pytest.org/)
- [Python unittest](https://docs.python.org/3/library/unittest.html)
- [Mocking Guide](https://docs.python.org/3/library/unittest.mock.html)

### Helpful Plugins
- pytest-asyncio: Async test support
- pytest-cov: Coverage reporting
- pytest-mock: Better mocking
- pytest-xdist: Parallel execution
- pytest-timeout: Test timeouts

## Support & Feedback

For questions or issues with the test suite:
1. Check this documentation
2. Review test files for examples
3. Check conftest.py for available fixtures
4. Consult Pytest documentation

---

**Last Updated**: May 2024
**Version**: 1.0
**Status**: Production Ready
