import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeft,
  CheckCircle2,
  Circle,
  Download,
  Eye,
  FileText,
  MessageSquare,
  Sparkles,
  Upload,
  XCircle,
} from "lucide-react";
import { useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { PdfViewerModal } from "@/components/candidates/PdfViewerModal";
import { ResumeBuildForm } from "@/components/candidates/ResumeBuildForm";
import { ResumeScoreCard } from "@/components/candidates/ResumeScoreCard";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { getErrorMessage } from "@/services/apiClient";
import { candidateService } from "@/services/candidateService";
import type { BuildResumePayload, RecruiterReviewDecision } from "@/types/candidate";
import { PIPELINE_STAGE_LABELS, PIPELINE_STEPS } from "@/types/candidate";

function StepIcon({ done }: { done: boolean }) {
  return done ? (
    <CheckCircle2 className="h-5 w-5 text-green-600" />
  ) : (
    <Circle className="h-5 w-5 text-muted-foreground" />
  );
}

export function ApplicationPipelinePage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [answer, setAnswer] = useState("");
  const [mcqSelection, setMcqSelection] = useState("");
  const [reviewNotes, setReviewNotes] = useState("");
  const [currentQuestion, setCurrentQuestion] = useState<{
    question: string;
    question_type: string;
    options: Array<{ id: string; text: string }>;
    question_number: number;
    phase_label?: string | null;
    total_questions: number;
    is_complete: boolean;
  } | null>(null);
  const [previewState, setPreviewState] = useState<{ url: string; mimeType: string } | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const { data: app, isLoading } = useQuery({
    queryKey: ["applications", id],
    queryFn: () => candidateService.getApplication(id!),
    enabled: !!id,
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["applications", id] });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => candidateService.uploadResume(id!, file),
    onSuccess: () => invalidate(),
    onError: (err) => setActionError(getErrorMessage(err)),
  });

  const buildMutation = useMutation({
    mutationFn: (payload: BuildResumePayload) => candidateService.buildResume(id!, payload),
    onSuccess: () => invalidate(),
    onError: (err) => setActionError(getErrorMessage(err)),
  });

  const reviewMutation = useMutation({
    mutationFn: ({ versionId, decision }: { versionId: string; decision: RecruiterReviewDecision }) =>
      candidateService.reviewResume(id!, versionId, decision, reviewNotes || undefined),
    onSuccess: () => {
      setReviewNotes("");
      invalidate();
    },
    onError: (err) => setActionError(getErrorMessage(err)),
  });

  const scoreParsedMutation = useMutation({
    mutationFn: () => candidateService.scoreResume(id!),
    onSuccess: () => invalidate(),
    onError: (err) => setActionError(getErrorMessage(err)),
  });

  const scheduleMutation = useMutation({
    mutationFn: () => candidateService.scheduleInterview(id!, { duration_minutes: 45 }),
    onSuccess: () => invalidate(),
    onError: (err) => setActionError(getErrorMessage(err)),
  });

  const startInterviewMutation = useMutation({
    mutationFn: () => candidateService.startInterview(id!),
    onSuccess: (data) => {
      setCurrentQuestion(data);
      setMcqSelection("");
      invalidate();
    },
    onError: (err) => setActionError(getErrorMessage(err)),
  });

  const answerMutation = useMutation({
    mutationFn: (text: string) => candidateService.submitAnswer(id!, text),
    onSuccess: (data) => {
      setAnswer("");
      setMcqSelection("");
      setCurrentQuestion(data);
      invalidate();
    },
    onError: (err) => setActionError(getErrorMessage(err)),
  });

  const completeMutation = useMutation({
    mutationFn: () => candidateService.completeInterview(id!),
    onSuccess: () => {
      setCurrentQuestion(null);
      invalidate();
    },
    onError: (err) => setActionError(getErrorMessage(err)),
  });

  const openResumePreview = async (versionId?: string) => {
    setActionError(null);
    const showPreview = (blob: Blob, mimeType: string) => {
      const url = URL.createObjectURL(new Blob([blob], { type: mimeType }));
      setPreviewState({ url, mimeType });
    };
    try {
      const pdfResponse = await candidateService.exportResume(id!, "pdf", versionId);
      showPreview(pdfResponse.data as Blob, "application/pdf");
    } catch {
      try {
        const htmlResponse = await candidateService.exportResume(id!, "html", versionId);
        showPreview(htmlResponse.data as Blob, "text/html");
      } catch (err) {
        setActionError(getErrorMessage(err));
      }
    }
  };

  const closeResumePreview = () => {
    if (previewState?.url) URL.revokeObjectURL(previewState.url);
    setPreviewState(null);
  };

  if (isLoading) return <div className="py-12 text-center text-muted-foreground">Loading pipeline...</div>;
  if (!app) return <div className="py-12 text-center text-destructive">Application not found</div>;

  const parsed = app.parsed_resume?.status === "completed";
  const hasVersion = app.resume_versions.length > 0;
  const latestVersion = app.resume_versions[app.resume_versions.length - 1];
  const canReview = latestVersion?.status === "pending_review";
  const reviewDecided =
    latestVersion &&
    (latestVersion.recruiter_review_decision != null ||
      ["approved", "rejected", "needs_changes"].includes(latestVersion.status));
  const parsedScores = app.resume_scores.filter((s) => !s.resume_version_id);
  const builtScores = latestVersion
    ? app.resume_scores.filter((s) => s.resume_version_id === latestVersion.id)
    : [];
  const latestParsedScore = parsedScores[parsedScores.length - 1];
  const latestBuiltScore = builtScores[builtScores.length - 1];
  const interview = app.screening_interview;
  const interviewDone = interview?.status === "completed";
  const activeQuestion = currentQuestion;

  const stepDone = {
    create: true,
    upload: parsed,
    parse: parsed,
    build: hasVersion,
    review: reviewDecided,
    export: hasVersion,
    score: parsedScores.length > 0 || builtScores.length > 0,
    schedule: interview != null,
    interview: interviewDone,
    summary: interviewDone && interview?.summary,
  };

  const submitCurrentAnswer = () => {
    const text =
      activeQuestion?.question_type === "mcq"
        ? mcqSelection
          ? `Selected option ${mcqSelection}`
          : ""
        : answer;
    if (!text.trim()) return;
    answerMutation.mutate(text);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-4">
        <Link to="/candidates">
          <Button variant="ghost" size="icon"><ArrowLeft className="h-4 w-4" /></Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{app.candidate.full_name}</h1>
          <p className="text-muted-foreground">{app.job_title} at {app.client_name}</p>
          <div className="mt-2 flex gap-2">
            <Badge variant="outline">{PIPELINE_STAGE_LABELS[app.pipeline_stage]}</Badge>
            <Badge variant="secondary">{app.status}</Badge>
          </div>
        </div>
      </div>

      {actionError && (
        <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">{actionError}</div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Pipeline Progress</CardTitle>
          <CardDescription>End-to-end AI recruitment workflow</CardDescription>
        </CardHeader>
        <CardContent>
          <ol className="grid gap-2 sm:grid-cols-2 lg:grid-cols-5">
            {PIPELINE_STEPS.map((step) => (
              <li key={step.key} className="flex items-center gap-2 text-sm">
                <StepIcon done={Boolean(stepDone[step.key as keyof typeof stepDone])} />
                <span>{step.label}</span>
              </li>
            ))}
          </ol>
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" /> Upload & Parse Resume
            </CardTitle>
            <CardDescription>Upload PDF or DOCX — AI extracts and scores against the job</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {app.parsed_resume && (
              <div className="rounded-md bg-muted p-3 text-sm">
                Status: <strong>{app.parsed_resume.status}</strong>
                {typeof app.parsed_resume.structured_data?.summary === "string" && (
                  <p className="mt-2 text-muted-foreground">
                    {app.parsed_resume.structured_data.summary.slice(0, 200)}...
                  </p>
                )}
              </div>
            )}
            <ResumeScoreCard label="Uploaded resume ATS score" score={latestParsedScore} />
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
            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                disabled={uploadMutation.isPending}
                onClick={() => fileRef.current?.click()}
              >
                <FileText className="h-4 w-4" />
                {uploadMutation.isPending ? "Processing..." : "Upload Resume"}
              </Button>
              <Button
                variant="outline"
                disabled={!parsed || scoreParsedMutation.isPending}
                onClick={() => scoreParsedMutation.mutate()}
              >
                {scoreParsedMutation.isPending ? "Scoring..." : "Re-score Uploaded Resume"}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" /> AI Resume Builder
            </CardTitle>
            <CardDescription>
              Pick a template layout, adjust candidate details, then build — export uses the same template
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResumeBuildForm
              applicationId={id!}
              parsed={parsed}
              latestBuiltScore={latestBuiltScore}
              latestVersionLabel={
                latestVersion
                  ? `Version ${latestVersion.version_number} — ${latestVersion.status}${
                      latestVersion.template_name ? ` · Template: ${latestVersion.template_name}` : ""
                    }`
                  : undefined
              }
              building={buildMutation.isPending}
              onBuild={(payload) => buildMutation.mutate(payload)}
            />
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Recruiter Review</CardTitle>
            <CardDescription>Preview built resume in PDF, add feedback, approve or request changes</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {!latestVersion && (
              <p className="text-sm text-muted-foreground">Build a resume first to enable review.</p>
            )}
            {latestVersion && (
              <>
                <div className="flex flex-wrap items-center gap-2">
                  <Button variant="outline" onClick={() => openResumePreview(latestVersion.id)}>
                    <Eye className="h-4 w-4" /> View Resume
                  </Button>
                  {reviewDecided && (
                    <Badge variant="outline">
                      Review: {latestVersion.status.replace("_", " ")}
                      {latestVersion.recruiter_review_decision
                        ? ` (${latestVersion.recruiter_review_decision.replace(/_/g, " ")})`
                        : ""}
                    </Badge>
                  )}
                </div>
                {latestVersion.recruiter_review_notes && (
                  <p className="text-sm text-muted-foreground">
                    Feedback: {latestVersion.recruiter_review_notes}
                  </p>
                )}
                {canReview && (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="reviewNotes">Recruiter feedback</Label>
                      <Textarea
                        id="reviewNotes"
                        rows={3}
                        placeholder="Optional notes for the candidate or internal team..."
                        value={reviewNotes}
                        onChange={(e) => setReviewNotes(e.target.value)}
                      />
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <Button
                        disabled={reviewMutation.isPending}
                        onClick={() =>
                          reviewMutation.mutate({ versionId: latestVersion.id, decision: "accept" })
                        }
                      >
                        Approve Resume
                      </Button>
                      <Button
                        variant="outline"
                        disabled={reviewMutation.isPending}
                        onClick={() =>
                          reviewMutation.mutate({
                            versionId: latestVersion.id,
                            decision: "needs_resume_changes",
                          })
                        }
                      >
                        Request Changes
                      </Button>
                      <Button
                        variant="destructive"
                        disabled={reviewMutation.isPending}
                        onClick={() =>
                          reviewMutation.mutate({ versionId: latestVersion.id, decision: "reject" })
                        }
                      >
                        <XCircle className="h-4 w-4" /> Reject
                      </Button>
                      <Button
                        variant="secondary"
                        disabled={reviewMutation.isPending}
                        onClick={() =>
                          reviewMutation.mutate({
                            versionId: latestVersion.id,
                            decision: "submit_to_client",
                          })
                        }
                      >
                        Approve & Submit to Client
                      </Button>
                    </div>
                  </>
                )}
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Download className="h-5 w-5" /> Export
            </CardTitle>
          </CardHeader>
          <CardContent className="flex gap-2">
            <Button variant="outline" disabled={!hasVersion} onClick={() => openResumePreview(latestVersion?.id)}>
              Resume Preview
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Screening Interview</CardTitle>
            <CardDescription>15 MCQ → 2 scenario → 1 coding question</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {!interview && (
              <Button disabled={scheduleMutation.isPending} onClick={() => scheduleMutation.mutate()}>
                {scheduleMutation.isPending ? "Scheduling..." : "Schedule Interview"}
              </Button>
            )}
            {interview && interview.status === "scheduled" && (
              <Button disabled={startInterviewMutation.isPending} onClick={() => startInterviewMutation.mutate()}>
                Start Interview
              </Button>
            )}
            {interview?.status === "in_progress" && activeQuestion && (
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Badge variant="outline">{activeQuestion.phase_label ?? activeQuestion.question_type}</Badge>
                  <span>
                    Question {activeQuestion.question_number} of {activeQuestion.total_questions}
                  </span>
                </div>
                {!activeQuestion.is_complete && activeQuestion.question && (
                  <div className="rounded-md border p-3 text-sm">
                    <p className="font-medium">{activeQuestion.question}</p>
                    {activeQuestion.question_type === "mcq" && activeQuestion.options.length > 0 && (
                      <div className="mt-3 space-y-2">
                        {activeQuestion.options.map((opt) => (
                          <label key={opt.id} className="flex items-center gap-2">
                            <input
                              type="radio"
                              name="mcq"
                              value={opt.id}
                              checked={mcqSelection === opt.id}
                              onChange={() => setMcqSelection(opt.id)}
                            />
                            <span>{opt.text}</span>
                          </label>
                        ))}
                      </div>
                    )}
                    {activeQuestion.question_type !== "mcq" && (
                      <Textarea
                        className="mt-3 font-mono text-sm"
                        rows={activeQuestion.question_type === "coding" ? 8 : 4}
                        placeholder={
                          activeQuestion.question_type === "coding"
                            ? "Write pseudocode or solution..."
                            : "Describe your approach..."
                        }
                        value={answer}
                        onChange={(e) => setAnswer(e.target.value)}
                      />
                    )}
                  </div>
                )}
                <div className="flex gap-2">
                  {!activeQuestion.is_complete && (
                    <Button disabled={answerMutation.isPending} onClick={submitCurrentAnswer}>
                      Submit Answer
                    </Button>
                  )}
                  <Button
                    variant="outline"
                    disabled={completeMutation.isPending}
                    onClick={() => completeMutation.mutate()}
                  >
                    {activeQuestion.is_complete ? "Finish Interview" : "Complete Early"}
                  </Button>
                </div>
              </div>
            )}
            {interviewDone && interview && (
              <div className="space-y-2 rounded-md bg-muted p-4 text-sm">
                <div className="flex items-center gap-2 font-medium">
                  <MessageSquare className="h-4 w-4" /> Interview Summary
                </div>
                <p>{interview.summary}</p>
                <p>
                  Recommendation: <strong>{interview.recommendation}</strong>
                  {interview.technical_score && ` · Technical: ${interview.technical_score}`}
                  {interview.coding_score && ` · Coding: ${interview.coding_score}`}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {app.job_description && (
        <Card>
          <CardHeader><CardTitle>Job Description</CardTitle></CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap text-sm text-muted-foreground">{app.job_description}</p>
          </CardContent>
        </Card>
      )}

      <PdfViewerModal
        url={previewState?.url ?? null}
        mimeType={previewState?.mimeType}
        title={`${app.candidate.full_name} — Resume`}
        onClose={closeResumePreview}
      />
    </div>
  );
}
