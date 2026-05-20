export type LineItem = {
  product_code: string | null;
  description: string | null;
  quantity: number | null;
  unit_price: number | null;
  amount: number | null;
  currency: string | null;
  confidence: number;
  source: "document_intelligence" | "gpt4o_vision" | "merged";
};

export type InvoiceMeta = {
  vendor_name: string | null;
  invoice_id: string | null;
  invoice_date: string | null;
  total: number | null;
  currency: string | null;
  language: "ja" | "en" | "mixed" | "unknown";
};

export type TraceStep = {
  tool: string;
  reason: string;
  duration_ms: number;
  confidence: number | null;
  note: string | null;
};

export type ExtractionResult = {
  meta: InvoiceMeta;
  line_items: LineItem[];
  trace: TraceStep[];
  math_check_passed: boolean;
  warnings: string[];
};
