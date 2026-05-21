from app.models import LineItem
from app.tools.verify_math import verify


def _li(qty, unit, amt, code="A"):
    return LineItem(product_code=code, quantity=qty, unit_price=unit, amount=amt, confidence=0.9)


def test_clean_invoice_passes():
    items = [_li(2, 100, 200), _li(3, 50, 150)]
    passed, warnings, _ = verify(items, total=350)
    assert passed
    assert warnings == []


def test_line_mismatch_warns():
    items = [_li(2, 100, 999)]  # qty*unit=200, amount=999
    passed, warnings, _ = verify(items, total=999)
    assert not passed
    assert len(warnings) == 1


def test_total_mismatch_warns():
    items = [_li(1, 100, 100), _li(1, 100, 100)]
    passed, warnings, _ = verify(items, total=999)
    assert not passed
    assert any("請求合計" in w for w in warnings)


def test_tax_exclusive_lines_with_tax_in_total_passes():
    items = [_li(2, 100, 200), _li(3, 50, 150)]
    passed, warnings, _ = verify(items, total=385, subtotal=350, tax=35)
    assert passed
    assert warnings == []


def test_tax_like_difference_passes_without_structured_tax():
    items = [_li(2, 100, 200), _li(3, 50, 150)]
    passed, warnings, _ = verify(items, total=385)
    assert passed
    assert warnings == []
