"use client";

import { useState } from "react";

import { useRuntime } from "@/components/runtime-provider";
import { api } from "@/lib/api";
import { RuntimeMode } from "@/lib/runtime";

export default function SettingsPage() {
  const { mode, setMode, apiBaseUrl, setApiBaseUrl, apiKey, setApiKey } = useRuntime();

  const [pendingUrl, setPendingUrl] = useState(apiBaseUrl);
  const [pendingApiKey, setPendingApiKey] = useState(apiKey);
  const [status, setStatus] = useState<string>("");
  const [error, setError] = useState<string>("");

  const saveSettings = () => {
    setApiBaseUrl(pendingUrl);
    setApiKey(pendingApiKey);
    setStatus("Settings saved locally.");
    setError("");
  };

  const checkConnection = async () => {
    setStatus("Checking connectivity...");
    setError("");
    try {
      await api.health(pendingUrl);
      setStatus("Backend is reachable.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Backend check failed");
      setStatus("");
    }
  };

  return (
    <div>
      <div className="card">
        <h2 className="page-title">Settings</h2>
        <p className="page-lead">Choose how this app connects and which features should be available.</p>
      </div>

      <div className="card">
        <label className="label" htmlFor="mode">Runtime Mode</label>
        <select
          id="mode"
          value={mode}
          onChange={(event) => setMode(event.target.value as RuntimeMode)}
        >
          <option value="api">API mode (full workflow)</option>
          <option value="parser">Parser mode (ingest + parse/chunk inspect only)</option>
        </select>

        <label className="label" htmlFor="backend">Backend URL</label>
        <input
          id="backend"
          value={pendingUrl}
          onChange={(event) => setPendingUrl(event.target.value)}
          placeholder="https://your-render-service.onrender.com"
        />

        <label className="label" htmlFor="apiKey">API Key (optional)</label>
        <input
          id="apiKey"
          type="password"
          value={pendingApiKey}
          onChange={(event) => setPendingApiKey(event.target.value)}
          placeholder="Used automatically when your backend requires authentication"
        />

        <div className="row">
          <button onClick={saveSettings}>Save Changes</button>
          <button className="secondary" onClick={() => void checkConnection()}>
            Test Connection
          </button>
        </div>

        {status ? <p>{status}</p> : null}
        {error ? <p className="error">{error}</p> : null}
      </div>
    </div>
  );
}
