import { useQuery } from "@tanstack/react-query";
import { AlertCircle, Eye, FileText, Plus, Sparkles, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { PdfViewerModal } from "@/components/candidates/PdfViewerModal";
import { ResumeScoreCard } from "@/components/candidates/ResumeScoreCard";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { getErrorMessage } from "@/services/apiClient";
import { candidateService } from "@/services/candidateService";
import { resumeTemplateService } from "@/services/resumeTemplateService";
import type {
  BuildResumePayload,
  ResumeEducationInput,
  ResumeExperienceInput,
  ResumeScore,
} from "@/types/candidate";

interface ResumeBuildFormProps {
  applicationId: string;
  parsed: boolean;
  latestBuiltScore: ResumeScore | undefined;
  latestVersionLabel?: string;
  building: boolean;
  onBuild: (payload: BuildResumePayload) => void;
}

const emptyExperience = (): ResumeExperienceInput => ({
  company: "",
  title: "",
  start_date: "",
  end_date: "",
  is_current: false,
  bullets: [],
});

const emptyEducation = (): ResumeEducationInput => ({
  institution: "",
  degree: "",
  field: "",
  graduation_year: "",
  start_year: "",
});

export function ResumeBuildForm({
  applicationId,
  parsed,
  latestBuiltScore,
  latestVersionLabel,
  building,
  onBuild,
}: ResumeBuildFormProps) {
  const { data: context, isLoading } = useQuery({
    queryKey: ["applications", applicationId, "resume-build-context"],
    queryFn: () => candidateService.getResumeBuildContext(applicationId),
    enabled: parsed,
  });

  const [gapStrategy, setGapStrategy] = useState("none");
  const [templateId, setTemplateId] = useState("");
  const [summary, setSummary] = useState("");
  const [skillsText, setSkillsText] = useState("");
  const [experience, setExperience] = useState<ResumeExperienceInput[]>([]);
  const [education, setEducation] = useState<ResumeEducationInput[]>([]);
  const [recruiterNotes, setRecruiterNotes] = useState("");
  const [targetYears, setTargetYears] = useState("");
  const [trainingEntry, setTrainingEntry] = useState<ResumeExperienceInput>(emptyExperience());
  const [previewState, setPreviewState] = useState<{ url: string; title: string; mimeType: string } | null>(null);
  const [previewError, setPreviewError] = useState<string | null>(null);

  const templates = context?.templates ?? [];
  const selectedTemplate = templates.find((t) => t.id === templateId);

  useEffect(() => {
    if (!context) return;
    setSummary(context.default_summary ?? "");
    setSkillsText((context.default_skills ?? []).join(", "));
    setExperience(
      (context.default_experience ?? []).map((e) => ({
        ...e,
        bullets: e.bullets ?? [],
      }))
    );
    setEducation(
      (context.default_education ?? []).map((e) => ({
        ...e,
        start_year: e.start_year ?? "",
      }))
    );
    if (context.experience_shortfall_years != null && context.job_experience_min_years != null) {
      setTargetYears(String(context.job_experience_min_years));
    }
    if (context.default_template_id) {
      setTemplateId(context.default_template_id);
    }
  }, [context]);

  const updateExperience = (index: number, field: keyof ResumeExperienceInput, value: string | boolean) => {
    setExperience((rows) =>
      rows.map((row, i) => (i === index ? { ...row, [field]: value } : row))
    );
  };

  const updateEducation = (index: number, field: keyof ResumeEducationInput, value: string) => {
    setEducation((rows) =>
      rows.map((row, i) => (i === index ? { ...row, [field]: value } : row))
    );
  };

  const previewSelectedTemplate = async () => {
    if (!templateId || !selectedTemplate) return;
    setPreviewError(null);
    try {
      if (selectedTemplate.source_type === "upload") {
        const blob = await resumeTemplateService.fetchSourceBlob(templateId);
        const mime = selectedTemplate.source_file_name?.toLowerCase().endsWith(".pdf")
          ? "application/pdf"
          : blob.type || "application/octet-stream";
        const url = URL.createObjectURL(new Blob([blob], { type: mime }));
        setPreviewState({ url, title: selectedTemplate.name, mimeType: mime });
      } else {
        const html = await resumeTemplateService.fetchPreviewHtml(templateId);
        const url = URL.createObjectURL(new Blob([html], { type: "text/html" }));
        setPreviewState({ url, title: selectedTemplate.name, mimeType: "text/html" });
      }
    } catch (err) {
      setPreviewError(getErrorMessage(err));
    }
  };

  const closePreview = () => {
    if (previewState?.url) URL.revokeObjectURL(previewState.url);
    setPreviewState(null);
  };

  const handleBuild = () => {
    if (!templateId) return;

    const skills = skillsText
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    const payload: BuildResumePayload = {
      template_id: templateId,
      gap_strategy: gapStrategy,
      summary,
      skills,
      experience,
      education,
      recruiter_notes: recruiterNotes || undefined,
      target_total_experience_years: targetYears ? Number(targetYears) : undefined,
    };

    if (gapStrategy === "add_training_entry" && trainingEntry.company && trainingEntry.title) {
      payload.training_entry = trainingEntry;
    }

    onBuild(payload);
  };

  if (!parsed) {
    return (
      <p className="text-sm text-muted-foreground">
        Upload and parse a resume first to configure build inputs.
      </p>
    );
  }

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading candidate details...</p>;
  }

  return (
    <div className="space-y-4">
      {latestVersionLabel && (
        <div className="rounded-md bg-muted p-3 text-sm">{latestVersionLabel}</div>
      )}
      <ResumeScoreCard label="Built resume ATS score" score={latestBuiltScore} />

      <Card className="border-primary/40 bg-primary/5">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <FileText className="h-5 w-5" />
            Step 1 — Choose resume template
          </CardTitle>
          <CardDescription>
            The AI builds content for the job, then renders it only in this layout. PDF preview uses this
            template too.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {templates.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No templates found.{" "}
              <Link to="/templates" className="underline">Upload a resume template</Link> first.
            </p>
          ) : (
            <>
              <div className="space-y-2">
                <Label htmlFor="resumeTemplate">Template</Label>
                <select
                  id="resumeTemplate"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={templateId}
                  onChange={(e) => setTemplateId(e.target.value)}
                >
                  {templates.map((tpl) => (
                    <option key={tpl.id} value={tpl.id}>
                      {tpl.name}
                      {tpl.is_default ? " (default)" : ""}
                      {tpl.source_type === "upload" ? " · uploaded" : ""}
                    </option>
                  ))}
                </select>
              </div>
              {selectedTemplate && (
                <div className="flex flex-wrap items-center gap-2 text-sm">
                  {selectedTemplate.source_type === "upload" ? (
                    <Badge variant="outline">Uploaded layout</Badge>
                  ) : selectedTemplate.is_system ? (
                    <Badge variant="outline">System layout</Badge>
                  ) : (
                    <Badge variant="secondary">Custom layout</Badge>
                  )}
                  {selectedTemplate.source_file_name && (
                    <span className="text-muted-foreground">{selectedTemplate.source_file_name}</span>
                  )}
                </div>
              )}
              {selectedTemplate?.description && (
                <p className="text-xs text-muted-foreground">{selectedTemplate.description}</p>
              )}
              <div className="flex flex-wrap gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={!templateId}
                  onClick={previewSelectedTemplate}
                >
                  <Eye className="h-4 w-4" />
                  Preview template
                </Button>
                <Link to="/templates">
                  <Button type="button" variant="ghost" size="sm">Manage templates</Button>
                </Link>
              </div>
              {previewError && (
                <p className="text-sm text-destructive">{previewError}</p>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {context && (
        <div className="rounded-md border border-border p-3 space-y-2 text-sm">
          <p className="font-medium">Step 2 — Candidate details & gap strategy</p>
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-medium">Experience vs job</span>
            {context.job_experience_min_years != null && (
              <Badge variant="outline">
                Job: {context.job_experience_min_years}
                {context.job_experience_max_years != null ? `–${context.job_experience_max_years}` : "+"} yrs
              </Badge>
            )}
            <Badge variant="secondary">
              Candidate: ~{context.candidate_total_experience_years} yrs
            </Badge>
            {context.experience_shortfall_years != null && context.experience_shortfall_years > 0 && (
              <Badge variant="destructive">
                Shortfall: {context.experience_shortfall_years} yrs
              </Badge>
            )}
          </div>
          {context.recommendations.map((note) => (
            <p key={note} className="flex gap-2 text-muted-foreground">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
              <span>{note}</span>
            </p>
          ))}
          {context.timeline_gaps.length > 0 && (
            <div className="space-y-1 pt-1">
              <p className="font-medium">Timeline gaps</p>
              {context.timeline_gaps.map((gap) => (
                <p key={`${gap.label}-${gap.from_date}`} className="text-muted-foreground">
                  {gap.label}: {gap.from_date} → {gap.to_date} ({gap.months} mo) — {gap.suggestion}
                </p>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="space-y-2">
        <Label htmlFor="gapStrategy">Gap / experience strategy</Label>
        <select
          id="gapStrategy"
          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          value={gapStrategy}
          onChange={(e) => setGapStrategy(e.target.value)}
        >
          {(context?.gap_strategy_options ?? []).map((opt) => (
            <option key={opt.id} value={opt.id}>{opt.label}</option>
          ))}
        </select>
        {context?.gap_strategy_options.find((o) => o.id === gapStrategy)?.description && (
          <p className="text-xs text-muted-foreground">
            {context.gap_strategy_options.find((o) => o.id === gapStrategy)?.description}
          </p>
        )}
      </div>

      {(gapStrategy === "extend_education" || context?.experience_shortfall_years) && (
        <div className="space-y-2">
          <Label htmlFor="targetYears">Target total experience (years) for narrative</Label>
          <Input
            id="targetYears"
            type="number"
            min={0}
            max={50}
            placeholder="e.g. 7"
            value={targetYears}
            onChange={(e) => setTargetYears(e.target.value)}
          />
        </div>
      )}

      <div className="space-y-2">
        <Label htmlFor="buildSummary">Professional summary</Label>
        <Textarea id="buildSummary" rows={3} value={summary} onChange={(e) => setSummary(e.target.value)} />
      </div>

      <div className="space-y-2">
        <Label htmlFor="buildSkills">Skills (comma-separated)</Label>
        <Input id="buildSkills" value={skillsText} onChange={(e) => setSkillsText(e.target.value)} />
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label>Work experience</Label>
          <Button type="button" variant="outline" size="sm" onClick={() => setExperience((r) => [...r, emptyExperience()])}>
            <Plus className="h-3 w-3" /> Add role
          </Button>
        </div>
        {experience.map((row, index) => (
          <div key={index} className="grid gap-2 rounded-md border p-3 sm:grid-cols-2">
            <Input placeholder="Company" value={row.company} onChange={(e) => updateExperience(index, "company", e.target.value)} />
            <Input placeholder="Title" value={row.title} onChange={(e) => updateExperience(index, "title", e.target.value)} />
            <Input placeholder="Start (e.g. Jan 2020)" value={row.start_date} onChange={(e) => updateExperience(index, "start_date", e.target.value)} />
            <Input
              placeholder="End or Present"
              value={row.end_date ?? ""}
              disabled={row.is_current}
              onChange={(e) => updateExperience(index, "end_date", e.target.value)}
            />
            <label className="flex items-center gap-2 text-sm sm:col-span-2">
              <input
                type="checkbox"
                checked={Boolean(row.is_current)}
                onChange={(e) => updateExperience(index, "is_current", e.target.checked)}
              />
              Current role
            </label>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="sm:col-span-2"
              onClick={() => setExperience((rows) => rows.filter((_, i) => i !== index))}
            >
              <Trash2 className="h-3 w-3" /> Remove
            </Button>
          </div>
        ))}
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label>Education</Label>
          <Button type="button" variant="outline" size="sm" onClick={() => setEducation((r) => [...r, emptyEducation()])}>
            <Plus className="h-3 w-3" /> Add education
          </Button>
        </div>
        {education.map((row, index) => (
          <div key={index} className="grid gap-2 rounded-md border p-3 sm:grid-cols-2">
            <Input placeholder="Institution" value={row.institution} onChange={(e) => updateEducation(index, "institution", e.target.value)} />
            <Input placeholder="Degree" value={row.degree} onChange={(e) => updateEducation(index, "degree", e.target.value)} />
            <Input placeholder="Field" value={row.field ?? ""} onChange={(e) => updateEducation(index, "field", e.target.value)} />
            <Input placeholder="Start year" value={row.start_year ?? ""} onChange={(e) => updateEducation(index, "start_year", e.target.value)} />
            <Input placeholder="Graduation year" value={row.graduation_year ?? ""} onChange={(e) => updateEducation(index, "graduation_year", e.target.value)} />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setEducation((rows) => rows.filter((_, i) => i !== index))}
            >
              <Trash2 className="h-3 w-3" /> Remove
            </Button>
          </div>
        ))}
      </div>

      {gapStrategy === "add_training_entry" && (
        <div className="space-y-2 rounded-md border border-dashed p-3">
          <Label>Internship / training entry (fills education → first job gap)</Label>
          <div className="grid gap-2 sm:grid-cols-2">
            <Input placeholder="Organization" value={trainingEntry.company} onChange={(e) => setTrainingEntry({ ...trainingEntry, company: e.target.value })} />
            <Input placeholder="Role (Intern, Trainee…)" value={trainingEntry.title} onChange={(e) => setTrainingEntry({ ...trainingEntry, title: e.target.value })} />
            <Input placeholder="Start" value={trainingEntry.start_date} onChange={(e) => setTrainingEntry({ ...trainingEntry, start_date: e.target.value })} />
            <Input placeholder="End" value={trainingEntry.end_date ?? ""} onChange={(e) => setTrainingEntry({ ...trainingEntry, end_date: e.target.value })} />
          </div>
        </div>
      )}

      <div className="space-y-2">
        <Label htmlFor="buildNotes">Recruiter notes for AI</Label>
        <Textarea
          id="buildNotes"
          rows={2}
          placeholder="e.g. Emphasize cloud projects; do not list employer X…"
          value={recruiterNotes}
          onChange={(e) => setRecruiterNotes(e.target.value)}
        />
      </div>

      <Button disabled={building || !templateId || templates.length === 0} onClick={handleBuild}>
        <Sparkles className="h-4 w-4" />
        {building
          ? "Building..."
          : selectedTemplate
            ? `Build resume with “${selectedTemplate.name}”`
            : "Select a template to build"}
      </Button>

      <PdfViewerModal
        url={previewState?.url ?? null}
        mimeType={previewState?.mimeType}
        title={previewState?.title ?? "Template preview"}
        onClose={closePreview}
      />
    </div>
  );
}
