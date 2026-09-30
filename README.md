# PocketSmart AI

A complete FastAPI + Jinja2 + SQLite implementation based on the supplied PocketSmart AI project documentation.

## Included
- Home Interior Budget Planner
- Party Budget Planner
- Jewelry Budget Planner with optional outfit image
- Gemini REST API integration with configurable model
- Deterministic fallback/mock recommendations
- Registration, login, logout and JWT HTTP-only cookie sessions
- Recommendation history
- Responsive HTML/CSS/JS frontend
- API documentation at `/docs`
- Automated tests

## Source-document alignment
The supplied document describes FastAPI, Gemini multimodal processing, the `/generate-home`, `/generate-party`, and `/generate-jewelry` routes, authentication/session routes, recommendation history, Jinja2 pages, and fallback/mock data. This implementation provides those pieces in a runnable modular project.

The document names Gemini 1.5 Flash Pro. Because Gemini model availability changes, the actual model is configurable through `GEMINI_MODEL`; the default is `gemini-2.5-flash`. Set it to another model available to your Google account if required.

The document names Amazon, Flipkart, IKEA, Swiggy, Zomato and OYO. This starter does not scrape those sites or claim live inventory. It creates transparent search links and uses deterministic fallback data. Authorized partner APIs can be integrated later.

## VS Code setup

### Windows PowerShell
```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

For zero-key testing, set `USE_MOCK_AI=true` in `.env`.

For Gemini, set:
```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

## Run
```bash
python run.py
```
Open http://127.0.0.1:8000

API docs: http://127.0.0.1:8000/docs

## Test
```bash
pytest -q
```

## Main endpoints
- `GET /health`
- `POST /register`
- `POST /login`
- `POST /logout`
- `GET /session-info`
- `GET /session-data`
- `POST /generate-home`
- `POST /generate-party`
- `POST /generate-jewelry`
- `GET /history`
- `GET /recommendations-details/{recommendation_id}`

## Production hardening
Use HTTPS, a strong secret, PostgreSQL, rate limiting, CSRF protection where appropriate, managed secret storage, image scanning/storage, and authorized product/vendor APIs before public deployment.
