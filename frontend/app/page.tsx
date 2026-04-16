"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { useRuntime } from "@/components/runtime-provider";
import { api } from "@/lib/api";
import { isFeatureEnabled, parserModeMessage } from "@/lib/runtime";

export default function DashboardPage() {
  const { mode, apiBaseUrl } = useRuntime();
  const [bookCount, setBookCount] = useState<number | null>(null);
  const [health, setHealth] = useState<string>("Checking...");

  useEffect(() => {
    api.listBooks(apiBaseUrl)
      .then((books) => setBookCount(books.length))
      .catch(() => setBookCount(null));

    api.health(apiBaseUrl)
      .then(() => setHealth("Connected"))
      .catch(() => setHealth("Connection failed"));
  }, [apiBaseUrl]);

  return (
    <div>
      <div className="card">
        <h2>Dashboard</h2>
        <ul className="kv">
          <li>Runtime mode: <span className="tag">{mode.toUpperCase()}</span></li>
          <li>Backend: <span className="mono">{apiBaseUrl}</span></li>
          <li>Connection: <strong>{health}</strong></li>
          <li>Books found: <strong>{bookCount ?? "Unavailable"}</strong></li>
        </ul>
        {mode === "parser" ? <p className="notice">{parserModeMessage()}</p> : null}
      </div>

      <div className="grid">
        <div className="card">
          <h3>Ingest Content</h3>
          <p>Upload EPUB files or submit supported URLs.</p>
          <Link href="/ingest"><button>Open Ingest</button></Link>
        </div>

        <div className="card">
          <h3>Inspect Books</h3>
          <p>Review sections and chunks for parse quality checks.</p>
          <Link href="/ingest"><button className="secondary">Find a book ID</button></Link>
        </div>

        <div className="card">
          <h3>Query with Citations</h3>
          <p>Ask grounded questions from indexed chunks.</p>
          <Link href="/query">
            <button disabled={!isFeatureEnabled(mode, "query")}>Open Query</button>
          </Link>
        </div>

        <div className="card">
          <h3>Collections and Export</h3>
          <p>Group books and export markdown bundles.</p>
          <Link href="/collections">
            <button disabled={!isFeatureEnabled(mode, "collections")}>Open Collections</button>
          </Link>
        </div>
      </div>
    </div>
  );
}
