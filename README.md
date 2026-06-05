# Fair Split

Split a restaurant bill from a **receipt photo** + **plain-English** description of who had what. Returns per-person totals (tax, service, discount), reconciliation, and settle-up.

**GitHub:** https://github.com/Shirapti-nath/fair-split

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Shirapti-nath/fair-split)

## Live demo

After deploying (one-click button above), open your Render URL — e.g. `https://fair-split.onrender.com`.

Try the built-in sample bills: click **R1**–**R4**, then **Split bill** (no receipt upload or API key needed for fixtures).

## API contract

**POST** `/split` — `Content-Type: application/json`

```json
{
  "receipt_base64": "<base64 image, no data-URI prefix>",
  "description": "Three of us — Ravi, Neha, Sameer. ..."
}
```

Response: `per_person`, `grand_total`, `reconciliation`, `paid_by`, `settle_up`, `assumptions`, `flags`.

### Offline fixtures (no API key)

```json
{ "receipt_base64": "", "description": "fixture:R1" }
```

Use `fixture:R1` through `fixture:R4` for the assignment sample bills.

## Local development

```bash
cd fair-split
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add ANTHROPIC_API_KEY

uvicorn api.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev   # proxies /split to :8000
```

### Tests

```bash
pytest -v
```

### Sample receipt images

```bash
pip install pillow
python scripts/generate_sample_receipts.py   # writes samples/R1.png … R4.png
```

## Deploy

### API (Render)

1. Connect repo; use `render.yaml` or Docker `Dockerfile`.
2. Set `ANTHROPIC_API_KEY`, `CORS_ORIGINS` to your Vercel URL.
3. Health check: `GET /health`.

### Frontend (Vercel)

1. Root directory: `frontend`
2. Env: `VITE_API_URL=https://your-api.onrender.com`
3. Build: `npm run build`

## Workspace note

If Cursor opened `/Users/shiraptinath/Desktop/FloSpace` as a **file** (ENOTDIR), sync this project:

```bash
bash scripts/sync_to_desktop.sh
```

Then reopen the **FloSpace folder** in Cursor.

## Docs

- [docs/PROMPT_LOG.md](docs/PROMPT_LOG.md)
- [docs/EDGE_CASES.md](docs/EDGE_CASES.md)
- [docs/AI_FAILURES.md](docs/AI_FAILURES.md)

## Architecture

Claude extracts structured receipt + intent; **all arithmetic is Python** — see PROMPT_LOG.
