# AGENTS.md

This repository follows the [agents.md](https://agents.md/) convention. Any AI coding agent (Codex CLI, Claude Code, Cursor, etc.) operating in this repo should read **`docs/HANDOFF.md` first** — it is the single source of truth for project context, current status, architecture, environment variables, run commands, the remaining roadmap, known pitfalls, and a handoff template.

## Quick context

- **Project**: PriceSheetAgent — Azure agent that extracts product codes and prices from multi-format / Japanese-English price notice and price sheet PDFs, including degraded scans (Excel → PDF → printed → scanned → PDF).
- **Submission**: Microsoft Agent Hackathon 2026 (individual track), deadline **2026-06-01 23:59 JST**.
- **Stack**: Python 3.12 + FastAPI (backend) · Next.js 16 + Tailwind v4 (frontend) · Azure Document Intelligence + Microsoft Foundry / Azure OpenAI GPT-4o.
- **Live**: frontend https://price-sheet-agent.vercel.app · backend https://mahted-backend.ashycliff-fac33dac.eastus.azurecontainerapps.io
- **Current state (2026-05-21)**: 本番デプロイ完了・公開稼働中。コアパイプ + 自己検証ループ + その trace 可視化まで実装済み、本番URLで実ブラウザ E2E 確認済み。提出物は README/Zenn記事ドラフト/GitHub public/デモ動画URLまで反映済み。**残り: Zenn公開・最終提出**。詳細は `docs/HANDOFF.md` §1。

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

- `backend/.venv/bin/pytest backend/tests/ -v` must stay green（現状10件 PASS）。
- `cd frontend && npx tsc --noEmit` must stay clean。本番ビルドは `npm run build`（= `next build --webpack`。Turbopack は制限環境で落ちることがあるため webpack 固定）。
- 本番ヘルス: `curl https://mahted-backend.ashycliff-fac33dac.eastus.azurecontainerapps.io/health` → `{"status":"ok"}`（scale-to-zero のため初回はコールドスタート 5〜10秒）。

## Handoff prompt for new sessions

```
このリポジトリは Microsoft Agent Hackathon 2026 への応募作品 PriceSheetAgent です。
まず docs/HANDOFF.md を読んでから作業を始めてください。
本番デプロイ済み（公開URLは HANDOFF §1）。デモ動画URL反映済み。残タスクはZenn公開と最終提出（〜2026-06-01）。
次のタスク: [ここに具体を書く]
```
