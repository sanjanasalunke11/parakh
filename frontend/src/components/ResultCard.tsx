import { History, Volume2, VolumeX } from "lucide-react";
import { useEffect } from "react";
import type { ClaimResult } from "../api/types";
import { useSpeechSynthesis } from "../hooks/useSpeech";
import { VERDICT_CONFIG } from "../lib/verdict";
import EvidenceStrengthMeter from "./EvidenceStrengthMeter";
import ShareButton from "./ShareButton";
import SourceList from "./SourceList";
import VerdictBadge from "./VerdictBadge";

export default function ResultCard({ result }: { result: ClaimResult }) {
  const cfg = VERDICT_CONFIG[result.verdict];
  const { isSupported, isSpeaking, speak, cancel } = useSpeechSynthesis();

  useEffect(() => cancel, [result.id, cancel]);

  const handleListen = () => {
    if (isSpeaking) {
      cancel();
      return;
    }
    const spoken = `Verdict: ${VERDICT_CONFIG[result.verdict].label}. ${result.explanation}`;
    speak(spoken, "en");
  };

  return (
    <div
      className={`glass-card ${cfg.glow} p-6 md:p-8 animate-rise`}
      key={result.id}
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-center gap-3 flex-wrap">
          <VerdictBadge verdict={result.verdict} size="lg" />
          {result.previously_verified && (
            <span className="tag-pill border-brand-400/30 bg-brand-500/10 text-brand-300">
              <History className="w-3.5 h-3.5" />
              Checked {result.check_count}× before
            </span>
          )}
          <span className="tag-pill border-white/10 bg-white/[0.03] text-slate-400">{result.category}</span>
        </div>

        <div className="flex items-center gap-2">
          {isSupported && (
            <button onClick={handleListen} className="btn-ghost !rounded-full !px-4 !py-2 text-sm">
              {isSpeaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              {isSpeaking ? "Stop" : "Listen to explanation"}
            </button>
          )}
          <ShareButton result={result} />
        </div>
      </div>

      <div className="mt-6">
        <p className="text-xs font-medium uppercase tracking-wider text-slate-500 mb-1.5">Claim analyzed</p>
        <p className="text-lg md:text-xl font-semibold text-slate-50 leading-snug">
          "{result.normalized_claim}"
        </p>
        {result.original_text !== result.normalized_claim && (
          <p className="text-xs text-slate-500 mt-2 line-clamp-2">Original input: {result.original_text}</p>
        )}
      </div>

      <div className="mt-5">
        <EvidenceStrengthMeter strength={result.evidence_strength} />
      </div>

      <div className="mt-6 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
        <p className="text-xs font-medium uppercase tracking-wider text-slate-500 mb-2">Explanation</p>
        <p className="text-sm text-slate-300 leading-relaxed">{result.explanation}</p>
      </div>

      <div className="mt-6">
        <p className="text-xs font-medium uppercase tracking-wider text-slate-500 mb-3">
          Sources ({result.sources.length})
        </p>
        <SourceList sources={result.sources} />
      </div>
    </div>
  );
}
