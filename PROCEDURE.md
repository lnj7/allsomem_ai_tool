# Jadon Family creatorOS & co. — how to run and edit

Use this file when you want to start the app or open the code in VS Code.

Project folder:

```text
~/Projects/creatoros
```

## 1. Open the code in VS Code

```bash
open -a "Visual Studio Code" ~/Projects/creatoros
```

Or, after the `code` command is available:

```bash
code ~/Projects/creatoros
```

## 2. Start the app

From Terminal:

```bash
~/Projects/creatoros/infrastructure/scripts/start-local.sh
```

Then open:

- App: http://localhost:3000
- Dashboard: http://localhost:3000/dashboard
- API health: http://localhost:8000/health
- API ready: http://localhost:8000/health/ready

## 3. Stop the app

```bash
~/Projects/creatoros/infrastructure/scripts/stop-local.sh
```

## 4. First-time setup (already done on this machine)

Only run these again on a new Mac, or if something was uninstalled.

```bash
brew install node python@3.12 postgresql@16 redis
brew install --cask visual-studio-code
brew install colima docker docker-compose

cd ~/Projects/creatoros
cp -n .env.example .env
python3.12 -m venv apps/api/.venv
apps/api/.venv/bin/pip install -r apps/api/requirements-dev.txt
npm install
brew services start postgresql@16
brew services start redis
cd apps/api && .venv/bin/alembic upgrade head
```

## 5. Useful checks

```bash
cd ~/Projects/creatoros/apps/api
.venv/bin/pytest
.venv/bin/ruff check app tests
.venv/bin/mypy app

cd ~/Projects/creatoros/apps/web
npm test
npm run lint
npm run typecheck
npm run build
```

## Notes

- Edit files in VS Code. After start-local, the API and web reload when you save.
- Auth, AI, and social publishing are not built yet.
- Docker Compose is optional. If you use it, stop Homebrew Postgres and Redis first so ports 5432 and 6379 are free.
