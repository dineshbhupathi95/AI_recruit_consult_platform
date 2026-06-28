import { useState } from "react";
import { Eye } from "lucide-react";
import { PdfViewerModal } from "@/components/candidates/PdfViewerModal";
import { Button } from "@/components/ui/button";
import { candidateService } from "@/services/candidateService";

interface BuiltResumePreviewButtonProps {
  applicationId: string;
  versionId: string;
  candidateName: string;
}

export function BuiltResumePreviewButton({
  applicationId,
  versionId,
  candidateName,
}: BuiltResumePreviewButtonProps) {
  const [previewState, setPreviewState] = useState<{ url: string; mimeType: string } | null>(null);
  const [loading, setLoading] = useState(false);

  const closePreview = () => {
    if (previewState?.url) URL.revokeObjectURL(previewState.url);
    setPreviewState(null);
  };

  const openPreview = async () => {
    setLoading(true);
    const showPreview = (blob: Blob, mimeType: string) => {
      const url = URL.createObjectURL(new Blob([blob], { type: mimeType }));
      setPreviewState({ url, mimeType });
    };
    try {
      const pdfResponse = await candidateService.exportResume(applicationId, "pdf", versionId);
      showPreview(pdfResponse.data as Blob, "application/pdf");
      } catch {
        try {
          const htmlResponse = await candidateService.exportResume(applicationId, "html", versionId);
          showPreview(htmlResponse.data as Blob, "text/html");
        } catch {
          // Preview unavailable — user can open full pipeline page
        }
      } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        onClick={openPreview}
        disabled={loading}
        aria-label="View built resume"
        title="View built resume"
      >
        <Eye className="h-4 w-4" />
      </Button>
      <PdfViewerModal
        url={previewState?.url ?? null}
        mimeType={previewState?.mimeType}
        title={`${candidateName} — Built Resume`}
        onClose={closePreview}
      />
    </>
  );
}
