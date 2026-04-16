"use client";

import { useState } from "react";

import { useRuntime } from "@/components/runtime-provider";
import { api } from "@/lib/api";
import { RuntimeMode } from "@/lib/runtime";

export default function SettingsPage() {
  const { mode, setMode, apiBaseUrl, setApiBaseUrl } = useRuntime();

  const [pendingUrl, setPendingUrl] = useState(apiBaseUrl);
  const [status, setStatus] = useState<string>("");
  const [error, setError] = useState<string>("");

  const saveSettings = () => {
    setApiBaseUrl(pendingUrl);
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
        <h2>Settings</h2>
        <p>Set your backend endpoint and runtime mode.</p>
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

        <div className="row">
          <button onClick={saveSettings}>Save Settings</button>
          <button className="secondary" onClick={() => void checkConnection()}>
            Connectivity Check
          </button>
        </div>

        {status ? <p>{status}</p> : null}
        {error ? <p className="error">{error}</p> : null}
      </div>
    </div>
  );
}
