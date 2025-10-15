# PortfolAI Testing Guide

This document explains how to run tests for the PortfolAI project.

## Prerequisites

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

Or install from pyproject.toml:

```bash
pip install -e ".[test]"
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest test_api.py

# Run specific test function
pytest test_api.py::test_stock_quote
```

### Advanced Test Options

```bash
# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term

# Run tests in parallel
pytest -n auto

# Run with HTML report
pytest --html=test_report.html --self-contained-html

# Run specific markers
pytest -m "api"
pytest -m "not slow"

# Run with custom output
pytest -v --tb=short --color=yes
```

### Using the Test Runner Script

```bash
# Basic run
python run_tests.py

# With coverage
python run_tests.py --coverage

# With HTML report
python run_tests.py --html --verbose

# Run specific file
python run_tests.py --file test_api.py --verbose
```

## Test Structure

### Test Files
- `test_api.py` - Main API tests
- `conftest.py` - Pytest configuration and fixtures

### Test Categories

#### Unit Tests
- Test individual functions
- Test data validation
- Test error handling

#### Integration Tests
- Test API endpoints
- Test database interactions
- Test external API calls

#### API Tests
- Test Django views
- Test URL routing
- Test response formats

## Test Markers

Use markers to categorize tests:

```python
@pytest.mark.slow
def test_heavy_computation():
    pass

@pytest.mark.integration
def test_api_integration():
    pass

@pytest.mark.api
def test_stock_quote():
    pass
```

Run specific markers:

```bash
pytest -m "api"           # Run only API tests
pytest -m "not slow"      # Skip slow tests
pytest -m "integration"   # Run only integration tests
```

## Fixtures

Available fixtures in `conftest.py`:

- `client` - Django test client
- `test_stocks` - List of test stock symbols
- `sample_quote_data` - Sample quote data
- `sample_profile_data` - Sample profile data
- `sample_search_data` - Sample search data
- `sample_candles_data` - Sample historical data
- `sample_market_status_data` - Sample market status

## Configuration

### pytest.ini
Basic pytest configuration with Django settings.

### pyproject.toml
Comprehensive project configuration including:
- Dependencies
- Test configuration
- Code quality tools (black, flake8, isort, mypy)
- Coverage settings

## Test Coverage

Generate coverage reports:

```bash
# Terminal coverage
pytest --cov=. --cov-report=term

# HTML coverage report
pytest --cov=. --cov-report=html
```

Coverage reports are generated in `htmlcov/` directory.

## Continuous Integration

For CI/CD pipelines:

```bash
# Run tests with coverage
pytest --cov=. --cov-report=xml --junitxml=test-results.xml

# Run with specific markers
pytest -m "not slow" --cov=.
```

## Troubleshooting

### Common Issues

1. **Django not configured**
   - Ensure `DJANGO_SETTINGS_MODULE` is set
   - Check `conftest.py` for Django setup

2. **Import errors**
   - Verify all dependencies are installed
   - Check Python path configuration

3. **Database issues**
   - Use `pytest.mark.django_db` for database tests
   - Ensure test database is properly configured

### Debug Mode

Run tests with debug output:

```bash
pytest -v -s --tb=long
```

## Best Practices

1. **Test Naming**
   - Use descriptive test names
   - Follow `test_` prefix convention

2. **Test Organization**
   - Group related tests in classes
   - Use fixtures for common setup

3. **Assertions**
   - Use specific assertions
   - Include helpful error messages

4. **Test Data**
   - Use fixtures for test data
   - Keep tests independent

5. **Performance**
   - Mark slow tests with `@pytest.mark.slow`
   - Use parallel execution for large test suites
