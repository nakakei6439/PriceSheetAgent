"""Azure AI Document Intelligence (prebuilt-invoice) ラッパー.

Tool: extract_with_document_intelligence
- 入力: PDF/画像のバイナリ
- 出力: InvoiceMeta + LineItem[] + 各セルの confidence

価格通知書・仕切り価格通知書・価格表PDFにも、商品明細テーブル抽出の初手として
prebuilt-invoice を利用する。
"""
from __future__ import annotations

import time
import re
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential

from app.models import InvoiceMeta, LineItem, TraceStep
from app.settings import get_settings


def _normalize_product_code(value: object | None) -> str | None:
    if value is None:
        return None
    normalized = re.sub(r"\s+", "", str(value))
    return normalized or None


def _client() -> DocumentIntelligenceClient:
    s = get_settings()
    return DocumentIntelligenceClient(
        endpoint=s.document_intelligence_endpoint,
        credential=AzureKeyCredential(s.document_intelligence_key),
    )


def _field_value(field) -> tuple[object | None, float]:
    if field is None:
        return None, 0.0
    value = (
        getattr(field, "value_string", None)
        or getattr(field, "value_number", None)
        or getattr(field, "value_currency", None)
        or getattr(field, "value_date", None)
        or getattr(field, "content", None)
    )
    if hasattr(value, "amount"):
        value = value.amount
    return value, float(getattr(field, "confidence", 0.0) or 0.0)


def extract(pdf_bytes: bytes) -> tuple[InvoiceMeta, list[LineItem], TraceStep]:
    started = time.time()
    poller = _client().begin_analyze_document(
        "prebuilt-invoice",
        AnalyzeDocumentRequest(bytes_source=pdf_bytes),
    )
    result = poller.result()

    items: list[LineItem] = []
    meta = InvoiceMeta()
    min_conf = 1.0

    for doc in result.documents or []:
        f = doc.fields or {}

        vendor, _ = _field_value(f.get("VendorName"))
        invoice_id, _ = _field_value(f.get("InvoiceId"))
        invoice_date, _ = _field_value(f.get("InvoiceDate"))
        subtotal, _ = _field_value(f.get("SubTotal"))
        tax, _ = _field_value(f.get("TotalTax"))
        total, _ = _field_value(f.get("InvoiceTotal"))
        meta = InvoiceMeta(
            vendor_name=str(vendor) if vendor else None,
            invoice_id=str(invoice_id) if invoice_id else None,
            invoice_date=str(invoice_date) if invoice_date else None,
            subtotal=float(subtotal) if isinstance(subtotal, (int, float)) else None,
            tax=float(tax) if isinstance(tax, (int, float)) else None,
            total=float(total) if isinstance(total, (int, float)) else None,
        )

        items_field = f.get("Items")
        if items_field and getattr(items_field, "value_array", None):
            for it in items_field.value_array:
                ff = getattr(it, "value_object", {}) or {}
                code, c1 = _field_value(ff.get("ProductCode"))
                desc, c2 = _field_value(ff.get("Description"))
                qty, c3 = _field_value(ff.get("Quantity"))
                unit, c4 = _field_value(ff.get("UnitPrice"))
                amount, c5 = _field_value(ff.get("Amount"))
                confs = [c for c in (c1, c2, c3, c4, c5) if c > 0]
                conf = sum(confs) / len(confs) if confs else 0.0
                min_conf = min(min_conf, conf) if confs else min_conf

                items.append(
                    LineItem(
                        product_code=_normalize_product_code(code),
                        description=str(desc) if desc else None,
                        quantity=float(qty) if isinstance(qty, (int, float)) else None,
                        unit_price=float(unit) if isinstance(unit, (int, float)) else None,
                        amount=float(amount) if isinstance(amount, (int, float)) else None,
                        confidence=conf,
                        source="document_intelligence",
                    )
                )

    elapsed = int((time.time() - started) * 1000)
    trace = TraceStep(
        tool="document_intelligence",
        reason="prebuilt-invoice で構造化抽出 (初回)",
        duration_ms=elapsed,
        confidence=min_conf if items else None,
        note=f"{len(items)} line items extracted",
    )
    return meta, items, trace
