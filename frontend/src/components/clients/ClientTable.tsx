import { Link } from "react-router-dom";
import { Building2, MapPin, Users } from "lucide-react";
import { ViewActionButton } from "@/components/ui/ViewActionButton";
import { ClientStatusBadge } from "@/components/clients/ClientStatusBadge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { ClientSummary } from "@/types/client";

interface ClientTableProps {
  clients: ClientSummary[];
}

export function ClientTable({ clients }: ClientTableProps) {
  if (clients.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border py-16 text-center">
        <Building2 className="mb-4 h-12 w-12 text-muted-foreground/50" />
        <h3 className="text-lg font-medium">No clients yet</h3>
        <p className="mt-1 text-sm text-muted-foreground">
          Create your first client company to get started.
        </p>
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Company</TableHead>
          <TableHead>Industry</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="text-center">
            <Users className="mx-auto h-4 w-4" />
          </TableHead>
          <TableHead className="text-center">
            <MapPin className="mx-auto h-4 w-4" />
          </TableHead>
          <TableHead>Hiring Managers</TableHead>
          <TableHead className="w-12 text-center">View</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {clients.map((client) => (
          <TableRow key={client.id}>
            <TableCell>
              <Link
                to={`/clients/${client.id}`}
                className="font-medium hover:text-primary hover:underline"
              >
                {client.name}
              </Link>
              {client.email && (
                <p className="text-xs text-muted-foreground">{client.email}</p>
              )}
            </TableCell>
            <TableCell className="text-muted-foreground">
              {client.industry ?? "—"}
            </TableCell>
            <TableCell>
              <ClientStatusBadge status={client.status} />
            </TableCell>
            <TableCell className="text-center">{client.contact_count}</TableCell>
            <TableCell className="text-center">{client.location_count}</TableCell>
            <TableCell>{client.hiring_manager_count}</TableCell>
            <TableCell className="text-center">
              <ViewActionButton to={`/clients/${client.id}`} label="View client" />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
