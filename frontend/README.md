# Frontend (Next.js 14)

This UI is designed for non-technical users and connects directly to the FastAPI backend.

## Runtime Modes
- `api`: full workflow (ingest, inspect, artifacts, query, collections/export)
- `parser`: ingest + book/section/chunk inspection only

When parser mode is enabled, the UI hides or disables unsupported actions and shows:
`Parser mode only supports ingestion/parsing/chunk inspection.`

If backend API-key protection is enabled (`APP_API_KEY`), set the same key in **Settings**.

## Environment
Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

## Local Development
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Tests
```bash
cd frontend
npm test
```

## Deploy to Vercel
- Connect the same GitHub repo in Vercel.
- Set **Root Directory** to `frontend`.
- Build command: `npm run build`
- Output: `.next`
- Add env var:
  - `NEXT_PUBLIC_API_BASE_URL=https://<render-backend-domain>`

## Lighthouse Deployment CI
- GitHub Actions workflow: `/.github/workflows/lighthouse-deployment.yml`
- Set repository variable or secret:
  - `LIGHTHOUSE_DEPLOYMENT_URL=https://<your-vercel-domain>`
- The workflow runs Lighthouse against deployed routes and enforces:
  - Performance >= 80
  - Accessibility >= 90
  - Best Practices >= 90
  - SEO >= 90
