# HANDOFF.md — マルチエージェント引き継ぎドキュメント

> **このファイルの目的**
> Claude Code の利用上限到達・別マシンへの移動・**OpenAI Codex (codex-cli / ChatGPT Codex) 等の別エージェントで開発を継続**するときに、このファイル1枚を読めば即座に開発を再開できるようにするための情報ハブ。
> 何かを変更・進捗を出したら **このファイルを更新してから commit する** ルール。

---

## 0. プロジェクト一行サマリ

**PriceSheetAgent** — Excel→PDF→紙印刷→スキャン と"参照リレー"を経て劣化した価格通知書・仕切り価格通知書・価格表 PDF (日英混在・多フォーマット) から、商品コード/品名/数量/単価/金額を **Azureエージェントが自己検証ループで抽出する Web アプリ**。Microsoft Agent Hackathon 2026 (個人部門) 応募作品。

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

## 1. 現状ステータス (Last updated: 2026-06-11, **ハッカソン終了・外部クローズ済み** — Azure リソース全削除 + Vercel 本番エイリアス削除で課金停止・公開停止)

> **2026-06-11 クローズ作業の記録**
> ハッカソン終了 (最終審査会 6/18 には非進出) に伴い外部公開を停止し課金を止めた。
> - **Azure**: `az group delete -n rg-mahted-dev --yes` で RG ごと全削除 (Foundry / GPT-4o 子リソース `nakak-mpeo8drm-eastus2` / DI / ACR / Container Apps Env+App / Log Analytics)。→ 課金停止。Cognitive Services 系はソフトデリート (48h) で自動消滅、再利用予定なしのため purge は未実施。
> - **Vercel**: 本番エイリアス 3 件 (`price-sheet-agent.vercel.app` 他) を `vercel alias rm` で削除し公開URLを 404 化。プロジェクト/デプロイ本体は残置 (再エイリアスで復活可能)。※Hobby プランは本番デプロイへの SSO 保護不可のためエイリアス削除で対応。プレビューには SSO 保護を有効化済み。
> - **GitHub Actions**: `build-backend.yml` を `gh workflow disable` で停止 (ACR 削除後のビルド失敗を回避)。
> - **GitHub リポジトリ / Zenn 記事 / YouTube デモ動画**: 現状維持 (リポジトリは public のまま、Zenn は published:false ドラフト、動画 https://youtu.be/VzxOywOETuw は残置)。
> - 復活させる場合: §6 で Azure リソースを再作成 → backend/.env 再設定 → BE 再デプロイ、Vercel は `vercel alias set` で再公開。

### 🚀 公開 URL (本番)
| 層 | URL | ホスト |
|---|---|---|
| フロント | https://price-sheet-agent.vercel.app | Vercel (project: `price-sheet-agent`, scope `nakakei6439s-projects`) |
| バックエンド | https://mahted-backend.ashycliff-fac33dac.eastus.azurecontainerapps.io | Azure Container Apps (`rg-mahted-dev` / env `mahted-env`) |

**デプロイ構成の要点 (Day 7〜9 で確定)**
- BE イメージは **GitHub Actions でビルド → ACR (`ca634368e688acr`) へ push** (`.github/workflows/build-backend.yml`)。
  理由: `az acr build` (ACR Tasks) が当サブスクリプションで `TasksOperationsNotAllowed` で禁止 + ローカル docker 無し。
- Container App は ACR の `mahted-backend:latest` を pull。Azure キー類は **Container App のシークレット/環境変数**に投入
  (`AZURE_OPENAI_API_KEY`/`DOCUMENT_INTELLIGENCE_KEY` は secretref)。**`min-replicas=0` (scale-to-zero) — デモ期間だけ起動・無負荷時は課金停止**。初回リクエストはコールドスタート 5〜10秒。デモ直前に `/health` を叩いて warmup 推奨。常時起動に戻すなら `az containerapp update -n mahted-backend -g rg-mahted-dev --min-replicas 1`。
- CORS は `CORS_ORIGINS` env に `https://price-sheet-agent.vercel.app`（+ `-nakakei6439s-projects` 別名, localhost）を設定済み。FE は build 時 `NEXT_PUBLIC_API_URL` に BE FQDN を inline
  (Vercel プロジェクト env の Production に永続化済み)。
- 公開URL `price-sheet-agent.vercel.app` はプロジェクトリネーム＋`vercel alias set` で取得。**Vercel Authentication (SSO保護) は無効化済み** (有効だと審査員がアクセスできず 401。`vercel project protection disable --sso` で解除)。
- 本番 E2E 済み: `POST /extract` に `ja_invoice_a_degraded_heavy.pdf` → HTTP 200、trace 4ステップ
  (`document_intelligence → verify_math(warn) → gpt4o_vision → verify_math(warn)`)、CORS preflight 200。

**再デプロイ手順**
- BE コード変更時: `backend/**` を push → Actions が自動ビルド&push → `az containerapp update -n mahted-backend -g rg-mahted-dev --image ca634368e688acr.azurecr.io/mahted-backend:latest` で新リビジョン反映。
- FE 変更時: `cd frontend && vercel deploy --prod --yes --scope nakakei6439s-projects` (env はプロジェクトに永続化済み)。
- ⚠ env 変更で複数リビジョンが active になったら、単一リビジョンモードのため旧リビジョンを `az containerapp revision deactivate` で落とす。

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
| **`pytest tests/` (verify_math)** | ✅ 5件 PASS | `backend/tests/test_verify_math.py` |
| **Azure OpenAI 疎通テスト** | ✅ | gpt-4o → "pong" 受信 |
| **Document Intelligence リソース作成** | ✅ | `mahted-di` (F0, East US) — `https://mahted-di.cognitiveservices.azure.com/` |
| **DI 疎通テスト (公開サンプル)** | ✅ | CONTOSO LTD サンプル帳票を prebuilt-invoice で正しく抽出 |
| **HTML 価格表テンプレ作成** | ✅ | `samples/templates/{ja_invoice_a,ja_invoice_b,en_invoice_a,en_invoice_b}.html` |
| **clean PDF 自動生成** | ✅ | 上記4テンプレを Chrome headless で `samples/*_clean.pdf` に変換 (300KB〜1.4MB) |
| **DI による clean PDF 抽出検証** | ✅ | JA: vendor `テクノロジー商事株式会社`, 6明細, conf 0.88 / EN: vendor `NORTHWIND COMPONENTS, INC.`, 6明細, conf 0.94 |
| **エージェント E2E 動作確認 (clean PDF)** | ✅ | DI → verify_math失敗 (税問題) → **GPT-4o Vision にフォールバック** → trace記録 → ExtractionResult を返す、まで動作 |
| **税考慮検算 + 商品コード正規化** | ✅ | `InvoiceMeta.subtotal/tax` 追加、DI の `SubTotal`/`TotalTax` 取得、税相当差分の許容、商品コード改行/空白除去 |
| **degraded PDF サンプル追加** | ✅ | `samples/{ja_invoice_a,ja_invoice_b,en_invoice_a,en_invoice_b}_degraded.pdf` (各1ページ, 764KB〜900KB) |
| **ファイルレビューUI + JSON出力UI** | ✅ | アップロードファイルのPDF/画像プレビュー、小型エージェントログ、JSONプレビュー、JSONコピー/JSONダウンロードを追加 |
| **デモ用サンプル選択UI** | ✅ | degraded PDF 4件をボタンで読み込める導線を追加 (`NEXT_PUBLIC_SAMPLE_BASE_URL` で取得元差し替え可) |
| **APIエラー処理改善** | ✅ | `/extract` で 15MB 上限、Azure DI/OpenAI失敗時の 502、フロント側の読みやすいエラー表示を追加 |
| **制限ネットワーク向け build 安定化** | ✅ | Google Fonts 取得依存を外し、`npm run build` は `next build --webpack` に固定 |
| **PriceSheetAgent 表記同期** | ✅ | 公開名・メタデータ・README・引き継ぎ文言を価格通知書/価格表PDF向けに更新 |
| **ローカル静的検証** | ✅ | `backend/.venv/bin/pytest backend/tests/ -v` 9件 PASS / `cd frontend && npx tsc --noEmit` PASS / `npm run build` PASS |
| GitHub リモート作成・初回 push | ✅ | `origin` → `https://github.com/nakakei6439/PriceSheetAgent.git` |
| 初回コミット〜直近 | ✅ | `main` は `origin/main` に push 済み |

### 既知の改善余地 / 未完了

**コード側 (Day 3〜4 で対応推奨)**
- [x] degraded PDF で agent.run() の E2E 実機確認 (2026-05-21, ネットワーク疎通環境)
  - degraded 4件すべて **DI 単独で抽出成功** (avg_conf 0.86〜0.96)、`math_check_passed=True`、warnings なし、明細6〜7件を正しく抽出。
  - `/extract` 経由でも HTTP 200 で同結果。空ファイルは 400 を確認。
  - degraded PDF は実体としてスキャン画像 (テキスト0字・全面画像1枚) だが、スキャン品質が良く DI が高精度で読めるため、**`CONFIDENCE_FLOOR=0.6` を割らず GPT-4o Vision フォールバックが一度も発火しない**。
- [x] **デモ方針確定 (2026-05-21): 自己検証ループ (`verify_math`) を主役にする**。録画動画中心。
  - **trace 可視化バグを修正**: `agent.run()` を `stamp_result` のリスト再構築に依存しない実装へ変更し、検算ステップを明示的に積み上げるようにした (`agent.py`)。これで「DI が自信満々で抽出 → 検算が不整合を検知 → ヒント付きで自己修正再抽出 → 残差を正直に提示」の **4ステップ推論チェーンが UI に出る**。
  - `TraceStep.status` (`ok`/`warn`/`info`) を追加 (`models.py`/`types.ts`)、`AgentTrace.tsx` で番号バッジを色分け + 「不整合検知」「↻ 自己修正」「整合」チップを表示。
  - **推奨デモサンプル = `samples/ja_invoice_a_degraded_heavy.pdf`** に確定。DI avg_conf=0.99 (信頼度フォールバックは発火しない) なのに `verify_math` が桁誤読5件を検知 → 自己修正ループが発火。Vision でも完全救済はできず残差5件を warnings で正直提示 → ナラティブ「自分の誤りに気づいて再試行し、直せない分は正直に出す」を体現。`Uploader.tsx` の先頭に「⭐推奨デモ」ボタンとして追加 (GitHub push 後に raw URL から取得可能)。
- 2026-05-21 の追加検証で以下が判明 (上記方針の根拠):
  - **Azure DI は劣化に非常に頑健**。確信度を `CONFIDENCE_FLOOR=0.6` 未満まで落とすには、**GPT-4o Vision でも桁を誤読するレベルの強劣化**が必要。「DI が諦める → Vision が完璧に救済」というキレイな窓はほぼ存在しない。
  - DI の `confidence` は過信ぎみで当てにならない場合あり (avg_conf 0.99 と報告しつつ単価の桁を誤読する例を確認)。
  - **実質の Agentic 見せ場は「検算ループ」の方**。劣化PDFでは DI/GPT-4o が桁を誤読 → `verify_math` が `qty×unit≠amount` を検知 → GPT-4o に hint 付きで再抽出、という連鎖が trace (`document_intelligence → gpt4o_vision → verify_math`) に現れる。結果は「完璧救済」ではなく「残差を warnings として正直に提示」になる。デモ・審査ではこの自己検証の正直さを前面に出すのが現実的。
  - heavy 劣化サンプル生成器 `samples/make_heavy_degraded.py` を追加 (Pillow + pdf2image)。env 変数で劣化強度を調整可。`hash()` のプロセス毎ランダム化バグを `hashlib.sha256` 決定論シードに修正済み。`samples/*_degraded_heavy.pdf` 4件は生成済みで残置 (デモ方針確定後に採用/再生成を判断)。
  - (旧メモ) Codex 環境の DI DNS 解決失敗はサンドボックス固有。通常ターミナルでは疎通する。
- [x] **GPT-4o Vision にタイムアウト/リトライ上限を設定済み (2026-05-21)** — `gpt4o_vision.py` の `AzureOpenAI` クライアントに `timeout`/`max_retries` を注入 (既定 60秒/2回, `settings.py` の `azure_openai_timeout`/`azure_openai_max_retries` で調整可)。heavy 劣化PDFの数分ハング対策。

**ユーザ作業 (今すぐできる)**
- [x] `samples/*_clean.pdf` を **紙印刷 → スキャン/スマホ撮影 → PDF化** → `samples/*_degraded.pdf` を作成 (本プロジェクトの核となる劣化PDF)
- [ ] ハッカソン特設 Discord に参加 (公式ページの招待リンク)

**ハッカソン後**
- [x] ~~Azure OpenAI キーをローテート~~ → **リソース全削除により不要化** (2026-06-11)
- [x] `rg-mahted-dev` リソースグループ全削除で課金停止 (2026-06-11 実施)
- [x] Vercel 本番エイリアス削除で公開停止 (2026-06-11 実施)

### ロードマップ上の現在地

> **Day 1〜10 ほぼ完了 → Day 11: Zenn公開・応募フォーム提出 (残りは最終提出)**

- [x] Day 1〜2: 環境構築 (Azure リソース / venv / 疎通)
- [x] Day 3〜4: バックエンド・コアパイプ実機検証 (DI / GPT-4o Vision / verify_math / `/extract`)
- [x] デモ方針確定 + 自己検証ループの trace 可視化
- [ ] Day 5〜6: AI Foundry Agent Service への置き換え (**任意・スキップ可** — 自前ループでも提出可)
- [x] Day 7〜8: フロント仕上げ + Vercel 本番デプロイ
- [x] Day 9: 本番 E2E (Container Apps + Vercel、実ブラウザ確認済み)
- [x] Day 10: 提出物制作 — README/Zenn記事ドラフト/GitHub public/デモ動画URL反映まで完了。デモ動画: https://youtu.be/VzxOywOETuw
- [ ] Day 11: 応募フォーム提出 + 全URL有効性の最終確認 (〜2026-06-01)

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
[Next.js: ファイルレビュー + ResultTable + AgentTrace + JSON/CSV 出力]
```

**設計意図**:
- DI を必ず最初に呼ぶ (Free F0 で無料 + 構造化に強い)
- GPT-4o Vision はフォールバック (画質劣化に強いが従量課金)
- `verify_math` で**自己検証** → 自律的再試行 → ハッカソンの"Agentic"要件を満たす
- すべての tool 呼び出しは `TraceStep` として記録 → フロントで可視化 → **デモ映え**

---

## 3. ディレクトリと主要ファイル

```
PriceSheetAgent/
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
├── samples/                   # 日英×clean/degraded の価格表サンプルPDF
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
# verify_math のユニットテストが5件パスする想定
```

### 単発ツール検証 (サンプルPDF配置後)
```bash
cd backend && source .venv/bin/activate
python -c "from app.tools import document_intelligence as di; \
  meta, items, trace = di.extract(open('../samples/ja_invoice_a_degraded.pdf','rb').read()); \
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
- [x] `/extract` の入力エラー・外部サービス失敗を画面で読める形に整備

### Day 5〜6 (5/25〜5/26): エージェント高度化 (任意)
- [ ] AI Foundry プロジェクト作成 (ポータル or Bicep 追加)
- [ ] `azure-ai-projects` の `AgentsClient` で Assistant 作成し、3 tool を function tool として登録
- [ ] `agent.py` を Foundry 版に置き換え (trace 形式は維持)
- [ ] (時間なければスキップ可) — 自前ループでも審査基準は満たせる

### Day 7〜8 (5/27〜5/28): フロント仕上げ
- [ ] エラーハンドリングUI改善 (大きすぎるPDF、タイムアウト)
- [ ] AgentTrace のアニメーション (リアルタイム感)
- [x] サンプルPDFのワンクリック試用ボタン (デモ用)
- [x] Vercel 本番デプロイ (2026-05-21, preview を飛ばして prod 公開)

### Day 9 (5/29): 本番E2E
- [x] Container Apps への image push & デプロイ確認 (GitHub Actions → ACR → Container Apps)
- [x] フロント本番デプロイ (URL は §1 公開URL表。Zenn 記事に貼る)
- [x] 本番URLで実ブラウザ E2E 確認 (2026-05-21): `price-sheet-agent.vercel.app` → ⭐推奨デモ読込 → 抽出 → DI(7.5s)→検算warn→GPT-4o Vision(13.9s 自己修正)→検算warn の4ステップが UI に表示、結果6明細・warnings5件まで描画。スクショ `docs/e2e_prod_demo.png`。残りサンプルの網羅確認は任意。
- [ ] エラーケース動作 (壊れたPDF、空ファイル) を本番URLで再確認

### Day 10 (5/30): 提出物制作
- [x] デモ動画 3分台本・撮影チェックリスト作成 (`docs/demo_video_script.md`)
- [x] デモ動画 3〜5 分を YouTube にアップロード: https://youtu.be/VzxOywOETuw
- [x] `docs/zenn_article.md` 執筆 + デモ動画URL反映
- [ ] Zenn 記事公開 (`published: true` にして公開URL確定)
- [ ] アーキ図 (Mermaid / Excalidraw) → `docs/architecture.png` (任意)
- [x] GitHub リポジトリ public 化 → README 整備

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
| **サンプルPDF取得元** | フロントのデモ用ボタンは `NEXT_PUBLIC_SAMPLE_BASE_URL` を参照。既定は GitHub raw URL なので、公開前や別ブランチ検証では `.env.local` で差し替える |
| **Next.js build** | 制限ネットワーク・sandbox でも通るよう `next/font/google` は使わず、`npm run build` は `next build --webpack`。Turbopack は環境によって internal port bind で落ちることがある |
| **Azure DI は劣化に強い / confidence 過信** | prebuilt-invoice は低画質スキャンでも高 confidence で読む。avg_conf 0.99 報告でも桁誤読あり。`CONFIDENCE_FLOOR=0.6` の確信度フォールバックは滅多に発火しない前提で設計・デモすること (実質の自己検証は `verify_math` ループ側) |
| **GPT-4o Vision の timeout 未設定** | 強劣化画像で呼び出しが数分ハングする事例あり。`gpt4o_vision.py` の `AzureOpenAI` クライアントに `timeout` / `max_retries` を設定しないと本番でリクエストが詰まる |
| **劣化サンプル生成** | `samples/make_heavy_degraded.py` で `*_degraded.pdf` → `*_degraded_heavy.pdf` を再現生成 (env 変数で強度調整)。シードは `hashlib.sha256` 決定論。実行は Azure 課金 (GPT-4o) を伴うので多重実行に注意 |

---

## 9. 別エージェント (Codex 等) への引き継ぎテンプレ

### 起動プロンプト (コピペ用 / 2026-05-21 時点 — 本番デプロイ完了後)

```
このプロジェクトは Microsoft Agent Hackathon 2026 への応募作品 "PriceSheetAgent" です。
劣化スキャンPDF (Excel→PDF→印刷→スキャン→PDF) の価格通知書・仕切り価格通知書・価格表から商品コード・品名・
数量・単価・金額を、Azure エージェントが自己検証ループで抽出する Web アプリです。

まず以下を順に読んでください:
1. /Users/nakagawakeita/Products/Hackathon/MAHTED/AGENTS.md
2. /Users/nakagawakeita/Products/Hackathon/MAHTED/docs/HANDOFF.md
3. (Azure を触る場合のみ) docs/SETUP_AZURE.md

現状 (本番公開済み):
- 公開URL: フロント https://price-sheet-agent.vercel.app / バックエンド (Container Apps) は §1 参照
- Azure リソース構築済み (Foundry / GPT-4o / DI)、backend/.env はローカルに存在 (.gitignore 済み)
- バックエンド: Azure Container Apps で稼働 (scale-to-zero)。イメージは GitHub Actions → ACR でビルド
- フロント: Vercel で稼働 (project `price-sheet-agent`)。SSO保護は無効化済み
- 自己検証ループ実装済み: DI抽出 → verify_math検算 → 不整合検知で GPT-4o Vision 再抽出 → 残差を warnings
  その推論チェーンは TraceStep.status 付きで UI 可視化済み (検知=warn, 自己修正=↻)
- 推奨デモサンプル: samples/ja_invoice_a_degraded_heavy.pdf (DI 99%でも桁誤読 → ループ発火)
- テスト: backend/.venv/bin/pytest backend/tests/ → 10件 PASS。tsc/build PASS
- 本番URLで実ブラウザ E2E 確認済み (スクショ docs/e2e_prod_demo.png)
- 提出物: README 整備済み / GitHub public / Zenn記事ドラフト docs/zenn_article.md (published:false) / デモ動画 https://youtu.be/VzxOywOETuw

残タスク (締切 2026-06-01 23:59 JST):
A. Zenn記事を published:true で公開し URL を確定
B. 応募フォーム提出 + 全URL有効性の最終確認
C. (任意) アーキ図を Mermaid/画像化して docs/ に追加・README/Zennに埋め込み

制約:
- 個人部門、Python 3.12 (backend) / Next.js 16 (frontend)
- 既存ファイルの形式 (特に TraceStep スキーマ) は維持
- Azure OpenAI のエンドポイントは Foundry 本体でなく子リソース nakak-mpeo8drm-eastus2 経由 (§4)
- 不明点は実装前にユーザに確認
```

### 引き継ぎ時の運用メモ (Codex がここから再開する場合)

- **Azure/Vercel の操作には CLI ログインが要る**: `az login`(サブスク `Azure subscription 1` / id 063f422a-…)、`vercel`(scope `nakakei6439s-projects`)、`gh`(nakakei6439)。いずれもユーザ環境で認証済みだが、別マシンでは再ログインが必要。
- **BE 再デプロイ**: `backend/**` を push → Actions が ACR にビルド&push → `az containerapp update -n mahted-backend -g rg-mahted-dev --image ca634368e688acr.azurecr.io/mahted-backend:latest`。env 更新時は旧リビジョンを `revision deactivate` で落とす (§1)。
- **FE 再デプロイ**: `cd frontend && vercel deploy --prod --yes --scope nakakei6439s-projects`。
- **ローカルでの単発確認** (Azure 疎通が要る環境で):
  ```bash
  cd backend && source .venv/bin/activate
  python -c "from app.agent import run; import json; r=run(open('../samples/ja_invoice_a_degraded_heavy.pdf','rb').read()); print(json.dumps([s.model_dump() for s in r.trace], ensure_ascii=False, indent=2))"
  ```
  ※旧メモ: 一部サンドボックスは `*.cognitiveservices.azure.com` の DNS 解決に失敗する。通常ターミナルでは疎通する。

### セッション間で引き継ぐべき "暗黙の決定"
1. **デモの主役は verify_math 自己検証ループ** (confidence フォールバックではない)。confidence は過信されるため検算で誤りを捕まえる、というのが本作の核。
2. Foundry Agent Service への置き換えは**任意** — 自前ループ実装でも審査要件を満たす (未実施)。
3. 商品コードは**自由形式** (不定形) を想定 — 業界固定マスタは持たない。
4. 検証は自作サンプルで行う — 機密データは使わない。
5. 提出物は GitHub public + Zenn 公開記事 + 公開 Web URL + Zenn記事埋め込み用デモ動画 (Web URL は確定済み)。

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
