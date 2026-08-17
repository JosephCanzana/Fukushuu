# AGENTS.md

## Project overview
This repository is a Django-based flashcard project called Fukushuu. The current implementation is a small starter app focused on:
- a Django project shell configured for PostgreSQL
- a sandbox app used to validate Tailwind CSS + Alpine.js behavior
- a future file-to-flashcard workflow with spaced repetition (SM-2 style logic)

This project is currently in an early setup phase, not a full production-ready app yet.

## Repository structure
- `manage.py` — Django entry point
- `fukushuu/` — project package
  - `settings.py` — global Django settings and PostgreSQL config
  - `urls.py` — project URL routing
  - `asgi.py`, `wsgi.py` — ASGI/WSGI app bootstraps
- `sandbox/` — disposable development app for testing UI/tooling
  - `views.py` — app views
  - `urls.py` — app routes
  - `templates/sandbox/test.html` — minimal Tailwind/Alpine test page
- `static/` — frontend static assets
  - `css/input.css` and `css/output.css` — Tailwind input/output
  - `js/alpine.min.js` — Alpine.js runtime
- `theme/` — Tailwind CLI binary gets downloaded here
- `Dockerfile` — production-style container for the web app
- `docker-compose.yml` — local stack for Django + PostgreSQL
- `Makefile` — Tailwind build/watch commands
- `requirements.txt` — Python dependencies
- `.env.example` — sample environment file
- `.env` — local environment values (not committed)

## Tech stack
- Python 3.12
- Django 5+
- PostgreSQL 16
- Tailwind CSS via standalone CLI
- Alpine.js
- Docker + Docker Compose

## Runtime and local development
Use Docker Compose as the default development path.

### First-time setup
From the repository root:

```bash
docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### Day-to-day workflow
```bash
docker compose up
make tailwind-watch
```

Run Tailwind in a separate terminal because it watches files continuously. The app is served at:
- http://127.0.0.1:8001/
- admin: http://127.0.0.1:8001/admin/

The sandbox page is available at:
- http://127.0.0.1:8001/sandbox/

## Important environment configuration
The app reads settings from `.env` via `python-decouple`.

Required values are defined in `.env.example`:
- `DEBUG`
- `SECRET_KEY`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

Current project config expects Postgres at host `db` on port `5432` in Docker.

## Django settings and app conventions
Key configuration facts:
- `fukushuu/settings.py` uses PostgreSQL, not SQLite
- `INSTALLED_APPS` currently includes `django.contrib.*` plus the `sandbox` app
- `ROOT_URLCONF` points to `fukushuu.urls`
- `STATIC_URL` is `static/`
- `STATICFILES_DIRS` includes the project-level `static/` folder
- `ALLOWED_HOSTS` is left empty; this is a local-development setup

URL structure:
- project URL root includes `admin/`
- project URL root also includes `sandbox/` via `sandbox.urls`

## Frontend behavior and tooling
The sandbox page is intentionally a simple smoke test to verify that Tailwind and Alpine are working.

`templates/sandbox/test.html` loads:
- compiled CSS from `static/css/output.css`
- Alpine.js from `static/js/alpine.min.js`

It uses a tiny interactive demo:
- a toggle button
- a counter with +/- controls

This is useful for confirming that:
- Tailwind compilation is working
- Alpine is loaded and responding
- the CSS pipeline is generating output correctly

## Tailwind commands
The project includes a Makefile for Tailwind:

```bash
make tailwind-build
make tailwind-watch
```

These commands compile from `static/css/input.css` to `static/css/output.css`.

## Docker and database notes
- `docker-compose.yml` defines a `db` service using Postgres 16
- the `web` service builds from `Dockerfile` and exposes localhost port `8001` to container port `8000`
- database data is persisted in a Docker volume named `postgres_data`

If Postgres authentication fails after changing `.env`, a common fix is:

```bash
docker compose down -v
docker compose up --build
```

This resets the local dev database volume.

## Working rules for future agents
- Prefer Docker-based commands when working with the app
- Use `docker compose exec web python manage.py ...` for Django management commands
- Treat `sandbox/` as a testing app; it may be replaced or removed later as the real flashcard functionality is built out
- Do not commit `.env` files or local secrets
- Keep configuration changes consistent with `.env.example`
- Tailwind-generated output files can be rebuilt rather than handwritten if the front-end tooling is in use

## Suggested next implementation path
The repository is set up as a starter Django project, not a finished product. The next meaningful work likely includes:
1. defining the actual flashcard models and data schema
2. creating a flashcard generation flow from uploaded files or text input
3. implementing spaced repetition logic (SM-2 style)
4. building user-facing views and templates around the actual core feature
5. replacing or expanding the sandbox app with real application code

## Quick reference
```bash
# start stack
docker compose up --build

# run migrations
docker compose exec web python manage.py migrate

# create superuser
docker compose exec web python manage.py createsuperuser

# watch Tailwind
make tailwind-watch

# build Tailwind once
make tailwind-build
```

## Notes for AI agents
When making changes in this repo:
- confirm whether the code belongs in `sandbox/` or in a new app
- verify database and env assumptions before editing settings
- prefer the existing Docker + Django patterns already in the project
- test the app with the smallest relevant Django command or page load after changes

This repository is simple and intentionally lightweight at the moment; the most important context is that it is a Django foundation for a future flashcard app, with local containerized development and Tailwind-based UI prototyping already in place.
