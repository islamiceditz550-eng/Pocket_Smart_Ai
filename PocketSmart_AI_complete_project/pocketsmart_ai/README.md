# PocketSmart AI

PocketSmart AI is a FastAPI + Jinja2 web application that turns a user's budget and preferences into structured recommendations for:

- Home interior planning
- Party/event planning
- Jewelry planning with optional outfit-image analysis
- Recommendation history
- Registration/login with JWT authentication

The original project document describes both Flask and FastAPI. This implementation standardizes the backend on **FastAPI**, because the later milestones explicitly define FastAPI routes, Pydantic models, Jinja2 templates, authentication, and Uvicorn startup.

## AI integration

The document names Gemini 1.5 Flash Pro. That model reference is historical. This implementation uses Google's current `google-genai` SDK and reads the model from `GEMINI_MODEL`, so you can change it without editing application code. The default is `gemini-3.8-flash`; use a currently available model in your Google AI account if that name is not enabled for your key.

The application also has a deterministic fallback recommendation engine. Therefore the full UI, authentication, database, history, validation, and planner flows work without a Gemini API key. Set `USE_GEMINI=false` for an offline demo.

## Important limitation about shopping/service platforms

The project document mentions Amazon, Flipkart, IKEA, Swiggy, Zomato, and OYO. This repository does not scrape those sites or pretend to have live inventory/pricing. It generates platform search links and clearly labels recommendations as planning/search suggestions. Real product feeds can later be connected through official APIs/affiliate APIs in `app/services/platforms.py`.

## Project structure

```text
pocketsmart_ai/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── pages.py
│   │   └── planners.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── fallback.py
│   │   ├── gemini.py
│   │   ├── planner.py
│   │   └── platforms.py
│   ├── static/
│   │   ├── css/styles.css
│   │   └── js/app.js
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── history.html
│       ├── planner.html
│       └── results.html
├── tests/
│   └── test_app.py
├── uploads/.gitkeep
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## VS Code setup — Windows

1. Install Python 3.11+.
2. Open this folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

5. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

6. Create your environment file:

```powershell
Copy-Item .env.example .env
```

7. For an AI-powered run, put your Gemini API key in `.env`:

```text
GEMINI_API_KEY=your_key_here
USE_GEMINI=true
```

For a no-key local demo:

```text
USE_GEMINI=false
```

8. Start the server:

```powershell
python -m uvicorn app.main:app --reload
```

9. Open:

- App: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## First test

Register an account, log in, open one of the planners, enter a budget, and submit it. The result is saved in SQLite history.

For Jewelry Planner, upload a JPG/PNG/WebP outfit image. The server validates the file size/type and sends the image to Gemini only when Gemini mode is enabled.

## Automated tests

```powershell
pytest -q
```

## API endpoints

### Public

- `GET /health`
- `POST /api/auth/register`
- `POST /api/auth/login`

### Authenticated

- `POST /api/auth/logout`
- `GET /api/session-info`
- `GET /api/session-data`
- `GET /api/history`
- `GET /api/recommendations-details/{recommendation_id}`
- `POST /api/generate-home`
- `POST /api/generate-party`
- `POST /api/generate-jewelry`

The browser UI uses the same backend.
