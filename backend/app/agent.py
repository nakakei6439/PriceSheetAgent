"""エージェントオーケストレーション.

シンプル実装版 (まずは動作優先):
1. Document Intelligence で抽出
2. 平均信頼度が低い or 抽出件数 0 の場合は GPT-4o Vision にフォールバック
3. 両者の結果をマージ
4. verify_math で検算 → ズレがあれば GPT-4o Vision に hint 付きで再試行
5. ExtractionResult を返す

将来 (Day 5〜6) に Azure AI Foundry Agent Service に置き換える設計上の余地を残しているが,
ハッカソン期限を優先し, まずは「自前で多ツール・自己検証ループ」を実装する.
"""
from __future__ import annotations

import re

from app.models import ExtractionResult, InvoiceMeta, LineItem, TraceStep
from app.tools import document_intelligence as di
from app.tools import gpt4o_vision as vision
from app.tools import verify_math


CONFIDENCE_FLOOR = 0.6
MAX_VISION_CALLS = 1  # フォールバック/再抽出を含む Vision 呼び出しの上限


def _normalize_product_code(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = re.sub(r"\s+", "", value)
    return normalized or None


def _normalize_items(items: list[LineItem]) -> list[LineItem]:
    return [
        LineItem(**{**item.model_dump(), "product_code": _normalize_product_code(item.product_code)})
        for item in items
    ]


def _merge(di_items: list[LineItem], vis_items: list[LineItem]) -> list[LineItem]:
    """信頼度の高い方を優先して同件数マージ. 件数差がある場合は長い方を採用."""
    if not di_items:
        return _normalize_items(vis_items)
    if not vis_items:
        return _normalize_items(di_items)
    if len(di_items) != len(vis_items):
        longer = di_items if len(di_items) >= len(vis_items) else vis_items
        return _normalize_items([LineItem(**{**i.model_dump(), "source": "merged"}) for i in longer])

    merged: list[LineItem] = []
    for a, b in zip(di_items, vis_items):
        pick = a if a.confidence >= b.confidence else b
        merged.append(LineItem(**{**pick.model_dump(), "source": "merged"}))
    return _normalize_items(merged)


def _verify(items: list[LineItem], meta: InvoiceMeta, trace: list[TraceStep]) -> tuple[bool, list[str]]:
    """検算を実行し, その TraceStep を trace に追記して (passed, warnings) を返す."""
    passed, warnings, step = verify_math.verify(
        items,
        meta.total,
        subtotal=meta.subtotal,
        tax=meta.tax,
    )
    trace.append(step)
    return passed, warnings


def run(pdf_bytes: bytes) -> ExtractionResult:
    trace: list[TraceStep] = []
    vision_calls = 0

    meta, di_items, di_step = di.extract(pdf_bytes)
    di_step.status = "info"
    trace.append(di_step)

    avg_conf = (sum(i.confidence for i in di_items) / len(di_items)) if di_items else 0.0
    items: list[LineItem] = _normalize_items(di_items)

    # 信頼度フォールバック (劣化が極端な場合のみ. 通常は発火しない)
    if not di_items or avg_conf < CONFIDENCE_FLOOR:
        hint = (
            f"DIの平均信頼度が {avg_conf:.2f} と低いです. 各明細を慎重に再抽出してください."
            if di_items
            else "DIで明細が抽出できませんでした. 画像から全明細を抽出してください."
        )
        vis_items, vis_step, currency = vision.extract(pdf_bytes, hint=hint)
        vis_step.status = "info"
        trace.append(vis_step)
        vision_calls += 1
        items = _merge(di_items, vis_items)
        if currency and not meta.currency:
            meta.currency = currency

    # 1回目の自己検証 (この "検知" ステップを trace に残すのが肝)
    passed, warnings = _verify(items, meta, trace)

    # 不整合を検知したら, ヒント付きで再抽出する自己修正ループ
    if not passed and vision_calls < MAX_VISION_CALLS:
        hint = "計算が合いません: " + " / ".join(warnings[:3])
        vis_items, vis_step, _ = vision.extract(pdf_bytes, hint=hint)
        vis_step.status = "info"
        vis_step.reason = f"検算で {len(warnings)} 件の不整合を検知 → 該当明細を再抽出"
        trace.append(vis_step)
        vision_calls += 1
        items = _merge(items, vis_items)
        passed, warnings = _verify(items, meta, trace)

    return ExtractionResult(
        meta=meta,
        line_items=items,
        trace=trace,
        math_check_passed=passed,
        warnings=warnings,
    )
