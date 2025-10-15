# PortfolAI - AI-Powered Stock Analysis Platform

Django-based web application for stock analysis and portfolio management with real-time market data.

**Repository:** https://github.com/skalyan04/PortfolAI-CS4300-Fall-2024-Group-4

## Setup Guide

1. Clone the repository: `git clone https://github.com/skalyan04/PortfolAI-CS4300-Fall-2024-Group-4.git`
2. Navigate to project directory: `cd PortfolAI-CS4300-Fall-2024-Group-4/portfolai`
3. Create virtual environment: `python -m venv myenv`
4. Activate virtual environment: `source myenv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Create `.env` file with your Finnhub API key:
   ```
   FINNHUB_API_KEY=your_finnhub_api_key_here
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```
7. Run migrations: `python manage.py migrate`
8. Start server: `python manage.py runserver 0.0.0.0:8000`
9. Access application at http://localhost:8000/

## Testing

Run tests: `pytest -v`

## Project Structure

```
PortfolAI-CS4300-Fall-2024-Group-4/
├── portfolai/                              # Main Django project directory
│   ├── home/                               # Django app for homepage and dashboard
│   │   ├── __init__.py
│   │   ├── admin.py                        # Django admin configuration
│   │   ├── apps.py                         # App configuration
│   │   ├── models.py                       # Database models
│   │   ├── tests.py                        # Unit tests
│   │   ├── urls.py                         # URL routing for home app
│   │   ├── views.py                        # View functions and API endpoints
│   │   ├── utils.py                        # Finnhub API utility functions
│   │   ├── migrations/                     # Database migration files
│   │   │   └── __init__.py
│   │   ├── static/home/                    # Static files for home app
│   │   │   ├── dashboard/                  # Dashboard-specific assets
│   │   │   │   ├── dashboard.css          # Dashboard styles
│   │   │   │   ├── dashboard.js           # Dashboard JavaScript
│   │   │   │   └── sidebar.js             # Sidebar functionality
│   │   │   ├── tailwind-build.css         # Compiled Tailwind CSS
│   │   │   ├── saasy-custom.css           # Custom CSS styles
│   │   │   ├── saasy.js                   # JavaScript functionality
│   │   │   └── assets/                    # Image and media assets (logo.png, images/, etc.)
│   │   └── templates/home/                 # HTML templates
│   │       ├── base.html                   # Base template
│   │       ├── index.html                  # Landing page template
│   │       ├── dashboard.html              # Dashboard template
│   │       └── landing_base.html           # Landing page base template
│   ├── portfolai/                          # Django project settings
│   │   ├── __init__.py
│   │   ├── asgi.py                         # ASGI configuration
│   │   ├── settings.py                     # Django settings
│   │   ├── urls.py                         # Main URL configuration
│   │   └── wsgi.py                         # WSGI configuration
│   ├── manage.py                           # Django management script
│   ├── db.sqlite3                          # SQLite database file
│   ├── requirements.txt                    # Python dependencies
│   ├── requirements-test.txt               # Test dependencies
│   ├── test_api.py                         # Comprehensive test suite
│   ├── run_tests.py                        # Test runner script
│   ├── conftest.py                         # Pytest configuration
│   ├── pytest.ini                          # Pytest settings
│   ├── pyproject.toml                    # Modern Python project configuration
│   ├── TESTING.md                          # Testing documentation
│   └── .gitignore                          # Git ignore rules
├── .gitignore                              # Root git ignore rules
├── README.md                               # Project documentation
└── LICENSE                                 # Project license
```

