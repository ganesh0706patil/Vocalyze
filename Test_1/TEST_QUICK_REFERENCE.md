# Vocalyze Testing Quick Reference Guide

Quick reference for running and understanding the Vocalyze test suite.

## File Structure

```
TestingFiles/
├── test_authentication.py      # User auth, login, password validation
├── test_assessment.py          # Assessment creation, scoring, feedback
├── test_audio_processing.py    # Audio transcription, fluency, pronunciation
├── test_feedback.py            # Feedback generation and delivery
├── test_api_integration.py     # API endpoints, system integration
├── conftest.py                 # Shared fixtures and configuration
├── README_TESTING.md           # Detailed documentation
└── TEST_QUICK_REFERENCE.md     # This file
```

## Test Summary

| Test File | Focus Area | Test Count | Key Features |
|-----------|-----------|-----------|--------------|
| test_authentication.py | User Management | 60+ | Registration, login, tokens, password validation |
| test_assessment.py | Assessments | 50+ | Question generation, scoring, answer evaluation |
| test_audio_processing.py | Audio Processing | 60+ | Transcription, fluency, pronunciation analysis |
| test_feedback.py | Feedback System | 70+ | Feedback generation, delivery, formatting |
| test_api_integration.py | System Integration | 80+ | API endpoints, data flow, performance |

## Quick Commands

### Installation
```bash
# Install testing dependencies
pip install pytest pytest-asyncio pytest-cov pytest-mock

# Or from requirements file (if exists)
pip install -r requirements-test.txt
```

### Run All Tests
```bash
pytest TestingFiles/
```

### Run Specific Test File
```bash
pytest TestingFiles/test_authentication.py
pytest TestingFiles/test_assessment.py
pytest TestingFiles/test_audio_processing.py
pytest TestingFiles/test_feedback.py
pytest TestingFiles/test_api_integration.py
```

### Run by Test Type
```bash
# Unit tests only
pytest TestingFiles/ -m unit

# Integration tests only
pytest TestingFiles/ -m integration

# API tests only
pytest TestingFiles/ -m api

# Audio processing tests only
pytest TestingFiles/ -m audio
```

### Run Specific Test Class
```bash
# Run all login tests
pytest TestingFiles/test_authentication.py::TestUserLogin

# Run assessment creation tests
pytest TestingFiles/test_assessment.py::TestAssessmentCreation
```

### Run Specific Test Case
```bash
# Run single test
pytest TestingFiles/test_authentication.py::TestUserLogin::test_login_success

# Run test matching pattern
pytest TestingFiles/ -k "login"
```

### Generate Coverage Report
```bash
# Terminal report
pytest TestingFiles/ --cov=. --cov-report=term-missing

# HTML report
pytest TestingFiles/ --cov=. --cov-report=html
# Open htmlcov/index.html

# JSON report
pytest TestingFiles/ --cov=. --cov-report=json
```

### Verbose Output
```bash
# Verbose mode
pytest TestingFiles/ -v

# Very verbose (show print statements)
pytest TestingFiles/ -vv

# Show local variables in errors
pytest TestingFiles/ -l
```

### Debugging
```bash
# Stop on first failure
pytest TestingFiles/ -x

# Drop into debugger on failure
pytest TestingFiles/ --pdb

# Show print statements
pytest TestingFiles/ -s

# Slow tests first
pytest TestingFiles/ --durations=10
```

## Test Organization by Feature

### Authentication Tests
```bash
pytest TestingFiles/test_authentication.py -v
```
Tests: Registration, login, password validation, email validation, sessions, tokens, profiles

### Assessment Tests
```bash
pytest TestingFiles/test_assessment.py -v
```
Tests: Creation, questions, scoring, answer evaluation, feedback, history, analytics

### Audio Tests
```bash
pytest TestingFiles/test_audio_processing.py -v
pytest TestingFiles/test_feedback.py::TestFluencyFeedback -v
pytest TestingFiles/test_feedback.py::TestPronunciationFeedback -v
```
Tests: Transcription, fluency, pronunciation, audio quality, format conversion

### Feedback Tests
```bash
pytest TestingFiles/test_feedback.py -v
```
Tests: Feedback generation, delivery, formatting, personalization, follow-up

### Integration Tests
```bash
pytest TestingFiles/test_api_integration.py -v
```
Tests: API endpoints, data flows, error handling, concurrency, performance

## Common Test Patterns

### Testing a Feature
```bash
# Example: Test user authentication
pytest TestingFiles/test_authentication.py::TestUserLogin -v
pytest TestingFiles/test_authentication.py::TestPasswordValidation -v
```

### Testing Error Scenarios
```bash
# Tests include error handling for:
# - Invalid credentials
# - Missing data
# - Network errors
# - Timeout scenarios
# - Concurrent operations

pytest TestingFiles/ -k "error" -v
pytest TestingFiles/ -k "exception" -v
```

### Testing API Endpoints
```bash
pytest TestingFiles/test_api_integration.py::TestAPIEndpoints -v
```

### Testing Performance
```bash
pytest TestingFiles/test_api_integration.py::TestPerformance -v
```

## Test Markers

### Available Markers
```python
@pytest.mark.unit           # Unit tests (fast, isolated)
@pytest.mark.integration    # Integration tests (test interactions)
@pytest.mark.api            # API endpoint tests
@pytest.mark.slow           # Long-running tests
@pytest.mark.audio          # Audio processing tests
@pytest.mark.db             # Database tests
```

### Running by Marker
```bash
# Run only fast unit tests
pytest TestingFiles/ -m unit

# Skip slow tests
pytest TestingFiles/ -m "not slow"

# Run multiple markers (OR logic)
pytest TestingFiles/ -m "unit or audio"

# Run specific markers (AND logic)
pytest TestingFiles/ -m "integration and api"
```

## Test Fixtures Used

### Common Fixtures
```python
sample_user              # User data
sample_assessment        # Assessment data
sample_question          # Question data
sample_feedback          # Feedback data
mock_database            # Database mock
mock_auth_service        # Auth service mock
assert_helpers           # Custom assertions
```

### Using Fixtures in Tests
```python
def test_user_login(sample_user, mock_auth_service):
    """Test uses fixtures automatically"""
    pass
```

## Expected Test Results

### Passing Tests
```
========== 320+ passed in 45.23s ==========
```

### Coverage Goals
- Authentication: 80%+
- Assessment: 75%+
- Audio: 85%+
- Feedback: 80%+
- API: 70%+
- Overall: 78%+

## Troubleshooting Quick Fixes

### Tests Not Found
```bash
# Make sure conftest.py is in TestingFiles/
# Run from project root
pytest TestingFiles/
```

### Import Errors
```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest TestingFiles/
```

### Mock Not Working
```bash
# Check patch path is correct
# Example: @patch('module.ClassName.method')
pytest TestingFiles/ -vv  # Show more details
```

### Tests Timeout
```bash
# Increase timeout
pytest TestingFiles/ --timeout=300  # 5 minutes
```

## Sample Test Run Scenarios

### Scenario 1: Test User Registration Flow
```bash
pytest TestingFiles/test_authentication.py::TestUserRegistration -v
```

### Scenario 2: Test Complete Assessment
```bash
pytest TestingFiles/test_assessment.py::TestAssessmentCreation -v
pytest TestingFiles/test_assessment.py::TestAssessmentScoring -v
pytest TestingFiles/test_assessment.py::TestAssessmentFeedback -v
```

### Scenario 3: Test Audio Processing Pipeline
```bash
pytest TestingFiles/test_audio_processing.py::TestAudioTranscription -v
pytest TestingFiles/test_audio_processing.py::TestFluencyAnalysis -v
pytest TestingFiles/test_audio_processing.py::TestPronunciationAnalysis -v
```

### Scenario 4: Test Full Integration
```bash
pytest TestingFiles/test_api_integration.py::TestEndToEndUserJourney -v
pytest TestingFiles/test_api_integration.py::TestEndToEndAssessmentWorkflow -v
pytest TestingFiles/test_api_integration.py::TestEndToEndAudioProcessing -v
```

### Scenario 5: Check Overall Coverage
```bash
pytest TestingFiles/ --cov=. --cov-report=term-missing
```

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Tests
  run: pytest TestingFiles/ --cov=. --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

### Jenkins Example
```groovy
stage('Test') {
    steps {
        sh 'pytest TestingFiles/ --junitxml=results.xml'
    }
}
```

## Performance Benchmarks

### Expected Execution Times
- Unit Tests: ~2-5 seconds
- Integration Tests: ~10-15 seconds
- API Tests: ~8-12 seconds
- Audio Tests: ~15-20 seconds (includes slow tests)
- Total: ~45-60 seconds

### Optimizing Test Speed
```bash
# Run in parallel (requires pytest-xdist)
pytest TestingFiles/ -n auto

# Run only changed tests
pytest TestingFiles/ --lf  # Last failed
pytest TestingFiles/ --ff  # Failed first
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)

## Next Steps

1. ✅ Install testing dependencies
2. ✅ Run all tests to verify setup
3. ✅ Check coverage report
4. ✅ Add new tests as features are added
5. ✅ Integrate with CI/CD pipeline

---

**Last Updated**: May 2024
**Test Suite Version**: 1.0
**Total Test Cases**: 320+
**Coverage Target**: 78%
