# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Read this first

**`docs/HANDOFF.md` is the single source of truth** for project status, environment variables, Azure resource layout, deploy procedures, known pitfalls, and remaining roadmap. Read it before any non-trivial work. `AGENTS.md` is a short pointer to the same file.

This is the Microsoft Agent Hackathon 2026 submission (deadline **2026-06-01 23:59 JST**). Production is already deployed and public; most remaining work is documentation/submission, not code.

## What this app is

Extracts product_code / description / quantity / unit_price / amount from degraded scanned price-sheet PDFs (Excel → PDF → printed → scanned → PDF). The point of the app — and the demo narrative — is the **self-verification loop**: Document Intelligence's `confidence` is unreliable (DI reports 0.99 while misreading digits), so the agent uses arithmetic checks (`qty × unit ≈ amount`, `Σitems ≈ total`) to catch its own errors and retry with GPT-4o Vision before honestly emitting residual mismatches as `warnings`.

## Architecture

```
Next.js 16 (Vercel)  ──POST /extract──▶  FastAPI (Azure Container Apps)
                                              │
                                              ▼  agent.run(pdf_bytes)
   ┌─────────────────────────────────────────────────────────────────┐
   │ 1) document_intelligence.extract  (prebuilt-invoice)            │
   │ 2) if avg_conf < CONFIDENCE_FLOOR(0.6) → gpt4o_vision.extract   │
   │ 3) verify_math (qty×unit≈amount, Σ≈total, tax-aware)            │
   │ 4) on mismatch → gpt4o_vision with hint, max 1 retry            │
   └─────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
                        ExtractionResult(meta, line_items, trace, warnings)
```

Key files:
- `backend/app/agent.py` — the self-verification loop. `CONFIDENCE_FLOOR=0.6`, `MAX_VISION_CALLS=1`. Builds the `trace` step-by-step (must remain in this shape — frontend depends on it).
- `backend/app/models.py` — `LineItem` / `InvoiceMeta` / `TraceStep` / `ExtractionResult`. **`TraceStep.status` (`ok`/`warn`/`info`) is a contract with `frontend/app/components/AgentTrace.tsx`**. Do not break it.
- `backend/app/tools/{document_intelligence,gpt4o_vision,verify_math}.py` — the three "tools" the agent orchestrates.
- `backend/app/main.py` — FastAPI: `/health`, `/extract` (multipart). Maps `AzureError`/`OpenAIError` to 502 and enforces `MAX_UPLOAD_BYTES`.
- `frontend/app/components/{Uploader,ResultTable,AgentTrace}.tsx` — single-page app at `frontend/app/page.tsx`.

The Azure OpenAI endpoint env vars point to the **child resource auto-created when you deployed the model** (e.g. `nakak-mpeo8drm-eastus2`), NOT the Foundry parent (`mahted-foundry`). See HANDOFF §4.

## Commands

### Backend (Python 3.12, FastAPI)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in Azure keys; see HANDOFF §4
uvicorn app.main:app --reload          # http://localhost:8000

.venv/bin/pytest tests/ -v             # 10 tests must pass
.venv/bin/pytest tests/test_verify_math.py::test_name -v   # run a single test
```

Local agent smoke test against a sample PDF (requires real Azure creds):
```bash
python -c "from app.agent import run; import json; \
  r=run(open('../samples/ja_invoice_a_degraded_heavy.pdf','rb').read()); \
  print(json.dumps([s.model_dump() for s in r.trace], ensure_ascii=False, indent=2))"
```

`pdf2image` needs poppler: `brew install poppler` on macOS (the Dockerfile already installs `poppler-utils`).

### Frontend (Next.js 16 + React 19 + Tailwind v4)

```bash
cd frontend
npm install
cp .env.local.example .env.local       # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev                            # http://localhost:3000

npx tsc --noEmit                       # must stay clean
npm run build                          # = `next build --webpack` (see below)
```

**Build is intentionally pinned to webpack, not Turbopack.** Turbopack fails on internal port-bind in restricted sandboxes. Do not switch back without testing in those environments.

**Next.js 16 has breaking changes vs. your training data.** Before writing frontend code, read the relevant chapter under `frontend/node_modules/next/dist/docs/01-app/`. See `frontend/AGENTS.md`.

### Deploy

- **Backend**: push to `main` → `.github/workflows/build-backend.yml` builds and pushes to ACR → then `az containerapp update -n mahted-backend -g rg-mahted-dev --image ca634368e688acr.azurecr.io/mahted-backend:latest`. `az acr build` is **blocked on this subscription** (`TasksOperationsNotAllowed`), so GitHub Actions is the only build path. Container App is `min-replicas=0` (scale-to-zero) — cold start 5–10s; warm it with `/health` before demos.
- **Frontend**: `cd frontend && vercel deploy --prod --yes --scope nakakei6439s-projects`. Env vars are already persisted in the Vercel project.
- After an env change creates a second active revision, deactivate the old one (`az containerapp revision deactivate ...`) — single-revision mode is in effect.

Production URLs are in HANDOFF §1.

## Working rules (project-specific)

- **Do not bump** the pinned Azure SDK versions in `backend/requirements.txt` (especially `azure-ai-documentintelligence==1.0.0`, `azure-ai-projects==1.0.0b6`) without a clear reason. The hackathon timeline is tight.
- **Preserve the `TraceStep` schema.** The frontend reads `tool` / `reason` / `duration_ms` / `confidence` / `note` / `status` directly. If you add a field, make it optional.
- **Prefer Document Intelligence F0 over GPT-4o where viable** — DI is free, GPT-4o is metered. The fallback at `CONFIDENCE_FLOOR=0.6` rarely fires in practice; the real "agentic" work happens in the `verify_math` loop. Don't redesign the loop to lean on `confidence`.
- The product code is **free-form** — no industry master list. Normalization is whitespace removal only (`_normalize_product_code` in `agent.py`).
- Update `docs/HANDOFF.md` alongside any architecture/dependency/status change and commit the doc update in the same change.
- Commit messages: imperative, prefixed (`feat:`, `fix:`, `docs:`, `chore:`).
