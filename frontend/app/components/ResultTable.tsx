import type { ExtractionResult } from "../types";

export function ResultTable({ result }: { result: ExtractionResult }) {
  const { meta, line_items } = result;
  return (
    <section className="rounded-lg border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h2 className="text-lg font-semibold">抽出結果</h2>
      <dl className="mt-3 grid grid-cols-2 gap-x-6 gap-y-1 text-sm md:grid-cols-4">
        <Meta label="ベンダー" value={meta.vendor_name} />
        <Meta label="請求書番号" value={meta.invoice_id} />
        <Meta label="日付" value={meta.invoice_date} />
        <Meta label="合計" value={meta.total !== null ? `${meta.total} ${meta.currency ?? ""}` : null} />
      </dl>
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="border-b border-zinc-200 text-left dark:border-zinc-800">
            <tr>
              <th className="px-2 py-2">#</th>
              <th className="px-2 py-2">商品コード</th>
              <th className="px-2 py-2">品名</th>
              <th className="px-2 py-2 text-right">数量</th>
              <th className="px-2 py-2 text-right">単価</th>
              <th className="px-2 py-2 text-right">金額</th>
              <th className="px-2 py-2 text-right">信頼度</th>
              <th className="px-2 py-2">抽出元</th>
            </tr>
          </thead>
          <tbody>
            {line_items.map((it, idx) => (
              <tr key={idx} className="border-b border-zinc-100 dark:border-zinc-800">
                <td className="px-2 py-2 text-zinc-500">{idx + 1}</td>
                <td className="px-2 py-2 font-mono">{it.product_code ?? "—"}</td>
                <td className="px-2 py-2">{it.description ?? "—"}</td>
                <td className="px-2 py-2 text-right">{it.quantity ?? "—"}</td>
                <td className="px-2 py-2 text-right">{it.unit_price ?? "—"}</td>
                <td className="px-2 py-2 text-right">{it.amount ?? "—"}</td>
                <td className="px-2 py-2 text-right">
                  <ConfidenceBadge value={it.confidence} />
                </td>
                <td className="px-2 py-2">
                  <SourceBadge source={it.source} />
                </td>
              </tr>
            ))}
            {line_items.length === 0 && (
              <tr>
                <td colSpan={8} className="px-2 py-6 text-center text-zinc-500">
                  明細が抽出できませんでした
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Meta({ label, value }: { label: string; value: string | null }) {
  return (
    <>
      <dt className="text-zinc-500">{label}</dt>
      <dd className="font-medium">{value ?? "—"}</dd>
    </>
  );
}

function ConfidenceBadge({ value }: { value: number }) {
  const color =
    value >= 0.8 ? "bg-green-100 text-green-800" : value >= 0.6 ? "bg-yellow-100 text-yellow-800" : "bg-red-100 text-red-800";
  return <span className={`rounded px-1.5 py-0.5 text-xs font-medium ${color}`}>{(value * 100).toFixed(0)}%</span>;
}

function SourceBadge({ source }: { source: string }) {
  const label =
    source === "document_intelligence" ? "DI" : source === "gpt4o_vision" ? "GPT-4o" : "merged";
  return (
    <span className="rounded border border-zinc-300 px-1.5 py-0.5 text-xs text-zinc-600 dark:border-zinc-700 dark:text-zinc-300">
      {label}
    </span>
  );
}
