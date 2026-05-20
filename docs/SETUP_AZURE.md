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

## 8. `azd up` でリソース一括作成

プロジェクトルートで以下を実行:

```bash
cd /Users/nakagawakeita/Products/Hackathon/MAHTED

# 1. azd 環境を初期化
azd env new mahted-dev

# 2. ロケーション選択プロンプト
#    location: japaneast (推奨 — DI/Storage/Container Apps はここ)
#    AZURE_OPENAI_LOCATION は param のデフォルト eastus を使用 (自動)

# 3. 一括デプロイ
azd up
```

実行されること:
- Resource Group `rg-mahted-dev` 作成
- Document Intelligence (F0) 作成
- Azure OpenAI + GPT-4o デプロイ
- Storage Account + Container 作成
- Log Analytics + Container Apps Environment 作成
- Container Registry 作成
- Container App (backend) 作成 (初回は hello-world イメージ)
- backend の Docker image をビルド → ACR push → Container App デプロイ

**所要時間**: 10〜20分。Bicep でリソースを並列作成するため初回は時間がかかる。

完了後の出力例:
```
SERVICE_BACKEND_URI: https://ca-backend-xxx.japaneast.azurecontainerapps.io
```

---

## 9. デプロイ後の確認

### 9-1. 環境変数を backend/.env に流し込む

```bash
azd env get-values > backend/.env
# 必要に応じて CORS_ORIGINS を Vercel URL に書き換え
```

### 9-2. 疎通確認

```bash
SERVICE_BACKEND_URI=$(azd env get-value SERVICE_BACKEND_URI)
curl ${SERVICE_BACKEND_URI}/health
# → {"status":"ok"}
```

### 9-3. ポータルでリソース確認

[https://portal.azure.com](https://portal.azure.com) → リソースグループ `rg-mahted-dev` を開く
→ 以下が並んでいれば成功:
- `di-xxxxxx` (Document Intelligence)
- `oai-xxxxxx` (Azure OpenAI)
- `stxxxxxx` (Storage)
- `log-xxxxxx` (Log Analytics)
- `cae-xxxxxx` (Container Apps Environment)
- `crxxxxxx` (Container Registry)
- `ca-backend-xxxxxx` (Container App)

---

## 10. よくあるエラーと対処

| エラー | 原因 | 対処 |
|---|---|---|
| `SubscriptionNotRegistered` | リソースプロバイダー未登録 | セクション6 を実行 |
| `OpenAI: location not available` | GPT-4o の対応リージョンでない | `azd env set AZURE_OPENAI_LOCATION swedencentral` で別リージョンを試す |
| `Insufficient quota for gpt-4o GlobalStandard` | デプロイクォータ不足 | Bicep の `capacity: 30` を `10` に下げる、または別リージョン |
| `ContainerRegistry admin user not enabled` | Bicep で `adminUserEnabled: true` 設定済み — 再デプロイで解消 | `azd provision --no-prompt` |
| `Container App returns 503` | コールドスタート (minReplicas=0) | 30秒待つか、minReplicas=1 に変更 |
| `azd up` が途中で固まる | リージョン障害 / 大量ユーザーで競合 | 数分待って再実行 |
| `pdf2image: poppler not found` (ローカル) | poppler未インストール | `brew install poppler` |
| Azure OpenAI が `403 Forbidden` | 利用申請未承認 | セクション7 の申請を提出 |

---

## 11. コスト管理 (予算アラート)

不安なら最初に予算上限を設定:

1. Azureポータル → サブスクリプション → 「**予算**」 → 「**+ 追加**」
2. 予算名: `mahted-budget`
3. 金額: **¥1,000** (絶対上限ではなく通知用)
4. リセット期間: 月次
5. アラート: 50% / 80% / 100% で通知メール

これで意図しない課金が発生しても即座に気づける。

**ハッカソン終了後**:
```bash
azd down --purge
```
で全リソースを削除すれば、それ以降の課金は停止します。

---

## 12. Discord で質問するときのテンプレ

ハッカソンの特設 Discord (Microsoft エンジニアが直接サポート) で詰まったら聞ける。
以下のフォーマットで投稿するとスムーズ:

```
【部門】個人部門
【環境】macOS / Azure無料アカウント (個人)
【やろうとしていること】azd up で MAHTED プロジェクトのリソースを一括デプロイ
【発生エラー】
（エラーメッセージをコピペ）

【試したこと】
- az provider register で必要プロバイダー登録
- リージョンを japaneast → eastus に変更
- azd env new で環境再作成

【質問】
Azure OpenAI の利用申請を出しましたが、まだ承認されません。
承認待ちの状態で先にデプロイを進める方法はありますか?
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

完了したら `docs/HANDOFF.md` のチェックリスト「Azure無料アカウント作成」にチェックを入れて次の手順 (Day 3 のローカル動作確認) に進んでください。
