import { X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface PdfViewerModalProps {
  url: string | null;
  mimeType?: string;
  title: string;
  onClose: () => void;
}

export function PdfViewerModal({ url, title, onClose }: PdfViewerModalProps) {
  if (!url) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="flex h-[90vh] w-full max-w-4xl flex-col rounded-lg border border-border bg-card shadow-lg">
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <h2 className="text-sm font-semibold">{title}</h2>
          <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close preview">
            <X className="h-4 w-4" />
          </Button>
        </div>
        <iframe src={url} title={title} className="flex-1 w-full border-0" />
      </div>
    </div>
  );
}
