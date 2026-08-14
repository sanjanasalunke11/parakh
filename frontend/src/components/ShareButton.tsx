import { Check, Copy, MessageCircle, Share2 } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { ClaimResult } from "../api/types";
import { buildShareText, buildWhatsAppShareUrl } from "../lib/share";

export default function ShareButton({ result }: { result: ClaimResult }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const canNativeShare = typeof navigator !== "undefined" && !!navigator.share;

  useEffect(() => {
    if (!menuOpen) return;
    const onClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, [menuOpen]);

  const handlePrimaryClick = async () => {
    const text = buildShareText(result);

    if (canNativeShare) {
      try {
        await navigator.share({ text });
        return;
      } catch {
        // user cancelled the native share sheet — no fallback needed
        return;
      }
    }

    setMenuOpen((open) => !open);
  };

  const handleWhatsApp = () => {
    window.open(buildWhatsAppShareUrl(buildShareText(result)), "_blank", "noopener,noreferrer");
    setMenuOpen(false);
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(buildShareText(result));
    setCopied(true);
    setMenuOpen(false);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative" ref={containerRef}>
      <button onClick={handlePrimaryClick} className="btn-ghost !rounded-full !px-4 !py-2 text-sm">
        {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Share2 className="w-4 h-4" />}
        {copied ? "Copied!" : "Share"}
      </button>

      {menuOpen && !canNativeShare && (
        <div className="absolute right-0 mt-2 w-56 rounded-xl border border-white/10 bg-base-850 shadow-card z-20 overflow-hidden animate-fade-in">
          <button
            onClick={handleWhatsApp}
            className="w-full flex items-center gap-2.5 px-4 py-3 text-sm text-slate-200 hover:bg-white/[0.06] transition"
          >
            <MessageCircle className="w-4 h-4 text-emerald-400" />
            Share to WhatsApp
          </button>
          <button
            onClick={handleCopy}
            className="w-full flex items-center gap-2.5 px-4 py-3 text-sm text-slate-200 hover:bg-white/[0.06] transition border-t border-white/[0.06]"
          >
            <Copy className="w-4 h-4 text-slate-400" />
            Copy summary
          </button>
        </div>
      )}
    </div>
  );
}
