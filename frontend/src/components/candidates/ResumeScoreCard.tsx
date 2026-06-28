import type { ResumeScore } from "@/types/candidate";

export function ResumeScoreCard({
  label,
  score,
}: {
  label: string;
  score: ResumeScore | undefined;
}) {
  if (!score) return null;

  return (
    <div className="rounded-md border border-border p-3 text-sm">
      <p className="font-medium">{label}</p>
      <p className="mt-1 text-2xl font-bold">{score.overall_score}</p>
      {score.suggestions.length > 0 && (
        <ul className="mt-2 list-disc space-y-1 pl-4 text-muted-foreground">
          {score.suggestions.slice(0, 3).map((s) => (
            <li key={s}>{s}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
