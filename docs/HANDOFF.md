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

## 1. 現状ステータス (Last updated: 2026-05-21, E2E 動作確認 (clean PDF) まで完了)

### 採用したデプロイ方針
**Azure ポータルから手動でリソースを作成する** (Foundry 中心) パスを採用。`azd up` (Bicep) は付録扱い。理由は `docs/SETUP_AZURE.md` セクション 8 冒頭を参照。

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
| Azure Bicep (代替パス用・参考) | ✅ | `infra/main.bicep`, `infra/main-resources.bicep` (※Foundry 対応には書き換えが必要) |
| Azure 無料アカウント作成 | ✅ | (ユーザ作業) |
| **Microsoft Foundry リソース作成** | ✅ | East US / `rg-mahted-dev` / `mahted-foundry` (`proj-default`) |
| **GPT-4o デプロイ** | ✅ | デプロイ名 `gpt-4o` / 2024-11-20 / **Standard** / **TPM 50K, RPM 300** / 子リソース `nakak-mpeo8drm-eastus2` (East US 2) 経由 |
| **`backend/.env` 作成 + キー類設定** | ✅ | Azure OpenAI と DI 両方完了。`.gitignore` 済みでローカルのみ |
| **Python 3.12 venv + 依存インストール** | ✅ | `backend/.venv/`、`pip install -r requirements.txt` 完走 |
| **`pytest tests/` (verify_math)** | ✅ 3件 PASS | `backend/tests/test_verify_math.py` |
| **Azure OpenAI 疎通テスト** | ✅ | gpt-4o → "pong" 受信 |
| **Document Intelligence リソース作成** | ✅ | `mahted-di` (F0, East US) — `https://mahted-di.cognitiveservices.azure.com/` |
| **DI 疎通テスト (公開サンプル)** | ✅ | CONTOSO LTD 請求書を prebuilt-invoice で正しく抽出 |
| **HTML 請求書テンプレ作成** | ✅ | `samples/templates/{ja_invoice_a,ja_invoice_b,en_invoice_a,en_invoice_b}.html` |
| **clean PDF 自動生成** | ✅ | 上記4テンプレを Chrome headless で `samples/*_clean.pdf` に変換 (300KB〜1.4MB) |
| **DI による clean PDF 抽出検証** | ✅ | JA: vendor `テクノロジー商事株式会社`, 6明細, conf 0.88 / EN: vendor `NORTHWIND COMPONENTS, INC.`, 6明細, conf 0.94 |
| **エージェント E2E 動作確認 (clean PDF)** | ✅ | DI → verify_math失敗 (税問題) → **GPT-4o Vision にフォールバック** → trace記録 → ExtractionResult を返す、まで動作 |
| 初回コミット〜直近 | ✅ | local commits `dbdb718`, `a88a8e6`, `be86d70`, `5df2034`, `afb17bf`, `(samples templates)` (リモート未push) |

### 既知の改善余地 / 未完了

**コード側 (Day 3〜4 で対応推奨)**
- [ ] `backend/app/tools/verify_math.py` を **税考慮版に強化** — 現状は「明細合計 ≒ 請求合計」を素朴に比較しているため、税抜明細+税込合計の通常の請求書で必ず警告が出る。`InvoiceMeta` に subtotal/tax/total を持たせる or 「総額の 1〜15% 以内の差なら税相当として許容」というヒューリスティック追加が候補
- [ ] `backend/app/tools/document_intelligence.py` で抽出された商品コードに `\n` (改行) が混入することがある (例: `'TC-A001-\n100'`)。後段で `.replace("\n", "")` クレンジング推奨

**ユーザ作業 (今すぐできる)**
- [ ] `samples/*_clean.pdf` を **紙印刷 → スキャン/スマホ撮影 → PDF化** → `samples/*_degraded.pdf` を作成 (本プロジェクトの核となる劣化PDF。最低 `ja_invoice_a_degraded.pdf` 1枚)
- [ ] ハッカソン特設 Discord に参加 (公式ページの招待リンク)

**ハッカソン後**
- [ ] Azure OpenAI キーをローテート (画面共有時に部分露出のため)
- [ ] `rg-mahted-dev` リソースグループ全削除で課金停止

### ロードマップ上の現在地

> **Day 1〜2: 環境構築 (完了) → Day 3〜4: バックエンド・コアパイプ (ここに入った)**

Day 3〜4 で行う作業の入口候補:
1. `verify_math` 強化 (税対応)
2. degraded PDF で DI 信頼度低下 → GPT-4o Vision フォールバックの実発火確認
3. FastAPI `/extract` を実 PDF で叩く + フロントから接続テスト
4. プロダクトコードの改行除去・正規化
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
| `infra/main-resources.bicep` | **現在は使用していない参考資料** (旧型 Azure OpenAI 前提)。採用パスは Azure ポータルでの Foundry リソース手動作成。`azd up` を再採用する場合は `kind: 'OpenAI'` → `kind: 'AIServices'` 等への書き換えが必要 |

---

## 4. 環境変数

### backend/.env (`backend/.env.example` をコピー)

⚠ 注意: `AZURE_OPENAI_*` は **Foundry リソース本体 (`mahted-foundry`) ではなく、モデルデプロイ時に Azure が自動作成した "接続リソース" (`<ユーザ名>-<ランダム>-eastus2` のような名前) から取得** します。Foundry を介してデプロイしても、実際にモデルをホストしているのは子リソース側です。

| 変数 | 取得方法 (ポータル手動パス) | 用途 |
|---|---|---|
| `DOCUMENT_INTELLIGENCE_ENDPOINT` | Azureポータル → `mahted-di` → 「キーとエンドポイント」 → エンドポイント | DI API ベース URL |
| `DOCUMENT_INTELLIGENCE_KEY` | 同上 → KEY 1 | DI 認証 |
| `AZURE_OPENAI_ENDPOINT` | Azureポータル → **接続リソース** (`*-eastus2` 等) → 「キーとエンドポイント」のエンドポイントを **ベース部分のみ** 抜き出して使用 | OpenAI 互換 API ベース URL |
| `AZURE_OPENAI_API_KEY` | 同上 → Key 1 | OpenAI 認証 |
| `AZURE_OPENAI_API_VERSION` | `2024-10-21` で固定 (新機能を試したい場合のみ `2025-01-01-preview`) | API バージョン |
| `AZURE_OPENAI_GPT4O_DEPLOYMENT` | Foundry ポータルで作ったデプロイメント名 (`gpt-4o` 推奨) | デプロイメント名 |
| `AI_FOUNDRY_PROJECT_ENDPOINT` | Day 5〜6 で Agent Service を使う場合のみ。Foundry ポータル → プロジェクトの概要 → エンドポイント | Agent Service 用 |
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

## 6. Azure リソース作成 — ポータル手動 (採用パス)

> ⚠ 詳細は [docs/SETUP_AZURE.md セクション 8](./SETUP_AZURE.md#8-リソース作成--採用パス-ポータル手動) を参照。ここでは要点のみ。

1. **Microsoft Foundry リソース作成** — Azure ポータルで `Foundry (おすすめ)` を選択。リージョン East US、リソースグループ `rg-mahted-dev`、名前 `mahted-foundry`、デフォルトプロジェクト `proj-default`
2. **GPT-4o デプロイ** — Foundry ポータル ([ai.azure.com](https://ai.azure.com)) → 「モデル + エンドポイント」→ gpt-4o (**2024-11-20**, **Standard**, **TPM 50K**)。新規アカウントでは Global Standard を選ぶとクォータ 0 で詰まるため、最初から Standard を選ぶのが実績ベースの正解。子リソース (例: `<名前>-<ランダム>-eastus2`) が East US 2 に自動作成される
3. **Document Intelligence (F0)** — Azure ポータルで別途作成、リージョンとリソースグループは Foundry と同じ
4. **`backend/.env` 作成** — 子リソースの Endpoint (ベースURL部分のみ) と Key、DI の Endpoint と Key を貼る
5. **疎通確認** — `python -c "from openai import AzureOpenAI; ..."` (詳細は SETUP_AZURE.md §8-5)

### 旧パス (azd up) は当面使わない
`infra/main-resources.bicep` は `kind: 'OpenAI'` (旧 Azure OpenAI) を作る前提で書かれており、現状の Foundry リソースと二重管理になります。`azd up` を使いたい場合は付録 A (SETUP_AZURE.md) を参照し、Bicep を `kind: 'AIServices'` 等へ書き換えてください。

### Container Apps へのバックエンドデプロイは Day 9 で別途検討
ポータル手動パスの場合、Container Apps Environment / Container App / ACR は手動で作るか、`infra/` の Bicep を Foundry 互換に修正してから利用します。当面は **ローカル `uvicorn` + Vercel フロント** で開発を進め、Day 9 に本番化を判断。

---

## 6.X (参考) `azd up` を使う場合の旧手順

```bash
# 0. 前提: Azure無料アカウント作成済 + az/azd CLI ログイン済 (詳細: SETUP_AZURE.md 付録 A)
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

### 起動プロンプト (コピペ用 / 2026-05-21 時点)

```
このプロジェクトは Microsoft Agent Hackathon 2026 への応募作品 "MAHTED" です。
劣化スキャンPDF (Excel→PDF→印刷→スキャン→PDF) の請求書から商品コード・品名・
数量・単価・金額を、Azure エージェントが自己検証ループで抽出する Web アプリです。

まず以下を順に読んでください:
1. /Users/nakagawakeita/Products/Hackathon/MAHTED/AGENTS.md
2. /Users/nakagawakeita/Products/Hackathon/MAHTED/docs/HANDOFF.md
3. (Azure を触る場合のみ) docs/SETUP_AZURE.md

現状:
- Azure リソース全て構築済み (Foundry / GPT-4o / DI)
- Python venv + 依存インストール済み (.venv/ は 3.12)
- backend/.env はローカルに存在 (.gitignore 済み)
- ユニットテスト 3件 PASS
- Azure OpenAI / Document Intelligence 両方疎通済み
- clean PDF を Chrome headless で生成済み (samples/*_clean.pdf)
- agent.run() の E2E 動作も確認済み (DI → 検算失敗 → GPT-4o Vision フォールバック)

次に取り組むタスク (どれか選ぶか、ユーザに聞く):
A. verify_math.py を税考慮版に強化
B. samples/*_degraded.pdf (ユーザが紙経由で作成済みの場合) で E2E 確認
C. FastAPI を起動して /extract をフロントから叩く動作確認
D. agent.py 中の商品コード `\n` 除去などのクレンジング追加
E. Day 5〜6 の Foundry Agent Service への置き換え

制約:
- 締切 2026-06-01 23:59 JST (要・残り日数確認)
- 個人部門、Python 3.12 (backend) / Next.js 16 (frontend)
- 既存ファイルの形式 (特に TraceStep スキーマ) は維持
- Azure OpenAI のエンドポイントは Foundry リソース本体ではなく
  子リソース nakak-mpeo8drm-eastus2 経由 (HANDOFF.md §4 参照)
- 不明点は実装前にユーザに確認
```

### 直前の対話で残した宿題 (Codex がここから再開する場合)

`agent.run()` を `ja_invoice_a_clean.pdf` に対して回したところ、以下が観測された:
- DI confidence 0.88 (フォールバック閾値 0.6 を超えており、信頼度起因では Vision 呼ばれない)
- ただし verify_math が **明細合計 1,099,200 ≠ 請求合計 1,209,120** で警告
- これは「明細は税抜・合計は税込」という普通の請求書では避けられない誤検知
- 警告を契機に Vision が呼ばれ、re-extract したものの同じ数字が返り、警告は残ったまま

→ 改善優先度の高いコードは `backend/app/tools/verify_math.py` の検算ロジック。`InvoiceMeta` に subtotal/tax を持たせる対応もセット。

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
