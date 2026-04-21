import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import CollectionsPage from "@/app/collections/page";

const exportCollectionMock = vi.fn(async () => ({ ok: true }));

afterEach(() => {
  cleanup();
  exportCollectionMock.mockClear();
});

vi.mock("@/components/runtime-provider", () => ({
  useRuntime: () => ({
    mode: "api",
    apiBaseUrl: "https://backend.example.com",
  }),
}));

vi.mock("@/lib/api", () => ({
  api: {
    exportCollection: (...args: unknown[]) => exportCollectionMock(...args),
    createCollection: vi.fn(async () => ({})),
    listCollections: vi.fn(async () => []),
    addBookToCollection: vi.fn(async () => ({})),
  },
}));

vi.mock("@/lib/mode-guard", () => ({
  runIfFeatureEnabled: async (
    _enabled: boolean,
    _setError: (value: string) => void,
    fn: () => Promise<void>,
  ) => {
    await fn();
  },
}));

describe("collections export UI", () => {
  it("shows enhanced toggle only when obsidian target is selected", () => {
    render(<CollectionsPage />);

    expect(
      screen.queryByText("Enhanced Obsidian format (frontmatter + tags + media handling)"),
    ).toBeNull();

    fireEvent.change(screen.getByRole("combobox"), { target: { value: "obsidian" } });

    expect(
      screen.getByText("Enhanced Obsidian format (frontmatter + tags + media handling)"),
    ).toBeTruthy();
  });

  it("sends enhanced profile when toggle is enabled", async () => {
    render(<CollectionsPage />);

    fireEvent.change(screen.getByPlaceholderText("Collection ID"), { target: { value: "col-1" } });
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "obsidian" } });
    fireEvent.click(
      screen.getByLabelText("Enhanced Obsidian format (frontmatter + tags + media handling)"),
    );
    fireEvent.click(screen.getByText("Start Export"));

    await waitFor(() => {
      expect(exportCollectionMock).toHaveBeenCalledWith(
        "https://backend.example.com",
        "col-1",
        "obsidian",
        "enhanced",
      );
    });
  });
});
