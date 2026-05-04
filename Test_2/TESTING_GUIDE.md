# Vocalyze Testing Guide

This guide explains how to run and maintain the testing files for the Vocalyze project.

## Overview

The Vocalyze project includes comprehensive test suites covering:

1. **Audio Processing** - `test_audio_processor.py`
2. **Feedback System** - `test_feedback_processor.py`
3. **FastAPI Endpoints** - `test_fastapi_endpoints.py`
4. **Express.js Backend Routes** - `test_backend_routes.js`
5. **Groq LLM Integration** - `test_groq_integration.py`
6. **Database Models** - `test_database_models.py`
7. **Groq API Connection** - `test11.py` (existing test file)

## Installation

### Python Dependencies

```bash
pip install pytest pytest-asyncio
pip install pytest-cov  # For coverage reports
pip install pytest-mock  # For mocking utilities
```

### Node.js Dependencies

```bash
npm install supertest mocha --save-dev
npm install chai --save-dev  # For assertions
```

## Running Tests

### Python Tests

#### Run all Python tests:
```bash
pytest
```

#### Run specific test file:
```bash
pytest test_audio_processor.py
pytest test_feedback_processor.py
pytest test_fastapi_endpoints.py
```

#### Run with verbose output:
```bash
pytest -v
```

#### Run with coverage report:
```bash
pytest --cov=. --cov-report=html
```

#### Run specific test class:
```bash
pytest test_audio_processor.py::TestAudioProcessing
```

#### Run specific test function:
```bash
pytest test_audio_processor.py::TestAudioProcessing::test_process_valid_audio_file
```

#### Run with markers:
```bash
pytest -m "not slow"  # Skip slow tests
pytest -m "integration"  # Run only integration tests
```

### Node.js Tests

#### Run all tests:
```bash
mocha test_backend_routes.js
```

#### Run with specific reporter:
```bash
mocha test_backend_routes.js --reporter spec
mocha test_backend_routes.js --reporter json
```

## Test Structure

### Python Tests

Each Python test file follows this structure:

```python
import pytest
from unittest.mock import patch, MagicMock

class TestFeatureName:
    """Test cases for feature name"""
    
    @pytest.fixture
    def setup_fixture(self):
        """Setup test data"""
        return data
    
    def test_functionality(self, setup_fixture):
        """Test description"""
        assert condition
```

### Node.js Tests

Each Node.js test file uses Mocha and follows this structure:

```javascript
const request = require('supertest');
const assert = require('assert');

describe('Feature Name', () => {
    it('should do something', async () => {
        const response = await request(app)
            .get('/route')
            .expect(200);
        
        assert(response.body !== null);
    });
});
```

## Test Categories

### Unit Tests
- `test_audio_processor.py` - Individual audio processing functions
- `test_feedback_processor.py` - Feedback generation logic
- `test_groq_integration.py` - LLM API interactions
- `test_database_models.py` - Model validation

### Integration Tests
- `test_fastapi_endpoints.py` - API endpoint testing
- `test_backend_routes.js` - Express.js route testing
- `test_groq_integration.py` - Full LLM workflow

### End-to-End Tests
- Combination of multiple modules working together

## Mocking Strategy

### Python Mocking

For external dependencies like APIs:

```python
@patch('module.external_function')
def test_function(self, mock_external):
    mock_external.return_value = expected_value
    result = my_function()
    assert result == expected_value
```

### Node.js Mocking

For Express routes and middleware:

```javascript
describe('Route Test', () => {
    it('should work', async () => {
        const response = await request(app)
            .post('/route')
            .send(testData)
            .expect(200);
    });
});
```

## Environment Setup

### Create .env file for testing

```env
GROQ_API_KEY=your_test_key
MONGODB_URI=mongodb://localhost:27017/vocalyze_test
API_FRONTEND_URL=http://localhost:3000
PORT=8000
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r fastapi/requirements.txt
      - run: pytest
      - uses: actions/setup-node@v2
      - run: npm install
      - run: npm test
```

## Coverage Reports

### Generate coverage report:
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### View coverage by file:
```bash
pytest --cov=. --cov-report=term-missing
```

## Common Issues and Solutions

### Issue: ModuleNotFoundError
**Solution:** Ensure all dependencies are installed and PYTHONPATH is set correctly

### Issue: Tests timeout
**Solution:** Increase timeout in pytest.ini or use `@pytest.mark.timeout(30)`

### Issue: Database connection errors
**Solution:** Ensure MongoDB is running and connection string is correct

### Issue: API rate limits in Groq tests
**Solution:** Use mocking for Groq API tests to avoid hitting rate limits

## Best Practices

1. **Use Fixtures**: Reuse test data setup with pytest fixtures
2. **Mock External Services**: Always mock API calls and database operations
3. **Test Edge Cases**: Include tests for invalid inputs and error conditions
4. **Clear Test Names**: Use descriptive names that explain what is being tested
5. **Keep Tests Independent**: Each test should be runnable independently
6. **Update Tests**: When modifying features, update corresponding tests
7. **Documentation**: Add docstrings explaining complex test logic

## Adding New Tests

When adding new features:

1. Create test file following naming convention: `test_feature_name.py`
2. Use existing test structures as template
3. Mock external dependencies
4. Add docstrings to test classes and methods
5. Run tests to ensure they pass
6. Update this guide if needed

## Test Execution Checklist

- [ ] All dependencies installed
- [ ] Environment variables set
- [ ] Run `pytest` for Python tests
- [ ] Run `mocha` for Node.js tests
- [ ] Check coverage report
- [ ] Verify no skipped tests
- [ ] Confirm all assertions pass

## Debugging Tests

### Print debugging information:
```python
def test_function():
    result = my_function()
    print(result)  # Will show in pytest output with -s flag
    assert result == expected
```

Run with output:
```bash
pytest -s
```

### Use pdb for debugging:
```python
import pdb; pdb.set_trace()
```

### Step through code:
```bash
pytest --pdb
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Mocha Documentation](https://mochajs.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-databases/)
- [Jest for Node.js](https://jestjs.io/) (Alternative to Mocha)

## Contact & Support

For questions about testing or to report issues, please check the project documentation or create an issue in the repository.

---

Last Updated: 2026-05-05
