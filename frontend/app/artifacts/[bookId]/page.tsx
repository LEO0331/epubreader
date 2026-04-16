"use client";

import { useParams } from "next/navigation";
import { useState } from "react";

import { useRuntime } from "@/components/runtime-provider";
import { api } from "@/lib/api";
import { isFeatureEnabled, parserModeMessage } from "@/lib/runtime";
import { runIfFeatureEnabled } from "@/lib/mode-guard";

export default function ArtifactsPage() {
  const params = useParams<{ bookId: string }>();
  const bookId = params.bookId;
  const { mode, apiBaseUrl } = useRuntime();
  const artifactsEnabled = isFeatureEnabled(mode, "artifacts");

  const [includeSkill, setIncludeSkill] = useState(false);
  const [artifactType, setArtifactType] = useState("summary");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");

  return (
    <div>
      <div className="card">
        <h2 className="page-title">Artifacts</h2>
        <p className="page-lead">Book ID: <span className="mono">{bookId}</span></p>
        <p>Artifacts are generated notes and Q&A outputs based on this book.</p>
        {!artifactsEnabled ? <p className="notice">{parserModeMessage()}</p> : null}
      </div>

      <div className="grid">
        <div className="card">
          <h3>Generate New Artifacts</h3>
          <label className="row">
            <input
              type="checkbox"
              checked={includeSkill}
              onChange={(event) => setIncludeSkill(event.target.checked)}
              style={{ width: "20px", flex: "0 0 auto" }}
            />
            Include skill guide artifact
          </label>
          <button
            disabled={!artifactsEnabled}
            onClick={() =>
              void runIfFeatureEnabled(artifactsEnabled, setError, async () => {
                const payload = await api.buildArtifacts(apiBaseUrl, bookId, includeSkill);
                setResult(payload as Record<string, unknown>);
              })
            }
          >
            Generate Artifacts
          </button>
        </div>

        <div className="card">
          <h3>View Existing Artifacts</h3>
          <button
            className="secondary"
            disabled={!artifactsEnabled}
            onClick={() =>
              void runIfFeatureEnabled(artifactsEnabled, setError, async () => {
                const payload = await api.listArtifacts(apiBaseUrl, bookId);
                setResult({ artifacts: payload });
              })
            }
          >
            Show Artifact List
          </button>
        </div>

        <div className="card">
          <h3>Open One Artifact</h3>
          <input value={artifactType} onChange={(event) => setArtifactType(event.target.value)} />
          <button
            disabled={!artifactsEnabled || !artifactType}
            onClick={() =>
              void runIfFeatureEnabled(artifactsEnabled, setError, async () => {
                const payload = await api.getArtifact(apiBaseUrl, bookId, artifactType);
                setResult(payload);
              })
            }
          >
            Open Artifact
          </button>
        </div>
      </div>

      {result ? (
        <div className="card">
          <h3>Result</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      ) : null}
      {error ? <div className="card error">{error}</div> : null}
    </div>
  );
}
