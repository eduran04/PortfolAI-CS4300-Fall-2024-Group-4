## Setup

Follow these steps to run PortfolAI locally.

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
```

4) Configure environment variables
Create `portfolai/.env` with the following keys:
```
# API KEYS
FINNHUB_API_KEY=
OPENAI_API_KEY=
NEWS_API_KEY=
ALPHA_VANTAGE_API_KEY=

# DJANGO KEYS
SECRET_KEY=
ALLOWED_HOSTS=

# DATABASE KEYS
SUPABASE_DB_URL=
SUPABASE_URL=
SUPABASE_KEY=
```
- `ALLOWED_HOSTS` should be a comma-separated list (e.g., `localhost,127.0.0.1`).
- If `SUPABASE_DB_URL` is set, the app will use that Postgres URL, otherwise it falls back to SQLite for local development. SUPABASE_DB_URL should be different for Production and Development environment.

5) Apply database migrations
```
python manage.py migrate
```

6) Collect Static Files
```
python manage.py collectstatic --noinput
```

7) Start the development server
```
python manage.py runserver 0.0.0.0:3000
```
Visit http://localhost:3000/

Testing instructions live in `TESTING.md`.

