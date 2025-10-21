# PortfolAI - AI-Powered Stock Analysis Platform

Django-based web application for stock analysis and portfolio management with real-time market data.

[![CI Pipeline](https://github.com/skalyan04/PortfolAI-CS4300-Fall-2024-Group-4/actions/workflows/ci.yml/badge.svg)](https://github.com/skalyan04/PortfolAI-CS4300-Fall-2024-Group-4/actions/workflows/ci.yml)
[![AI Code Review](https://github.com/skalyan04/PortfolAI-CS4300-Fall-2024-Group-4/actions/workflows/ai-code-review.yml/badge.svg)](https://github.com/skalyan04/PortfolAI-CS4300-Fall-2024-Group-4/actions/workflows/ai-code-review.yml)
[![Deployed on Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?logo=render)](https://portfolai.onrender.com)

**Repository:** https://github.com/skalyan04/PortfolAI-CS4300-Fall-2024-Group-4  
**Live Demo:** https://portfolai.onrender.com

## Setup Guide

1. Clone and enter the Repository

```
git clone https://github.com/skalyan04/PortfolAI-CS4300-Fall-2024-Group-4.git
cd PortfolAI-CS4300-Fall-2024-Group-4/portfolai
```

2. Create and Activate a Virtual Environment

```
python -m venv venv
source venv/bin/activate  # macOS/Linux
```

3. Install Dependencies

```
pip install -r requirements.txt
```

4. Configure Environment Variables

Create a .env file in the project root:

```
touch .env
```

Add Key to .env file:
```
FINNHUB_API_KEY=your_finnhub_api_key_here
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. Run Migrations

```
python manage.py migrate
```

7. Start the Development Server

```
python manage.py runserver 0.0.0.0:3000
```

Visit ➜ http://localhost:3000/

8. Running Tests

To run all tests with coverage:

```bash
cd portfolai
pytest -v --cov=core --cov-report=term-missing
```

To run tests with HTML coverage report:

```bash
cd portfolai
pytest --cov=core --cov-report=html
open htmlcov/index.html
```

To check coverage threshold (must be 80%+):

```bash
cd portfolai
coverage report --fail-under=80
```

## Project Structure

```
PortfolAI-CS4300-Fall-2024-Group-4/
├── portfolai/                              # Main Django project directory
│   ├── core/                               # Django app for core functionality
│   │   ├── __init__.py
│   │   ├── admin.py                        # Django admin configuration
│   │   ├── apps.py                         # App configuration
│   │   ├── models.py                       # Database models
│   │   ├── tests.py                        # Unit tests
│   │   ├── views.py                        # View functions and API endpoints
│   │   └── migrations/                     # Database migration files
│   │       └── __init__.py
│   ├── mysite/                             # Django project settings
│   │   ├── __init__.py
│   │   ├── asgi.py                         # ASGI configuration
│   │   ├── settings.py                     # Django settings
│   │   ├── urls.py                         # Main URL configuration
│   │   └── wsgi.py                         # WSGI configuration
│   ├── templates/                          # HTML templates
│   │   ├── base.html                       # Base template
│   │   ├── landing.html                    # Landing page template
│   │   └── home.html                       # Dashboard template
│   ├── static/                             # Static files
│   │   ├── landing/                        # Landing page assets
│   │   ├── script.js                       # Main JavaScript file
│   │   └── style.css                       # Custom CSS styles
│   ├── manage.py                           # Django management script
│   ├── db.sqlite3                          # SQLite database file
│   └── requirements.txt                    # Python dependencies
├── .gitignore                              # Root git ignore rules
├── README.md                               # Project documentation
├── LICENSE                                 # Project license
├── Reflection1.txt                         # Team reflection document
└── render.yaml                             # Deployment configuration
```

