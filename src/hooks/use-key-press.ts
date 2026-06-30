import { useEffect } from "react";

/**
 * Fires a callback when a specific keyboard key is pressed.
 */
export function useKeyPress(key: string, callback: (e: KeyboardEvent) => void) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === key) callback(e);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [key, callback]);
}
