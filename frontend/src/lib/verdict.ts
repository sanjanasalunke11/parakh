import type { EvidenceStrength, ReliabilityTier, Verdict } from "../api/types";

export const VERDICT_CONFIG: Record<
  Verdict,
  { label: string; emoji: string; text: string; bg: string; border: string; glow: string }
> = {
  VERIFIED: {
    label: "Verified",
    emoji: "🟢",
    text: "text-verdict-verified",
    bg: "bg-verdict-verified/10",
    border: "border-verdict-verified/30",
    glow: "shadow-[0_0_40px_-12px_rgba(45,212,167,0.5)]",
  },
  FALSE: {
    label: "False",
    emoji: "🔴",
    text: "text-verdict-false",
    bg: "bg-verdict-false/10",
    border: "border-verdict-false/30",
    glow: "shadow-[0_0_40px_-12px_rgba(251,111,146,0.5)]",
  },
  MISLEADING: {
    label: "Misleading",
    emoji: "🟡",
    text: "text-verdict-misleading",
    bg: "bg-verdict-misleading/10",
    border: "border-verdict-misleading/30",
    glow: "shadow-[0_0_40px_-12px_rgba(246,196,83,0.5)]",
  },
  UNVERIFIED: {
    label: "Unverified",
    emoji: "⚪",
    text: "text-verdict-unverified",
    bg: "bg-verdict-unverified/10",
    border: "border-verdict-unverified/30",
    glow: "shadow-[0_0_40px_-12px_rgba(148,163,184,0.4)]",
  },
};

export const STRENGTH_CONFIG: Record<EvidenceStrength, { label: string; pct: number; color: string }> = {
  HIGH: { label: "High", pct: 100, color: "bg-emerald-400" },
  MEDIUM: { label: "Medium", pct: 60, color: "bg-amber-400" },
  LOW: { label: "Low", pct: 25, color: "bg-slate-500" },
};

export const RELIABILITY_CONFIG: Record<ReliabilityTier, { label: string; text: string; bg: string; border: string }> = {
  HIGH: { label: "High reliability", text: "text-emerald-300", bg: "bg-emerald-400/10", border: "border-emerald-400/30" },
  MEDIUM: { label: "Medium reliability", text: "text-amber-300", bg: "bg-amber-400/10", border: "border-amber-400/30" },
  LOW: { label: "Low reliability", text: "text-slate-300", bg: "bg-slate-400/10", border: "border-slate-400/30" },
};
