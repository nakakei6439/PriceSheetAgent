# AGENTS.md

This repository follows the [agents.md](https://agents.md/) convention. Any AI coding agent (Codex CLI, Claude Code, Cursor, etc.) operating in this repo should read **`docs/HANDOFF.md` first** — it is the single source of truth for project context, current status, architecture, environment variables, run commands, the remaining roadmap, known pitfalls, and a handoff template.

## Quick context

- **Project**: PriceSheetAgent — Azure agent that extracts product codes and prices from multi-format / Japanese-English price notice and price sheet PDFs, including degraded scans (Excel → PDF → printed → scanned → PDF).
- **Submission**: Microsoft Agent Hackathon 2026 (individual track), deadline **2026-06-01 23:59 JST**.
- **Stack**: Python 3.12 + FastAPI (backend) · Next.js 16 + Tailwind v4 (frontend) · Azure Document Intelligence + Microsoft Foundry / Azure OpenAI GPT-4o.
- **Current state**: Day 1〜2 complete — Azure resources provisioned (portal manual path), Python venv ready, all SDK connectivity verified, `agent.run()` end-to-end working on clean PDFs. About to start Day 3〜4 (backend tuning + degraded PDF tests).

## Before you start

1. Read `docs/HANDOFF.md` end-to-end.
2. Read `frontend/AGENTS.md` only if you will edit frontend code — it warns that **Next.js 16 has breaking changes**; consult `frontend/node_modules/next/dist/docs/01-app/` for current APIs.
3. Confirm the user's intended task. If unclear, ask before writing code.

## Working rules

- Preserve the `TraceStep` schema in `backend/app/models.py` — the frontend (`frontend/app/components/AgentTrace.tsx`) depends on it.
- Do not bump pinned Azure SDK versions (`azure-ai-documentintelligence`, `azure-ai-projects`) without a clear reason — the hackathon timeline is tight.
- Free-tier first: prefer Document Intelligence F0 over GPT-4o where viable to conserve credits.
- Commit messages: imperative mood, prefix with type (`feat:`, `fix:`, `docs:`, `chore:`).
- **Update `docs/HANDOFF.md` whenever you change architecture, dependencies, or task status**, then commit the doc update in the same change.

## Verification

- `pytest backend/tests/ -v` must stay green.
- `cd frontend && npx tsc --noEmit` must stay clean.
- After Azure deploy, `curl $SERVICE_BACKEND_URI/health` should return `{"status":"ok"}`.

## Handoff prompt for new sessions

```
このリポジトリは Microsoft Agent Hackathon 2026 への応募作品 MAHTED です。
まず docs/HANDOFF.md を読んでから作業を始めてください。
次のタスク: [ここに具体を書く]
```
