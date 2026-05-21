import type { TraceStep } from "../types";

type Props = {
  trace: TraceStep[];
  mathOk: boolean;
  warnings: string[];
};

export function AgentTrace({ trace, mathOk, warnings }: Props) {
  return (
    <section className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold">エージェント実行ログ</h2>
        <span
          className={`rounded px-2 py-1 text-xs font-semibold ${
            mathOk ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
          }`}
        >
          検算: {mathOk ? "OK" : "要確認"}
        </span>
      </div>
      <ol className="mt-3 space-y-2">
        {trace.map((step, idx) => {
          const isSelfCorrection = step.tool === "gpt4o_vision" && step.reason.includes("検知");
          return (
            <li key={idx} className="flex gap-2">
              <span className={`flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full text-xs font-semibold ring-1 ${badgeClass(step.status)}`}>
                {idx + 1}
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-baseline gap-2">
                  <code className="rounded bg-zinc-100 px-1.5 py-0.5 text-xs font-semibold dark:bg-zinc-800">
                    {getToolLabel(step.tool)}
                  </code>
                  {step.status === "warn" && (
                    <span className="rounded bg-yellow-100 px-1.5 py-0.5 text-[10px] font-semibold text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-200">
                      不整合検知
                    </span>
                  )}
                  {step.status === "ok" && step.tool === "verify_math" && (
                    <span className="rounded bg-green-100 px-1.5 py-0.5 text-[10px] font-semibold text-green-800 dark:bg-green-900/40 dark:text-green-200">
                      整合
                    </span>
                  )}
                  {isSelfCorrection && (
                    <span className="rounded bg-blue-100 px-1.5 py-0.5 text-[10px] font-semibold text-blue-800 dark:bg-blue-900/40 dark:text-blue-200">
                      ↻ 自己修正
                    </span>
                  )}
                  <span className="text-xs text-zinc-500">{step.duration_ms} ms</span>
                  {step.confidence !== null && (
                    <span className="text-xs text-zinc-500">
                      conf={(step.confidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
                <p className="mt-0.5 line-clamp-2 text-xs text-zinc-700 dark:text-zinc-300">{step.reason}</p>
                {step.note && <p className="truncate text-xs text-zinc-500">{step.note}</p>}
              </div>
            </li>
          );
        })}
      </ol>
      {warnings.length > 0 && (
        <div className="mt-3 rounded border border-yellow-200 bg-yellow-50 p-3 text-xs text-yellow-900 dark:border-yellow-900/40 dark:bg-yellow-900/20 dark:text-yellow-200">
          <p className="font-medium">注意点</p>
          <ul className="mt-1 space-y-1">
            {warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

function badgeClass(status: TraceStep["status"]) {
  if (status === "warn")
    return "bg-yellow-50 text-yellow-700 ring-yellow-200 dark:bg-yellow-950/40 dark:text-yellow-200 dark:ring-yellow-900";
  if (status === "ok")
    return "bg-green-50 text-green-700 ring-green-200 dark:bg-green-950/40 dark:text-green-200 dark:ring-green-900";
  return "bg-blue-50 text-blue-700 ring-blue-100 dark:bg-blue-950/40 dark:text-blue-200 dark:ring-blue-900";
}

function getToolLabel(tool: string) {
  if (tool === "document_intelligence") return "Document Intelligence";
  if (tool === "gpt4o_vision") return "GPT-4o Vision";
  if (tool === "verify_math") return "検算";
  return tool;
}
