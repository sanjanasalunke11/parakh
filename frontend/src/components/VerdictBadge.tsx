import type { Verdict } from "../api/types";
import { VERDICT_CONFIG } from "../lib/verdict";

export default function VerdictBadge({ verdict, size = "md" }: { verdict: Verdict; size?: "sm" | "md" | "lg" }) {
  const cfg = VERDICT_CONFIG[verdict];
  const sizing =
    size === "lg"
      ? "px-5 py-2.5 text-lg gap-2.5"
      : size === "sm"
      ? "px-2.5 py-1 text-xs gap-1"
      : "px-3.5 py-1.5 text-sm gap-1.5";

  return (
    <span
      className={`tag-pill ${sizing} ${cfg.bg} ${cfg.border} ${cfg.text} font-bold tracking-wide uppercase`}
    >
      <span className="text-[1.1em] leading-none">{cfg.emoji}</span>
      {cfg.label}
    </span>
  );
}
