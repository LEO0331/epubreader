"use client";

import { useState } from "react";

import { useRuntime } from "@/components/runtime-provider";
import { api } from "@/lib/api";
import { isFeatureEnabled, parserModeMessage } from "@/lib/runtime";

export default function CollectionsPage() {
  const { mode, apiBaseUrl } = useRuntime();
  const collectionsEnabled = isFeatureEnabled(mode, "collections");

  const [name, setName] = useState("");
  const [collectionId, setCollectionId] = useState("");
  const [bookId, setBookId] = useState("");
  const [target, setTarget] = useState<"filesystem" | "obsidian" | "github">("filesystem");
  const [result, setResult] = useState<Record<string, unknown> | Array<Record<string, unknown>> | null>(null);
  const [error, setError] = useState("");

  const withGuard = async (task: () => Promise<void>) => {
    if (!collectionsEnabled) {
      setError(parserModeMessage());
      return;
    }
    setError("");
    await task();
  };

  return (
    <div>
      <div className="card">
        <h2>Collections & Export</h2>
        {!collectionsEnabled ? <p className="notice">{parserModeMessage()}</p> : null}
      </div>

      <div className="grid">
        <div className="card">
          <h3>Create Collection</h3>
          <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Collection name" />
          <button
            disabled={!collectionsEnabled || !name}
            onClick={() =>
              void withGuard(async () => {
                const payload = await api.createCollection(apiBaseUrl, name);
                setResult(payload);
              })
            }
          >
            Create
          </button>
        </div>

        <div className="card">
          <h3>List Collections</h3>
          <button
            className="secondary"
            disabled={!collectionsEnabled}
            onClick={() =>
              void withGuard(async () => {
                const payload = await api.listCollections(apiBaseUrl);
                setResult(payload);
              })
            }
          >
            Refresh List
          </button>
        </div>

        <div className="card">
          <h3>Add Book To Collection</h3>
          <input value={collectionId} onChange={(event) => setCollectionId(event.target.value)} placeholder="Collection ID" />
          <input value={bookId} onChange={(event) => setBookId(event.target.value)} placeholder="Book ID" />
          <button
            disabled={!collectionsEnabled || !collectionId || !bookId}
            onClick={() =>
              void withGuard(async () => {
                const payload = await api.addBookToCollection(apiBaseUrl, collectionId, bookId);
                setResult(payload);
              })
            }
          >
            Add Book
          </button>
        </div>

        <div className="card">
          <h3>Export</h3>
          <select value={target} onChange={(event) => setTarget(event.target.value as "filesystem" | "obsidian" | "github")}>
            <option value="filesystem">filesystem</option>
            <option value="obsidian">obsidian</option>
            <option value="github">github</option>
          </select>
          <button
            disabled={!collectionsEnabled || !collectionId}
            onClick={() =>
              void withGuard(async () => {
                const payload = await api.exportCollection(apiBaseUrl, collectionId, target);
                setResult(payload);
              })
            }
          >
            Export Collection
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
