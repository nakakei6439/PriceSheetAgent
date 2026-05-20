# HANDOFF.md — マルチエージェント引き継ぎドキュメント

> **このファイルの目的**
> Claude Code の利用上限到達・別マシンへの移動・**OpenAI Codex (codex-cli / ChatGPT Codex) 等の別エージェントで開発を継続**するときに、このファイル1枚を読めば即座に開発を再開できるようにするための情報ハブ。
> 何かを変更・進捗を出したら **このファイルを更新してから commit する** ルール。

---

## 0. プロジェクト一行サマリ

**MAHTED** — Excel→PDF→紙印刷→スキャン と"参照リレー"を経て劣化した請求書 (日英混在・多フォーマット) から、商品コード/品名/数量/単価/金額を **Azureエージェントが自己検証ループで抽出する Web アプリ**。Microsoft Agent Hackathon 2026 (個人部門) 応募作品。

### ハッカソン要件
- **応募締切**: 2026-06-01 (月) 23:59 ← **クリティカル**
- テーマ: "業務改革につながるAgentic AIを作ろう"
- 必須技術: Azure / Copilot Studio + Microsoft AI技術
- 提出物: 成果物公開URL、Zenn記事、GitHub URL (任意)
- 賞: 個人部門 最優秀50万 / 優秀30万 / 特別20万 / 奨励10万×2
- 公式: https://zenn.dev/hackathons/microsoft-agent-hackathon-2026

### スケジュール (全日程)
| 日付 | イベント |
|---|---|
| 2026-04-07 (火) | LP公開・申込開始 |
| 2026-05-14 (木) 12:30〜14:30 | エントリーセッション (**企業部門のみ・任意**) |
| **2026-06-01 (月) 23:59** | **申込・提出締切** |
| 2026-06-02〜09 | 審査期間 |
| 2026-06-10 (水) | 最終審査進出通知 |
| 2026-06-11〜17 | ピッチ準備期間 (通過したチームのみ) |
| 2026-06-18 (木) | 最終審査会・表彰式 |

### 参加者特典 (重要)
- **🎯 特設 Discord サーバー** — Microsoft エンジニアが直接サポート。Azure 設定で詰まったらここで聞ける (最大の特典)
- 事前学習リソース:
  - Microsoft Learn の AI エージェント開発パス
  - YouTube トレーニング動画 (初学者向け・エージェント開発向け)
  - Copilot Studio 参考コンテンツ
- ※ ハッカソン専用の Azure クレジット (Azure Pass等) は **提供されていません** — 通常の無料アカウントを各自で作成 (→ [docs/SETUP_AZURE.md](./SETUP_AZURE.md))

---

## 1. 現状ステータス (Last updated: 2026-05-21, commit `a88a8e6` 以降)

### 完了 ✅
| 項目 | 状態 | 参照 |
|---|---|---|
| ディレクトリスケルトン | ✅ | `frontend/`, `backend/`, `infra/`, `samples/`, `docs/` |
| FastAPI バックエンド雛形 | ✅ | `backend/app/` |
| 自己検証ループの自前実装 | ✅ | `backend/app/agent.py` |
| Document Intelligence ラッパー | ✅ | `backend/app/tools/document_intelligence.py` |
| GPT-4o Vision ラッパー | ✅ | `backend/app/tools/gpt4o_vision.py` |
| 数値検算ロジック + テスト | ✅ | `backend/app/tools/verify_math.py`, `backend/tests/test_verify_math.py` |
| Next.js 16 + Tailwind v4 フロント | ✅ | `frontend/app/` (`tsc --noEmit` パス) |
| アップロードUI / 結果テーブル / エージェントログUI | ✅ | `frontend/app/components/` |
| Azure Bicep (azd up 一発デプロイ) | ✅ | `infra/main.bicep`, `infra/main-resources.bicep` |
| 初回コミット | ✅ | local commit `dbdb718` (リモート未push) |

### 未完了 / TODO
- [ ] **ユーザ作業**: Azure無料アカウント作成 → `az login` / `azd auth login` ([詳細手順は SETUP_AZURE.md](./SETUP_AZURE.md))
- [ ] **ユーザ作業**: Azure OpenAI 利用申請 ([SETUP_AZURE.md セクション7](./SETUP_AZURE.md#7--azure-openai-利用申請-重要最優先))
- [ ] **ユーザ作業**: サンプル劣化請求書PDF (日英×2〜3 フォーマット) 5〜10枚を `samples/` に配置
- [ ] **ユーザ作業**: ハッカソン特設 Discord に参加 (公式ページから招待リンク)
- [ ] GitHubリモートリポジトリ作成 & `git push`
- [ ] `azd up` 実行 → 出力値を `backend/.env` に貼り付け
- [ ] バックエンドのローカル動作確認 (`uvicorn`)
- [ ] フロントのローカル動作確認 (`npm run dev`)
- [ ] Day 5〜6: AI Foundry Agent Service への置き換え (任意・自前ループでも提出可)
- [ ] Day 7〜8: Vercel フロントデプロイ
- [ ] Day 9: 本番 E2E
- [ ] Day 10: デモ動画 + Zenn記事執筆
- [ ] Day 11: 提出

---

## 2. アーキテクチャ

```
[ブラウザ]
   │ multipart upload (PDF/PNG/JPG)
   ▼
[Next.js 16 (Vercel Hobby)]   ← frontend/
   │ POST /extract → NEXT_PUBLIC_API_URL
   ▼
[FastAPI on Azure Container Apps]   ← backend/
   │
   ▼ run(pdf_bytes)
┌──────────────── agent.py 自己検証ループ ────────────────┐
│ 1) Document Intelligence (prebuilt-invoice)               │
│       │ avg_conf < 0.6 or items==0                        │
│       ▼                                                   │
│ 2) GPT-4o Vision (pdf2image + JSON Schema 構造化出力)     │
│       │ merge                                             │
│       ▼                                                   │
│ 3) verify_math (qty×unit≈amount, sum≈total)               │
│       │ 不一致あれば                                      │
│       ▼                                                   │
│ 4) GPT-4o Vision にヒント付き再抽出 (最大1回)             │
└───────────────────────────────────────────────────────────┘
   │
   ▼ ExtractionResult(meta, line_items, trace, warnings)
[Next.js: AgentTrace + ResultTable + CSVダウンロード]
```

**設計意図**:
- DI を必ず最初に呼ぶ (Free F0 で無料 + 構造化に強い)
- GPT-4o Vision はフォールバック (画質劣化に強いが従量課金)
- `verify_math` で**自己検証** → 自律的再試行 → ハッカソンの"Agentic"要件を満たす
- すべての tool 呼び出しは `TraceStep` として記録 → フロントで可視化 → **デモ映え**

---

## 3. ディレクトリと主要ファイル

```
MAHTED/
├── README.md
├── azure.yaml                 # azd 設定 (services.backend → ./backend)
├── .gitignore
│
├── backend/                   # Python 3.12 + FastAPI
│   ├── app/
│   │   ├── main.py            # FastAPI app + /extract /health
│   │   ├── agent.py           # 自己検証ループ (Foundry Agent Service 置換可能設計)
│   │   ├── settings.py        # pydantic-settings, .env 読み込み
│   │   ├── models.py          # LineItem / InvoiceMeta / TraceStep / ExtractionResult
│   │   └── tools/
│   │       ├── document_intelligence.py
│   │       ├── gpt4o_vision.py
│   │       └── verify_math.py
│   ├── tests/
│   │   └── test_verify_math.py
│   ├── requirements.txt
│   ├── Dockerfile             # poppler-utils 同梱 (pdf2image 用)
│   └── .env.example
│
├── frontend/                  # Next.js 16.2.6 + React 19 + Tailwind v4
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── types.ts           # ExtractionResult/LineItem の型
│   │   └── components/
│   │       ├── Uploader.tsx   # "use client"; PDF→FastAPI POST
│   │       ├── ResultTable.tsx
│   │       └── AgentTrace.tsx # tool 呼出ログタイムライン (デモ映え)
│   ├── package.json
│   ├── tsconfig.json
│   ├── AGENTS.md              # ⚠ Next.js 16 は破壊的変更あり。実装前にこれを参照
│   └── .env.local.example
│
├── infra/
│   ├── main.bicep             # subscription scope, RG作成
│   ├── main-resources.bicep   # DI / OpenAI / Storage / Log / CAE / ACR / Container App
│   └── main.parameters.json
│
├── samples/                   # ⚠ 未配置。ユーザ作業で日英×2〜3形式の劣化PDFを用意
│
└── docs/
    ├── HANDOFF.md             # ← 本ファイル
    └── (future: zenn_article.md, architecture.png)
```

### ファイル別 "次に触る人へのメモ"

| ファイル | 引き継ぎ時の注意 |
|---|---|
| `backend/app/agent.py` | 現在は **自前のループ**。`CONFIDENCE_FLOOR=0.6` がトリガー閾値。Foundry Agent Service に置き換える場合は `azure-ai-projects` の `AgentsClient.create_agent` + function tool 定義に書き換える。trace 形式は維持すること (フロントが依存) |
| `backend/app/tools/document_intelligence.py` | `azure-ai-documentintelligence==1.0.0` の API を使用。`AnalyzeDocumentRequest(bytes_source=...)` がポイント。古い `azure-ai-formrecognizer` ではないので注意 |
| `backend/app/tools/gpt4o_vision.py` | `pdf2image` は **poppler-utils** が必要 (Dockerfile で apt install 済)。ローカル macOS では `brew install poppler` |
| `frontend/app/components/Uploader.tsx` | API URL は `process.env.NEXT_PUBLIC_API_URL` 経由。本番は Vercel の env で設定 |
| `frontend/AGENTS.md` | **Next.js 16 は破壊的変更がある**旨の警告。新規 Next.js コードを書く前に `node_modules/next/dist/docs/01-app/` を読むこと |
| `infra/main-resources.bicep` | GPT-4o のモデルバージョンは `2024-11-20`。`GlobalStandard` SKU + capacity 30。リージョン制約あり (`openAiLocation=eastus` デフォルト) |

---

## 4. 環境変数

### backend/.env (`backend/.env.example` をコピー)

| 変数 | 取得方法 | 用途 |
|---|---|---|
| `DOCUMENT_INTELLIGENCE_ENDPOINT` | `azd env get-values` or Azureポータル → DI リソース → Keys and Endpoint | DI API ベース URL |
| `DOCUMENT_INTELLIGENCE_KEY` | 同上 (Key1) | DI 認証 |
| `AZURE_OPENAI_ENDPOINT` | `azd env get-values` or Azureポータル → OpenAI リソース → Keys and Endpoint | OpenAI API ベース URL |
| `AZURE_OPENAI_API_KEY` | 同上 (Key1) | OpenAI 認証 |
| `AZURE_OPENAI_API_VERSION` | デフォルト `2024-10-21` でOK | API バージョン |
| `AZURE_OPENAI_GPT4O_DEPLOYMENT` | デフォルト `gpt-4o` (Bicep で作成済) | デプロイメント名 |
| `AI_FOUNDRY_PROJECT_ENDPOINT` | Day 5〜6 で Foundry 使う場合のみ | Agent Service 用 |
| `AZURE_STORAGE_CONNECTION_STRING` | 任意 (PDF永続化する場合のみ) | Blob 接続 |
| `CORS_ORIGINS` | ローカルは `http://localhost:3000`、本番は Vercel URL | CORS 許可元 |

### frontend/.env.local

| 変数 | 値 |
|---|---|
| `NEXT_PUBLIC_API_URL` | ローカル: `http://localhost:8000` / 本番: `azd up` で出力された Container App URL |

---

## 5. ローカル実行手順

### 前提
- macOS 想定 (ユーザ環境)
- Node.js 25 + npm 11 (確認済)
- Python 3.12+
- `brew install poppler` (pdf2image 用)
- (任意) `brew install azure-cli azd`

### バックエンド
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 値を埋める
uvicorn app.main:app --reload
# → http://localhost:8000/health で {"status":"ok"}
```

### フロントエンド (別ターミナル)
```bash
cd frontend
npm install            # 初回のみ
cp .env.local.example .env.local
npm run dev
# → http://localhost:3000
```

### テスト
```bash
cd backend
pytest tests/ -v
# verify_math のユニットテストが3件パスする想定
```

### 単発ツール検証 (サンプルPDF配置後)
```bash
cd backend && source .venv/bin/activate
python -c "from app.tools import document_intelligence as di; \
  meta, items, trace = di.extract(open('../samples/ja_invoice_degraded.pdf','rb').read()); \
  print(meta, len(items), trace)"
```

---

## 6. Azure デプロイ手順 (azd up 一発)

> ⚠ **Azure をこれから初めて使う場合は、まず [docs/SETUP_AZURE.md](./SETUP_AZURE.md) を完了させてからこのセクションに戻ってきてください。** アカウント作成・CLI セットアップ・OpenAI 利用申請・予算アラートまでをカバーしています。

```bash
# 0. 前提: Azure無料アカウント作成済 + az/azd CLI ログイン済 (詳細: SETUP_AZURE.md)
az login
azd auth login

# 1. 環境初期化 (初回のみ)
azd env new mahted-dev
# プロンプトで location を聞かれる → japaneast 推奨 (DI/Storage はここ)
# openAiLocation は param のデフォルト eastus を使用

# 2. リソース作成 + Container App デプロイ
azd up
# → 完了後、出力に SERVICE_BACKEND_URI が表示される

# 3. 出力を backend/.env に反映 (今後ローカル開発でも使う)
azd env get-values > backend/.env
# 必要に応じて CORS_ORIGINS を Vercel URL に書き換え

# 4. フロント (Vercel) は別途
cd frontend && npx vercel
# 環境変数 NEXT_PUBLIC_API_URL に SERVICE_BACKEND_URI を設定
```

### 部分デプロイ
- バックエンドのみ再デプロイ: `azd deploy backend`
- インフラのみ: `azd provision`
- 破棄: `azd down --purge`

---

## 7. 残タスク (Day 3〜11 ロードマップ)

### Day 3〜4 (5/23〜5/24): バックエンド・コアパイプ実機検証
- [ ] `azd up` 成功
- [ ] サンプルPDFで `document_intelligence.py` がローカル実行できる
- [ ] サンプルPDFで `gpt4o_vision.py` がローカル実行できる
- [ ] `agent.py` の `run()` が end-to-end で `ExtractionResult` を返す
- [ ] FastAPI 経由で curl `POST /extract -F file=@samples/xx.pdf` が動く

### Day 5〜6 (5/25〜5/26): エージェント高度化 (任意)
- [ ] AI Foundry プロジェクト作成 (ポータル or Bicep 追加)
- [ ] `azure-ai-projects` の `AgentsClient` で Assistant 作成し、3 tool を function tool として登録
- [ ] `agent.py` を Foundry 版に置き換え (trace 形式は維持)
- [ ] (時間なければスキップ可) — 自前ループでも審査基準は満たせる

### Day 7〜8 (5/27〜5/28): フロント仕上げ
- [ ] エラーハンドリングUI改善 (大きすぎるPDF、タイムアウト)
- [ ] AgentTrace のアニメーション (リアルタイム感)
- [ ] サンプルPDFのワンクリック試用ボタン (デモ用)
- [ ] Vercel preview デプロイ

### Day 9 (5/29): 本番E2E
- [ ] Container Apps への docker image push 確認
- [ ] フロント本番デプロイ、URL を Zenn 記事に貼る
- [ ] 日英×劣化/クリーンの全サンプルで動作確認
- [ ] エラーケース動作 (壊れたPDF、空ファイル)

### Day 10 (5/30): 提出物制作
- [ ] デモ動画 3〜5 分 (Loom or QuickTime 画面録画)
- [ ] `docs/zenn_article.md` 執筆 → Zenn にアップ
- [ ] アーキ図 (Mermaid / Excalidraw) → `docs/architecture.png`
- [ ] GitHub リポジトリ public 化 → README 整備

### Day 11 (5/31): 予備日 / 応募
- [ ] 全URL有効性確認
- [ ] **6/1 までに応募フォーム提出** ← 絶対

---

## 8. 既知の落とし穴・注意事項

| 落とし穴 | 対処 |
|---|---|
| **GPT-4o の API バージョンと SKU** | `2024-11-20` モデル + `GlobalStandard` SKU を使用。古い `2024-08-06` だと一部画像処理に差がある |
| **Azure OpenAI のリージョン制約** | GPT-4o は `eastus` / `swedencentral` / `westus3` などに限定。Bicep の `openAiLocation` で指定 |
| **Document Intelligence Free F0 の制限** | 月500ページまで。デモ用は十分だが、大量サンプルテストで枯渇注意 |
| **pdf2image の poppler 依存** | Dockerfile に `apt install poppler-utils` 入れた。ローカル macOS は `brew install poppler` |
| **Next.js 16 は破壊的変更あり** | `frontend/AGENTS.md` 参照。新規コードを書く前に `node_modules/next/dist/docs/01-app/` の該当章を読むこと |
| **Container Apps の cold start** | minReplicas=0 設定。初回リクエスト 5〜10秒待つことあり。デモ前に warmup リクエスト推奨 |
| **JSON Schema strict mode** | `gpt4o_vision.py` で `"strict": true` 使用。スキーマ違反でエラーになるので変更時は慎重に |
| **CORS** | `CORS_ORIGINS` 未設定だと本番でブラウザが弾く。Vercel の本番URLを必ず追加 |
| **trace 形式** | `TraceStep` のフィールドはフロントが直接参照。`agent.py` を書き換えても **形式を維持** |

---

## 9. 別エージェント (Codex 等) への引き継ぎテンプレ

### 起動プロンプト (コピペ用)

```
このプロジェクトは Microsoft Agent Hackathon 2026 への応募作品 "MAHTED" です。
劣化スキャンPDF (Excel→PDF→印刷→スキャン→PDF) の請求書から商品コードと価格を、
Azure エージェントが自己検証ループで抽出する Web アプリです。

まず `docs/HANDOFF.md` を読んでプロジェクトの現状・アーキテクチャ・残タスク・
ローカル実行手順を把握してください。

次に取り組むタスクは: [ここに具体的なタスクを書く。例: "Day 3 の Document Intelligence
ローカル実機検証"]

制約:
- 締切 2026-06-01 23:59 (残り日数を確認)
- 個人部門、Python (backend) + TypeScript/Next.js (frontend)
- 既存ファイルの形式 (特に TraceStep のスキーマ) は維持
- 不明点は実装前に確認してください
```

### Codex CLI に最適化したいなら
- リポジトリルートに `AGENTS.md` を作成し、内容を本ファイルへの参照 (`@docs/HANDOFF.md`) にする (Codex CLI は AGENTS.md を自動読み込み)
- → **これは Day 3 までに実施推奨**

### セッション間で引き継ぐべき "暗黙の決定"
1. Foundry Agent Service への置き換えは**任意** — 自前ループ実装でも審査要件を満たす
2. 商品コードは**自由形式** (不定形) を想定 — 業界固定マスタは持たない
3. 検証は自作サンプルで行う — 機密データは使わない
4. 提出物は GitHub public + Zenn 公開記事 + 公開 Web URL の3点セット

---

## 10. 参照リンク

### ハッカソン
- 公式: https://zenn.dev/hackathons/microsoft-agent-hackathon-2026
- スケジュールタブ: https://zenn.dev/hackathons/microsoft-agent-hackathon-2026?tab=schedule
- 事前学習 (公式案内):
  - Microsoft Learn AI エージェント開発パス: https://learn.microsoft.com/training/ (検索で "AI Agent")
  - YouTube Microsoft Developer チャンネル

### Azure セットアップ
- 本リポジトリの [docs/SETUP_AZURE.md](./SETUP_AZURE.md) — アカウント作成から `azd up` まで
- Azure 無料アカウント: https://azure.microsoft.com/ja-jp/free/
- Azure for Students: https://azure.microsoft.com/ja-jp/free/students/
- Azure OpenAI 利用申請: https://aka.ms/oai/access

### Azure ドキュメント
- Document Intelligence (prebuilt-invoice): https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/invoice
- `azure-ai-documentintelligence` (Python): https://learn.microsoft.com/python/api/overview/azure/ai-documentintelligence-readme
- Azure OpenAI Vision: https://learn.microsoft.com/azure/ai-services/openai/how-to/gpt-with-vision
- AI Foundry Agent Service: https://learn.microsoft.com/azure/ai-foundry/agents/overview
- Azure Developer CLI (azd): https://learn.microsoft.com/azure/developer/azure-developer-cli/
- Container Apps: https://learn.microsoft.com/azure/container-apps/

### フレームワーク
- Next.js 16 docs: ローカルの `frontend/node_modules/next/dist/docs/`
- FastAPI: https://fastapi.tiangolo.com/
- pdf2image: https://pdf2image.readthedocs.io/

---

## 11. 更新ルール

このファイルを更新するタイミング:
- ✅ 新しいタスクが完了したら → セクション1の "完了" 表に追加 + Last updated 日付更新
- ✅ アーキテクチャや依存を変えたら → 該当セクションを更新
- ✅ 新しい落とし穴を踏んだら → セクション8に追記
- ✅ commit する前に **このファイルが現実と一致しているか確認**

更新後は必ず commit に `docs: update HANDOFF.md (...)` を含める。
