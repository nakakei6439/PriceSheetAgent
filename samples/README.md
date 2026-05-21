# samples/ — テスト用価格表 PDF 置き場

ハッカソンのデモと開発検証で使う PDF をここに集めます。**`samples/` は git に含めても OK** (機密データではないため)。

## 必要なファイル (推奨)

| ファイル名 | 内容 | 用途 |
|---|---|---|
| `ja_invoice_a_clean.pdf` | `templates/ja_invoice_a.html` をブラウザでそのまま PDF 化したもの | Digital PDF のベースライン (DI が読める想定) |
| `ja_invoice_a_degraded.pdf` | 上記を **紙印刷 → スマホ撮影 or スキャン → PDF 化** | **本プロジェクトの核**。劣化スキャン |
| `ja_invoice_b_clean.pdf` | `templates/ja_invoice_b.html` を PDF 化 | フォーマット違い (縦書き/明朝/軽減税率) |
| `ja_invoice_b_degraded.pdf` | 上記の紙経由 | 複雑日本語価格表の劣化版 |
| `en_invoice_a_clean.pdf` | `templates/en_invoice_a.html` を PDF 化 | 英文価格表 (Northwind) |
| `en_invoice_a_degraded.pdf` | 上記の紙経由 | 英文劣化スキャン |
| `en_invoice_b_clean.pdf` | `templates/en_invoice_b.html` を PDF 化 | 英文+欧州VAT (Contoso Pharma) |
| `en_invoice_b_degraded.pdf` | 上記の紙経由 | 多通貨/多税率の劣化 |

**最低でも `ja_invoice_a_degraded.pdf` 1枚** があれば、エージェントの自己検証ループのデモは成立します。

## 作成手順

### Step 1: clean 版を作る (5分)

1. Finder で `templates/ja_invoice_a.html` をダブルクリック → ブラウザで開く
2. `Cmd + P` (印刷) → 「PDFとして保存」または「PDF」プルダウン → 「PDFとして保存」
3. 保存先: `samples/ja_invoice_a_clean.pdf`
4. 4テンプレすべて同様に処理 (`ja_invoice_a`, `ja_invoice_b`, `en_invoice_a`, `en_invoice_b`)

### Step 2: degraded (劣化スキャン) 版を作る ⭐ 本プロジェクトの核

clean 版 PDF をベースに、**「Excel → PDF → 紙 → スキャン → PDF」 という参照リレー** を実機で再現:

1. clean 版 PDF を **自宅プリンタで紙印刷**
2. 紙を:
   - **(a) プリンタの複合機でスキャンして PDF 化** ← もっとも王道
   - **(b) スマホ (iPhoneの「メモ」アプリ書類スキャン機能 や Adobe Scan) で撮影 → PDF 化** ← 手軽
   - **(c) (上級) プリンタ→ 1回スキャン→印刷→もう一度スキャン** で意図的に劣化を増やす
3. ファイル名を `*_degraded.pdf` の規約で保存

なるべく**斜め・影・しわ・コピー特有のノイズ**を含ませると、本プロジェクトのエージェント性 (GPT-4o Visionへのフォールバック動作) が分かりやすく発火します。

### Step 3: `samples/` に配置 → エージェントで動作確認

```bash
ls samples/
# → ja_invoice_a_clean.pdf, ja_invoice_a_degraded.pdf, ... が並ぶ
```

配置後、以下の Python ワンライナーで E2E 動作確認:

```bash
cd backend && source .venv/bin/activate
python -c "
from app.agent import run
import json
with open('../samples/ja_invoice_a_degraded.pdf', 'rb') as f:
    result = run(f.read())
print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
"
```

DI の `confidence` が低ければ自動で GPT-4o Vision が呼ばれ、`trace` に複数ステップが記録されることを確認してください。

## テンプレートの内容ハイライト

| テンプレ | 言語 | 売り | 含まれる難所 |
|---|---|---|---|
| `ja_invoice_a.html` | 日本語 (ゴシック) | テクノロジー商事 | 商品コード、単価、金額、印影、登録番号 |
| `ja_invoice_b.html` | 日本語 (明朝) | みどり物産 | **軽減税率 8% / 10% 混在**、和暦 (令和)、マイナス値引行 |
| `en_invoice_a.html` | 英語 | Northwind Components | USD、Net 30、Discount 行 |
| `en_invoice_b.html` | 英語 (一部独語) | Contoso Pharma EU | **EUR**、複数 VAT 率 (0/7/19%)、Lot 番号、PAID スタンプ |

これだけバリエーションがあると「多形式・多言語に対応している」とハッカソン審査でアピールしやすいです。
