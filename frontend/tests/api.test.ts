import { afterEach, describe, expect, it, vi } from "vitest";

import { api } from "@/lib/api";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("api client", () => {
  it("posts ingest url payload to expected endpoint", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch" as never).mockResolvedValue({
      ok: true,
      json: async () => ({ book_id: "b1", job_id: "j1" }),
    } as Response);

    const result = await api.ingestUrl("https://backend.example.com", {
      url: "https://books.miz.com.tw/read/abc",
      source_type: "miz_books",
    });

    expect(result.book_id).toBe("b1");
    expect(result.job_id).toBe("j1");
    expect(fetchMock).toHaveBeenCalledWith(
      "https://backend.example.com/api/v1/ingest/url",
      expect.objectContaining({
        method: "POST",
      }),
    );
    expect((fetchMock.mock.calls[0]?.[1] as RequestInit).body).toBe(
      JSON.stringify({ url: "https://books.miz.com.tw/read/abc", source_type: "miz_books" }),
    );
  });

  it("posts query answer payload to expected endpoint", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch" as never).mockResolvedValue({
      ok: true,
      json: async () => ({ answer: "ok", citations: [] }),
    } as Response);

    const payload = { question: "what is this", top_k: 5 };
    const result = await api.runQuery("http://127.0.0.1:8000", payload);

    expect(result.answer).toBe("ok");
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/v1/query",
      expect.objectContaining({ method: "POST", body: JSON.stringify(payload) }),
    );
  });

  it("includes request id detail from JSON error", async () => {
    vi.spyOn(globalThis, "fetch" as never).mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({ detail: "boom", request_id: "req-123" }),
    } as Response);

    await expect(api.health("http://127.0.0.1:8000")).rejects.toThrow("boom [request_id=req-123]");
  });
});
