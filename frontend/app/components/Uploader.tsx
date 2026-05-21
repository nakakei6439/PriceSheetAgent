"use client";

import { useEffect, useState } from "react";
import type { ExtractionResult } from "../types";
import { ResultTable } from "./ResultTable";
import { AgentTrace } from "./AgentTrace";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function Uploader() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [jsonCopied, setJsonCopied] = useState(false);

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  async function handleSubmit() {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setJsonCopied(false);
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

  function downloadJson() {
    if (!result) return;
    const json = JSON.stringify(result, null, 2);
    const blob = new Blob([json], { type: "application/json;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${result.meta.invoice_id ?? file?.name.replace(/\.[^.]+$/, "") ?? "price-sheet"}-result.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  async function copyJsonToClipboard() {
    if (!result) return;
    try {
      await navigator.clipboard.writeText(JSON.stringify(result, null, 2));
      setJsonCopied(true);
      window.setTimeout(() => setJsonCopied(false), 1800);
    } catch {
      setError("JSONをクリップボードにコピーできませんでした");
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
            <>
              <button
                onClick={downloadJson}
                className="rounded-md border border-zinc-300 bg-white px-4 py-2 text-sm font-semibold hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800 dark:hover:bg-zinc-700"
              >
                JSON ダウンロード
              </button>
              <button
                onClick={downloadCsv}
                className="rounded-md border border-zinc-300 bg-white px-4 py-2 text-sm font-semibold hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800 dark:hover:bg-zinc-700"
              >
                CSV ダウンロード
              </button>
            </>
          )}
        </div>
        {error && (
          <p className="mt-3 text-sm text-red-600 dark:text-red-400">{error}</p>
        )}
      </section>

      {result && (
        <ResultTable result={result} />
      )}

      {file && previewUrl && (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
          <FileReview file={file} previewUrl={previewUrl} />
          <div className="space-y-6">
            {result ? (
              <>
                <AgentTrace trace={result.trace} mathOk={result.math_check_passed} warnings={result.warnings} />
                <JsonPreview copied={jsonCopied} onCopy={copyJsonToClipboard} result={result} />
              </>
            ) : (
              <section className="rounded-lg border border-zinc-200 bg-white p-4 text-sm text-zinc-600 shadow-sm dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-400">
                抽出後、ここに実行ログとJSONプレビューが表示されます。
              </section>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function FileReview({ file, previewUrl }: { file: File; previewUrl: string }) {
  const isPdf = file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
  const isImage = file.type.startsWith("image/");

  return (
    <section className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold">ファイルレビュー</h2>
          <p className="mt-1 max-w-xl truncate text-sm text-zinc-600 dark:text-zinc-400">{file.name}</p>
        </div>
        <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-zinc-500">
          <dt>形式</dt>
          <dd className="text-right">{file.type || "unknown"}</dd>
          <dt>サイズ</dt>
          <dd className="text-right">{formatFileSize(file.size)}</dd>
        </dl>
      </div>
      <div className="mt-4 h-[520px] overflow-hidden rounded border border-zinc-200 bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-950">
        {isPdf && (
          <object data={previewUrl} type="application/pdf" className="h-full w-full">
            <a className="p-4 text-sm text-blue-600" href={previewUrl} target="_blank" rel="noreferrer">
              PDFを開く
            </a>
          </object>
        )}
        {isImage && !isPdf && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={previewUrl} alt={file.name} className="h-full w-full object-contain" />
        )}
        {!isPdf && !isImage && (
          <div className="flex h-full items-center justify-center text-sm text-zinc-500">
            プレビューできないファイル形式です
          </div>
        )}
      </div>
    </section>
  );
}

function JsonPreview({
  copied,
  onCopy,
  result,
}: {
  copied: boolean;
  onCopy: () => void;
  result: ExtractionResult;
}) {
  return (
    <section className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold">JSONプレビュー</h2>
        <button
          onClick={onCopy}
          className="rounded border border-zinc-300 px-2.5 py-1 text-xs font-semibold text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-200 dark:hover:bg-zinc-800"
        >
          {copied ? "コピー済み" : "コピー"}
        </button>
      </div>
      <pre className="mt-3 max-h-72 overflow-auto rounded bg-zinc-950 p-3 text-xs leading-relaxed text-zinc-100">
        {JSON.stringify(result, null, 2)}
      </pre>
    </section>
  );
}

function formatFileSize(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}
