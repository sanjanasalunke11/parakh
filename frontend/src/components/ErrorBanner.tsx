import { AlertCircle } from "lucide-react";

export default function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-rose-400/20 bg-rose-400/5 p-4 animate-fade-in">
      <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
      <p className="text-sm text-rose-200">{message}</p>
    </div>
  );
}
