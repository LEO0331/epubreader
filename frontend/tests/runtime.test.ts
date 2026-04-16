import { describe, expect, it } from "vitest";

import { isFeatureEnabled, parserModeMessage } from "@/lib/runtime";

describe("runtime mode gating", () => {
  it("enables all features in api mode", () => {
    expect(isFeatureEnabled("api", "query")).toBe(true);
    expect(isFeatureEnabled("api", "artifacts")).toBe(true);
    expect(isFeatureEnabled("api", "collections")).toBe(true);
  });

  it("restricts query/artifacts/collections in parser mode", () => {
    expect(isFeatureEnabled("parser", "ingest")).toBe(true);
    expect(isFeatureEnabled("parser", "books")).toBe(true);
    expect(isFeatureEnabled("parser", "query")).toBe(false);
    expect(isFeatureEnabled("parser", "artifacts")).toBe(false);
    expect(isFeatureEnabled("parser", "collections")).toBe(false);
  });

  it("returns parser mode explanation text", () => {
    expect(parserModeMessage()).toContain("Parser mode only supports ingestion");
  });
});
