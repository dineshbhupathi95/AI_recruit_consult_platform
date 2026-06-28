import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ClientForm, clientToFormValues } from "@/components/clients/ClientForm";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { clientFormSchema, type ClientFormValues } from "@/forms/clientSchemas";
import { clientService } from "@/services/clientService";
import { getErrorMessage } from "@/services/apiClient";

export function ClientEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const { data: client, isLoading } = useQuery({
    queryKey: ["clients", id],
    queryFn: () => clientService.getById(id!),
    enabled: !!id,
  });

  const mutation = useMutation({
    mutationFn: (values: ClientFormValues) => {
      const parsed = clientFormSchema.parse(values);
      return clientService.update(id!, {
        name: parsed.name,
        legal_name: parsed.legal_name || undefined,
        industry: parsed.industry || undefined,
        website: parsed.website || undefined,
        phone: parsed.phone || undefined,
        email: parsed.email || undefined,
        status: parsed.status,
        description: parsed.description || undefined,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      navigate(`/clients/${id}`);
    },
    onError: (err) => setError(getErrorMessage(err)),
  });

  if (isLoading) {
    return <div className="py-12 text-center text-muted-foreground">Loading client...</div>;
  }

  if (!client) {
    return <div className="py-12 text-center text-destructive">Client not found</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to={`/clients/${id}`}>
          <Button variant="ghost" size="icon"><ArrowLeft className="h-4 w-4" /></Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Edit Client</h1>
          <p className="text-muted-foreground">{client.name}</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Company Details</CardTitle>
          <CardDescription>Update client company information</CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-4 rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              {error}
            </div>
          )}
          <ClientForm
            defaultValues={clientToFormValues(client)}
            onSubmit={async (values) => {
              setError(null);
              await mutation.mutateAsync(values);
            }}
            isSubmitting={mutation.isPending}
            submitLabel="Save Changes"
            onCancel={() => navigate(`/clients/${id}`)}
          />
        </CardContent>
      </Card>
    </div>
  );
}
