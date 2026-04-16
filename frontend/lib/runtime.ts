export type RuntimeMode = "api" | "parser";

export type Feature =
  | "ingest"
  | "books"
  | "sections"
  | "chunks"
  | "artifacts"
  | "query"
  | "collections";

const RUNTIME_MODE_KEY = "bookqa.runtime_mode";
const API_BASE_URL_KEY = "bookqa.api_base_url";
const API_KEY_VALUE_KEY = "bookqa.api_key";

const PARSER_ALLOWED: Feature[] = ["ingest", "books", "sections", "chunks"];

export function isFeatureEnabled(mode: RuntimeMode, feature: Feature): boolean {
  if (mode === "api") {
    return true;
  }
  return PARSER_ALLOWED.includes(feature);
}

export function parserModeMessage(): string {
  return "Parser mode only supports ingestion/parsing/chunk inspection.";
}

export function getInitialApiBaseUrl(): string {
  const envUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (envUrl && envUrl.trim().length > 0) {
    return envUrl.trim();
  }
  return "http://127.0.0.1:8000";
}

export function loadRuntimeMode(): RuntimeMode {
  if (typeof window === "undefined") {
    return "api";
  }
  const raw = window.localStorage.getItem(RUNTIME_MODE_KEY);
  return raw === "parser" ? "parser" : "api";
}

export function saveRuntimeMode(mode: RuntimeMode): void {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(RUNTIME_MODE_KEY, mode);
  }
}

export function loadApiBaseUrl(): string {
  if (typeof window === "undefined") {
    return getInitialApiBaseUrl();
  }
  const raw = window.localStorage.getItem(API_BASE_URL_KEY);
  if (raw && raw.trim().length > 0) {
    return raw.trim();
  }
  return getInitialApiBaseUrl();
}

export function saveApiBaseUrl(url: string): void {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(API_BASE_URL_KEY, url.trim());
  }
}

export function loadApiKey(): string {
  if (typeof window === "undefined") {
    return "";
  }
  return window.localStorage.getItem(API_KEY_VALUE_KEY)?.trim() ?? "";
}

export function saveApiKey(value: string): void {
  if (typeof window !== "undefined") {
    const clean = value.trim();
    if (clean.length === 0) {
      window.localStorage.removeItem(API_KEY_VALUE_KEY);
    } else {
      window.localStorage.setItem(API_KEY_VALUE_KEY, clean);
    }
  }
}
