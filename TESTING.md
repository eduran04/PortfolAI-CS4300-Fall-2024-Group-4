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

## Run Bandit (Security Scan)
```bash
cd portfolai
bandit -r core -c bandit.yaml -s MEDIUM # Requires Python 3.12.3
```

## Run Pylint (Code Quality Check)
```bash
cd portfolai
python -m pylint core
```

## Run Flake8 (Style Check)
```bash
cd portfolai
flake8 core
```

## Run Safety (Dependency Vulnerability Check)
```bash
cd portfolai
safety scan # Required me to make an account
```