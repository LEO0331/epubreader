import type { Metadata } from "next";
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
  title: "Book QA Library",
  description: "Non-technical UI for local-first book QA pipeline"
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
