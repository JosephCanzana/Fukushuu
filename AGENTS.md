# AGENTS.md

## Project overview
This repository is a Django-based flashcard project called Fukushuu. It has
moved past the initial scaffolding phase: the app structure and core models
are defined, though views/templates for most features are still stubs. The
project is focused on:
- a Django project shell configured for PostgreSQL
- a custom user model (`accounts.User`) with email-based identity
- the core flashcard domain (`decks`: `Tag`, `Deck`, `Card`) with SM-2
  spaced-repetition fields on `Card`
- admin-managed landing page content (`pages.LandingPage`, a singleton)
- Tailwind CSS + Alpine.js for the frontend, verified during the earlier
  scaffolding phase via a now-removed `sandbox` app

This project is still pre-production: migrations for `accounts`, `decks`,
and `pages` have been generated and applied to the local dev database, and
an initial superuser exists. Views are largely route stubs, templates are
minimal or absent, and no models are yet registered in any `admin.py`.

## Repository structure
- `manage.py` — Django entry point
- `fukushuu/` — project package (config only, not an app)
  - `settings.py` — global Django settings, PostgreSQL config, `AUTH_USER_MODEL`
  - `urls.py` — project URL routing, `include()`s each app's `urls.py`
  - `asgi.py`, `wsgi.py` — ASGI/WSGI app bootstraps
- `accounts/` — custom user identity and preferences
  - `models.py` — `User` (extends `AbstractUser`), `Setting`
  - `views.py`, `urls.py` — auth-related routes (currently stubs)
- `decks/` — the core flashcard domain
  - `models.py` — `Tag`, `Deck`, `Card`
  - `views.py`, `urls.py` — deck/card CRUD and review routes (currently stubs)
- `pages/` — admin-managed static content
  - `models.py` — `LandingPage` (singleton pattern via `save()` override)
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

**Note:** `sandbox/`, previously used to validate Tailwind/Alpine wiring, has
been removed now that real apps exist. If you encounter it on an older
branch, see the "Removing sandbox" steps in `README.md` before assuming it's
still part of `INSTALLED_APPS`.

## Tech stack
- Python 3.12
- Django 6.0
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

`createsuperuser` will prompt for `username`, `email`, `password` — `email`
is required and unique on the custom `User` model, so don't skip it.

### Day-to-day workflow
```bash
docker compose up
make tailwind-watch
```

Run Tailwind in a separate terminal because it watches files continuously.
The app is served at:
- http://127.0.0.1:8001/
- admin: http://127.0.0.1:8001/admin/

Use `127.0.0.1`, not `localhost` — this project has a known IPv6/IPv4
resolution quirk on `localhost` in local dev.

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
- `AUTH_USER_MODEL = 'accounts.User'` — **must** stay set; this was
  configured before the first `migrate` and should never be changed on an
  existing database without a deliberate, careful migration
- `INSTALLED_APPS` includes `django.contrib.*` plus the project apps:
  `pages`, `accounts`, `decks`
- `ROOT_URLCONF` points to `fukushuu.urls`
- `STATIC_URL` is `static/`
- `STATICFILES_DIRS` includes the project-level `static/` folder
- `ALLOWED_HOSTS` is left empty; this is a local-development setup

## App structure and model ownership
Apps are split by domain/feature (vertical slices), not by technical layer.
Before adding a new model, check whether it belongs in an existing app
first — a new app is only warranted when the data has no relational or
lifecycle overlap with an existing app's models.

### `accounts`
- `User(AbstractUser)` — drops `first_name`/`last_name`; `email` is
  overridden to be unique. No custom `role` field — roles are handled via
  built-in `is_staff` (admin panel access) and `is_superuser` (full bypass).
  `is_active` (inherited) is used as the soft-archive flag; a separate
  `archived` field was deliberately not added to avoid two flags disagreeing
  with each other. `suspended` / `suspended_until` are informational only —
  they do **not** block login automatically; check `is_currently_suspended`
  wherever suspension needs to be enforced.
- `Setting` — `OneToOneField` to `User` (not a plain `ForeignKey` — one
  settings row per user, enforced at the DB level). Currently just `theme`.

### `decks`
- `Tag` — per-user label, `unique_together`/`UniqueConstraint` on
  `(user, title)` to prevent duplicate tag names per user.
- `Deck` — belongs to a `User` (`CASCADE` on delete) and optionally a `Tag`
  (`SET_NULL` on delete — deleting a tag should untag decks, not delete them).
- `Card` — belongs to a `Deck` (`CASCADE`). Carries independent SM-2 state:
  `easiness_factor` (float, starts at 2.5), `interval` (days, int),
  `repetitions` (int, resets to 0 on a failed review), `due_date` (date,
  recalculated by the review logic — not `auto_now_add`), `last_reviewed`
  (nullable — unset until the first review).

### `pages`
- `LandingPage` — singleton (only one row should ever exist). Enforced by
  overriding `save()` to force `pk=1` on every save, and `delete()` to be a
  no-op. Fetch via `LandingPage.load()` (a `get_or_create`-based classmethod),
  not `.objects.first()` or `.objects.get()`.

### Shared conventions across models
- Every model that needs "soft delete" state uses `archived = BooleanField(default=False)`
  — except `User`, which uses `is_active` instead (see above).
- Timestamp fields always use `auto_now_add=True` (set once, at creation) or
  `auto_now=True` (updated every save) — never a bare `DateTimeField()` with
  no default, which breaks at `makemigrations` time.
- Every model defines `__str__` for readable output in the admin/shell.
- FK/O2O fields are named after the relation (`user`, `deck`, `tag`), never
  the raw column (`user_id`, `deck_id`) — Django creates the `_id` column
  automatically.

## Frontend behavior and tooling
Tailwind and Alpine wiring was originally verified via a `sandbox` app
(now removed). Frontend verification currently happens against real pages as
they're built out — there is no dedicated smoke-test route at the moment.

## Theming system
Colors and fonts are driven entirely by CSS custom properties ("design
tokens"), not raw Tailwind palette classes (`slate-*`, `indigo-*`, etc.) or
Tailwind's built-in `dark:` variant. Two files split the responsibility:

- `static/css/theme-tokens.css` — declares the token *names* (so Tailwind
  generates utilities like `bg-primary`, `text-txt-secondary`, `font-main`)
  and sets the `neutral` preset's light-mode values as the default fallback.
  Also holds the `@font-face` declarations (Space Grotesk, JetBrains Mono,
  self-hosted from `static/fonts/`, variable-weight files preferred so one
  `@font-face` block covers the full weight range).
- `static/css/themes.css` — override blocks for every state that differs
  from the default: `.theme-neutral.dark`, `.theme-slate`,
  `.theme-slate.dark`. `theme-neutral` (light) needs no block since it's
  already the default in `theme-tokens.css`.

Two presets (`neutral`, `slate`) × two modes (light, dark) = 4 rendered
combinations, expressed as 1 default + 3 override blocks. Adding a new
preset means adding its light block (if it isn't the default) and its dark
block to `themes.css`, plus a `theme-<name>` class option.

`<html>` carries both a preset class (`theme-neutral` / `theme-slate`,
currently hardcoded to `theme-neutral` in `base.html` since the preset
picker doesn't exist yet) and, independently, an optional `dark` class.
These two are deliberately decoupled — a user's light/dark preference and
their color preset are separate choices with separate scopes:

- **Light/dark** is per-device: stored in `localStorage`, applied via an
  inline synchronous script in `base.html`'s `<head>` (before any
  stylesheet, to avoid a flash of the wrong mode). No login required, works
  on public pages.
- **Preset** is meant to be an account-level choice once built (planned:
  `accounts.Setting`, following the same field the `theme` column already
  reserves), so it should follow a logged-in user across devices rather
  than living in `localStorage`.

When building new pages/components: use the token utilities (`bg-bg`,
`bg-surface`, `text-txt-primary`, `text-txt-secondary`, `border-border`,
`bg-accent`, etc.) exclusively for color — never hardcode a Tailwind
palette color or reach for `dark:` variants, since neither responds to the
`.dark` class this project actually toggles.

A temporary preset-cycling button may be present in `navbar.html` for
manual testing (clearly marked `TEMPORARY` in a comment above it, not
persisted anywhere) — remove it once the real settings-page picker exists.

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
- Apps are organized by domain (`accounts`, `decks`, `pages`), not by
  technical layer — when adding a model, place it by asking "which existing
  app's data does this share a lifecycle/relationship with," not "what type
  of thing is this." Only create a new app if the answer is genuinely "none."
- `AUTH_USER_MODEL` must remain `'accounts.User'`. Do not introduce code that
  assumes the default `django.contrib.auth.models.User`.
- Do not commit `.env` files or local secrets
- Keep configuration changes consistent with `.env.example`
- Tailwind-generated output files can be rebuilt rather than handwritten if the front-end tooling is in use
- Before running `migrate` on a fresh setup, confirm `AUTH_USER_MODEL` and
  `INSTALLED_APPS` are correctly set — both are effectively one-shot
  decisions that are costly to change after the first migration.

## Suggested next implementation path
The core schema is defined and migrated. The next meaningful work likely
includes:
1. registering models in each app's `admin.py` so they're editable via
   `/admin/` — nothing is registered yet, so `/admin/` currently only shows
   Django's built-in `Groups`, not `User`/`Setting`/`Tag`/`Deck`/`Card`/
   `LandingPage`. Note: `User` is a custom user model, so it needs a proper
   `UserAdmin` subclass, not a bare `admin.site.register(User)`.
2. implementing the SM-2 review logic as a method on `Card`
   (e.g. `apply_review(quality)`), not as a standalone utility function
3. building out real views/templates for `accounts` (auth) and `decks`
   (deck/card CRUD, review flow) to replace current route stubs
4. building the file-to-flashcard generation flow from uploaded files or text input

## Quick reference
```bash
# start stack
docker compose up --build

# generate + review + apply migrations (only needed after model changes)
docker compose exec web python manage.py makemigrations accounts
docker compose exec web python manage.py makemigrations decks
docker compose exec web python manage.py makemigrations pages
docker compose exec web python manage.py migrate

# create superuser
docker compose exec web python manage.py createsuperuser

# inspect the database directly
docker compose exec db psql -U <POSTGRES_USER> -d <POSTGRES_DB>
# inside psql: \dt (list tables), \d <table> (describe), \pset pager off

# watch Tailwind
make tailwind-watch

# build Tailwind once
make tailwind-build
```

## Known footguns encountered so far
- Running `makemigrations`/`migrate` from the host (outside Docker) will
  fail to connect to Postgres — `POSTGRES_HOST=db` only resolves inside the
  Docker network. `makemigrations` still works from the host (it only reads
  models, doesn't need a DB connection) but will print a harmless
  `RuntimeWarning` about host resolution. `migrate` genuinely needs to run
  inside the `web` container.
- If `migrate` is ever run before `AUTH_USER_MODEL` is set / before
  `accounts` exists, Django's `admin` app will migrate against the default
  user model, and later raise `InconsistentMigrationHistory` once
  `accounts.User` becomes the real `AUTH_USER_MODEL`. Pre-launch, the fix is
  `docker compose down -v` and a fresh `migrate`, not a manual reorder.

## Notes for AI agents
When making changes in this repo:
- confirm which existing app a new model/view belongs to before creating a
  new app — see "App structure and model ownership" above
- verify database and env assumptions before editing settings
- never change `AUTH_USER_MODEL` on a database that has already been
  migrated without a deliberate migration plan
- prefer the existing Docker + Django patterns already in the project
- test the app with the smallest relevant Django command or page load after changes
- if `sandbox/` is still present in a given checkout, treat it as legacy —
  do not add new functionality to it
- keep `{# ... #}` Django comments at file-top or on their own line between
  tags — never inside a tag's attribute list (see "Template comment
  placement" above)
- use theme token utility classes (`bg-bg`, `text-txt-primary`, `bg-accent`,
  etc.) for all color; never raw Tailwind palette classes or `dark:`
  variants (see "Theming system" above)

This repository has moved from bare scaffolding into real domain modeling:
the most important context is the `accounts` / `decks` / `pages` app split,
the custom `User` model, and the SM-2 fields on `Card`, all of which future
work should build on rather than restructure without cause.


## Template layout system
A base/layout template structure now exists under `templates/`:

- `templates/base.html` — shared HTML shell only: static asset loading,
  `<title>` block, the self-hosted Alpine.js `<script>` tag, and a single
  `{% block base %}` that `base_public.html` / `base_app.html` override.
  Contains no navigation or page-specific markup.
- `templates/base_public.html` — layout for logged-out/public pages.
  Extends `base.html`, includes `includes/navbar.html` (top nav bar), and
  exposes `{% block body %}` for page content.
- `templates/base_app.html` — layout for authenticated app pages. Extends
  `base.html`, includes `includes/sidebar.html` (left sidebar nav instead of
  a top navbar), and exposes `{% block body %}` for page content.
- `templates/includes/navbar.html` — public navbar partial: brand link,
  Log in / Sign up links, and a disabled dark-mode toggle placeholder.
- `templates/includes/sidebar.html` — app sidebar partial: brand link, nav
  links (Dashboard, Decks, Review, Settings), and a disabled dark-mode
  toggle placeholder.

Navigation links in both partials currently use `href="#"` with `TODO`
comments — `accounts` and `decks` URL names aren't finalized yet, so these
need to be swapped for `{% url %}` tags once those routes are named. The
dark/light mode toggles are inert placeholders (`disabled`, no Alpine
`x-data`/`@click` wiring) — behavior is intentionally not implemented yet.

When building new pages: extend `base_public.html` for logged-out/marketing
pages (e.g. `pages.LandingPage`) and `base_app.html` for authenticated pages
(deck/card CRUD, review flow). Add new nav entries to the relevant partial
in `templates/includes/`, not inline in the layout templates, so navigation
stays centralized and easy to update.

### Template comment placement
`{# ... #}` Django template comments should only appear at the top of a
file (file-level notes, e.g. "included by base_public.html") or on their
own line between tags (e.g. a `TEMPORARY` note above a block being called
out). Do not place a `{# ... #}` comment *inside* an HTML tag's attribute
list — e.g. between a tag's opening `<button ...` and its closing `>`. It
still renders correctly, but it's easy to misread as part of the tag or to
break with a careless edit, and it hurts scanability in already
attribute-heavy tags (Alpine's `x-data`/`@click`/`:aria-label` in this
project makes tags long enough already). Put the comment on its own line
immediately above the tag instead.