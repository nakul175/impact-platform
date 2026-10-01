import type React from "react";
// Arrow-key movement between the tabs of a role="tablist" (WAI-ARIA tabs pattern, manual
// activation): Left/Right (and Up/Down) move focus, Home/End jump to the ends, and Enter or
// Space activates the focused tab as before. Every tab also stays reachable with Tab.
export function tabListKeys(e: React.KeyboardEvent<HTMLElement>) {
  const tabs = Array.from(
    e.currentTarget.querySelectorAll<HTMLElement>('[role="tab"]'),
  );
  const index = tabs.indexOf(document.activeElement as HTMLElement);
  if (index < 0) return;
  const next = {
    ArrowRight: index + 1,
    ArrowDown: index + 1,
    ArrowLeft: index - 1,
    ArrowUp: index - 1,
    Home: 0,
    End: tabs.length - 1,
  }[e.key];
  if (next === undefined) return;
  e.preventDefault();
  tabs[(next + tabs.length) % tabs.length].focus();
}
