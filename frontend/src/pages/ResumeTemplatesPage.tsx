import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Eye, FileText, Trash2, Upload } from "lucide-react";
import { useRef, useState } from "react";
import { PdfViewerModal } from "@/components/candidates/PdfViewerModal";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { getErrorMessage } from "@/services/apiClient";
import { resumeTemplateService } from "@/services/resumeTemplateService";
import type { ResumeTemplateSummary } from "@/types/resumeTemplate";

export function ResumeTemplatesPage() {
  const queryClient = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [isDefault, setIsDefault] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewState, setPreviewState] = useState<{
    url: string;
    title: string;
    mimeType: string;
  } | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["resume-templates"],
    queryFn: resumeTemplateService.list,
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) =>
      resumeTemplateService.upload(file, {
        name: name || undefined,
        description: description || undefined,
        is_default: isDefault,
      }),
    onSuccess: () => {
      setError(null);
      setName("");
      setDescription("");
      setIsDefault(false);
      if (fileRef.current) fileRef.current.value = "";
      queryClient.invalidateQueries({ queryKey: ["resume-templates"] });
    },
    onError: (err) => setError(getErrorMessage(err)),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => resumeTemplateService.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["resume-templates"] }),
    onError: (err) => setError(getErrorMessage(err)),
  });

  const openUploadedPreview = async (template: ResumeTemplateSummary) => {
    try {
      const blob = await resumeTemplateService.fetchSourceBlob(template.id);
      const mime =
        template.source_file_name?.toLowerCase().endsWith(".pdf")
          ? "application/pdf"
          : blob.type || "application/octet-stream";
      const url = URL.createObjectURL(new Blob([blob], { type: mime }));
      setPreviewState({ url, title: `${template.name} (uploaded)`, mimeType: mime });
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const openSamplePreview = async (template: ResumeTemplateSummary) => {
    try {
      const html = await resumeTemplateService.fetchPreviewHtml(template.id);
      const url = URL.createObjectURL(new Blob([html], { type: "text/html" }));
      setPreviewState({ url, title: `${template.name} (sample data)`, mimeType: "text/html" });
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const closePreview = () => {
    if (previewState?.url) URL.revokeObjectURL(previewState.url);
    setPreviewState(null);
  };

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2">
          <FileText className="h-7 w-7" />
          <h1 className="text-3xl font-bold tracking-tight">Resume Templates</h1>
        </div>
        <p className="text-muted-foreground">
          Upload a resume (PDF or DOCX) to use its layout as a template when building candidate resumes with AI.
        </p>
      </div>

      {error && (
        <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">{error}</div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Upload resume template</CardTitle>
          <CardDescription>
            We store your file and convert its layout into a reusable template. AI-built resume content is rendered
            in this layout when you export or preview.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="tplName">Template name (optional)</Label>
              <Input
                id="tplName"
                placeholder="e.g. Client standard resume"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="tplDesc">Description (optional)</Label>
              <Input
                id="tplDesc"
                placeholder="Short note for recruiters"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={isDefault} onChange={(e) => setIsDefault(e.target.checked)} />
            Set as default for new AI resume builds
          </label>
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.docx"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) uploadMutation.mutate(file);
            }}
          />
          <Button
            disabled={uploadMutation.isPending}
            onClick={() => fileRef.current?.click()}
          >
            <Upload className="h-4 w-4" />
            {uploadMutation.isPending ? "Processing upload..." : "Upload PDF or DOCX Resume"}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Template library</CardTitle>
          <CardDescription>System layouts plus your uploaded resume templates.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Loading templates...</p>
          ) : !data?.items.length ? (
            <p className="text-sm text-muted-foreground">No templates yet.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead>File</TableHead>
                  <TableHead className="text-center">Preview</TableHead>
                  <TableHead className="w-12" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.items.map((tpl) => (
                  <TableRow key={tpl.id}>
                    <TableCell className="font-medium">
                      {tpl.name}
                      {tpl.is_default && (
                        <Badge variant="secondary" className="ml-2 text-[10px]">Default</Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      {tpl.source_type === "upload" ? (
                        <Badge variant="outline">Uploaded</Badge>
                      ) : tpl.is_system ? (
                        <Badge variant="outline">System</Badge>
                      ) : (
                        <Badge variant="secondary">Custom HTML</Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {tpl.source_file_name ?? "—"}
                    </TableCell>
                    <TableCell className="text-center">
                      <div className="flex justify-center gap-1">
                        {tpl.source_type === "upload" && (
                          <Button
                            variant="ghost"
                            size="icon"
                            title="View uploaded file"
                            onClick={() => openUploadedPreview(tpl)}
                          >
                            <FileText className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="icon"
                          title="Preview with sample data"
                          onClick={() => openSamplePreview(tpl)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                    <TableCell>
                      {!tpl.is_system && (
                        <Button
                          variant="ghost"
                          size="icon"
                          title="Delete template"
                          disabled={deleteMutation.isPending}
                          onClick={() => deleteMutation.mutate(tpl.id)}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <PdfViewerModal
        url={previewState?.url ?? null}
        mimeType={previewState?.mimeType}
        title={previewState?.title ?? "Template preview"}
        onClose={closePreview}
      />
    </div>
  );
}
