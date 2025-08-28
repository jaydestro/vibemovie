# VibeMovie

Simple Flask app to list movies and allow 0–5 star ratings and comments, backed by Azure Cosmos DB Emulator.

## Quick start (Windows PowerShell)

1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

1. Install dependencies

```powershell
pip install -r requirements.txt
```

1. Create a local .env (emulator-ready)

   ```powershell
   Copy-Item .env.example .env
   ```

1. Start the Azure Cosmos DB Linux Emulator (Docker) — do this before running the app
   - Prereqs: Docker Desktop (WSL2 backend enabled) running

   Pull the image (first time only):

   ```powershell
   docker pull mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:latest
   ```

   Run the container (first time):

   ```powershell
   docker run --name cosmos-emulator -p 8081:8081 -p 10251:10251 -p 10252:10252 -p 10253:10253 -p 10254:10254 --memory=3g -it mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:latest
   ```

   After the first run, you can stop/start it with:

   ```powershell
   docker stop cosmos-emulator
   docker start cosmos-emulator
   ```

   Notes:
   - The app defaults to endpoint `https://localhost:8081/` and the emulator master key.
   - If you see SSL errors, download the emulator certificate from <https://localhost:8081/_explorer/emulator.pem> and import it into “Current User > Trusted Root Certification Authorities”. As a temporary fallback for local dev only, you can do: `$env:PYTHONHTTPSVERIFY=0` before `python app.py`.

1. Run the app (only after the emulator is running)

```powershell
set PORT=3000
python app.py
```

Then open <http://localhost:3000/>

## Configuration

Environment variables (optional):

- `COSMOS_ENDPOINT` (default: <https://localhost:8081/>)
- `COSMOS_KEY` (default: emulator master key)
- `COSMOS_DB_NAME` (default: vibemovie-db)
- `COSMOS_MOVIES_CONTAINER` (default: movies)
- `COSMOS_RATINGS_CONTAINER` (default: ratings)
- `COSMOS_COMMENTS_CONTAINER` (default: comments)

## Build, test, run, lint — validated sequences

Always activate the virtual environment first:

```powershell
.\.venv\Scripts\Activate.ps1
```

Bootstrap from a clean clone:

```powershell
pip install -r requirements.txt ; pip install -r requirements-dev.txt
```

Lint (check only):

```powershell
python -m ruff check .
```

Lint (auto-fix safe issues):

```powershell
python -m ruff check . --fix
```

Run unit tests:

```powershell
python -m pytest -q
```

Run the app (ensure emulator is running):

```powershell
$env:PORT=3000
python app.py
```

Preconditions checked:

- Python 3.11+ available; virtual environment activated
- Dependencies installed without error
- Emulator container reachable at <https://localhost:8081/>

Observed misbehaviors and mitigations:

- SSL trust errors: install emulator cert to Current User > Trusted Root or set `$env:PYTHONHTTPSVERIFY=0` for local-only dev.
- Port 3000 in use: stop the conflicting process or set a different `$env:PORT`.

VS Code tasks:

- Run: Flask app — starts the server in background using the venv interpreter
- Test: pytest — runs tests quietly
- Lint: ruff — checks code style; ruff (fix) applies safe fixes

## One-command start (emulator + app)

Use the provided PowerShell script to always start the emulator first and then the app:

```powershell
./scripts/start-app.ps1
```

Or start the emulator alone:

```powershell
./scripts/start-cosmos-emulator.ps1
```
