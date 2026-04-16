export type IngestResponse = { book_id: string; job_id: string };
export type JobResponse = { id: string; status: string; payload?: Record<string, unknown> };

export type BookSummary = {
  id: string;
  title: string;
  source_type: string;
  source_ref: string;
  ingest_status: string;
  parse_quality_score?: number | null;
};

export type SectionsResponse = {
  book_id: string;
  count: number;
  limit: number;
  offset: number;
  sections: Array<Record<string, unknown>>;
};

export type ChunksResponse = {
  book_id: string;
  count: number;
  limit: number;
  offset: number;
  section_id?: string | null;
  chunks: Array<Record<string, unknown>>;
};

export type ArtifactRecord = {
  id: string;
  artifact_type: string;
  path: string;
  created_at: string;
  metadata?: Record<string, unknown>;
};

export type QueryResponse = {
  answer: string;
  citations: Array<Record<string, unknown>>;
  diagnostics?: Record<string, unknown>;
};

async function request<T>(
  apiBaseUrl: string,
  path: string,
  init?: RequestInit,
): Promise<T> {
  const url = `${apiBaseUrl.replace(/\/$/, "")}/api/v1${path}`;
  const response = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    }
  });

  if (!response.ok) {
    let errorDetail = `Request failed (${response.status})`;
    try {
      const payload = (await response.json()) as { detail?: string; request_id?: string };
      if (payload.detail) {
        errorDetail = payload.detail;
      }
      if (payload.request_id) {
        errorDetail = `${errorDetail} [request_id=${payload.request_id}]`;
      }
    } catch {
      // Keep default text when response is not JSON.
    }
    throw new Error(errorDetail);
  }

  return (await response.json()) as T;
}

export const api = {
  health(apiBaseUrl: string) {
    return request<Record<string, unknown>>(apiBaseUrl, "/health", { method: "GET" });
  },
  ingestUrl(apiBaseUrl: string, payload: { url: string; source_type?: string }) {
    return request<IngestResponse>(apiBaseUrl, "/ingest/url", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  async ingestUpload(apiBaseUrl: string, file: File): Promise<IngestResponse> {
    const url = `${apiBaseUrl.replace(/\/$/, "")}/api/v1/ingest/upload`;
    const form = new FormData();
    form.append("file", file);

    const response = await fetch(url, {
      method: "POST",
      body: form
    });

    if (!response.ok) {
      let detail = `Upload failed (${response.status})`;
      try {
        const payload = (await response.json()) as { detail?: string };
        if (payload.detail) {
          detail = payload.detail;
        }
      } catch {
        // Keep default detail.
      }
      throw new Error(detail);
    }

    return (await response.json()) as IngestResponse;
  },
  getJob(apiBaseUrl: string, jobId: string) {
    return request<JobResponse>(apiBaseUrl, `/jobs/${jobId}`, { method: "GET" });
  },
  listBooks(apiBaseUrl: string, limit = 50, offset = 0) {
    return request<BookSummary[]>(
      apiBaseUrl,
      `/books?limit=${limit}&offset=${offset}`,
      { method: "GET" },
    );
  },
  getBook(apiBaseUrl: string, bookId: string) {
    return request<Record<string, unknown>>(apiBaseUrl, `/books/${bookId}`, { method: "GET" });
  },
  getSections(apiBaseUrl: string, bookId: string, limit = 20, offset = 0) {
    return request<SectionsResponse>(
      apiBaseUrl,
      `/books/${bookId}/sections?limit=${limit}&offset=${offset}`,
      { method: "GET" },
    );
  },
  getChunks(apiBaseUrl: string, bookId: string, limit = 20, offset = 0, sectionId?: string) {
    const sectionQuery = sectionId ? `&section_id=${encodeURIComponent(sectionId)}` : "";
    return request<ChunksResponse>(
      apiBaseUrl,
      `/books/${bookId}/chunks?limit=${limit}&offset=${offset}${sectionQuery}`,
      { method: "GET" },
    );
  },
  buildArtifacts(apiBaseUrl: string, bookId: string, includeSkill: boolean) {
    return request<Record<string, unknown>>(apiBaseUrl, `/books/${bookId}/artifacts/build`, {
      method: "POST",
      body: JSON.stringify({ include_skill: includeSkill })
    });
  },
  listArtifacts(apiBaseUrl: string, bookId: string) {
    return request<ArtifactRecord[]>(apiBaseUrl, `/books/${bookId}/artifacts`, { method: "GET" });
  },
  getArtifact(apiBaseUrl: string, bookId: string, artifactType: string) {
    return request<Record<string, unknown>>(
      apiBaseUrl,
      `/books/${bookId}/artifacts/${encodeURIComponent(artifactType)}`,
      { method: "GET" },
    );
  },
  previewQuery(apiBaseUrl: string, payload: Record<string, unknown>) {
    return request<Record<string, unknown>>(apiBaseUrl, "/query/preview", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  runQuery(apiBaseUrl: string, payload: Record<string, unknown>) {
    return request<QueryResponse>(apiBaseUrl, "/query", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  createCollection(apiBaseUrl: string, name: string) {
    return request<Record<string, unknown>>(apiBaseUrl, "/collections", {
      method: "POST",
      body: JSON.stringify({ name })
    });
  },
  listCollections(apiBaseUrl: string) {
    return request<Array<Record<string, unknown>>>(apiBaseUrl, "/collections", { method: "GET" });
  },
  addBookToCollection(apiBaseUrl: string, collectionId: string, bookId: string) {
    return request<Record<string, unknown>>(apiBaseUrl, `/collections/${collectionId}/books`, {
      method: "POST",
      body: JSON.stringify({ book_id: bookId })
    });
  },
  exportCollection(apiBaseUrl: string, collectionId: string, target: "filesystem" | "obsidian" | "github") {
    return request<Record<string, unknown>>(apiBaseUrl, `/collections/${collectionId}/export`, {
      method: "POST",
      body: JSON.stringify({ target })
    });
  }
};
