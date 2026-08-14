import { FileText, Image as ImageIcon, Link2, Mic } from "lucide-react";

export type VerifyTab = "text" | "image" | "url" | "voice";

const TABS: { key: VerifyTab; label: string; icon: typeof FileText }[] = [
  { key: "text", label: "Text", icon: FileText },
  { key: "image", label: "Image", icon: ImageIcon },
  { key: "url", label: "URL", icon: Link2 },
  { key: "voice", label: "Voice", icon: Mic },
];

export default function VerifyTabs({
  active,
  onChange,
}: {
  active: VerifyTab;
  onChange: (tab: VerifyTab) => void;
}) {
  return (
    <div className="grid grid-cols-4 gap-1.5 p-1.5 rounded-2xl bg-base-900/60 border border-white/[0.06]">
      {TABS.map(({ key, label, icon: Icon }) => {
        const isActive = active === key;
        return (
          <button
            key={key}
            onClick={() => onChange(key)}
            className={`relative flex flex-col sm:flex-row items-center justify-center gap-1.5 rounded-xl px-3 py-3 sm:py-2.5 text-sm font-semibold transition-all ${
              isActive
                ? "bg-gradient-to-b from-brand-500 to-brand-600 text-white shadow-glow"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]"
            }`}
          >
            <Icon className="w-4 h-4" />
            <span>{label}</span>
          </button>
        );
      })}
    </div>
  );
}
