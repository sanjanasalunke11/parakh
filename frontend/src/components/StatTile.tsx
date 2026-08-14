import type { LucideIcon } from "lucide-react";

export default function StatTile({
  label,
  value,
  icon: Icon,
  accent,
}: {
  label: string;
  value: number | string;
  icon: LucideIcon;
  accent: string;
}) {
  return (
    <div className="glass-card p-5 flex items-center gap-4">
      <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${accent}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div className="min-w-0">
        <p className="text-2xl font-extrabold text-white tabular-nums">{value}</p>
        <p className="text-xs text-slate-500 font-medium truncate">{label}</p>
      </div>
    </div>
  );
}
