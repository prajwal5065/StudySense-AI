import { useState, useCallback } from "react";

type AsyncState<T> =
  | { status: "idle"; data: null; error: null }
  | { status: "loading"; data: null; error: null }
  | { status: "success"; data: T; error: null }
  | { status: "error"; data: null; error: string };

/**
 * Hook for managing async operations with typed loading/error/success states.
 */
export function useAsync<T>() {
  const [state, setState] = useState<AsyncState<T>>({
    status: "idle",
    data: null,
    error: null,
  });

  const execute = useCallback(async (promise: Promise<T>) => {
    setState({ status: "loading", data: null, error: null });
    try {
      const data = await promise;
      setState({ status: "success", data, error: null });
      return data;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      setState({ status: "error", data: null, error: message });
      throw err;
    }
  }, []);

  const reset = useCallback(() => {
    setState({ status: "idle", data: null, error: null });
  }, []);

  return { ...state, execute, reset };
}
