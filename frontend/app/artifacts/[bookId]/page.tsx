"use client";

import { useParams } from "next/navigation";
import { useState } from "react";

import { useRuntime } from "@/components/runtime-provider";
import { api } from "@/lib/api";
import { isFeatureEnabled, parserModeMessage } from "@/lib/runtime";

export default function ArtifactsPage() {
  const params = useParams<{ bookId: string }>();
  const bookId = params.bookId;
  const { mode, apiBaseUrl } = useRuntime();
  const artifactsEnabled = isFeatureEnabled(mode, "artifacts");

  const [includeSkill, setIncludeSkill] = useState(false);
  const [artifactType, setArtifactType] = useState("summary");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");

  const withGuard = async (action: () => Promise<void>) => {
    if (!artifactsEnabled) {
      setError(parserModeMessage());
      return;
    }
    setError("");
    await action();
  };

  return (
    <div>
      <div className="card">
        <h2>Artifacts</h2>
        <p>Book ID: <span className="mono">{bookId}</span></p>
        {!artifactsEnabled ? <p className="notice">{parserModeMessage()}</p> : null}
      </div>

      <div className="grid">
        <div className="card">
          <h3>Build</h3>
          <label className="row">
            <input
              type="checkbox"
              checked={includeSkill}
              onChange={(event) => setIncludeSkill(event.target.checked)}
              style={{ width: "20px", flex: "0 0 auto" }}
            />
            Include skill artifact
          </label>
          <button
            disabled={!artifactsEnabled}
            onClick={() =>
              void withGuard(async () => {
                const payload = await api.buildArtifacts(apiBaseUrl, bookId, includeSkill);
                setResult(payload as Record<string, unknown>);
              })
            }
          >
            Build Artifacts
          </button>
        </div>

        <div className="card">
          <h3>List</h3>
          <button
            className="secondary"
            disabled={!artifactsEnabled}
            onClick={() =>
              void withGuard(async () => {
                const payload = await api.listArtifacts(apiBaseUrl, bookId);
                setResult({ artifacts: payload });
              })
            }
          >
            List Artifacts
          </button>
        </div>

        <div className="card">
          <h3>Get One Artifact</h3>
          <input value={artifactType} onChange={(event) => setArtifactType(event.target.value)} />
          <button
            disabled={!artifactsEnabled || !artifactType}
            onClick={() =>
              void withGuard(async () => {
                const payload = await api.getArtifact(apiBaseUrl, bookId, artifactType);
                setResult(payload);
              })
            }
          >
            Fetch Artifact
          </button>
        </div>
      </div>

      {result ? (
        <div className="card">
          <h3>Response</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      ) : null}
      {error ? <div className="card error">{error}</div> : null}
    </div>
  );
}
