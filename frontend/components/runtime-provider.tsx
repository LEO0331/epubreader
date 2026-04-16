"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

import {
  RuntimeMode,
  loadApiKey,
  getInitialApiBaseUrl,
  loadApiBaseUrl,
  loadRuntimeMode,
  saveApiKey,
  saveApiBaseUrl,
  saveRuntimeMode,
} from "@/lib/runtime";

type RuntimeContextValue = {
  mode: RuntimeMode;
  setMode: (mode: RuntimeMode) => void;
  apiBaseUrl: string;
  setApiBaseUrl: (url: string) => void;
  apiKey: string;
  setApiKey: (value: string) => void;
};

const RuntimeContext = createContext<RuntimeContextValue | undefined>(undefined);

export function RuntimeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setModeState] = useState<RuntimeMode>("api");
  const [apiBaseUrl, setApiBaseUrlState] = useState<string>(getInitialApiBaseUrl());
  const [apiKey, setApiKeyState] = useState<string>("");

  useEffect(() => {
    setModeState(loadRuntimeMode());
    setApiBaseUrlState(loadApiBaseUrl());
    setApiKeyState(loadApiKey());
  }, []);

  const value = useMemo<RuntimeContextValue>(
    () => ({
      mode,
      setMode: (nextMode) => {
        setModeState(nextMode);
        saveRuntimeMode(nextMode);
      },
      apiBaseUrl,
      setApiBaseUrl: (url) => {
        setApiBaseUrlState(url);
        saveApiBaseUrl(url);
      },
      apiKey,
      setApiKey: (value) => {
        setApiKeyState(value);
        saveApiKey(value);
      },
    }),
    [mode, apiBaseUrl, apiKey],
  );

  return <RuntimeContext.Provider value={value}>{children}</RuntimeContext.Provider>;
}

export function useRuntime(): RuntimeContextValue {
  const context = useContext(RuntimeContext);
  if (!context) {
    throw new Error("useRuntime must be used inside RuntimeProvider");
  }
  return context;
}
