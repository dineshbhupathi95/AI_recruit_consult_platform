import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { jobFormSchema, parseSkillsInput, skillsToInput, type JobFormValues } from "@/forms/jobSchemas";
import { clientService } from "@/services/clientService";
import type { JobDetail } from "@/types/job";

interface JobFormProps {
  defaultValues?: Partial<JobFormValues>;
  onSubmit: (values: JobFormValues) => Promise<void>;
  isSubmitting?: boolean;
  submitLabel?: string;
  onCancel?: () => void;
  lockClient?: boolean;
}

export function JobForm({
  defaultValues,
  onSubmit,
  isSubmitting = false,
  submitLabel = "Save Job",
  onCancel,
  lockClient = false,
}: JobFormProps) {
  const { register, handleSubmit, watch, formState: { errors } } = useForm<JobFormValues>({
    resolver: zodResolver(jobFormSchema),
    defaultValues: {
      client_id: "",
      title: "",
      hiring_manager_id: "",
      client_location_id: "",
      experience_min_years: "",
      experience_max_years: "",
      budget_min: "",
      budget_max: "",
      budget_currency: "USD",
      notice_period_days: "",
      location_text: "",
      employment_type: "full_time",
      priority: "medium",
      status: "draft",
      description: "",
      required_skills: "",
      preferred_skills: "",
      ...defaultValues,
    },
  });

  const clientId = watch("client_id");

  const { data: clientsData } = useQuery({
    queryKey: ["clients", { page_size: 100 }],
    queryFn: () => clientService.list({ page_size: 100 }),
  });

  const { data: clientDetail } = useQuery({
    queryKey: ["clients", clientId],
    queryFn: () => clientService.getById(clientId),
    enabled: !!clientId,
  });

  const hiringManagers = clientDetail?.contacts.filter((c) => c.contact_type === "hiring_manager" || c.contact_type === "primary") ?? [];
  const locations = clientDetail?.locations ?? [];

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2 sm:col-span-2">
          <Label htmlFor="title">Job Title *</Label>
          <Input id="title" {...register("title")} placeholder="Senior Software Engineer" />
          {errors.title && <p className="text-sm text-destructive">{errors.title.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="client_id">Client *</Label>
          <Select id="client_id" {...register("client_id")} disabled={lockClient}>
            <option value="">Select client</option>
            {clientsData?.items.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </Select>
          {errors.client_id && <p className="text-sm text-destructive">{errors.client_id.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="hiring_manager_id">Hiring Manager</Label>
          <Select id="hiring_manager_id" {...register("hiring_manager_id")} disabled={!clientId}>
            <option value="">None</option>
            {hiringManagers.map((c) => (
              <option key={c.id} value={c.id}>{c.full_name}</option>
            ))}
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="employment_type">Employment Type</Label>
          <Select id="employment_type" {...register("employment_type")}>
            <option value="full_time">Full Time</option>
            <option value="part_time">Part Time</option>
            <option value="contract">Contract</option>
            <option value="temporary">Temporary</option>
            <option value="internship">Internship</option>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="priority">Priority</Label>
          <Select id="priority" {...register("priority")}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="status">Status</Label>
          <Select id="status" {...register("status")}>
            <option value="draft">Draft</option>
            <option value="open">Open</option>
            <option value="on_hold">On Hold</option>
            <option value="filled">Filled</option>
            <option value="closed">Closed</option>
            <option value="cancelled">Cancelled</option>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="experience_min_years">Min Experience (years)</Label>
          <Input id="experience_min_years" type="number" min={0} {...register("experience_min_years")} />
        </div>

        <div className="space-y-2">
          <Label htmlFor="experience_max_years">Max Experience (years)</Label>
          <Input id="experience_max_years" type="number" min={0} {...register("experience_max_years")} />
        </div>

        <div className="space-y-2">
          <Label htmlFor="budget_min">Budget Min</Label>
          <Input id="budget_min" type="number" min={0} {...register("budget_min")} />
        </div>

        <div className="space-y-2">
          <Label htmlFor="budget_max">Budget Max</Label>
          <Input id="budget_max" type="number" min={0} {...register("budget_max")} />
        </div>

        <div className="space-y-2">
          <Label htmlFor="budget_currency">Currency</Label>
          <Input id="budget_currency" maxLength={3} {...register("budget_currency")} />
        </div>

        <div className="space-y-2">
          <Label htmlFor="notice_period_days">Notice Period (days)</Label>
          <Input id="notice_period_days" type="number" min={0} {...register("notice_period_days")} />
        </div>

        <div className="space-y-2">
          <Label htmlFor="client_location_id">Client Location</Label>
          <Select id="client_location_id" {...register("client_location_id")} disabled={!clientId}>
            <option value="">None</option>
            {locations.map((loc) => (
              <option key={loc.id} value={loc.id}>{loc.name}</option>
            ))}
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="location_text">Location (text)</Label>
          <Input id="location_text" {...register("location_text")} placeholder="Remote / Hybrid / City" />
        </div>

        <div className="space-y-2 sm:col-span-2">
          <Label htmlFor="required_skills">Required Skills (comma-separated)</Label>
          <Input id="required_skills" {...register("required_skills")} placeholder="Python, AWS, PostgreSQL" />
        </div>

        <div className="space-y-2 sm:col-span-2">
          <Label htmlFor="preferred_skills">Preferred Skills (comma-separated)</Label>
          <Input id="preferred_skills" {...register("preferred_skills")} placeholder="Kubernetes, React" />
        </div>

        <div className="space-y-2 sm:col-span-2">
          <Label htmlFor="description">Job Description</Label>
          <Textarea id="description" {...register("description")} rows={6} placeholder="Full job description..." />
        </div>
      </div>

      <div className="flex justify-end gap-2">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} disabled={isSubmitting}>Cancel</Button>
        )}
        <Button type="submit" disabled={isSubmitting}>{isSubmitting ? "Saving..." : submitLabel}</Button>
      </div>
    </form>
  );
}

export function jobToFormValues(job: JobDetail): JobFormValues {
  return {
    client_id: job.client_id,
    title: job.title,
    hiring_manager_id: job.hiring_manager_id ?? "",
    client_location_id: job.client_location_id ?? "",
    experience_min_years: job.experience_min_years ?? "",
    experience_max_years: job.experience_max_years ?? "",
    budget_min: job.budget_min ? Number(job.budget_min) : "",
    budget_max: job.budget_max ? Number(job.budget_max) : "",
    budget_currency: job.budget_currency,
    notice_period_days: job.notice_period_days ?? "",
    location_text: job.location_text ?? "",
    employment_type: job.employment_type,
    priority: job.priority,
    status: job.status,
    description: job.description ?? "",
    required_skills: skillsToInput(job.required_skills),
    preferred_skills: skillsToInput(job.preferred_skills),
  };
}

export function formValuesToPayload(values: JobFormValues) {
  return {
    client_id: values.client_id,
    title: values.title,
    hiring_manager_id: values.hiring_manager_id || undefined,
    client_location_id: values.client_location_id || undefined,
    experience_min_years: values.experience_min_years === "" ? undefined : Number(values.experience_min_years),
    experience_max_years: values.experience_max_years === "" ? undefined : Number(values.experience_max_years),
    budget_min: values.budget_min === "" ? undefined : Number(values.budget_min),
    budget_max: values.budget_max === "" ? undefined : Number(values.budget_max),
    budget_currency: values.budget_currency,
    notice_period_days: values.notice_period_days === "" ? undefined : Number(values.notice_period_days),
    location_text: values.location_text || undefined,
    employment_type: values.employment_type,
    priority: values.priority,
    status: values.status,
    description: values.description || undefined,
    required_skills: parseSkillsInput(values.required_skills),
    preferred_skills: parseSkillsInput(values.preferred_skills),
  };
}
