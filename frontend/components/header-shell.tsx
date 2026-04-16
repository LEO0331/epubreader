"use client";

import { Nav } from "@/components/nav";
import { useRuntime } from "@/components/runtime-provider";
import { parserModeMessage } from "@/lib/runtime";

const PIPELINE_STEPS = [
  "Ingest",
  "Parse",
  "Chunk",
  "Generate",
  "Index",
  "Query",
  "Export",
];

export function HeaderShell() {
  const { mode } = useRuntime();

  return (
    <header className="shell-header">
      <div className="brand-block">
        <p className="eyebrow">Book QA Library</p>
        <h1 className="brand-title">Private Library Command Center</h1>
        <p className="brand-subtitle">
          Guided workflows for ingestion, parser QA, and evidence-based answers.
        </p>
      </div>

      <div className="header-meta">
        <span className={`mode-pill ${mode === "api" ? "mode-pill-api" : "mode-pill-parser"}`}>
          {mode === "api" ? "API Mode" : "Parser Mode"}
        </span>
        {mode === "parser" ? <p className="mode-note">{parserModeMessage()}</p> : null}
      </div>

      <Nav />

      <div className="pipeline-rail" aria-label="Pipeline stages">
        {PIPELINE_STEPS.map((step, index) => (
          <span className="rail-chip" key={step}>
            <span className="rail-index">{index + 1}</span>
            {step}
          </span>
        ))}
      </div>
    </header>
  );
}
