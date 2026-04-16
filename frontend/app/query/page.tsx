"use client";

import { useState } from "react";

import { useRuntime } from "@/components/runtime-provider";
import { api } from "@/lib/api";
import { isFeatureEnabled, parserModeMessage } from "@/lib/runtime";
import { runIfFeatureEnabled } from "@/lib/mode-guard";

function splitCsv(raw: string): string[] {
  return raw
    .split(",")
    .map((value) => value.trim())
    .filter((value) => value.length > 0);
}

export default function QueryPage() {
  const { mode, apiBaseUrl } = useRuntime();
  const queryEnabled = isFeatureEnabled(mode, "query");

  const [question, setQuestion] = useState("");
  const [bookIds, setBookIds] = useState("");
  const [collectionId, setCollectionId] = useState("");
  const [topK, setTopK] = useState(5);
  const [preview, setPreview] = useState<Record<string, unknown> | null>(null);
  const [answer, setAnswer] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");

  const payload = {
    question,
    book_ids: splitCsv(bookIds),
    collection_id: collectionId || null,
    top_k: topK,
  };

  return (
    <div>
      <div className="card">
        <h2 className="page-title">Query</h2>
        <p className="page-lead">Ask a question in plain language and review source-backed answers.</p>
        {!queryEnabled ? <p className="notice">{parserModeMessage()}</p> : null}
      </div>

      <div className="card">
        <p>Tip: start with one clear question, then narrow by book or collection if needed.</p>
        <label className="label" htmlFor="question">Your Question</label>
        <textarea id="question" rows={4} value={question} onChange={(event) => setQuestion(event.target.value)} />

        <div className="row">
          <div>
            <label className="label" htmlFor="bookIds">Book IDs (comma-separated, optional)</label>
            <input id="bookIds" value={bookIds} onChange={(event) => setBookIds(event.target.value)} />
          </div>
          <div>
            <label className="label" htmlFor="collectionId">Collection ID (optional)</label>
            <input id="collectionId" value={collectionId} onChange={(event) => setCollectionId(event.target.value)} />
          </div>
          <div>
            <label className="label" htmlFor="topK">Top K</label>
            <input
              id="topK"
              type="number"
              min={1}
              max={20}
              value={topK}
              onChange={(event) => setTopK(Number(event.target.value))}
            />
          </div>
        </div>

        <div className="row">
          <button
            disabled={!queryEnabled || !question}
            onClick={() =>
              void runIfFeatureEnabled(queryEnabled, setError, async () => {
                const response = await api.previewQuery(apiBaseUrl, payload);
                setPreview(response);
              })
            }
          >
            Preview Evidence
          </button>
          <button
            disabled={!queryEnabled || !question}
            onClick={() =>
              void runIfFeatureEnabled(queryEnabled, setError, async () => {
                const response = await api.runQuery(apiBaseUrl, payload);
                setAnswer(response as Record<string, unknown>);
              })
            }
          >
            Generate Answer with Citations
          </button>
        </div>
      </div>

      {preview ? (
        <div className="card">
          <h3>Evidence Preview</h3>
          <pre>{JSON.stringify(preview, null, 2)}</pre>
        </div>
      ) : null}

      {answer ? (
        <div className="card">
          <h3>Answer and Citations</h3>
          <pre>{JSON.stringify(answer, null, 2)}</pre>
        </div>
      ) : null}

      {error ? <div className="card error">{error}</div> : null}
    </div>
  );
}
