"use client";

import React from "react";
import { useState } from "react";

import { useRuntime } from "@/components/runtime-provider";
import { api } from "@/lib/api";
import { isFeatureEnabled, parserModeMessage } from "@/lib/runtime";
import { runIfFeatureEnabled } from "@/lib/mode-guard";

export default function CollectionsPage() {
  const { mode, apiBaseUrl } = useRuntime();
  const collectionsEnabled = isFeatureEnabled(mode, "collections");

  const [name, setName] = useState("");
  const [collectionId, setCollectionId] = useState("");
  const [bookId, setBookId] = useState("");
  const [target, setTarget] = useState<"filesystem" | "obsidian" | "github">("filesystem");
  const [obsidianEnhanced, setObsidianEnhanced] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | Array<Record<string, unknown>> | null>(null);
  const [error, setError] = useState("");

  return (
    <div>
      <div className="card">
        <h2 className="page-title">Collections & Export</h2>
        <p className="page-lead">Group related books, then export a reusable knowledge bundle.</p>
        {!collectionsEnabled ? <p className="notice">{parserModeMessage()}</p> : null}
      </div>

      <div className="grid">
        <div className="card">
          <h3>Create a Collection</h3>
          <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Collection name" />
          <button
            disabled={!collectionsEnabled || !name}
            onClick={() =>
              void runIfFeatureEnabled(collectionsEnabled, setError, async () => {
                const payload = await api.createCollection(apiBaseUrl, name);
                setResult(payload);
              })
            }
          >
            Create Collection
          </button>
        </div>

        <div className="card">
          <h3>View Collections</h3>
          <button
            className="secondary"
            disabled={!collectionsEnabled}
            onClick={() =>
              void runIfFeatureEnabled(collectionsEnabled, setError, async () => {
                const payload = await api.listCollections(apiBaseUrl);
                setResult(payload);
              })
            }
          >
            Refresh Collections
          </button>
        </div>

        <div className="card">
          <h3>Add a Book to a Collection</h3>
          <input value={collectionId} onChange={(event) => setCollectionId(event.target.value)} placeholder="Collection ID" />
          <input value={bookId} onChange={(event) => setBookId(event.target.value)} placeholder="Book ID" />
          <button
            disabled={!collectionsEnabled || !collectionId || !bookId}
            onClick={() =>
              void runIfFeatureEnabled(collectionsEnabled, setError, async () => {
                const payload = await api.addBookToCollection(apiBaseUrl, collectionId, bookId);
                setResult(payload);
              })
            }
          >
            Add Book to Collection
          </button>
        </div>

        <div className="card">
          <h3>Export Collection</h3>
          <select value={target} onChange={(event) => setTarget(event.target.value as "filesystem" | "obsidian" | "github")}>
            <option value="filesystem">filesystem</option>
            <option value="obsidian">obsidian</option>
            <option value="github">github</option>
          </select>
          {target === "obsidian" ? (
            <label>
              <input
                type="checkbox"
                checked={obsidianEnhanced}
                onChange={(event) => setObsidianEnhanced(event.target.checked)}
              />{" "}
              Enhanced Obsidian format (frontmatter + tags + media handling)
            </label>
          ) : null}
          <button
            disabled={!collectionsEnabled || !collectionId}
            onClick={() =>
              void runIfFeatureEnabled(collectionsEnabled, setError, async () => {
                const payload = await api.exportCollection(
                  apiBaseUrl,
                  collectionId,
                  target,
                  target === "obsidian" ? (obsidianEnhanced ? "enhanced" : "basic") : undefined,
                );
                setResult(payload);
              })
            }
          >
            Start Export
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
