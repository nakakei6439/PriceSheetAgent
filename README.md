# MAHTED — Multi-format / multilingual invoice extraction Agent

Microsoft Agent Hackathon 2026 応募作品。

Excel → PDF → 紙印刷 → スキャン → PDF と"参照リレー"を経て劣化した請求書から、商品コード・品名・数量・単価・金額を Azure エージェントが自己検証ループで抽出する Web アプリ。

## アーキテクチャ

```
[Next.js (Vercel)]
        │ POST /extract (multipart PDF)
        ▼
[FastAPI on Azure Container Apps]
        │
        ▼
[AI Foundry Agent Service]
   ├── extract_with_document_intelligence  (Prebuilt-Invoice)
   ├── extract_with_gpt4o_vision           (Azure OpenAI GPT-4o)
   └── verify_math                         (Pure Python 検算)
        │
        ▼ JSON (lineItems, trace, confidence)
[Next.js: 結果テーブル + AgentTrace + CSV)
```

## ディレクトリ

| パス | 内容 |
|---|---|
| `frontend/` | Next.js App Router (TypeScript + Tailwind)、Vercel デプロイ |
| `backend/` | FastAPI + Python、Azure Container Apps デプロイ |
| `infra/` | `azd up` で一発デプロイする Bicep テンプレート |
| `samples/` | テスト用 PDF (日/英 × clean/degraded) |
| `docs/` | アーキテクチャ図、Zenn 記事の下書き |

## セットアップ

### 1. Azure リソース

```bash
azd auth login
azd up    # infra/main.bicep でリソース一括作成
```

### 2. バックエンド (ローカル)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # azd up の出力値を貼る
uvicorn app.main:app --reload
```

### 3. フロントエンド (ローカル)

```bash
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

## 提出物

- 公開URL: TBD (Vercel)
- GitHub: TBD
- Zenn 記事: `docs/zenn_article.md`
- デモ動画: TBD
