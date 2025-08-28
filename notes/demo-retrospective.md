# VibeMovie demo retrospective

Purpose: capture what worked, what failed, and how to simplify this into a reliable 20‑minute conference demo.

## Context and environment

- OS: Windows, PowerShell (v5.1)
- Python: 3.11 (venv at `.venv/`)
- Frameworks/SDKs: Flask 3.x, Jinja2, azure-cosmos 4.7.x, python-dotenv
- Tools: Docker Desktop (WSL2 backend), VS Code tasks
- Emulator image: `mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:latest`
- App start script: `scripts/start-app.ps1` (starts emulator first, then app)

## What worked well

- App scaffolding
  - Flask routes for list/add movie, details with ratings/comments, average rating.
  - Jinja templates and basic CSS rendered correctly.
- Local dev flow
  - Virtual environment and dependency install succeeded.
  - One-command start script reliably brought up the emulator (readiness via `curl -k`) and then the app.
  - App served homepage at <http://localhost:3000> consistently.
- Dev ergonomics
  - `.env.example` and `python-dotenv` made config straightforward.
  - VS Code tasks for run/lint/test were convenient.
  - Ruff linting and pytest test skeletons in place (unit tests stub DB to avoid emulator dependency).

## What failed or caused friction

- Git repo initialization
  - Initially created a repo at the wrong parent directory; fixed by removing parent `.git` and keeping repo scoped to `vibemovie/`.
- TLS and cert trust (emulator)
  - Self-signed certs caused HTTPS verification failures.
  - Mitigation used for local dev: `PYTHONHTTPSVERIFY=0` in `start-app.ps1` and `curl -k` for readiness. This is noisy (warnings) and not ideal for a live demo.
- SDK code edits churn
  - Attempts to weave TLS logic into `cosmos_client.py` introduced syntax and type issues midstream.
  - Resolution: keep TLS handling in the script/env; keep the Cosmos client simple.
- Emulator authorization (blocking)
  - Observed `(Unauthorized) The input authorization token can't serve the request` despite using the classic emulator master key.
  - Likely causes: default key mismatch on the Linux/vNext emulator or protocol/endpoint mismatch.
  - Potential mitigations (not yet validated in this repo):
    - Start emulator with an explicit key file: mount a file and set `KEY_FILE`/`--key-file` so the key is deterministic; set `COSMOS_KEY` to match.
    - Confirm protocol is `https` on container (`--protocol https`) and the app uses the same endpoint.
    - As a fallback for demo, switch to cloud Cosmos DB with a read/write key stored in local env (requires reliable network and caution with secrets).
- Time costs and fragility for a live talk
  - First-time Docker image pull and emulator boot can eat minutes.
  - Cert trust and HTTP(S) mode nuances are easy to derail a 20‑minute slot.

## Known good sequence (repeatable)

- Pre-reqs: Docker Desktop running; Python venv activated; deps installed.
- Start using the script (always):
  - `./scripts/start-app.ps1` → starts emulator, waits for readiness (HTTPS), runs Flask on port 3000.
- Navigate: <http://localhost:3000> → homepage renders.
- UI flows: Adding movies/ratings/comments works with the DB layer present; however, with the current emulator auth issue, DB operations may fail until the key/protocol mismatch is resolved.

## Representative errors (for reference)

- TLS trust (expected during readiness): `InsecureRequestWarning: Unverified HTTPS request ...`.
- Cosmos client creation (blocking):
  - `Failed to create CosmosClient ... (Unauthorized) The input authorization token can't serve the request ... Server used the following payload to sign: 'get thu, 28 aug 2025 ...'`

## Why this is too complex for a 20‑minute demo

- External dependency (Docker + emulator) introduces variable startup time and moving parts (ports, TLS, keys, protocols).
- Certificate trust and protocol toggles are environment‑sensitive and brittle on stage.
- A single misconfigured key or protocol yields opaque `Unauthorized` errors that are hard to debug live.

## Recommendations to simplify

- Option A: Decouple storage for the live demo
  - Replace Cosmos calls with an in‑memory store (feature flag), so the core Flask UI flow is guaranteed.
  - Keep Cosmos integration as an “after” slide or short pre‑recorded clip.
- Option B: Pre-bake the environment
  - Pre‑pull emulator image; run it ahead of time; validate HTTPS and key.
  - Use `--protocol https` and `--key-file` to pin a known key; set `COSMOS_KEY` accordingly.
  - Import the emulator cert into Trusted Root to remove warnings; avoid `PYTHONHTTPSVERIFY=0` on stage.
- Option C: Dev container
  - Ship a devcontainer that runs the emulator as a service with a fixed key and exposes port 8081; the demo becomes “open folder → run task → open browser”.
- Option D: Cloud fallback (only if network is reliable)
  - Provision a Cosmos DB NoSQL account in Azure; inject endpoint/key via `.env` (not committed); demonstrate the same app against the cloud.

## Concrete action items

- Update `start-cosmos-emulator.ps1` (optional): pass `--protocol https` and mount a `--key-file` with a known key.
- Add a short “offline mode” code path (in‑memory) controlled by `USE_INMEMORY=1` for talk day.
- Add a pre‑talk checklist: Docker up, emulator running, cert trusted, `GET /` returns 200.
- Keep a rescue slide with the exact troubleshooting tips (TLS trust and KEY_FILE override) and a QR link to the repo.

## Bottom line

The current end‑to‑end is functional but fragile. For a 20‑minute conference slot, either run an offline mode for the live portion or pre‑bake the emulator with a fixed key and trusted certs so the on‑stage workflow reduces to a single start script and a browser refresh.
