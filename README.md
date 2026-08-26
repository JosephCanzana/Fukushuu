# Fukushuu

A file-to-flashcard generator with SM-2 spaced repetition, built for CS50x.

## Tech Stack
- Django, PostgreSQL, Docker
- Tailwind CSS (standalone CLI)
- Alpine.js

## Setup

### Prerequisites
- Docker & Docker Compose
- `make`

### First-time setup
Status: models, migrations, and the initial superuser are already in place on
`main`. These steps are for a fresh clone / fresh environment.

1. Clone the repo
2. Copy `.env.example` to `.env` and fill in values
3. Download Tailwind CLI (one-time):
   ```bash
   curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
   chmod +x tailwindcss-linux-x64
   mv tailwindcss-linux-x64 theme/tailwindcss
   ```
4. Download Alpine.js (one-time):
   ```bash
   mkdir -p static/js
   curl -sLo static/js/alpine.min.js https://cdn.jsdelivr.net/npm/alpinejs@3.14.9/dist/cdn.min.js
   ```
5. Build containers and set up the database:
   ```bash
   docker compose up --build
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   ```
   Note: `createsuperuser` will prompt for `username`, `email`, and `password` —
   `email` is required and unique on this project's custom user model.

### Day-to-day development
```bash
docker compose up
make tailwind-watch    # in a separate terminal
```

App: `http://127.0.0.1:8001/`
Admin panel: `http://127.0.0.1:8001/admin/`

> Use `127.0.0.1`, not `localhost` — this project has a known IPv6/IPv4
> resolution quirk on `localhost` in local dev.

## Project Structure

```
fukushuu/          # Django settings package (config only, not an app)
accounts/          # Custom User model, UserSettings, auth views
decks/             # Tag, Deck, Card — the core flashcard domain
pages/             # Admin-managed static content (LandingPage, singleton)
theme/             # Tailwind CLI binary (gitignored)
static/            # Project-wide static files (Tailwind output, Alpine.js)
templates/         # Project-wide templates (base.html)
```

### App responsibilities

| App | Owns | Notes |
|---|---|---|
| `accounts` | `User` (custom, `AUTH_USER_MODEL`), `Setting` | `User` drops `first_name`/`last_name`, requires unique `email`. Roles use built-in `is_staff`/`is_superuser`, not a custom field. `is_active` doubles as soft-archive. |
| `decks` | `Tag`, `Deck`, `Card` | `Card` carries SM-2 spaced-repetition state (`easiness_factor`, `interval`, `repetitions`, `due_date`). |
| `pages` | `LandingPage` | Singleton row (enforced in `save()`, not at the DB level) for admin-editable landing page copy. |

`sandbox/` (the original Tailwind/Alpine smoke-test app) has been removed now
that real apps exist. If you're on an older branch/checkout that still has it,
see **Removing sandbox** below before merging.

### Icons

Icons are [Heroicons](https://heroicons.com) (outline, 24px), self-hosted as
a single SVG sprite at `static/icons/sprite.svg` — no icon font, no Google
Fonts/Material Icons, no CDN.

```html
{% load static %}
<svg class="size-6 text-txt-secondary" aria-hidden="true">
  <use href="{% static 'icons/sprite.svg' %}#moon"></use>
</svg>
```

- Icon name = the Heroicons filename without `.svg` (`moon`, `check`, etc.)
- Color/size follow the same theme-token classes as everything else
  (`text-txt-secondary`, `text-accent`) — icons inherit `currentColor`
- Put `aria-hidden="true"` on the icon, `aria-label` on the parent
  `<button>`/`<a>` — the icon itself has no accessible text
- The sprite bundles all Heroicons outline icons, so new icons never
  require a rebuild — just reference `#icon-name`

### Template layout

Pages extend one of two layouts, both of which extend the shared `base.html`
shell (static assets, `<title>` block, Alpine.js):

- **`base_public.html`** — logged-out/marketing pages (e.g. `pages.LandingPage`).
  Includes `includes/navbar.html`: brand link, Log in / Sign up, and a
  dark-mode toggle placeholder.
- **`base_app.html`** — authenticated app pages (deck/card CRUD, review flow).
  Includes `includes/sidebar.html`: brand link, nav links, and a dark-mode
  toggle placeholder.

Nav links in both partials use `href="#"` for now — `accounts`/`decks` URL
names aren't finalized yet. Add new nav entries to the relevant partial in
`templates/includes/`, not inline in the layout templates, so navigation
stays centralized. Dark/light mode toggles are inert placeholders; the
behavior itself isn't implemented yet.

## Verify Tailwind + Alpine are working

There's currently no dedicated smoke-test page (that was `sandbox/`, since
removed). Confirm the frontend pipeline is working by checking any real page
that extends `base_public.html` or `base_app.html` (both inherit from
`base.html`):
- Styled layout, correct colors/spacing → Tailwind is compiling correctly.
- Any Alpine-driven interaction (toggles, dropdowns) responds on click → Alpine.js is loaded.

If a page loads with no styling (plain black text, no layout), check that
`make tailwind-watch` is running. If styling is fine but interactive elements
don't respond, open the browser console (F12) and check for a 404 on
`alpine.min.js`.

## Removing sandbox (if present on your checkout)

```bash
docker compose exec web python manage.py showmigrations sandbox
# if migrations show [X] applied:
docker compose exec web python manage.py migrate sandbox zero
```
Then remove `'sandbox'` from `INSTALLED_APPS` in `fukushuu/settings.py`,
delete any `path('sandbox/', include('sandbox.urls'))` from the project
`urls.py`, and delete the `sandbox/` directory.

## Troubleshooting

- **"password authentication failed" on `db`**: You likely changed `.env`
  Postgres credentials after the volume was already initialized. Fix:
  `docker compose down -v` then `docker compose up --build` (wipes local dev
  data, safe pre-launch).
- **`createsuperuser` fails or behaves unexpectedly**: Confirm
  `AUTH_USER_MODEL = 'accounts.User'` is set in `settings.py` *before* running
  `migrate` for the first time. Setting this after tables already exist
  requires a manual migration fix, not a quick setting change.
- **`InconsistentMigrationHistory: Migration admin.0001_initial is applied
  before its dependency accounts.0001_initial`**: happens if `migrate` was
  ever run before `AUTH_USER_MODEL` was set / before `accounts` existed. Fix
  by wiping the local dev volume and re-migrating fresh (safe pre-launch,
  destroys local dev data only):
  ```bash
  docker compose down -v
  docker compose up --build
  docker compose exec web python manage.py migrate
  docker compose exec web python manage.py createsuperuser
  ```
- **Inspecting the database directly**: `docker compose exec db psql -U
  <POSTGRES_USER> -d <POSTGRES_DB>` (or `docker compose exec web python
  manage.py dbshell`, which reads credentials from `.env` for you). Once
  inside: `\dt` lists tables, `\d <table_name>` describes one, `\pset pager
  off` prevents long output from getting swallowed by the pager. Tables are
  named `<app_label>_<model_name>`, e.g. `accounts_user`, `decks_card`.

## License