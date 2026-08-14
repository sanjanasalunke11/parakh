import { ImageUp, X } from "lucide-react";
import { useRef, useState } from "react";

export default function ImagePanel({
  onSubmit,
  disabled,
}: {
  onSubmit: (file: File) => void;
  disabled: boolean;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const acceptFile = (f: File | undefined | null) => {
    if (!f || !f.type.startsWith("image/")) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
  };

  const clear = () => {
    setFile(null);
    setPreview(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (file) onSubmit(file);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          acceptFile(e.dataTransfer.files?.[0]);
        }}
        onClick={() => inputRef.current?.click()}
        className={`relative rounded-xl border-2 border-dashed transition cursor-pointer overflow-hidden ${
          isDragging ? "border-brand-400 bg-brand-500/5" : "border-white/10 hover:border-white/20"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => acceptFile(e.target.files?.[0])}
        />

        {preview ? (
          <div className="relative">
            <img src={preview} alt="Selected screenshot preview" className="w-full max-h-72 object-contain bg-base-950" />
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                clear();
              }}
              className="absolute top-2 right-2 p-1.5 rounded-full bg-black/60 text-white hover:bg-black/80"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center gap-2 py-14 text-center px-4">
            <div className="w-12 h-12 rounded-xl bg-white/[0.04] flex items-center justify-center">
              <ImageUp className="w-6 h-6 text-slate-400" />
            </div>
            <p className="text-sm font-medium text-slate-300">Drop a screenshot here, or click to browse</p>
            <p className="text-xs text-slate-500">WhatsApp forwards, news screenshots, social posts — PNG/JPG up to 8MB</p>
          </div>
        )}
      </div>

      <div className="flex justify-end">
        <button type="submit" disabled={disabled || !file} className="btn-primary w-full sm:w-auto">
          Extract &amp; Verify
        </button>
      </div>
    </form>
  );
}
