"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { useRuntime } from "@/components/runtime-provider";
import { api, ChunksResponse, SectionsResponse } from "@/lib/api";

const PAGE_SIZE = 10;

export default function BookDetailPage() {
  const params = useParams<{ bookId: string }>();
  const bookId = params.bookId;
  const { apiBaseUrl } = useRuntime();

  const [book, setBook] = useState<Record<string, unknown> | null>(null);
  const [sections, setSections] = useState<SectionsResponse | null>(null);
  const [chunks, setChunks] = useState<ChunksResponse | null>(null);
  const [sectionOffset, setSectionOffset] = useState(0);
  const [chunkOffset, setChunkOffset] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      setError("");
      try {
        const [bookPayload, sectionPayload, chunkPayload] = await Promise.all([
          api.getBook(apiBaseUrl, bookId),
          api.getSections(apiBaseUrl, bookId, PAGE_SIZE, sectionOffset),
          api.getChunks(apiBaseUrl, bookId, PAGE_SIZE, chunkOffset),
        ]);
        setBook(bookPayload);
        setSections(sectionPayload);
        setChunks(chunkPayload);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load book data");
      }
    };

    void load();
  }, [apiBaseUrl, bookId, sectionOffset, chunkOffset]);

  return (
    <div>
      <div className="card">
        <h2 className="page-title">Book Detail</h2>
        <p className="page-lead">Book ID: <span className="mono">{bookId}</span></p>
        <p>This page helps you confirm parsing quality before running AI features.</p>
        {book ? <pre>{JSON.stringify(book, null, 2)}</pre> : <p>Loading book information...</p>}
      </div>

      <div className="grid">
        <div className="card">
          <h3>Sections</h3>
          {sections ? (
            <>
              <p>Showing {sections.count} sections from offset {sections.offset}.</p>
              <pre>{JSON.stringify(sections.sections, null, 2)}</pre>
              <div className="row">
                <button
                  className="secondary"
                  onClick={() => setSectionOffset(Math.max(0, sectionOffset - PAGE_SIZE))}
                  disabled={sectionOffset === 0}
                >
                  Previous Page
                </button>
                <button
                  onClick={() => setSectionOffset(sectionOffset + PAGE_SIZE)}
                  disabled={sections.count < PAGE_SIZE}
                >
                  Next Page
                </button>
              </div>
            </>
          ) : (
            <p>Loading sections...</p>
          )}
        </div>

        <div className="card">
          <h3>Chunks</h3>
          {chunks ? (
            <>
              <p>Showing {chunks.count} chunks from offset {chunks.offset}.</p>
              <pre>{JSON.stringify(chunks.chunks, null, 2)}</pre>
              <div className="row">
                <button
                  className="secondary"
                  onClick={() => setChunkOffset(Math.max(0, chunkOffset - PAGE_SIZE))}
                  disabled={chunkOffset === 0}
                >
                  Previous Page
                </button>
                <button
                  onClick={() => setChunkOffset(chunkOffset + PAGE_SIZE)}
                  disabled={chunks.count < PAGE_SIZE}
                >
                  Next Page
                </button>
              </div>
            </>
          ) : (
            <p>Loading chunks...</p>
          )}
        </div>
      </div>

      {error ? <div className="card error">{error}</div> : null}
    </div>
  );
}
