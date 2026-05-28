# PriceSheetAgent 3分デモ動画台本

Microsoft Agent Hackathon 2026 提出用のデモ動画台本。動画は Zenn 記事に埋め込む想定。

## 録画前チェックリスト

- 録画前にバックエンドを起こす:
  `curl https://mahted-backend.ashycliff-fac33dac.eastus.azurecontainerapps.io/health`
- 本番アプリだけを開く:
  `https://price-sheet-agent.vercel.app`
- 画面上部のデモボタンを使う:
  `⭐推奨デモ（自己検証ループ）`
- ブラウザのズームは 100% または 110% にする。重要なのは右側の `エージェント実行ログ`。
- 録画方法は **macOS標準の QuickTime Player で画面全体を録画** に固定する。音声ナレーションあり。
- Azure キー、ローカル `.env`、ターミナル履歴、非公開の管理画面は映さない。

## 録画方法

今回は **QuickTime Player の画面収録** を使う。Loom は使わない。音声は、録画時に話す方法と、録画後に自動音声を重ねる方法のどちらでもよい。提出用は聞き直して違和感が少ない方を使う。

1. Chrome か Safari で `https://price-sheet-agent.vercel.app` を開く。
2. 不要なタブ、通知、メニューバー上の機密情報が映らないように整理する。
3. macOS の通知をオフにする。可能なら「集中モード」をオンにする。
4. QuickTime Player を開く。
5. メニューから `ファイル` → `新規画面収録` を選ぶ。
6. 自分で話しながら録る場合は、`オプション` でマイクを選択する。後から自動音声を重ねる場合は、マイクなしでもよい。
7. 収録範囲は **画面全体** を選ぶ。ブラウザだけの範囲指定にすると、Zenn記事やREADMEへ切り替えるときに途切れやすい。
8. 録画開始後、2秒待ってから話し始める。
9. 3分台本どおりにデモする。
10. 録画停止後、不要な前後だけを QuickTime でトリミングする。
11. ファイル名は `pricesheetagent-demo-2026-05-21.mov` にする。
12. YouTube に **限定公開** でアップロードする。
13. 完了済み: YouTube の動画ID `VzxOywOETuw` を `docs/zenn_article.md` に `@[youtube](VzxOywOETuw)` として埋め込み済み。

録画は一発撮りにこだわらない。1本目はリハーサル、2本目を提出候補にする。

## 自動音声で後から読み上げる方法

macOS 標準の `say` で日本語ナレーション音声を作り、`ffmpeg` で録画動画に重ねる。

### 1. 読み上げ音声を作る

読み上げ用テキストは `docs/demo_narration.txt` に置く。まず音声ファイルを作る。

```bash
say -v Kyoko -r 185 -f docs/demo_narration.txt -o docs/demo_narration.aiff
```

生成後に、音声ファイルが空でないことを確認する。

```bash
ls -lh docs/demo_narration.aiff
afinfo docs/demo_narration.aiff
```

ファイルサイズが数KBしかない、または再生できない場合は、Codex 等の制限環境ではなく、通常の macOS Terminal から同じ `say` コマンドを実行する。

声を変えたい場合は、利用できる日本語音声を確認する。

```bash
say -v '?' | rg -i 'ja|japan|日本|kyoko'
```

### 2. 録画動画に音声を重ねる

QuickTime で録画した無音または低音量の動画を `pricesheetagent-demo-2026-05-21.mov` として保存してから実行する。

```bash
ffmpeg \
  -i pricesheetagent-demo-2026-05-21.mov \
  -i docs/demo_narration.aiff \
  -map 0:v:0 \
  -map 1:a:0 \
  -c:v copy \
  -c:a aac \
  -shortest \
  pricesheetagent-demo-2026-05-21-voiced.mp4
```

`-shortest` は、映像と音声の短い方で出力を止める指定。音声が途中で切れる場合は、画面録画を少し長めに撮り直す。映像が先に終わる場合は、読み上げ速度を上げる。

```bash
say -v Kyoko -r 200 -f docs/demo_narration.txt -o docs/demo_narration.aiff
```

## 3分構成

| 時間 | 画面 | 話す目的 |
|---|---|---|
| 0:00-0:20 | アプリ上部 / アップロード欄 | 劣化した価格PDFは人間の確認が残る、という業務課題を伝える。 |
| 0:20-0:45 | デモサンプルボタン | Document Intelligence 抽出、検算、GPT-4o Vision 再試行という解決策を説明する。 |
| 0:45-1:15 | 推奨サンプル読込 / 抽出クリック | 本番環境で実際に動いている流れを見せる。 |
| 1:15-2:15 | 結果テーブル / エージェント実行ログ | 抽出、不整合検知、再試行、warnings提示という Agentic な流れを主役にする。 |
| 2:15-2:40 | Zenn記事またはREADMEのアーキテクチャ欄 | Azure Container Apps、Document Intelligence、Foundry / GPT-4o Vision の構成を見せる。 |
| 2:40-3:00 | アプリの結果画面 | 業務価値と、誤りを隠さない信頼性の設計で締める。 |

## 読み上げ台本

PriceSheetAgent は、劣化した価格通知書や価格表 PDF から、商品コード、数量、単価、金額を抽出する Azure エージェントです。

実務では、Excel から PDF 化され、印刷され、さらにスキャンされた書類がよくあります。OCR や AI の confidence が高くても、単価の桁を間違えることがあります。

そこでこのアプリでは、まず Azure AI Document Intelligence で構造化抽出し、その後に数量かける単価が金額と合っているかを検算します。計算が合わなければ、Microsoft Foundry 経由の GPT-4o Vision に、どの明細が合わないかをヒントとして渡し、再抽出します。

実際に推奨デモを実行します。ここで劣化 PDF が読み込まれ、抽出が始まります。バックエンドは Azure Container Apps 上で動いていて、初回だけ少し待つ場合があります。

結果を見ると、明細テーブルだけでなく、右側にエージェント実行ログが出ます。

ログでは、Document Intelligence が高い confidence で抽出した後、検算ステップが不整合を検知しています。その結果、GPT-4o Vision が自己修正として再抽出され、最後にもう一度検算しています。

重要なのは、直せなかった箇所を隠さず warnings として出すことです。業務では、全部正しいと言い切るより、確認すべき箇所を明示する方が安全です。

構成は、フロントエンドが Next.js on Vercel、バックエンドが FastAPI on Azure Container Apps、抽出に Azure AI Document Intelligence、再抽出に Microsoft Foundry / Azure OpenAI GPT-4o Vision を使っています。

PriceSheetAgent は、価格表処理の確認工数を減らしつつ、人間が見るべき箇所を明確にする、実務向けの自己検証型エージェントです。

## 画面操作

1. `https://price-sheet-agent.vercel.app` を開く。
2. `⭐推奨デモ（自己検証ループ）` をクリックする。
3. ファイル名が読み込まれたことを確認する。
4. `抽出する` をクリックする。
5. 待ち時間には、Azure 側で抽出と検算をしていることを説明する。
6. `結果テーブル` と `エージェント実行ログ` が両方見える位置にスクロールまたはフォーカスする。
7. trace では次の流れを指摘する:
   - `Document Intelligence`: 高 confidence の初回抽出。
   - `検算`: 不整合の検知。
   - `GPT-4o Vision`: 自己修正のための再試行。
   - 最後の `検算`: 残った warnings を要確認箇所として正直に提示。
8. `docs/zenn_article.md` または README のアーキテクチャ図を短く見せる。
9. 結果画面に戻って締めの一言を話す。

## 録画後タスク

1. YouTube デモ動画: https://youtu.be/VzxOywOETuw
2. `docs/zenn_article.md` には `@[youtube](VzxOywOETuw)` で埋め込み済み。
3. 提出前に公開アプリURL、GitHub URL、Zenn公開URL、YouTube URL を再確認する。
4. 2026-06-01 23:59 JST までに提出する。
