# Testing Guide

## Run Tests
```bash
cd portfolai
pytest -v
```

## Run Tests with Coverage
```bash
cd portfolai
pytest --cov=core --cov-report=term-missing
```

## Check Coverage
```bash
cd portfolai
coverage report --fail-under=80
```