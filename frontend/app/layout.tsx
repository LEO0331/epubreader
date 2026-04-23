import type { Metadata, Viewport } from "next";
import { Space_Grotesk, Source_Serif_4 } from "next/font/google";

import { HeaderShell } from "@/components/header-shell";
import { RuntimeProvider } from "@/components/runtime-provider";

import "./globals.css";

const displayFont = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display",
});

const bodyFont = Source_Serif_4({
  subsets: ["latin"],
  variable: "--font-body",
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL ?? "https://book-qa-library.vercel.app"),
  title: "Book QA Library",
  description: "Non-technical UI for local-first book QA pipeline",
  applicationName: "Book QA Library",
  keywords: ["book qa", "epub", "pdf", "parser", "citations", "obsidian"],
  robots: {
    index: true,
    follow: true,
  },
  openGraph: {
    type: "website",
    title: "Book QA Library",
    description: "Ingest books, inspect parsing/chunks, and generate source-grounded answers.",
    siteName: "Book QA Library",
  },
  twitter: {
    card: "summary_large_image",
    title: "Book QA Library",
    description: "Ingest books and ask questions with citations.",
  },
};

export const viewport: Viewport = {
  themeColor: "#0f1f35",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${displayFont.variable} ${bodyFont.variable}`}>
        <RuntimeProvider>
          <div className="app-shell">
            <div className="ambient-gradient" aria-hidden="true" />
            <div className="app">
              <HeaderShell />
              <main className="content">{children}</main>
            </div>
          </div>
        </RuntimeProvider>
      </body>
    </html>
  );
}
