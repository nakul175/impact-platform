import { useRef } from "react";

/**
 * One operation identifier per pending action, so that a retry after a lost response or a
 * network failure repeats the exact command and the server returns the original receipt
 * instead of applying it again or rejecting it as stale. The identifier is reused while the
 * action key and payload are unchanged, replaced when the user changes the payload, and
 * released once the command succeeds.
 */
export function usePendingOperations() {
  const pending = useRef(new Map<string, { payload: string; id: string }>());
  return {
    id(action: string, payload: unknown) {
      const fingerprint = JSON.stringify(payload);
      const current = pending.current.get(action);
      if (current && current.payload === fingerprint) return current.id;
      const id = crypto.randomUUID();
      pending.current.set(action, { payload: fingerprint, id });
      return id;
    },
    done(action: string) {
      pending.current.delete(action);
    },
  };
}
