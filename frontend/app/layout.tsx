import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PriceSheetAgent — 価格通知書読取エージェント",
  description: "Excel→PDF→印刷→スキャン と劣化した価格通知書・価格表PDFから商品コードと価格を抽出するAzureエージェント",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
