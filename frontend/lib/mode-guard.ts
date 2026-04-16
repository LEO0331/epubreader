import { parserModeMessage } from "@/lib/runtime";

export async function runIfFeatureEnabled(
  enabled: boolean,
  setError: (value: string) => void,
  action: () => Promise<void>,
): Promise<void> {
  if (!enabled) {
    setError(parserModeMessage());
    return;
  }

  setError("");
  await action();
}
