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
        <h2 className="page-title">Dashboard</h2>
        <p className="page-lead">Run your full book workflow here, step by step, without writing code.</p>

        <div className="metric-grid">
          <article className="metric-card">
            <p className="metric-label">Runtime</p>
            <p className="metric-value">{mode.toUpperCase()}</p>
          </article>
          <article className="metric-card">
            <p className="metric-label">Server Status</p>
            <p className="metric-value">{health}</p>
          </article>
          <article className="metric-card">
            <p className="metric-label">Books in Library</p>
            <p className="metric-value">{bookCount ?? "N/A"}</p>
          </article>
        </div>

        <ul className="kv">
          <li>Connected server: <span className="mono">{apiBaseUrl}</span></li>
        </ul>

        {mode === "parser" ? <p className="notice">{parserModeMessage()}</p> : null}
      </div>

      <div className="grid">
        <div className="card">
          <h3>1. Add a Book</h3>
          <p>Upload an EPUB file or paste a supported book URL to start.</p>
          <Link href="/ingest" className="button-link">Start Ingestion</Link>
        </div>

        <div className="card">
          <h3>2. Review Parsing Results</h3>
          <p>Check sections and chunks to confirm the content structure looks right.</p>
          <Link href="/ingest" className="button-link secondary">Find Book ID</Link>
        </div>

        <div className="card">
          <h3>3. Ask Questions with Sources</h3>
          <p>Get grounded answers and see which passages were used as evidence.</p>
          {isFeatureEnabled(mode, "query") ? (
            <Link href="/query" className="button-link">Open Q&A</Link>
          ) : (
            <span className="button-link disabled" aria-disabled="true">Open Q&A</span>
          )}
        </div>

        <div className="card">
          <h3>4. Organize and Export</h3>
          <p>Create collections, then export notes for Obsidian, GitHub, or local folders.</p>
          {isFeatureEnabled(mode, "collections") ? (
            <Link href="/collections" className="button-link">Open Collections</Link>
          ) : (
            <span className="button-link disabled" aria-disabled="true">Open Collections</span>
          )}
        </div>
      </div>
    </div>
  );
}
