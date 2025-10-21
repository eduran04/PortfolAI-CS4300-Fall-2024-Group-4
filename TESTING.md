# Testing Guide

## Quick Start

### Run Tests
```bash
cd portfolai
pytest -v
```

### Run Tests with Coverage
```bash
cd portfolai
pytest --cov=core --cov-report=term-missing
```

### Check Coverage Threshold
```bash
cd portfolai
coverage report --fail-under=80
```

## Test Coverage

- **Target**: 80%+ code coverage
- **Current**: Comprehensive test suite covering all API endpoints
- **Tools**: pytest, pytest-django, pytest-cov

## Test Categories

### API Endpoints
- Stock data retrieval
- Market movers
- News feed
- AI analysis
- Error handling
- Fallback scenarios

### Views
- Landing page
- Dashboard
- Template rendering

### Edge Cases
- Invalid symbols
- API failures
- Empty responses
- Missing API keys

## CI/CD Integration

Tests run automatically on:
- Every push to main/develop
- Every pull request
- Coverage reports generated
- 80% threshold enforced

## Local Development

1. Install dependencies: `pip install -r requirements.txt`
2. Run tests: `pytest -v`
3. Check coverage: `coverage report --fail-under=80`

## Test Files

- `portfolai/core/tests.py` - Main test suite
- `portfolai/pytest.ini` - pytest configuration
- `portfolai/pyproject.toml` - Coverage configuration
