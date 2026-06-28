import type { ClientStatus } from "@/types/client";
import { CLIENT_STATUS_LABELS } from "@/types/client";
import { Badge } from "@/components/ui/badge";

const STATUS_VARIANTS: Record<ClientStatus, "default" | "success" | "warning" | "secondary" | "destructive"> = {
  prospect: "secondary",
  active: "success",
  inactive: "destructive",
  on_hold: "warning",
};

export function ClientStatusBadge({ status }: { status: ClientStatus }) {
  return <Badge variant={STATUS_VARIANTS[status]}>{CLIENT_STATUS_LABELS[status]}</Badge>;
}
