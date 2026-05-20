import type { TraceStep } from "../types";

type Props = {
  trace: TraceStep[];
  mathOk: boolean;
  warnings: string[];
};

export function AgentTrace({ trace, mathOk, warnings }: Props) {
  return (
    <section className="rounded-lg border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">エージェント実行ログ</h2>
        <span
          className={`rounded px-2 py-1 text-xs font-semibold ${
            mathOk ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
          }`}
        >
          検算: {mathOk ? "OK" : "要確認"}
        </span>
      </div>
      <ol className="mt-4 space-y-3">
        {trace.map((step, idx) => (
          <li key={idx} className="flex gap-3">
            <span className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-zinc-100 text-xs font-semibold text-zinc-700 dark:bg-zinc-800 dark:text-zinc-200">
              {idx + 1}
            </span>
            <div className="flex-1">
              <div className="flex flex-wrap items-baseline gap-2">
                <code className="rounded bg-zinc-100 px-1.5 py-0.5 text-xs font-semibold dark:bg-zinc-800">
                  {step.tool}
                </code>
                <span className="text-xs text-zinc-500">{step.duration_ms} ms</span>
                {step.confidence !== null && (
                  <span className="text-xs text-zinc-500">
                    conf={(step.confidence * 100).toFixed(0)}%
                  </span>
                )}
              </div>
              <p className="text-sm text-zinc-700 dark:text-zinc-300">{step.reason}</p>
              {step.note && <p className="text-xs text-zinc-500">{step.note}</p>}
            </div>
          </li>
        ))}
      </ol>
      {warnings.length > 0 && (
        <div className="mt-4 rounded border border-yellow-200 bg-yellow-50 p-3 text-sm text-yellow-900 dark:border-yellow-900/40 dark:bg-yellow-900/20 dark:text-yellow-200">
          <p className="font-medium">検算で見つかった注意点:</p>
          <ul className="mt-1 list-inside list-disc">
            {warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
