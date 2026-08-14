import type { EvidenceStrength } from "../api/types";
import { STRENGTH_CONFIG } from "../lib/verdict";

export default function EvidenceStrengthMeter({ strength }: { strength: EvidenceStrength }) {
  const cfg = STRENGTH_CONFIG[strength];
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs font-medium uppercase tracking-wider text-slate-400 whitespace-nowrap">
        Evidence Strength
      </span>
      <div className="flex-1 h-1.5 rounded-full bg-white/[0.06] overflow-hidden min-w-[80px] max-w-[140px]">
        <div
          className={`h-full rounded-full ${cfg.color} transition-all duration-700 ease-out`}
          style={{ width: `${cfg.pct}%` }}
        />
      </div>
      <span className="text-xs font-semibold text-slate-200">{cfg.label}</span>
    </div>
  );
}
