"use client";

import Link from "next/link";
import { useState } from "react";

import { useRuntime } from "@/components/runtime-provider";
import { api } from "@/lib/api";

type SubmitResult = {
  book_id: string;
  job_id: string;
};

export default function IngestPage() {
  const { apiBaseUrl } = useRuntime();
  const [url, setUrl] = useState("");
  const [sourceType, setSourceType] = useState("");
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [result, setResult] = useState<SubmitResult | null>(null);
  const [jobStatus, setJobStatus] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const runIngestAction = async (
    action: () => Promise<SubmitResult>,
    fallbackMessage: string,
  ) => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const response = await action();
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : fallbackMessage);
    } finally {
      setLoading(false);
    }
  };

  const submitUrl = async () => {
    await runIngestAction(
      () =>
        api.ingestUrl(apiBaseUrl, {
          url,
          source_type: sourceType || undefined,
        }),
      "Could not submit this URL. Please try again.",
    );
  };

  const submitUpload = async () => {
    if (!uploadFile) {
      setError("Select an EPUB file first.");
      return;
    }
    await runIngestAction(
      () => api.ingestUpload(apiBaseUrl, uploadFile),
      "Upload failed. Please try again.",
    );
  };

  const pollJob = async () => {
    if (!result?.job_id) {
      return;
    }

    setError("");
    try {
      const job = await api.getJob(apiBaseUrl, result.job_id);
      setJobStatus(job.status);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not refresh job status.");
    }
  };

  return (
    <div>
      <div className="card">
        <h2 className="page-title">Ingest</h2>
        <p className="page-lead">Step 1: add your book source (EPUB URL, MIZ URL, or file upload).</p>
      </div>

      <div className="grid">
        <div className="card">
          <h3>Use a URL</h3>
          <p>Paste a direct EPUB link or a supported reading-page link.</p>
          <label className="label" htmlFor="url">Book URL</label>
          <input id="url" value={url} onChange={(event) => setUrl(event.target.value)} placeholder="https://..." />
          <label className="label" htmlFor="sourceType">Source Type (optional)</label>
          <input
            id="sourceType"
            value={sourceType}
            onChange={(event) => setSourceType(event.target.value)}
            placeholder="Usually auto-detected (example: miz_books)"
          />
          <button disabled={!url || loading} onClick={submitUrl}>Start from URL</button>
        </div>

        <div className="card">
          <h3>Upload an EPUB File</h3>
          <p>Use this option when the file is already on your device.</p>
          <input
            type="file"
            accept=".epub"
            onChange={(event) => setUploadFile(event.target.files?.[0] ?? null)}
          />
          <button disabled={loading || !uploadFile} onClick={submitUpload}>Upload and Start</button>
        </div>
      </div>

      {result ? (
        <div className="card">
          <h3>Book Added Successfully</h3>
          <p>Save these IDs if you want to return to this book later.</p>
          <ul className="kv">
            <li>Book ID: <span className="mono">{result.book_id}</span></li>
            <li>Ingestion Job ID: <span className="mono">{result.job_id}</span></li>
            <li>Current Job Status: <strong>{jobStatus || "Not checked yet"}</strong></li>
          </ul>
          <div className="row">
            <button className="secondary" onClick={pollJob}>Check Job Status</button>
            <Link href={`/books/${result.book_id}`}><button>Open Book Page</button></Link>
            <Link href={`/artifacts/${result.book_id}`}><button className="secondary">Open Artifact Tools</button></Link>
          </div>
        </div>
      ) : null}

      {error ? <div className="card error">{error}</div> : null}
    </div>
  );
}
