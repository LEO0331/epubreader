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

  const submitUrl = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const response = await api.ingestUrl(apiBaseUrl, {
        url,
        source_type: sourceType || undefined,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected ingest failure");
    } finally {
      setLoading(false);
    }
  };

  const submitUpload = async () => {
    if (!uploadFile) {
      setError("Select an EPUB file first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    try {
      const response = await api.ingestUpload(apiBaseUrl, uploadFile);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected upload failure");
    } finally {
      setLoading(false);
    }
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
      setError(err instanceof Error ? err.message : "Unable to load job status");
    }
  };

  return (
    <div>
      <div className="card">
        <h2>Ingest</h2>
        <p>Step 1: add a source (EPUB URL, MIZ URL, or upload).</p>
      </div>

      <div className="grid">
        <div className="card">
          <h3>Ingest URL</h3>
          <label className="label" htmlFor="url">Source URL</label>
          <input id="url" value={url} onChange={(event) => setUrl(event.target.value)} placeholder="https://..." />
          <label className="label" htmlFor="sourceType">Source Type (optional)</label>
          <input
            id="sourceType"
            value={sourceType}
            onChange={(event) => setSourceType(event.target.value)}
            placeholder="miz_books or epub_url"
          />
          <button disabled={!url || loading} onClick={submitUrl}>Submit URL</button>
        </div>

        <div className="card">
          <h3>Upload EPUB</h3>
          <input
            type="file"
            accept=".epub"
            onChange={(event) => setUploadFile(event.target.files?.[0] ?? null)}
          />
          <button disabled={loading || !uploadFile} onClick={submitUpload}>Upload File</button>
        </div>
      </div>

      {result ? (
        <div className="card">
          <h3>Submission Result</h3>
          <ul className="kv">
            <li>Book ID: <span className="mono">{result.book_id}</span></li>
            <li>Job ID: <span className="mono">{result.job_id}</span></li>
            <li>Job status: <strong>{jobStatus || "not checked"}</strong></li>
          </ul>
          <div className="row">
            <button className="secondary" onClick={pollJob}>Refresh Job Status</button>
            <Link href={`/books/${result.book_id}`}><button>Open Book Detail</button></Link>
            <Link href={`/artifacts/${result.book_id}`}><button className="secondary">Open Artifacts</button></Link>
          </div>
        </div>
      ) : null}

      {error ? <div className="card error">{error}</div> : null}
    </div>
  );
}
