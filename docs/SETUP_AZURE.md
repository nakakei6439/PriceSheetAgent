# SETUP_AZURE.md — Azure アカウント作成 〜 `azd up` 完全ガイド

> このプロジェクトを Azure 上で動かすまでの **全工程**。`docs/HANDOFF.md` から参照される詳細手順書。
> 既に Azure サブスクリプションをお持ちの方は **セクション5** から読んでください。
> 最終更新: 2026-05-21

---

## ⚠ 最初に読むべき注意

1. **ハッカソン専用の特別クレジット (Azure Pass等) は提供されていません** (2026-05-21 時点で公式に明記なし)。**自分の Microsoft 無料アカウント** を使います。
2. **Azure OpenAI の利用申請に時間がかかる可能性があります**。承認まで数時間〜数営業日。**Day 1 のうちに申請に出す** ことを最優先。
3. クレジットカード登録は必須ですが、**初回30日 ¥27,500 (約 $200) のクレジット枠内であれば請求は発生しません**。心配なら本ガイドのセクション11で予算アラートを設定。

---

## 1. 必要なもの

| 項目 | 用途 | 補足 |
|---|---|---|
| **メールアドレス** | Microsoft アカウント作成 | gmail/outlook/独自ドメイン何でも可。**学生は `.ac.jp` ドメインを推奨** (セクション4) |
| **クレジットカード** | 本人確認 + 従量課金の保険 | デビット不可。VisaかMastercard推奨。**無料枠内なら請求は発生しない** |
| **電話番号** | SMS 認証 | 日本の携帯番号で OK |
| **本人確認書類** | (基本不要だが、稀に求められる) | パスポート/免許証画像など |

---

## 2. Microsoft 無料アカウント作成手順 (個人)

### 2-1. サインアップ開始
[https://azure.microsoft.com/ja-jp/free/](https://azure.microsoft.com/ja-jp/free/) を開く → 「**無料で始める**」をクリック。

### 2-2. Microsoft アカウントでサインイン
- 既存の Microsoft アカウントがあればそれを使用
- なければ「**アカウントを作成**」 → メアド入力 → パスワード設定 → メール認証コード入力

### 2-3. プロフィール情報入力
- 国/地域: **日本**
- 氏名: 本名 (請求書記載に使われる)
- メアド・電話番号確認

### 2-4. 本人確認 (電話)
- 携帯番号入力 → SMS 受信 → コード入力

### 2-5. カード登録
- VISA / Mastercard を入力
- 「**¥100 程度の与信が一時的に走ります** (請求はされない)」
- ⚠ **このカード登録だけで自動的に請求は発生しません**。¥27,500 クレジット枠内 + 12ヶ月無料サービスのみで運用すれば 0円

### 2-6. 規約同意 → サインアップ完了
- 通常5分以内に Azure ポータル ([https://portal.azure.com](https://portal.azure.com)) にアクセス可能になる

### 2-7. サブスクリプションの確認
1. Azureポータル → 検索バーで「サブスクリプション」 → 「**Azure subscription 1**」 のような名前で1つ存在
2. ステータスが「**アクティブ**」になっているか確認
3. **サブスクリプション ID** を控えておく (UUID形式)

---

## 3. 無料枠の内訳

| 種別 | 内容 | 期限 |
|---|---|---|
| **¥27,500 クレジット** | 任意の Azure サービスに利用可能 | サインアップから **30日間** |
| **12ヶ月無料サービス** | App Service B1 / Container Apps 一部 / Storage 5GB など | サインアップから **12ヶ月** |
| **常時無料サービス** | Functions 100万実行 / Cosmos DB 1000RU / Document Intelligence F0 (500ページ/月) など | 永久 |

**本プロジェクトでの想定消費**:
- Document Intelligence: F0 (Free) → ¥0
- Azure OpenAI GPT-4o: 入力 $2.50 / 1M tokens、出力 $10 / 1M tokens — 1リクエスト数円程度
- Container Apps: 最初の 180,000 vCPU秒/月 無料 → ¥0
- Container Registry Basic: 月 ¥720 程度 (12ヶ月無料対象外)
- Storage / Log Analytics: 数十円

**ハッカソン期間中のトータル**: ¥500〜2,000 程度の想定 (デモ実行回数次第)。¥27,500 クレジット内に十分収まる。

---

## 4. Azure for Students 代替案 (学生のみ)

学生で `.ac.jp` などの教育機関ドメインメールが使える場合、**個人版より安全** です:
- **クレジットカード不要**
- ¥15,000 相当の年間クレジット
- 多くの教育向け無料サービス
- 12ヶ月後に再認証で延長可能

[https://azure.microsoft.com/ja-jp/free/students/](https://azure.microsoft.com/ja-jp/free/students/) で申し込み。
**ただし Azure OpenAI が使えない場合があります** — その時は個人版に切り替え。

---

## 5. CLI セットアップ (macOS)

```bash
# Azure CLI
brew install azure-cli
az --version

# Azure Developer CLI (azd) — 本プロジェクトのデプロイに必須
brew install azd
azd version

# ログイン (両方必要)
az login
# → ブラウザが開く → 作成した Microsoft アカウントでサインイン

azd auth login
# → 同じくブラウザ認証
```

成功したら以下で確認:
```bash
az account show
# → サブスクリプション情報が表示される
```

複数サブスクをお持ちなら:
```bash
az account list --output table
az account set --subscription <SUBSCRIPTION_ID>
```

---

## 6. リソースプロバイダー登録

新規サブスクでは一部のリソースプロバイダーが無効になっていることがあります。本プロジェクト用に有効化:

```bash
az provider register --namespace Microsoft.CognitiveServices
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.OperationalInsights
az provider register --namespace Microsoft.Storage

# 状態確認 (Registered になればOK)
az provider show --namespace Microsoft.CognitiveServices --query registrationState
```

各プロバイダーの有効化に数分かかります。

---

## 7. ⚠ Azure OpenAI 利用申請 (重要・最優先)

**個人サブスクリプションでは、Azure OpenAI を使うには事前申請フォームが必要なケースがあります**。
時期や政策により変化するため、まずポータルで確認:

1. [Azureポータル](https://portal.azure.com) → 「Azure OpenAI」を検索
2. 「リソースの作成」を試行
3. もし **「アクセス申請が必要」と表示された場合** → 表示される申請フォーム ([https://aka.ms/oai/access](https://aka.ms/oai/access)) を提出

申請時に書く内容のコツ:
- **用途**: 「Microsoft Agent Hackathon 2026 への応募作品開発のため」
- **モデル**: GPT-4o
- **想定リクエスト数**: 1日100〜500リクエスト程度
- **データ取扱**: 「個人開発のため機密データは扱わない」

**承認まで数時間〜数営業日**。Day 1 のうちに必ず申請を出す。
申請なしで使えるリージョンに当たれば、そのまま `azd up` に進めます。

---

## 8. リソース作成 — **採用パス: ポータル手動**

本プロジェクトは **Azure ポータルから手動で各リソースを作成するパス** を採用しています。理由:
- ハッカソンの "Agentic AI" テーマ整合のため、**Microsoft Foundry (旧 AI Foundry)** リソースを利用する
- Foundry は Azure OpenAI + Agent Service が統合された新型リソース。Bicep の `kind: 'OpenAI'` (旧型) とは別物
- 初期セットアップを最短にするため、Foundry ポータル (ai.azure.com) を併用する

> 💡 `azd up` (Bicep 一括デプロイ) を希望する場合は **付録A** を参照。ただし Foundry 対応に Bicep の書き換えが必要。

### 8-1. Microsoft Foundry リソース作成 (Azureポータル)

1. [Azureポータル](https://portal.azure.com) → 検索バーで「**Foundry**」または「**Microsoft Foundry**」
2. 「**+ 作成**」→ 「**Foundry (おすすめ)**」を選択
3. **基本情報** タブ:
   - サブスクリプション: `Azure subscription 1`
   - リソースグループ: 「新規作成」→ `rg-mahted-dev`
   - 名前: `mahted-foundry` (グローバル一意。既存なら末尾に suffix)
   - リージョン: **East US** (GPT-4o の可用性最高)
   - Default project name: `proj-default` (そのまま)
4. **ストレージ** タブ: 何も触らずデフォルトのまま「次へ」
5. **ネットワーク** タブ: 「インターネットを含むすべてのネットワーク」(デフォルト) のまま「次へ」
6. **Identity** タブ: 「**システム割り当て**」(デフォルト) のまま「次へ」 — これでユーザに `Azure AI User` ロールが自動付与される
7. **暗号化** タブ: カスタマー マネージド キーは **チェックしない** (Microsoft 管理キーで暗号化)
8. **タグ** タブ: 任意 (例: `project: mahted`)。スキップ可
9. **確認と作成** タブ: 「検証に成功しました」を確認 → 「**作成**」
10. 2〜5分で完了。完了通知 → 「リソースに移動」

### 8-2. GPT-4o モデルのデプロイ (Foundry ポータル)

1. 作成した Foundry リソース画面の上部 「**Microsoft Foundry に移動**」 をクリック (または直接 [ai.azure.com](https://ai.azure.com) を開く)
2. 左上ドロップダウン or ダッシュボードから `proj-default` を選択
3. 左サイドバー → 「**モデル + エンドポイント**」 (英語: "Models + endpoints")
4. 右上 「**+ モデルのデプロイ**」 → 「**基本モデルのデプロイ**」
5. 検索ボックスに `gpt-4o` → リストから **gpt-4o** (OpenAI 製) を選択 → 「確認」
6. デプロイ設定:
   - **デプロイ名**: `gpt-4o`
   - **モデルバージョン**: `2024-11-20` (なければ最新)
   - **デプロイの種類**: **Global Standard** ← 重要
   - **1分あたりのトークン (TPM)**: **30K** (クォータ範囲の最大)
   - **コンテンツフィルター**: デフォルト
7. 「**デプロイ**」 → 数秒〜1分で "成功"

### 8-3. Document Intelligence リソース作成 (Azureポータル)

Foundry には Document Intelligence の F0 無料枠が含まれないため、別途作成します。

1. Azureポータルに戻り → 検索バーで 「**Document Intelligence**」
2. 「**+ 作成**」 を選択
3. 設定:
   - サブスクリプション: 同じ
   - **リソースグループ**: `rg-mahted-dev` (Foundry と同じ)
   - リージョン: **East US** (Foundry と同じ)
   - 名前: `mahted-di`
   - **価格レベル: Free F0** ← 重要 (無料 / 500ページ/月)
4. **確認と作成** → 「**作成**」 → 1〜2分で完了

### 8-4. エンドポイント・キーの取得と backend/.env への書き込み

#### Foundry (Azure OpenAI 互換) の値
- Foundry リソース画面 → 左メニュー「**キーと エンドポイント**」 (または Foundry ポータルの「プロジェクトの概要 → エンドポイント」)
- 控える項目:
  - **エンドポイント** (例: `https://mahted-foundry.openai.azure.com/` または `https://mahted-foundry.services.ai.azure.com/`)
  - **Key 1**

#### Document Intelligence の値
- `mahted-di` リソース → 左メニュー「**キーと エンドポイント**」
- 控える項目:
  - **エンドポイント**
  - **KEY 1**

#### backend/.env を作成
```bash
cd /Users/nakagawakeita/Products/Hackathon/MAHTED/backend
cp .env.example .env
```
そして `.env` を以下のように埋める:
```
DOCUMENT_INTELLIGENCE_ENDPOINT=（mahted-di のエンドポイント）
DOCUMENT_INTELLIGENCE_KEY=（mahted-di の Key 1）

AZURE_OPENAI_ENDPOINT=（Foundry のエンドポイント）
AZURE_OPENAI_API_KEY=（Foundry の Key 1）
AZURE_OPENAI_API_VERSION=2024-10-21
AZURE_OPENAI_GPT4O_DEPLOYMENT=gpt-4o

CORS_ORIGINS=http://localhost:3000
```

⚠ Foundry エンドポイントが `*.services.ai.azure.com` 形式だった場合は、Azure OpenAI SDK が解釈できないことがあります。その場合は同じリソースの「Azure OpenAI 互換エンドポイント」(`*.openai.azure.com`) を Foundry ポータルの "コードを表示" タブから確認してください。

### 8-5. ローカルで疎通確認
```bash
cd backend && source .venv/bin/activate
python -c "from openai import AzureOpenAI; \
  from app.settings import get_settings; \
  s = get_settings(); \
  c = AzureOpenAI(api_key=s.azure_openai_api_key, api_version=s.azure_openai_api_version, azure_endpoint=s.azure_openai_endpoint); \
  r = c.chat.completions.create(model=s.azure_openai_gpt4o_deployment, messages=[{'role':'user','content':'ping'}]); \
  print(r.choices[0].message.content)"
```
"pong" 系の応答が返れば OK。

---

## 9. デプロイ後の確認 (ポータル)

[Azureポータル](https://portal.azure.com) → リソースグループ `rg-mahted-dev` を開いて以下が並べばOK:
- `mahted-foundry` (Foundry / AI Services)
- `mahted-di` (Document Intelligence)
- (Foundry作成時に自動で付随する Storage Account など複数)

GPT-4o のデプロイ確認は [ai.azure.com](https://ai.azure.com) → プロジェクト → 「モデル + エンドポイント」で `gpt-4o` が "成功" 状態であること。

---

## 10. よくあるエラーと対処

| エラー | 原因 | 対処 |
|---|---|---|
| `Insufficient quota for gpt-4o GlobalStandard` | デプロイクォータ不足 | TPM を 30K → 10K に下げる / 別リージョン (swedencentral 等) で Foundry を再作成 |
| `OpenAI: location not available` | GPT-4o の対応リージョンでない | Foundry リソース自体を East US / Sweden Central / West US 3 のいずれかで再作成 |
| `Azure OpenAI が 403 Forbidden` | 利用申請未承認 / Foundry のリージョン外 | セクション7 の申請を提出、または East US で Foundry を再作成 |
| `pdf2image: poppler not found` (ローカル) | poppler未インストール | `brew install poppler` |
| `BadRequest: model not found` (SDK 呼出時) | デプロイメント名のミスマッチ | `.env` の `AZURE_OPENAI_GPT4O_DEPLOYMENT` と Foundry ポータルのデプロイ名を一致させる |
| `InvalidApiVersion` | API バージョン不一致 | `.env` の `AZURE_OPENAI_API_VERSION=2024-10-21` を確認。新しい場合 `2025-01-01-preview` も可 |
| Foundry エンドポイントが `services.ai.azure.com` で SDK が解釈不可 | エンドポイント形式の差 | Foundry ポータル → "コードを表示" → `*.openai.azure.com` 形式のエンドポイントに置き換える |
| `429 Too Many Requests` | TPM 上限到達 | デプロイメント編集で TPM を増やす |

---

## 11. コスト管理 (予算アラート)

不安なら最初に予算上限を設定:

1. Azureポータル → サブスクリプション → 「**予算**」 → 「**+ 追加**」
2. 予算名: `mahted-budget`
3. 金額: **¥1,000** (絶対上限ではなく通知用)
4. リセット期間: 月次
5. アラート: 50% / 80% / 100% で通知メール

これで意図しない課金が発生しても即座に気づける。

**ハッカソン終了後の片付け**:
- Azureポータル → リソースグループ `rg-mahted-dev` → 「**リソースグループの削除**」
- グループ名を入力して確定 → 配下のリソースがすべて消える = 課金停止

---

## 12. Discord で質問するときのテンプレ

ハッカソンの特設 Discord (Microsoft エンジニアが直接サポート) で詰まったら聞ける。
以下のフォーマットで投稿するとスムーズ:

```
【部門】個人部門
【環境】macOS / Azure無料アカウント (個人)
【やろうとしていること】Microsoft Foundry リソース (East US) で gpt-4o をデプロイし、
                       Document Intelligence F0 と組み合わせて請求書から商品コード/価格を抽出
【発生エラー】
（エラーメッセージをコピペ）

【試したこと】
- Foundry を East US で再作成
- TPM を 30K → 10K に下げて再デプロイ

【質問】
Azure OpenAI の利用申請を出しましたが、まだ承認されません。
承認待ちの状態で先に開発を進める方法はありますか?
```

---

## 13. 参照リンク

- Azure 無料アカウント: https://azure.microsoft.com/ja-jp/free/
- Azure for Students: https://azure.microsoft.com/ja-jp/free/students/
- Azure OpenAI アクセス申請: https://aka.ms/oai/access
- Azure CLI ドキュメント: https://learn.microsoft.com/cli/azure/
- azd ドキュメント: https://learn.microsoft.com/azure/developer/azure-developer-cli/
- ハッカソン公式: https://zenn.dev/hackathons/microsoft-agent-hackathon-2026

---

完了したら `docs/HANDOFF.md` のチェックリスト「Azure無料アカウント作成」「Azure OpenAI 利用申請」にチェックを入れて次の手順 (Day 3 のローカル動作確認) に進んでください。

---

## 付録 A. `azd up` でリソース一括作成 (代替パス・上級者向け)

ポータル手動の代わりに Infrastructure-as-Code で行いたい場合のパスです。**本プロジェクトは現在ポータル手動を採用しているため、`azd up` を実行する前に Bicep を Foundry 対応に書き換える必要があります**。

### 8A-1. Bicep を Foundry 対応に書き換え (要編集)

`infra/main-resources.bicep` 内で `Microsoft.CognitiveServices/accounts` を 2 つ作っている部分のうち、Azure OpenAI 用 (`kind: 'OpenAI'`) を **`kind: 'AIServices'`** に書き換えると Foundry 互換のリソースになります。プロジェクトリソースは `Microsoft.CognitiveServices/accounts/projects` で別途定義が必要 (現状未実装)。

### 8A-2. CLI コマンド

```bash
cd /Users/nakagawakeita/Products/Hackathon/MAHTED

# Azure CLI / azd セットアップ (既にセクション5で完了)
az login
azd auth login

# 環境初期化
azd env new mahted-dev
# location プロンプト → eastus

# 一括デプロイ (10〜20分)
azd up
```

### 8A-3. 完了後

```bash
azd env get-values > backend/.env
SERVICE_BACKEND_URI=$(azd env get-value SERVICE_BACKEND_URI)
curl ${SERVICE_BACKEND_URI}/health
```

### 8A-4. 片付け

```bash
azd down --purge
```

---

## 付録 B. リソースプロバイダー登録 (azd up を使う場合のみ)

新規サブスクで `azd up` がプロバイダー未登録で失敗する場合:

```bash
az provider register --namespace Microsoft.CognitiveServices
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.OperationalInsights
az provider register --namespace Microsoft.Storage

az provider show --namespace Microsoft.CognitiveServices --query registrationState
```

ポータル手動パスでは Azure が必要に応じて自動登録するため通常不要。
