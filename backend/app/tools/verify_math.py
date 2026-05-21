"""数値整合性検算 Tool.

Tool: verify_math
- 各明細: quantity * unit_price ≈ amount
- 明細合計: sum(amounts) ≈ document total
- 許容誤差は割合 (rel) と最小絶対値 (abs_) で指定
"""
from __future__ import annotations

import time

from app.models import ExtractionResult, LineItem, TraceStep


def _close(a: float | None, b: float | None, rel: float = 0.02, abs_: float = 1.0) -> bool:
    if a is None or b is None:
        return False
    return abs(a - b) <= max(abs_, rel * max(abs(a), abs(b)))


def _looks_like_tax_exclusive_total(
    line_sum: float,
    total: float | None,
    subtotal: float | None,
    tax: float | None,
) -> bool:
    if total is None:
        return True

    if subtotal is not None and _close(line_sum, subtotal, rel=0.03):
        if tax is None or _close(subtotal + tax, total, rel=0.03):
            return True

    if tax is not None and _close(line_sum + tax, total, rel=0.03):
        return True

    if line_sum <= 0:
        return False

    diff = total - line_sum
    inferred_tax_rate = diff / line_sum
    return 0.01 <= inferred_tax_rate <= 0.15


def verify(
    items: list[LineItem],
    total: float | None,
    subtotal: float | None = None,
    tax: float | None = None,
) -> tuple[bool, list[str], TraceStep]:
    started = time.time()
    warnings: list[str] = []

    for idx, it in enumerate(items, start=1):
        if it.quantity is not None and it.unit_price is not None and it.amount is not None:
            expected = it.quantity * it.unit_price
            if not _close(expected, it.amount):
                warnings.append(
                    f"明細#{idx} ({it.product_code or '-'}): qty×unit={expected:.2f} ≠ amount={it.amount:.2f}"
                )

    summed = sum((i.amount or 0) for i in items if i.amount is not None)
    if total is not None and items:
        if not _close(summed, total, rel=0.03) and not _looks_like_tax_exclusive_total(
            summed,
            total,
            subtotal,
            tax,
        ):
            warnings.append(f"明細合計 {summed:.2f} ≠ 文書合計 {total:.2f}")

    passed = len(warnings) == 0
    elapsed = int((time.time() - started) * 1000)
    trace = TraceStep(
        tool="verify_math",
        reason="抽出後の数値整合性チェック",
        duration_ms=elapsed,
        note=f"{'OK' if passed else f'{len(warnings)} warnings'}",
    )
    return passed, warnings, trace


def stamp_result(items: list[LineItem], total: float | None, meta, trace_so_far: list[TraceStep]) -> ExtractionResult:
    passed, warnings, step = verify(
        items,
        total,
        subtotal=getattr(meta, "subtotal", None),
        tax=getattr(meta, "tax", None),
    )
    return ExtractionResult(
        meta=meta,
        line_items=items,
        trace=trace_so_far + [step],
        math_check_passed=passed,
        warnings=warnings,
    )
