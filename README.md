# TalentLens — See Talent Beyond the Resume

A Python-first talent discovery platform with a premium Streamlit experience, FastAPI services, SQLAlchemy persistence, explainable profile-to-role matching, resume skill extraction and public GitHub profile sync.

## Stack

- Python 3.11+
- Streamlit (web UI)
- FastAPI + Uvicorn (API)
- SQLAlchemy 2 (SQLite locally; PostgreSQL/Supabase PostgreSQL via `DATABASE_URL`)
- Pandas + Plotly (data display and visual analytics)
- pypdf (selectable-text PDF parsing)
- GitHub REST API (public profile/repository metadata)
- Optional OpenAI API (career narrative; requires your own key)

## Architecture

```text
TalentLens_Final/
├── backend/
│   └── app/
│       ├── main.py             # FastAPI routes and validation
│       ├── models.py           # SQLAlchemy models
│       ├── schemas.py          # Pydantic request schemas
│       ├── database.py         # SQLite/PostgreSQL connection
│       ├── security.py         # Password hashing + JWT
│       ├── matching.py         # Explainable weighted matching
│       └── integrations.py     # GitHub + optional OpenAI
├── streamlit_app/
│   ├── app.py                  # Landing page and portals
│   └── api_client.py            # Authenticated API client
├── assets/
│   ├── talentlens-logo.svg
│   └── favicon.svg
├── tests/
│   └── test_matching.py
├── .env.example
└── requirements.txt
```

## Windows / VS Code setup

Open the extracted `TalentLens_Final` folder in VS Code.

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once in the same terminal and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

Run from the project root:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure environment

```powershell
Copy-Item .env.example .env
```

For local demo, the default SQLite database works. Before deployment, replace `JWT_SECRET` with a long random secret. Optional integrations:
- `GITHUB_TOKEN`: optional personal access token to improve GitHub API rate limits. Public unauthenticated API may work without it.
- `OPENAI_API_KEY`: optional key for generated profile feedback. The feature returns a clear configuration message if no key is set.
- `DATABASE_URL`: optional PostgreSQL connection string. Use a managed PostgreSQL/Supabase URL with the `postgresql+psycopg://` SQLAlchemy prefix for deployment.

### 4. Start FastAPI (Terminal 1)

From project root:

```powershell
uvicorn backend.app.main:app --reload --port 8000
```

Check:
- API health: http://127.0.0.1:8000/health
- Swagger docs: http://127.0.0.1:8000/docs

### 5. Start Streamlit (Terminal 2)

From project root:

```powershell
streamlit run streamlit_app/app.py --server.port 8501
```

Open http://localhost:8501.

Keep both terminals running. Streamlit is the browser UI; FastAPI is the backend.

## Features included

### Student
- Signup/sign in
- Student profile with education, skills, projects, certifications, experience, GitHub and role/location preferences
- PDF resume parsing (selectable text PDFs, max 8 MB); extracted skills saved as reviewable resume evidence
- GitHub public profile/repository language sync
- Explore roles and apply
- Application tracker
- Optional OpenAI career feedback with an explicitly configured key

### Recruiter
- Signup/sign in
- Company profile
- Publish and pause/activate roles
- Required/preferred skills, education, experience, location and work mode
- Candidate ranking against a selected role
- Match explanations, missing skills and evidence summaries
- Application pipeline statuses: applied, shortlisted, interview, rejected, hired

### Matching model

The original Python MVP's six-factor weights are retained:

| Signal | Weight |
|---|---:|
| Skills | 35% |
| Project evidence | 25% |
| GitHub languages | 15% |
| Education | 10% |
| Experience | 10% |
| Location / remote | 5% |

Preferred-role alignment is shown separately to preserve the legacy score calculation. The score is a transparent profile-to-role fit indicator, not a probability of hiring. It must not be used as an automatic hiring decision. Missing or unconnected GitHub evidence contributes a zero GitHub sub-score, so encourage candidates to connect their public profile or review their evidence. Human review is essential.

## Visual assets and photography

The original TalentLens logo is provided as local SVG and embedded in the Streamlit UI. Photographic sections use Unsplash image CDN URLs. An internet connection is required to load those photos; the layout retains its forest-green gradient treatment if external images are unavailable. Replace photo URLs with company-owned/licensed image assets before commercial launch.

## Tests

From project root:

```powershell
python -m unittest discover -s tests -v
```

Compile-check the Python source:

```powershell
python -m compileall backend streamlit_app
```

## Deployment outline

1. Provision PostgreSQL (for example Supabase PostgreSQL) and set `DATABASE_URL`.
2. Set a strong `JWT_SECRET`, `CORS_ORIGINS`, `GITHUB_TOKEN` (optional), and `OPENAI_API_KEY` (optional) in the hosting provider's secret manager.
3. Deploy FastAPI as a Python web service using:
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Deploy Streamlit as a separate Python service using:
   ```bash
   streamlit run streamlit_app/app.py --server.address 0.0.0.0 --server.port $PORT
   ```
5. Set `TALENTLENS_API_URL` in the Streamlit service to the public FastAPI URL.
6. Set FastAPI `CORS_ORIGINS` to the deployed Streamlit origin.
7. Use HTTPS, rotate secrets, configure database backups, logging, rate limiting and monitoring before production use.

## Important production notes

- This is a functional MVP foundation, not a security/compliance certification or a fully load-tested enterprise service.
- SQLite is for local development. Use PostgreSQL for hosted multi-user deployments.
- Resume parsing extracts selectable PDF text; scanned image PDFs require OCR, which is not enabled by default.
- GitHub integration reads public profile and public repository metadata. It does not infer code quality or private activity.
- OpenAI-generated profile feedback is optional and only works when a valid API key is configured.
- Add email verification, password reset, rate limiting, audit logs, data retention controls, consent/privacy notices and automated database migrations before public launch.
