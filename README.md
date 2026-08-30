<div align="center">
  <img src="./readme-banner.svg" alt="PitchPanel Ai" width="900">

  <h3>PitchPanel Ai</h3>
  <p><i>Get your startup idea reviewed by an AI panel before you build it.</i></p>

  <p>
    <img src="https://img.shields.io/badge/Django-5.x-0b0b14?style=for-the-badge&logo=django&logoColor=white&labelColor=0b0b14&color=6657C3" alt="Django">
    <img src="https://img.shields.io/badge/Database-Supabase%20Postgres-0b0b14?style=for-the-badge&logo=supabase&logoColor=white&labelColor=0b0b14&color=6657C3" alt="Supabase">
    <img src="https://img.shields.io/badge/AI-Gemini%20Flash--Lite-0b0b14?style=for-the-badge&logo=googlegemini&logoColor=white&labelColor=0b0b14&color=6657C3" alt="Gemini">
    <img src="https://img.shields.io/badge/Deploy-Vercel-0b0b14?style=for-the-badge&logo=vercel&logoColor=white&labelColor=0b0b14&color=6657C3" alt="Vercel">
  </p>
</div>

---

## ✨ What it does

PitchPanel Ai puts your startup idea in front of a 4-persona AI panel:

| Persona | Role |
|---|---|
| 💼 **Investor** | Grills the business model and market size |
| 🧐 **Skeptical Customer** | Pushes back on whether anyone would actually pay for it |
| ⚔️ **Competitor** | Points out who's already doing this, and better |
| ⚖️ **Verdict** | Synthesizes all three takes into one final call |

Full Django rewrite of the original static HTML + Vercel serverless +
Supabase-Auth project — same dark glassmorphism / Bootstrap 5 look,
now backed by a proper backend:

- 🔐 **Django auth** — signup / login / logout / forgot-password (via email)
- 🐘 **Supabase Postgres** as the database, via `DATABASE_URL`
- 🤖 **Gemini API** (`gemini-3.1-flash-lite` by default) for the 4 panel calls
- ▲ Deployable on **Vercel** as a Python serverless function

The landing page, FAQ, and footer only describe things that actually
exist in the app — no fake testimonials, pricing tiers, or partner logos.

---

## 🚀 Quick start (local)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` → `.env` and fill in the values (table below), then:

```bash
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

> 💡 Leave `DATABASE_URL` blank and the app auto-falls-back to a local
> `db.sqlite3` file — handy for a quick test before wiring up Supabase.

---

## 🔧 Environment variables

| Variable | What it's for |
|---|---|
| `SECRET_KEY` | Django's secret key — generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `True` locally, `False` in production |
| `ALLOWED_HOSTS` | Comma-separated hosts, e.g. `127.0.0.1,localhost,.vercel.app` |
| `CSRF_TRUSTED_ORIGINS` | Your deployed HTTPS URL, e.g. `https://your-project.vercel.app` |
| `DATABASE_URL` | Supabase Postgres connection string (see below) |
| `GEMINI_API_KEY` | From [Google AI Studio](https://aistudio.google.com/apikey) |
| `GEMINI_MODEL` | Defaults to `gemini-3.1-flash-lite` — free-tier "lite" model with a much higher daily quota, since each pitch = 4 calls |
| `DAILY_PITCH_LIMIT` | Max pitches per user per 24 hours (default `3`) |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | Gmail address + [App Password](https://myaccount.google.com/apppasswords) for "forgot password" emails |
| `DEFAULT_FROM_EMAIL` | Usually same as `EMAIL_HOST_USER` |

> ⚠️ **Never commit `.env`.** It's already git-ignored — only
> `.env.example` (placeholder values) should reach GitHub. If a real
> key or password ever gets exposed (pushed, pasted, screenshotted),
> rotate it immediately rather than assuming it's fine.

### Getting the Supabase `DATABASE_URL`

**Project Settings → Database → Connection string → Transaction pooler**
(port `6543`). Use the *pooler* URI, not the direct connection — it
plays nicely with Vercel's short-lived serverless functions.

```
postgresql://postgres.xxxxxxxxxxxx:YOUR-DB-PASSWORD@aws-0-<region>.pooler.supabase.com:6543/postgres
```

Once set in `.env`, run:

```bash
python manage.py migrate
```

This creates every table (Django auth + `Pitch` + `ContactMessage`)
directly in Supabase Postgres — migration files are already included,
no need to run `makemigrations`.

---

## ▲ Deploying to Vercel

This repo ships `vercel.json` and `api/index.py`, wrapping the Django
app as a Python serverless function. Static files (`/static/*`) are
served via WhiteNoise directly — no `collectstatic` step needed.

1. Push this repo to GitHub.
2. Import it into Vercel.
3. **Settings → Environment Variables** → add every var from
   `.env.example` with real values.
4. Deploy.
5. **Run migrations once against Supabase** — Vercel functions are
   stateless, so do this from your own machine with `DATABASE_URL`
   pointed at Supabase in your local `.env`:
   ```bash
   python manage.py migrate
   ```
6. Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` in Vercel to
   include your real `*.vercel.app` domain (or custom domain).

> ⏱️ **Request duration:** each pitch makes 4 Gemini calls (3 parallel +
> 1 verdict). `vercel.json` sets `maxDuration: 60` for headroom — if
> your plan caps functions lower than that, bump it in your Vercel
> project settings too.

---

## 🩺 Troubleshooting

**Signup/login "succeeds" but nothing shows up in Supabase**
`DATABASE_URL` is missing, unset for the *Production* environment in
Vercel, or has a typo — the app silently falls back to local SQLite,
which doesn't persist on serverless. Double-check the variable in
Vercel → Settings → Environment Variables, redeploy, and make sure
`python manage.py migrate` has been run once against Supabase directly
(step 5 above) — otherwise the tables won't exist yet even with the
right connection string.

**Contact form submits (200 OK) but no email arrives**
By design, the contact form only saves to the `ContactMessage` table —
it doesn't send an email. Check Django admin (`/admin/`) or the
Supabase Table Editor for submissions. Password-reset emails are the
only flow that actually sends mail (via Gmail SMTP).

**Vercel Function Logs show "No outgoing requests"**
That means the code path never reached an external API call — usually
a form failing validation, or (as above) the email step simply isn't
implemented for that particular form. Check `views.py` for the relevant
view first before assuming it's an env-variable issue.

---

## 📁 Project structure

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
- Each user is capped at `DAILY_PITCH_LIMIT` (default `3`) pitches per
  rolling 24 hours — enforced server-side in `panel/views.py`.

---

<div align="center">
  <sub>Built by <a href="https://github.com/vraj537">vraj537</a></sub>
</div>
