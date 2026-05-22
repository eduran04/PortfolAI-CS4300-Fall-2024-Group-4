## Setup

Follow these steps to run PortfolAI locally in **demo mode**.

1) Clone and enter the repo
```
git clone https://github.com/skalyan04/PortfolAI-CS4300-Fall-2024-Group-4.git
cd PortfolAI-CS4300-Fall-2024-Group-4/portfolai
```

2) Create and activate a virtual environment
```
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

3) Install dependencies
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

`requirements.txt` is production-only (Render uses this alone). `requirements-dev.txt` adds pytest, linters, and Safety for local testing and CI.

4) Configure environment variables

Create `portfolai/.env` with the following keys:
```
# Market data API keys (required for live demo data)
FINNHUB_API_KEY=
ALPHA_VANTAGE_API_KEY=
NEWS_API_KEY=

# Django
SECRET_KEY=
ALLOWED_HOSTS=localhost,127.0.0.1

# Demo login (shared account)
DEMO_USERNAME=demo
DEMO_PASSWORD=demo123
```

- `ALLOWED_HOSTS` should be a comma-separated list (e.g., `localhost,127.0.0.1`).
- The app uses **SQLite** for the demo user and sessions only — no Supabase or Postgres required.
- OpenAI is not used in demo mode.

5) Apply database migrations and create the demo user
```
python manage.py migrate
python manage.py ensure_demo_user
```

6) Collect static files
```
python manage.py collectstatic --noinput
```

7) Start the development server
```
python manage.py runserver 0.0.0.0:3000
```

Visit http://localhost:3000/ and log in with your `DEMO_USERNAME` / `DEMO_PASSWORD`.

Testing instructions live in `TESTING.md`.
