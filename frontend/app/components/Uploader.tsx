"use client";

import { useState } from "react";
import type { ExtractionResult } from "../types";
import { ResultTable } from "./ResultTable";
import { AgentTrace } from "./AgentTrace";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function Uploader() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ExtractionResult | null>(null);

  async function handleSubmit() {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(`${API_URL}/extract`, { method: "POST", body: fd });
      if (!res.ok) throw new Error(`API error: ${res.status} ${await res.text()}`);
      setResult((await res.json()) as ExtractionResult);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  function downloadCsv() {
    if (!result) return;
    const rows = [
      ["product_code", "description", "quantity", "unit_price", "amount", "confidence", "source"],
      ...result.line_items.map((i) => [
        i.product_code ?? "",
        i.description ?? "",
        i.quantity ?? "",
        i.unit_price ?? "",
        i.amount ?? "",
        i.confidence.toFixed(2),
        i.source,
      ]),
    ];
    const csv = rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${result.meta.invoice_id ?? "invoice"}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-8">
      <section className="rounded-lg border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <label className="block text-sm font-medium">PDF / 画像をアップロード</label>
        <input
          type="file"
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="mt-2 block w-full text-sm file:mr-4 file:rounded-md file:border-0 file:bg-zinc-900 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white hover:file:bg-zinc-700 dark:file:bg-zinc-100 dark:file:text-zinc-900"
        />
        <div className="mt-4 flex items-center gap-3">
          <button
            onClick={handleSubmit}
            disabled={!file || loading}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-zinc-400"
          >
            {loading ? "抽出中..." : "抽出する"}
          </button>
          {result && (
            <button
              onClick={downloadCsv}
              className="rounded-md border border-zinc-300 bg-white px-4 py-2 text-sm font-semibold hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800 dark:hover:bg-zinc-700"
            >
              CSV ダウンロード
            </button>
          )}
        </div>
        {error && (
          <p className="mt-3 text-sm text-red-600 dark:text-red-400">{error}</p>
        )}
      </section>

      {result && (
        <>
          <AgentTrace trace={result.trace} mathOk={result.math_check_passed} warnings={result.warnings} />
          <ResultTable result={result} />
        </>
      )}
    </div>
  );
}
