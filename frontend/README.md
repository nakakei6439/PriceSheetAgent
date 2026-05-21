# PriceSheetAgent Frontend

Next.js 16 + Tailwind v4 frontend for PriceSheetAgent.

The UI lets users upload a PDF or image, review the selected file, send it to the FastAPI backend, inspect extracted product code / price rows, and export the result as JSON or CSV.

## Local Run

```bash
npm install
cp .env.local.example .env.local
npm run dev
```

Open http://localhost:3000.

`NEXT_PUBLIC_API_URL` should point to the backend, usually:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Checks

```bash
npx tsc --noEmit
npm run build
```
