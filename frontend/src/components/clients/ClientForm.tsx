import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { clientFormSchema, type ClientFormValues } from "@/forms/clientSchemas";
import type { ClientDetail } from "@/types/client";

interface ClientFormProps {
  defaultValues?: Partial<ClientFormValues>;
  onSubmit: (values: ClientFormValues) => Promise<void>;
  isSubmitting?: boolean;
  submitLabel?: string;
  onCancel?: () => void;
}

export function ClientForm({
  defaultValues,
  onSubmit,
  isSubmitting = false,
  submitLabel = "Save Client",
  onCancel,
}: ClientFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ClientFormValues>({
    resolver: zodResolver(clientFormSchema),
    defaultValues: {
      name: "",
      legal_name: "",
      industry: "",
      website: "",
      phone: "",
      email: "",
      status: "prospect",
      description: "",
      ...defaultValues,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2 sm:col-span-2">
          <Label htmlFor="name">Company Name *</Label>
          <Input id="name" {...register("name")} placeholder="Acme Corporation" />
          {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="legal_name">Legal Name</Label>
          <Input id="legal_name" {...register("legal_name")} placeholder="Acme Corp LLC" />
        </div>

        <div className="space-y-2">
          <Label htmlFor="industry">Industry</Label>
          <Input id="industry" {...register("industry")} placeholder="Technology" />
        </div>

        <div className="space-y-2">
          <Label htmlFor="email">Company Email</Label>
          <Input id="email" type="email" {...register("email")} placeholder="info@company.com" />
          {errors.email && <p className="text-sm text-destructive">{errors.email.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="phone">Phone</Label>
          <Input id="phone" {...register("phone")} placeholder="+1-555-0100" />
        </div>

        <div className="space-y-2">
          <Label htmlFor="website">Website</Label>
          <Input id="website" {...register("website")} placeholder="https://company.com" />
          {errors.website && <p className="text-sm text-destructive">{errors.website.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="status">Status</Label>
          <Select id="status" {...register("status")}>
            <option value="prospect">Prospect</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="on_hold">On Hold</option>
          </Select>
        </div>

        <div className="space-y-2 sm:col-span-2">
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            {...register("description")}
            placeholder="Brief description of the client..."
            rows={3}
          />
        </div>
      </div>

      <div className="flex justify-end gap-2">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} disabled={isSubmitting}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : submitLabel}
        </Button>
      </div>
    </form>
  );
}

export function clientToFormValues(client: ClientDetail): ClientFormValues {
  return {
    name: client.name,
    legal_name: client.legal_name ?? "",
    industry: client.industry ?? "",
    website: client.website ?? "",
    phone: client.phone ?? "",
    email: client.email ?? "",
    status: client.status,
    description: client.description ?? "",
  };
}
