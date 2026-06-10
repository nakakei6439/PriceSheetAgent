# PriceSheetAgent — Multi-format price sheet extraction Agent

Microsoft Agent Hackathon 2026 応募作品。

🎬 **デモ動画: https://youtu.be/VzxOywOETuw**
> ⚠️ ハッカソン終了に伴い、ライブデモ（`https://price-sheet-agent.vercel.app`）と Azure バックエンドは **2026-06-11 をもって公開終了**しました（課金停止のため）。動作はデモ動画でご確認ください。ローカル実行は [`docs/HANDOFF.md`](docs/HANDOFF.md) §5 を参照。

Excel → PDF → 紙印刷 → スキャン → PDF と"参照リレー"を経て劣化した価格通知書・仕切り価格通知書・価格表 PDF から、商品コード・品名・数量・単価・金額を Azure エージェントが自己検証ループで抽出する Web アプリ。

## なぜ「自己検証」なのか（本作の核）

OCR/AI の `confidence` は当てになりません。**Azure Document Intelligence は劣化スキャンでも `confidence 99%` を返しながら単価の桁を誤読します**。そこで本作は confidence ではなく **検算（数量×単価＝金額、明細合計≒文書合計）でエージェントに自分を疑わせ**、矛盾を検知したら GPT-4o Vision にヒント付きで再抽出させ、**直せない分は warnings として正直に申告**します。

実行ログ（trace）に「① 抽出 → ② 検算で不整合検知 → ③ ↻ 自己修正で再抽出 → ④ 残差を提示」という推論チェーンが可視化されるのが見どころです。

## アーキテクチャ

```
[Next.js 16 (Vercel)]
        │ POST /extract (multipart PDF)
        ▼
[FastAPI (Azure Container Apps)]
        │ run(pdf_bytes)
[agent.py 自己検証ループ]
   1) document_intelligence (prebuilt-invoice) で抽出
   2) verify_math: 数量×単価≒金額 / 明細合計≒文書合計 を検算
        └ 不整合を検知したら ▼
   3) gpt4o_vision に「どこが合わない」ヒント付きで再抽出 (Azure OpenAI GPT-4o)
   4) verify_math 再検算 → 残差は warnings に
        │
        ▼ ExtractionResult (meta, line_items, trace, warnings)
[Next.js: ファイルレビュー + 結果テーブル + AgentTrace + JSON/CSV 出力]
```

## ディレクトリ

| パス | 内容 |
|---|---|
| `frontend/` | Next.js App Router (TypeScript + Tailwind)、Vercel デプロイ |
| `backend/` | FastAPI + Python、Azure Container Apps デプロイ |
| `infra/` | `azd up` で一発デプロイする Bicep テンプレート |
| `samples/` | テスト用価格表 PDF (日/英 × clean/degraded) |
| `docs/` | アーキテクチャ図、Zenn 記事の下書き |

## セットアップ

### 1. Azure リソース (採用パス: ポータル手動)

詳細手順は [`docs/SETUP_AZURE.md`](docs/SETUP_AZURE.md) を参照。要点:
1. Azure ポータルで **Microsoft Foundry** リソース作成 (East US, `rg-mahted-dev`)
2. Foundry ポータル ([ai.azure.com](https://ai.azure.com)) で **GPT-4o** をデプロイ
3. Azure ポータルで **Document Intelligence (F0)** を別途作成 (同リソースグループ)

`azd up` を希望する場合は SETUP_AZURE.md 付録 A を参照 (Bicep の書き換え必要)。

### 2. バックエンド (ローカル)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Foundry / Document Intelligence のキーを貼る
uvicorn app.main:app --reload
```

### 3. フロントエンド (ローカル)

```bash
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

## デプロイ

- フロント: Vercel（本番 https://price-sheet-agent.vercel.app ※2026-06-11 公開終了）
- バックエンド: Azure Container Apps（`rg-mahted-dev` / `mahted-backend`、scale-to-zero ※2026-06-11 リソース削除）
- イメージビルド: GitHub Actions → ACR（`az acr build` が当サブスクで禁止のため。`.github/workflows/build-backend.yml`）
- 詳細・再デプロイ手順は [`docs/HANDOFF.md`](docs/HANDOFF.md) §1 を参照

## 提出物

- 公開URL: https://price-sheet-agent.vercel.app （※2026-06-11 公開終了）
- GitHub: https://github.com/nakakei6439/PriceSheetAgent
- Zenn 記事: `docs/zenn_article.md`
- デモ動画: https://youtu.be/VzxOywOETuw
