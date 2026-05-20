"""Azure OpenAI GPT-4o Vision で劣化PDFを直接読み取る Tool.

Tool: extract_with_gpt4o_vision
- 入力: PDFバイナリ + 必要に応じて「再読取りすべきフィールド」のヒント
- 出力: LineItem[] (JSON Schema 構造化出力)
"""
from __future__ import annotations

import base64
import io
import json
import time
from pdf2image import convert_from_bytes
from openai import AzureOpenAI

from app.models import LineItem, TraceStep
from app.settings import get_settings


_SYSTEM = (
    "あなたは多形式・多言語(日本語/英語)の請求書から商品明細を抽出する精密OCRアシスタントです。"
    "画像はスキャン劣化している場合があります。読めない文字は '?' で表現してください。"
    "商品コードは英数字とハイフン/スラッシュのみ。価格は数値のみ(通貨記号やカンマは除外)。"
)


_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "language": {"type": "string", "enum": ["ja", "en", "mixed", "unknown"]},
        "currency": {"type": ["string", "null"]},
        "line_items": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "product_code": {"type": ["string", "null"]},
                    "description": {"type": ["string", "null"]},
                    "quantity": {"type": ["number", "null"]},
                    "unit_price": {"type": ["number", "null"]},
                    "amount": {"type": ["number", "null"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": [
                    "product_code",
                    "description",
                    "quantity",
                    "unit_price",
                    "amount",
                    "confidence",
                ],
            },
        },
    },
    "required": ["language", "currency", "line_items"],
}


def _client() -> AzureOpenAI:
    s = get_settings()
    return AzureOpenAI(
        api_key=s.azure_openai_api_key,
        api_version=s.azure_openai_api_version,
        azure_endpoint=s.azure_openai_endpoint,
    )


def _pdf_to_data_urls(pdf_bytes: bytes, dpi: int = 200) -> list[str]:
    pages = convert_from_bytes(pdf_bytes, dpi=dpi)
    urls: list[str] = []
    for img in pages:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        urls.append(f"data:image/png;base64,{b64}")
    return urls


def extract(pdf_bytes: bytes, hint: str | None = None) -> tuple[list[LineItem], TraceStep, str | None]:
    started = time.time()
    s = get_settings()
    data_urls = _pdf_to_data_urls(pdf_bytes)

    user_text = "請求書の全明細を上記のJSONスキーマで抽出してください。"
    if hint:
        user_text += f"\n特に次の点に注意: {hint}"

    content: list[dict] = [{"type": "text", "text": user_text}]
    for url in data_urls:
        content.append({"type": "image_url", "image_url": {"url": url}})

    resp = _client().chat.completions.create(
        model=s.azure_openai_gpt4o_deployment,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": content},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "invoice_extraction", "schema": _SCHEMA, "strict": True},
        },
        temperature=0.0,
    )

    payload = json.loads(resp.choices[0].message.content or "{}")
    items = [LineItem(**i, source="gpt4o_vision") for i in payload.get("line_items", [])]
    currency = payload.get("currency")
    elapsed = int((time.time() - started) * 1000)

    avg_conf = sum(i.confidence for i in items) / len(items) if items else None
    trace = TraceStep(
        tool="gpt4o_vision",
        reason=hint or "DI の低信頼セル/未検出を補完",
        duration_ms=elapsed,
        confidence=avg_conf,
        note=f"{len(items)} line items, lang={payload.get('language')}",
    )
    return items, trace, currency
