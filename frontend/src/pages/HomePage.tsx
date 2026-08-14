import { useState } from "react";
import { verifyImage, verifyText, verifyUrl, verifyVoice } from "../api/client";
import type { ClaimResult } from "../api/types";
import ErrorBanner from "../components/ErrorBanner";
import LoadingSpinner from "../components/LoadingSpinner";
import ImagePanel from "../components/panels/ImagePanel";
import TextPanel from "../components/panels/TextPanel";
import UrlPanel from "../components/panels/UrlPanel";
import VoicePanel from "../components/panels/VoicePanel";
import ResultCard from "../components/ResultCard";
import VerifyTabs, { type VerifyTab } from "../components/VerifyTabs";

export default function HomePage() {
  const [tab, setTab] = useState<VerifyTab>("text");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ClaimResult | null>(null);

  const runVerification = async (fn: () => Promise<ClaimResult>) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await fn();
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-4 md:px-6 py-12 md:py-20">
      <div className="text-center mb-10 animate-fade-in">
        <div className="inline-flex items-center gap-1.5 tag-pill border-brand-400/20 bg-brand-500/5 text-brand-300 mb-5">
          <span className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-pulse" />
          The Truth Agent — now in your browser
        </div>
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-white">
          Para<span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-400 to-brand-glow">kh</span>
        </h1>
        <p className="mt-4 text-lg md:text-xl text-slate-400 font-medium">
          Before you believe it. <span className="text-slate-200">Verify it.</span>
        </p>
      </div>

      <div className="glass-panel p-5 md:p-7 animate-rise">
        <VerifyTabs active={tab} onChange={setTab} />

        <div className="mt-6">
          {tab === "text" && (
            <TextPanel disabled={loading} onSubmit={(text) => runVerification(() => verifyText(text))} />
          )}
          {tab === "image" && (
            <ImagePanel disabled={loading} onSubmit={(file) => runVerification(() => verifyImage(file))} />
          )}
          {tab === "url" && (
            <UrlPanel disabled={loading} onSubmit={(url) => runVerification(() => verifyUrl(url))} />
          )}
          {tab === "voice" && (
            <VoicePanel
              disabled={loading}
              onSubmit={(text, language) => runVerification(() => verifyVoice(text, language))}
            />
          )}
        </div>
      </div>

      <div className="mt-8 space-y-4">
        {loading && <LoadingSpinner />}
        {error && !loading && <ErrorBanner message={error} />}
        {result && !loading && <ResultCard result={result} />}
      </div>
    </div>
  );
}
