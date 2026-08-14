import { Sparkles } from "lucide-react";
import { useState } from "react";

const EXAMPLES = [
  "Good morning! Please forward: 5G towers are spreading coronavirus, share with everyone!",
  "The RBI has banned the 2000 rupee note and it is now worthless paper.",
  "PM Kisan Yojana gives 6000 rupees per year to eligible farmers.",
];

export default function TextPanel({
  onSubmit,
  disabled,
}: {
  onSubmit: (text: string) => void;
  disabled: boolean;
}) {
  const [text, setText] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim().length < 3) return;
    onSubmit(text.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste the forwarded message, headline, or claim you want to check…"
        rows={5}
        className="input-field resize-none"
        maxLength={5000}
      />
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex flex-wrap gap-2">
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              type="button"
              onClick={() => setText(ex)}
              className="tag-pill border-white/10 bg-white/[0.02] text-slate-500 hover:text-slate-300 hover:border-white/20 transition"
            >
              <Sparkles className="w-3 h-3" />
              {ex.length > 42 ? ex.slice(0, 42) + "…" : ex}
            </button>
          ))}
        </div>
        <button type="submit" disabled={disabled || text.trim().length < 3} className="btn-primary w-full sm:w-auto">
          Verify Claim
        </button>
      </div>
    </form>
  );
}
