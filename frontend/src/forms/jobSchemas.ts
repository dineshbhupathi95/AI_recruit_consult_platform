import { z } from "zod";

export const employmentTypeSchema = z.enum(["full_time", "part_time", "contract", "temporary", "internship"]);
export const jobPrioritySchema = z.enum(["low", "medium", "high", "urgent"]);
export const jobStatusSchema = z.enum(["draft", "open", "on_hold", "filled", "closed", "cancelled"]);

export const jobFormSchema = z.object({
  client_id: z.string().uuid("Select a client"),
  title: z.string().min(1, "Job title is required").max(255),
  hiring_manager_id: z.string().optional().or(z.literal("")),
  client_location_id: z.string().optional().or(z.literal("")),
  experience_min_years: z.coerce.number().min(0).max(50).optional().or(z.literal("")),
  experience_max_years: z.coerce.number().min(0).max(50).optional().or(z.literal("")),
  budget_min: z.coerce.number().min(0).optional().or(z.literal("")),
  budget_max: z.coerce.number().min(0).optional().or(z.literal("")),
  budget_currency: z.string().length(3).default("USD"),
  notice_period_days: z.coerce.number().min(0).max(365).optional().or(z.literal("")),
  location_text: z.string().max(255).optional().or(z.literal("")),
  employment_type: employmentTypeSchema.default("full_time"),
  priority: jobPrioritySchema.default("medium"),
  status: jobStatusSchema.default("draft"),
  description: z.string().max(20000).optional().or(z.literal("")),
  required_skills: z.string().optional().or(z.literal("")),
  preferred_skills: z.string().optional().or(z.literal("")),
});

export type JobFormValues = z.infer<typeof jobFormSchema>;

export function parseSkillsInput(input: string | undefined): string[] {
  if (!input?.trim()) return [];
  return input.split(",").map((s) => s.trim()).filter(Boolean);
}

export function skillsToInput(skills: string[]): string {
  return skills.join(", ");
}
