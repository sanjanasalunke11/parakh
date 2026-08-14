import { Link2 } from "lucide-react";
import { useState } from "react";

export default function UrlPanel({
  onSubmit,
  disabled,
}: {
  onSubmit: (url: string) => void;
  disabled: boolean;
}) {
  const [url, setUrl] = useState("");

  const isValid = /^https?:\/\/.+\..+/i.test(url.trim());

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid) return;
    onSubmit(url.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="relative">
        <Link2 className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/news/article-to-verify"
          className="input-field pl-11"
        />
      </div>
      <p className="text-xs text-slate-500">
        We'll fetch the article, extract its key claims, and verify them against reliable sources.
      </p>
      <div className="flex justify-end">
        <button type="submit" disabled={disabled || !isValid} className="btn-primary w-full sm:w-auto">
          Fetch &amp; Verify
        </button>
      </div>
    </form>
  );
}
