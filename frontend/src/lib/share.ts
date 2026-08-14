import type { ClaimResult } from "../api/types";
import { VERDICT_CONFIG } from "./verdict";

export function buildShareText(result: ClaimResult): string {
  const cfg = VERDICT_CONFIG[result.verdict];
  const lines = [
    `${cfg.emoji} *${cfg.label.toUpperCase()}* — checked with Parakh`,
    "",
    `Claim: "${result.normalized_claim}"`,
    "",
    result.explanation,
  ];

  if (result.sources.length > 0) {
    lines.push("", "Sources:");
    for (const source of result.sources.slice(0, 3)) {
      lines.push(`• ${source.source_name} — ${source.source_url}`);
    }
  }

  lines.push("", "Before you believe it. Verify it. 🔎");

  return lines.join("\n");
}

export function buildWhatsAppShareUrl(text: string): string {
  return `https://wa.me/?text=${encodeURIComponent(text)}`;
}
