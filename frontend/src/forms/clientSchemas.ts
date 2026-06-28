import { z } from "zod";

export const clientStatusSchema = z.enum(["prospect", "active", "inactive", "on_hold"]);
export const contactTypeSchema = z.enum(["general", "hiring_manager", "primary"]);

export const clientFormSchema = z.object({
  name: z.string().min(1, "Company name is required").max(255),
  legal_name: z.string().max(255).optional().or(z.literal("")),
  industry: z.string().max(100).optional().or(z.literal("")),
  website: z.string().url("Invalid URL").max(512).optional().or(z.literal("")),
  phone: z.string().max(50).optional().or(z.literal("")),
  email: z.string().email("Invalid email").max(255).optional().or(z.literal("")),
  status: clientStatusSchema.default("prospect"),
  description: z.string().max(5000).optional().or(z.literal("")),
});

export const contactFormSchema = z.object({
  first_name: z.string().min(1, "First name is required").max(100),
  last_name: z.string().min(1, "Last name is required").max(100),
  email: z.string().email("Invalid email"),
  phone: z.string().max(50).optional().or(z.literal("")),
  job_title: z.string().max(150).optional().or(z.literal("")),
  department: z.string().max(150).optional().or(z.literal("")),
  contact_type: contactTypeSchema.default("general"),
  is_active: z.boolean().default(true),
});

export const locationFormSchema = z.object({
  name: z.string().min(1, "Location name is required").max(255),
  address_line1: z.string().max(255).optional().or(z.literal("")),
  address_line2: z.string().max(255).optional().or(z.literal("")),
  city: z.string().max(100).optional().or(z.literal("")),
  state: z.string().max(100).optional().or(z.literal("")),
  country: z.string().max(100).optional().or(z.literal("")),
  postal_code: z.string().max(20).optional().or(z.literal("")),
  is_headquarters: z.boolean().default(false),
});

export const noteFormSchema = z.object({
  content: z.string().min(1, "Note content is required").max(10000),
});

export type ClientFormValues = z.infer<typeof clientFormSchema>;
export type ContactFormValues = z.infer<typeof contactFormSchema>;
export type LocationFormValues = z.infer<typeof locationFormSchema>;
export type NoteFormValues = z.infer<typeof noteFormSchema>;
