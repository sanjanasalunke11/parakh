import { FileText, Image as ImageIcon, Link2, Mic, RotateCcw } from "lucide-react";
import type { InputType, LedgerListItem } from "../api/types";
import { formatRelativeTime, truncate } from "../lib/format";
import VerdictBadge from "./VerdictBadge";

const INPUT_ICONS: Record<InputType, typeof FileText> = {
  text: FileText,
  image: ImageIcon,
  url: Link2,
  voice: Mic,
};

export default function LedgerRow({ item, onClick }: { item: LedgerListItem; onClick?: () => void }) {
  const Icon = INPUT_ICONS[item.input_type];
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-3 rounded-xl border border-white/[0.05] bg-white/[0.015] px-4 py-3 text-left transition hover:bg-white/[0.04] hover:border-white/[0.1]"
    >
      <Icon className="w-4 h-4 text-slate-500 shrink-0" />
      <p className="text-sm text-slate-200 flex-1 min-w-0 truncate">{truncate(item.normalized_claim, 90)}</p>
      <span className="tag-pill border-white/10 bg-white/[0.03] text-slate-400 hidden sm:inline-flex shrink-0">
        {item.category}
      </span>
      {item.check_count > 1 && (
        <span className="hidden md:inline-flex items-center gap-1 text-xs text-slate-500 shrink-0">
          <RotateCcw className="w-3 h-3" />
          {item.check_count}
        </span>
      )}
      <span className="text-xs text-slate-500 shrink-0 hidden sm:inline">{formatRelativeTime(item.created_at)}</span>
      <VerdictBadge verdict={item.verdict} size="sm" />
    </button>
  );
}
