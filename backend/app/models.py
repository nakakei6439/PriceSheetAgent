from typing import Literal
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    product_code: str | None = Field(None, description="商品コード/型番。読めない場合は null")
    description: str | None = Field(None, description="品名")
    quantity: float | None = None
    unit_price: float | None = None
    amount: float | None = None
    currency: str | None = Field(None, description="JPY / USD など")
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    source: Literal["document_intelligence", "gpt4o_vision", "merged"] = "document_intelligence"


class InvoiceMeta(BaseModel):
    vendor_name: str | None = None
    invoice_id: str | None = None
    invoice_date: str | None = None
    subtotal: float | None = None
    tax: float | None = None
    total: float | None = None
    currency: str | None = None
    language: Literal["ja", "en", "mixed", "unknown"] = "unknown"


class TraceStep(BaseModel):
    tool: str
    reason: str
    duration_ms: int
    confidence: float | None = None
    note: str | None = None
    status: Literal["ok", "warn", "info"] | None = None


class ExtractionResult(BaseModel):
    meta: InvoiceMeta
    line_items: list[LineItem]
    trace: list[TraceStep]
    math_check_passed: bool
    warnings: list[str] = Field(default_factory=list)
