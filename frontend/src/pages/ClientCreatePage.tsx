import { useMutation } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { ClientForm } from "@/components/clients/ClientForm";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { clientFormSchema, type ClientFormValues } from "@/forms/clientSchemas";
import { clientService } from "@/services/clientService";
import { getErrorMessage } from "@/services/apiClient";
import { useState } from "react";

export function ClientCreatePage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: clientService.create,
    onSuccess: (client) => {
      navigate(`/clients/${client.id}`);
    },
    onError: (err) => {
      setError(getErrorMessage(err));
    },
  });

  const handleSubmit = async (values: ClientFormValues) => {
    setError(null);
    const parsed = clientFormSchema.parse(values);
    await mutation.mutateAsync({
      name: parsed.name,
      legal_name: parsed.legal_name || undefined,
      industry: parsed.industry || undefined,
      website: parsed.website || undefined,
      phone: parsed.phone || undefined,
      email: parsed.email || undefined,
      status: parsed.status,
      description: parsed.description || undefined,
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/clients")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">New Client</h1>
          <p className="text-muted-foreground">Add a new client company</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Company Details</CardTitle>
          <CardDescription>Enter the client company information</CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-4 rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              {error}
            </div>
          )}
          <ClientForm onSubmit={handleSubmit} isSubmitting={mutation.isPending} submitLabel="Create Client" />
        </CardContent>
      </Card>
    </div>
  );
}
