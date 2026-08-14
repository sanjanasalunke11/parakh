import { Mic, Square } from "lucide-react";
import { useEffect, useState } from "react";
import { useSpeechRecognition, type VoiceLanguage } from "../../hooks/useSpeech";

export default function VoicePanel({
  onSubmit,
  disabled,
}: {
  onSubmit: (text: string, language: VoiceLanguage) => void;
  disabled: boolean;
}) {
  const [language, setLanguage] = useState<VoiceLanguage>("en");
  const { isSupported, isListening, transcript, error, start, stop, setTranscript } =
    useSpeechRecognition(language);

  useEffect(() => {
    setTranscript("");
  }, [language, setTranscript]);

  const handleSubmit = () => {
    if (transcript.trim().length < 3) return;
    onSubmit(transcript.trim(), language);
  };

  if (!isSupported) {
    return (
      <div className="rounded-xl border border-amber-400/20 bg-amber-400/5 p-5 text-sm text-amber-200">
        Voice input needs the Web Speech API, which isn't available in this browser. Try Chrome
        or Edge on desktop or Android — or use the Text tab instead.
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-center gap-2">
        {(["en", "hi"] as VoiceLanguage[]).map((lang) => (
          <button
            key={lang}
            type="button"
            onClick={() => setLanguage(lang)}
            className={`px-4 py-1.5 rounded-full text-sm font-semibold transition ${
              language === lang
                ? "bg-brand-500 text-white shadow-glow"
                : "bg-white/[0.03] text-slate-400 hover:text-slate-200"
            }`}
          >
            {lang === "en" ? "English" : "हिन्दी"}
          </button>
        ))}
      </div>

      <div className="flex flex-col items-center gap-4 py-6">
        <button
          type="button"
          onClick={isListening ? stop : start}
          disabled={disabled}
          className={`relative w-20 h-20 rounded-full flex items-center justify-center transition ${
            isListening
              ? "bg-gradient-to-b from-rose-500 to-rose-600 shadow-[0_0_0_8px_rgba(244,63,94,0.15)]"
              : "bg-gradient-to-b from-brand-500 to-brand-600 shadow-glow"
          }`}
        >
          {isListening && <span className="absolute inset-0 rounded-full bg-rose-500/40 animate-ping" />}
          {isListening ? <Square className="w-7 h-7 text-white relative" /> : <Mic className="w-7 h-7 text-white relative" />}
        </button>
        <p className="text-sm text-slate-400">
          {isListening ? "Listening… tap to stop" : "Tap to speak your claim"}
        </p>
      </div>

      {error && <p className="text-sm text-rose-400 text-center">{error}</p>}

      {transcript && (
        <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500 mb-1.5">Heard</p>
          <p className="text-sm text-slate-200">{transcript}</p>
        </div>
      )}

      <div className="flex justify-end">
        <button
          type="button"
          onClick={handleSubmit}
          disabled={disabled || transcript.trim().length < 3}
          className="btn-primary w-full sm:w-auto"
        >
          Verify What I Said
        </button>
      </div>
    </div>
  );
}
