# PortfolAI - Stock Analysis Demo Platform

Django-based demo web application for stock analysis with live market data.

[![CI Pipeline](https://github.com/skalyan04/PortfolAI-CS4300-Fall-2024-Group-4/actions/workflows/code-coverage.yml/badge.svg)](https://github.com/skalyan04/PortfolAI-CS4300-Fall-2024-Group-4/actions/workflows/code-coverage.yml)
[![Deployed on Render (Custom Domain)](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?logo=render)](https://www.portfolai.org/)

**Repository:** https://github.com/skalyan04/PortfolAI-CS4300-Fall-2024-Group-4  
**Live Demo:** https://www.portfolai.org/

## Key Features
- **Demo login:** shared demo account — no public registration
- **Live market data:** quotes, market movers, and news via Finnhub, Alpha Vantage, and NewsAPI
- **Browser watchlist:** add/remove tickers stored in localStorage
- **Demo insights:** template stock analysis enriched with live quote data
- **Guided learning:** curated investing fundamentals with mock explanations
- **Demo help chat:** navigation and feature guidance (no AI)

## Demo Mode

This project runs as a **demo-only** deployment:

| Included | Removed |
|----------|---------|
| Shared demo login (`DEMO_USERNAME` / `DEMO_PASSWORD`) | OpenAI / AI chat & analysis |
| Live market APIs (Finnhub, Alpha Vantage, NewsAPI) | Supabase / Postgres |
| SQLite (demo user + sessions only) | Watchlist database persistence |
| Browser localStorage watchlist | Public signup |

### Required environment variables

```
SECRET_KEY=
FINNHUB_API_KEY=
ALPHA_VANTAGE_API_KEY=
NEWS_API_KEY=
DEMO_PASSWORD=
DEMO_USERNAME=demo          # optional, defaults to "demo"
ALLOWED_HOSTS=localhost,127.0.0.1
```

### First-time setup

```bash
cd portfolai
pip install -r requirements.txt
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py ensure_demo_user
python manage.py runserver 0.0.0.0:3000
```

See [SETUP.md](SETUP.md) for full instructions.

## Technologies
- Backend: Django, Django REST Framework, Python
- Database: SQLite (demo user and sessions only)
- Frontend: JavaScript, HTML, CSS (Django templates/static assets)
- Deployment: Render, Cloudflare
- APIs: Finnhub, Alpha Vantage, NewsAPI
- Tooling: pytest/coverage, Bandit, Flake8, Pylint, Gunicorn, Whitenoise

## Project Structure

```
PortfolAI-CS4300-Fall-2024-Group-4/
├── .github/                                # GitHub configuration
│   ├── dependabot.yml                      # Dependabot configuration
│   └── workflows/                          # GitHub Actions workflows
│       ├── ai-code-review.yml              # AI code review workflow
│       ├── code-coverage.yml               # CI pipeline with code coverage workflow
│       ├── dependency-review.yml           # Dependency review workflow
│       ├── deploy.yml                      # Deployment workflow
│       └── security-check.yml              # Security scanning workflow
├── portfolai/                              # Main Django project directory
│   ├── core/                               # Django app for core functionality
│   │   ├── __init__.py
│   │   ├── admin.py                        # Django admin configuration
│   │   ├── api_helpers.py                  # API helper functions
│   │   ├── apps.py                         # App configuration
│   │   ├── forms.py                        # Django forms
│   │   ├── models.py                       # Database models
│   │   ├── serializers.py                  # API serializers
│   │   ├── services.py                     # Business logic and services
│   │   ├── urls.py                         # URL routing
│   │   ├── views/                          # View functions organized by feature
│   │   │   ├── __init__.py                 # Exports all views
│   │   │   ├── _clients.py                 # Shared API client initialization
│   │   │   ├── analysis.py                 # portfolai_analysis
│   │   │   ├── auth.py                     # SignUpView
│   │   │   ├── basic.py                    # Landing, dashboard, hello_api
│   │   │   ├── chat.py                     # chat_api
│   │   │   ├── learn.py                    # Learn endpoints
│   │   │   ├── market_movers.py            # get_market_movers
│   │   │   ├── news.py                     # get_news
│   │   │   ├── stock_data.py               # get_stock_data, stock_summary
│   │   │   └── watchlist.py                # Watchlist endpoints
│   │   ├── tests/                          # Test directory
│   │   │   ├── __init__.py
│   │   │   ├── analysis_test.py            # AI analysis tests
│   │   │   ├── auth_test.py                # Authentication tests
│   │   │   ├── chat_test.py                # Chatbot tests
│   │   │   ├── learn_test.py               # Learn tests
│   │   │   ├── market_movers_test.py       # Market movers tests
│   │   │   ├── news_test.py                # News feed tests
│   │   │   ├── stock_data_test.py          # Stock data tests
│   │   │   ├── summary_test.py             # Stock summary tests
│   │   │   ├── test_helpers.py             # Test helper utilities
│   │   │   ├── view_test.py                # Basic views tests
│   │   │   └── watchlist_test.py           # Watchlist tests
│   │   ├── migrations/                     # Database migration files
│   │   │   ├── __init__.py
│   │   │   └── 0001_initial.py             # Initial migration
│   │   ├── static/                         # Static files (CSS, JS, images)
│   │   │   ├── chat/                       # Chat widget assets (CSS, JS, images)
│   │   │   ├── home/                       # Dashboard assets (CSS, JS)
│   │   │   └── landing/                    # Landing page assets (CSS, JS, images)
│   │   └── templates/                      # HTML templates
│   │       ├── base.html
│   │       ├── chat_widget.html
│   │       ├── home.html
│   │       ├── landing.html
│   │       ├── learn.html
│   │       └── registration/
│   │           ├── login.html
│   │           └── signup.html
│   ├── mysite/                             # Django project settings
│   │   ├── __init__.py
│   │   ├── asgi.py                         # ASGI configuration
│   │   ├── settings.py                     # Django settings
│   │   ├── urls.py                         # Main URL configuration
│   │   └── wsgi.py                         # WSGI configuration
│   ├── staticfiles/                        # Django static files collection (generated)
│   ├── bandit.yaml                         # Bandit security scanner config
│   ├── build.sh                            # Build script
│   ├── manage.py                           # Django management script
│   ├── db.sqlite3                          # SQLite database file
│   ├── pyproject.toml                      # Python project configuration
│   ├── pytest.ini                          # Pytest configuration
│   ├── requirements.txt                    # Production Python dependencies
│   ├── requirements-dev.txt                # Dev/CI: pytest, linters, Safety
│   └── htmlcov/                            # Coverage HTML reports (generated)
├── Pylint.txt                              # Pylint output
├── README.md                               # Project documentation
├── LICENSE                                 # Project license
├── Reflection1.txt                         # Team reflection document
├── TESTING.md                              # Testing documentation
├── WORKFLOW_GUIDE.md                       # CI/CD workflow documentation
├── review.py                               # Code review script
├── security_report.py                      # Security report script
└── render.yaml                             # Deployment configuration
```

## Team
- Alexis Liew
- Elizandro Duran
- Jessica Webb
- Sreya Kalyan

## AI Integration and Tools Used

This project leverages AI tools in the following ways:

### 1. Application-Level AI Features
- **OpenAI API Integration**:  
  Used within `/api/stock-summary/` and `/api/portfolai-analysis/` endpoints to generate AI-driven summaries and insights based on real-time stock data.  
  - Fallback mock responses are used during offline testing or when API limits are reached.  
  - AI summaries combine structured market data with sentiment and performance analysis.

### 2. Development Assistance
AI tools were responsibly used to improve productivity and creativity during development:
- **ChatGPT (OpenAI GPT-5)** and **Claude Sonnet 4.5** were used to assist in:
  - Writing and refining Django view logic and API exception handling.
  - Drafting and verifying unit tests and mock data generation.
  - Improving code readability and documentation.
- **Cursor IDE (AI Pair Programming)** assisted in integrating the landing page and dashboard templates with Django.
- All AI-generated or assisted code was **reviewed, debugged, and verified manually** by us [Group 4] before inclusion in the team repo.
