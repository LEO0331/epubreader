import type { Metadata } from "next";

import { Nav } from "@/components/nav";
import { RuntimeProvider } from "@/components/runtime-provider";

import "./globals.css";

export const metadata: Metadata = {
  title: "Book QA Library",
  description: "Non-technical UI for local-first book QA pipeline"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <RuntimeProvider>
          <div className="app">
            <header className="header">
              <div className="brand">Book QA Library</div>
              <Nav />
            </header>
            <main>{children}</main>
          </div>
        </RuntimeProvider>
      </body>
    </html>
  );
}
