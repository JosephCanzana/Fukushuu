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
1. Clone the repo
2. Copy `.env.example` to `.env` and fill in values
3. Download Tailwind CLI (one-time):
   \`\`\`bash
   curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
   chmod +x tailwindcss-linux-x64
   mv tailwindcss-linux-x64 theme/tailwindcss
   \`\`\`
4. Download Alpine.js (one-time):
   \`\`\`bash
   mkdir -p static/js
   curl -sLo static/js/alpine.min.js https://cdn.jsdelivr.net/npm/alpinejs@3.14.9/dist/cdn.min.js
   \`\`\`
5. Build containers:
   \`\`\`bash
   docker compose up --build
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   \`\`\`

### Day-to-day development
\`\`\`bash
docker compose up
make tailwind-watch    # in a separate terminal
\`\`\`


Admin panel: `http://127.0.0.1:8001/admin` or `http:/localhost:8001/admin` 

## Verify it's working

Visit `http://127.0.0.1:8001/sandbox/` — you should see a white card on a gray background with a "Toggle Message" button and a +/− counter.

- Styled card + colors → Tailwind is compiling correctly
- Button toggles a message, counter changes on click → Alpine.js is loaded and working

If the page loads with no styling (plain black text, no layout), check that `make tailwind-watch` is running. If the page is styled but buttons don't respond, open the browser console (F12) and check for a 404 on `alpine.min.js`.

## Project Structure

\`\`\`
fukushuu/          # Django settings package (config only)
sandbox/           # Throwaway app for testing Tailwind/Alpine — safe to delete
theme/             # Tailwind CLI binary (gitignored)
static/            # Project-wide static files (Tailwind output, Alpine.js)
templates/         # Project-wide templates (base.html)
\`\`\`

## Troubleshooting

- **"password authentication failed" on `db`**: You likely changed `.env` Postgres credentials after the volume was already initialized. Fix: `docker compose down -v` then `docker compose up --build` (wipes local dev data, safe pre-launch).


## License