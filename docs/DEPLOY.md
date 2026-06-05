# Deployment checklist

## Render (API)

1. Push repo to GitHub.
2. [Render Dashboard](https://dashboard.render.com) → New → Blueprint → select `render.yaml`.
3. Add secret `ANTHROPIC_API_KEY`.
4. Set `CORS_ORIGINS` to your Vercel frontend URL (comma-separated).
5. Note service URL, e.g. `https://fair-split-api.onrender.com`.
6. Verify: `curl https://YOUR_API/health`

## Vercel (frontend)

```bash
cd frontend
npm i -g vercel   # if needed
vercel --prod
```

Environment variable:

- `VITE_API_URL` = Render API URL (no trailing slash)

Update root `README.md` live URL table.

## Smoke test

```bash
curl -s -X POST https://YOUR_API/split \
  -H 'Content-Type: application/json' \
  -d '{"receipt_base64":"","description":"fixture:R2"}' | jq .reconciliation
```

Expected: `"matches_bill": true`
