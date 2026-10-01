# Resume Optimizer

A private, admin-only resume optimization workspace built with **HTML/CSS/JavaScript + FastAPI + Supabase + Groq (`openai/gpt-oss-20b`)**.

## Features

- Supabase email/password authentication; sign-up is intentionally not exposed.
- Optional `ADMIN_EMAILS` allow-list so only your account(s) can enter the application.
- Glassmorphism dashboard with motion effects and resume analytics.
- Canonical/original resume configuration editor backed by Supabase JSONB.
- Current Resume preview with PDF/DOCX export.
- ATS checker for both the original resume and a JD-tailored resume.
- JD-driven resume optimizer using separate LLM passes for summary, skills, and experience.
- Generated resume history with rename, preview and export.
- JD-specific cover-letter generation using the tailored resume.
- ATS reports, generation events and analytics stored in Supabase.
- No Groq key is exposed to the browser.
- Structured LLM output with JSON-schema validation and anti-hallucination instructions.

## Architecture

```text
Browser (HTML/CSS/JS)
        |
        | Supabase Auth JWT
        v
FastAPI backend --------------------> Groq API
        |
        | service-role DB access after JWT validation
        v
Supabase Postgres + RLS
```

The browser only receives the Supabase URL/anon key. The Groq API key and Supabase service-role key stay on the backend.

## 1. Supabase setup

Create a Supabase project and enable **Email** authentication. Create the database objects in `db/schema.sql` using the SQL editor.

Create your single admin user from the Supabase dashboard (Authentication → Users). Do not expose a sign-up page.

The SQL enables RLS and limits direct database access to the authenticated owner. The FastAPI server uses the service-role key only after validating the user's Supabase access token.

Supabase's password sign-in is handled through `signInWithPassword`; Supabase Auth issues JWTs which are used for authorization. See the official docs: https://supabase.com/docs/guides/auth and https://supabase.com/docs/reference/python/auth-signinwithpassword

## 2. Environment

Copy `.env.example` to `.env`:

```env
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=YOUR_SUPABASE_SERVICE_ROLE_KEY
GROQ_API_KEY=YOUR_GROQ_API_KEY
ADMIN_EMAILS=you@example.com
GROQ_MODEL=openai/gpt-oss-20b
APP_NAME=Resume Optimizer
APP_ENV=development
```

`ADMIN_EMAILS` is a comma-separated allow-list. Leave it empty only if you deliberately want every authenticated Supabase user to access the app.

## 3. Install

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r backend/requirements.txt
```

For PDF export, the project uses WeasyPrint. If your OS needs additional native libraries, follow WeasyPrint's installation guide.

## 4. Run

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Open `http://localhost:8000`.

## 5. First login

1. Create your admin account directly in Supabase.
2. Put that email in `ADMIN_EMAILS`.
3. Log in through the application.
4. The first authenticated request automatically seeds the resume from `seed/priyankDetails.json` if no saved canonical resume exists.

## Production notes

- Serve FastAPI behind HTTPS.
- Keep `SUPABASE_SERVICE_ROLE_KEY` and `GROQ_API_KEY` server-side only.
- Set a strong Supabase Auth password and enable appropriate MFA if desired.
- Restrict CORS to your deployed frontend origin instead of `*`.
- For multi-admin use, add each email to `ADMIN_EMAILS`.
- Review generated content before using it in an application; the optimizer is instructed not to invent experience, credentials or metrics, but LLM output should still be reviewed.

## Project structure

```text
ResumeOptimizer/
├── backend/
│   ├── app/main.py
│   ├── services/groq_service.py
│   ├── services/resume_service.py
│   ├── templates/resume.html
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/app.css
│   └── js/app.js
├── db/schema.sql
├── seed/priyankDetails.json
├── scripts/seed_resume.py
├── .env.example
└── README.md
```
