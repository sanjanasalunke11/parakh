import { ExternalLink } from "lucide-react";
import type { EvidenceItemOut } from "../api/types";
import { domainOf } from "../lib/format";
import { RELIABILITY_CONFIG } from "../lib/verdict";

export default function SourceList({ sources }: { sources: EvidenceItemOut[] }) {
  if (sources.length === 0) {
    return (
      <p className="text-sm text-slate-500 italic">
        No corroborating sources were found for this claim.
      </p>
    );
  }

  return (
    <ul className="space-y-2.5">
      {sources.map((source, idx) => {
        const rel = RELIABILITY_CONFIG[source.reliability];
        return (
          <li
            key={idx}
            className="group rounded-xl border border-white/[0.06] bg-white/[0.02] p-3.5 transition hover:bg-white/[0.04] hover:border-white/[0.12]"
          >
            <a
              href={source.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-start justify-between gap-3"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-semibold text-sm text-slate-100 truncate">{source.source_name}</span>
                  <span className={`tag-pill px-2 py-0.5 text-[10px] ${rel.bg} ${rel.border} ${rel.text}`}>
                    {rel.label}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">{domainOf(source.source_url)}</p>
                <p className="text-sm text-slate-400 mt-1.5 line-clamp-2">{source.snippet}</p>
              </div>
              <ExternalLink className="w-4 h-4 text-slate-500 group-hover:text-brand-400 shrink-0 mt-0.5 transition" />
            </a>
          </li>
        );
      })}
    </ul>
  );
}
