import { Uploader } from "./components/Uploader";

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
      <header className="border-b border-zinc-200 dark:border-zinc-800">
        <div className="mx-auto max-w-5xl px-6 py-6">
          <h1 className="text-2xl font-bold tracking-tight">
            MAHTED — 請求書抽出エージェント
          </h1>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            Excel→PDF→印刷→スキャン と劣化したPDFから、Azureエージェントが
            自己検証ループで商品コードと価格を抽出します。
          </p>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-10">
        <Uploader />
      </main>
    </div>
  );
}
