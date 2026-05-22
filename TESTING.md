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
bandit -r core -c bandit.yaml
# CI fails only on HIGH severity — check bandit.json summary locally if needed
```

## Run Pylint (Code Quality Check)
```bash
cd portfolai
python -m pylint core --fail-on=E,F
```

## Run Flake8 (Style Check)
```bash
cd portfolai
flake8 core
# Deploy CI reports style issues but does not fail on them
```

## Run Safety (Dependency Vulnerability Check)

Install dev dependencies first (`pip install -r requirements-dev.txt`).

```bash
cd portfolai
safety check -r requirements.txt
# Safety 3.x (requirements-dev.txt); scans production deps; CI reports advisories but does not fail on them
```