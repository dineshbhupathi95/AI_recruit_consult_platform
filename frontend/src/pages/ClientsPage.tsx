import { useQuery } from "@tanstack/react-query";
import { Plus, Search } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { ClientTable } from "@/components/clients/ClientTable";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { clientService } from "@/services/clientService";
import type { ClientStatus } from "@/types/client";

export function ClientsPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<ClientStatus | "">("");
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = useQuery({
    queryKey: ["clients", { search, status, page }],
    queryFn: () =>
      clientService.list({
        search: search || undefined,
        status: status || undefined,
        page,
        page_size: 20,
      }),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Clients</h1>
          <p className="text-muted-foreground">Manage client companies and contacts</p>
        </div>
        <Link to="/clients/new">
          <Button>
            <Plus className="h-4 w-4" />
            Add Client
          </Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Client Directory</CardTitle>
          <CardDescription>
            {data ? `${data.total} client${data.total !== 1 ? "s" : ""} total` : "Loading..."}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                className="pl-9"
                placeholder="Search by name, industry, or email..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
              />
            </div>
            <Select
              className="sm:w-48"
              value={status}
              onChange={(e) => {
                setStatus(e.target.value as ClientStatus | "");
                setPage(1);
              }}
            >
              <option value="">All Statuses</option>
              <option value="prospect">Prospect</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="on_hold">On Hold</option>
            </Select>
          </div>

          {isLoading && (
            <div className="py-12 text-center text-muted-foreground">Loading clients...</div>
          )}

          {error && (
            <div className="py-12 text-center text-destructive">Failed to load clients</div>
          )}

          {data && <ClientTable clients={data.items} />}

          {data && data.total_pages > 1 && (
            <div className="flex items-center justify-between pt-4">
              <p className="text-sm text-muted-foreground">
                Page {data.page} of {data.total_pages}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= data.total_pages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
