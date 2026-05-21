from azure.core.exceptions import ServiceRequestError
from fastapi.testclient import TestClient

from app.main import app
from app.models import ExtractionResult, InvoiceMeta, LineItem, TraceStep


client = TestClient(app)


def _result() -> ExtractionResult:
    return ExtractionResult(
        meta=InvoiceMeta(vendor_name="Demo Vendor", total=1000, currency="JPY"),
        line_items=[
            LineItem(
                product_code="ABC-001",
                description="Demo item",
                quantity=1,
                unit_price=1000,
                amount=1000,
                currency="JPY",
                confidence=0.95,
            )
        ],
        trace=[TraceStep(tool="test", reason="stubbed", duration_ms=1)],
        math_check_passed=True,
        warnings=[],
    )


def test_extract_rejects_unsupported_extension() -> None:
    res = client.post("/extract", files={"file": ("memo.txt", b"hello", "text/plain")})
    assert res.status_code == 400
    assert "PDF" in res.json()["detail"]


def test_extract_rejects_empty_file() -> None:
    res = client.post("/extract", files={"file": ("empty.pdf", b"", "application/pdf")})
    assert res.status_code == 400
    assert res.json()["detail"] == "空のファイルです"


def test_extract_rejects_large_file(monkeypatch) -> None:
    monkeypatch.setattr("app.main.settings.max_upload_bytes", 4)
    res = client.post("/extract", files={"file": ("large.pdf", b"12345", "application/pdf")})
    assert res.status_code == 413
    assert "ファイルサイズ" in res.json()["detail"]


def test_extract_returns_agent_result(monkeypatch) -> None:
    monkeypatch.setattr("app.main.run_agent", lambda _: _result())
    res = client.post("/extract", files={"file": ("sample.pdf", b"%PDF-demo", "application/pdf")})
    assert res.status_code == 200
    payload = res.json()
    assert payload["meta"]["vendor_name"] == "Demo Vendor"
    assert payload["line_items"][0]["product_code"] == "ABC-001"
    assert payload["math_check_passed"] is True


def test_extract_returns_502_for_azure_failure(monkeypatch) -> None:
    def fail(_):
        raise ServiceRequestError("DNS failure")

    monkeypatch.setattr("app.main.run_agent", fail)
    res = client.post("/extract", files={"file": ("sample.pdf", b"%PDF-demo", "application/pdf")})
    assert res.status_code == 502
    assert "Azure Document Intelligence" in res.json()["detail"]
