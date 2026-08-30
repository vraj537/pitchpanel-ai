<div align="center">
  <img src="./readme-banner.svg" alt="PitchPanel Ai" width="900">

  <p>
    <img src="https://img.shields.io/badge/Django-5.x-0b0b14?style=for-the-badge&logo=django&logoColor=white&labelColor=0b0b14&color=6657C3" alt="Django">
    <img src="https://img.shields.io/badge/Database-Supabase%20Postgres-0b0b14?style=for-the-badge&logo=supabase&logoColor=white&labelColor=0b0b14&color=6657C3" alt="Supabase">
    <img src="https://img.shields.io/badge/AI-Gemini%20Flash--Lite-0b0b14?style=for-the-badge&logo=googlegemini&logoColor=white&labelColor=0b0b14&color=6657C3" alt="Gemini">
    <img src="https://img.shields.io/badge/Deploy-Vercel-0b0b14?style=for-the-badge&logo=vercel&logoColor=white&labelColor=0b0b14&color=6657C3" alt="Vercel">
  </p>
</div>

# PitchPanel Ai (Django)

Get your startup idea reviewed by an AI panel — an **Investor**, a **Skeptical
Customer**, and a **Competitor** — before you build it. A fourth call
synthesizes their feedback into one overall **verdict**.

This is a full Django rewrite of the original static HTML + Vercel
serverless + Supabase-Auth project. Same visual design (dark
glassmorphism, Bootstrap 5), now backed by:

- **Django auth** (signup / login / logout / forgot-password via email)
- **Supabase Postgres** as the database (via `DATABASE_URL`)
- **Gemini API** (`gemini-3.1-flash-lite` by default) for the 4 panel calls
- Deployable on **Vercel** as a Python serverless function

The landing page, FAQ and footer have been rewritten to only describe
things that actually exist in this app — no fake testimonials, pricing
tiers, blog posts, or partner logos.

---

## 1. Local setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in the values (see below), then:

```bash
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

If `DATABASE_URL` is left blank, the app automatically falls back to a
local `db.sqlite3` file — handy for a quick test before wiring up Supabase.

---

## 2. Environment variables (`.env`)

| Variable | What it's for |
|---|---|
| `SECRET_KEY` | Django's secret key. Generate one with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `True` locally, `False` in production |
| `ALLOWED_HOSTS` | Comma-separated hosts, e.g. `127.0.0.1,localhost,.vercel.app` |
| `CSRF_TRUSTED_ORIGINS` | Your deployed HTTPS URL, e.g. `https://your-project.vercel.app` |
| `DATABASE_URL` | Supabase Postgres connection string (see below) |
| `GEMINI_API_KEY` | Your Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey) |
| `GEMINI_MODEL` | Defaults to `gemini-3.1-flash-lite` — the free-tier "lite" model with a much higher daily request quota, since each pitch uses 4 calls |
| `DAILY_PITCH_LIMIT` | Max pitches a user can submit per 24 hours (default `3`) |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | Gmail address + [App Password](https://myaccount.google.com/apppasswords) for sending "forgot password" emails |
| `DEFAULT_FROM_EMAIL` | Usually the same as `EMAIL_HOST_USER` |

**Never commit `.env`.** `.gitignore` already excludes it — only
`.env.example` (with placeholder values) should go to GitHub.

### Getting the Supabase `DATABASE_URL`

In your Supabase project: **Project Settings → Database → Connection
string → Transaction pooler** (port `6543`). Use the *pooler* URI, not
the direct connection — it plays nicely with Vercel's short-lived
serverless functions. It looks like:

```
postgresql://postgres.xxxxxxxxxxxx:YOUR-DB-PASSWORD@aws-0-<region>.pooler.supabase.com:6543/postgres
```

Once it's set in `.env`, run:

```bash
python manage.py migrate
```

This creates all tables (Django auth tables + `Pitch` + `ContactMessage`)
directly in your Supabase Postgres database — no need to run
`makemigrations` yourself, the migration files are already included.

---

## 3. Deploying to Vercel

This repo includes `vercel.json` and `api/index.py`, which wrap the
Django app as a Python serverless function and serve `/static/*` via
WhiteNoise directly from the `static/` folder (no `collectstatic` step
needed).

1. Push this repo to GitHub.
2. Import it into Vercel.
3. In Vercel → Project → Settings → Environment Variables, add every
   variable from `.env.example` (with your real values).
4. Deploy.
5. **Run migrations once against Supabase** — Vercel functions are
   stateless, so do this from your machine with `DATABASE_URL` pointed
   at Supabase in your local `.env`:
   ```bash
   python manage.py migrate
   ```
6. Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` in your Vercel env
   vars to include your real `*.vercel.app` domain (or custom domain).

**Note on request duration:** each pitch makes 4 Gemini calls (3 in
parallel + 1 verdict call). `vercel.json` sets `maxDuration: 60` for the
function so this has room to complete; if you're on a plan/tier with a
lower cap, this may need adjusting in your Vercel project settings too.

---

## 4. Project structure

```
pitchpanel/          # Django settings, root urls, wsgi/asgi
core/                # Landing page, FAQ, Contact (+ ContactMessage model)
accounts/            # Signup, login, logout, password reset (Django auth)
panel/               # Pitch model, Gemini integration, AI Chat views
templates/           # base.html / base_auth.html / base_app.html + app templates
static/              # Ported CSS/JS/images/plugins (design untouched)
api/index.py         # Vercel serverless entrypoint (wraps Django WSGI app)
vercel.json          # Vercel build/route config
requirements.txt
.env.example
```

### Auth notes
- Uses Django's built-in `django.contrib.auth` — no Supabase Auth
  involved. A user's email is stored as their `username`.
- Password reset sends a real email via Gmail SMTP.

### AI panel notes
- `panel/gemini.py` calls Gemini directly over HTTPS with `requests`
  (same approach as the original `validate-pitch.js`, just in Python).
- Investor / Customer / Competitor run in parallel via
  `ThreadPoolExecutor`; the Verdict call runs after, using all three
  responses as context.
- Each user is capped at `DAILY_PITCH_LIMIT` (default 3) pitches per
  rolling 24 hours — enforced server-side in `panel/views.py`.
