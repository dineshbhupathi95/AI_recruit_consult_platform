import { Eye } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

export function ViewActionButton({ to, label = "View" }: { to: string; label?: string }) {
  return (
    <Link to={to}>
      <Button variant="ghost" size="icon" aria-label={label} title={label}>
        <Eye className="h-4 w-4" />
      </Button>
    </Link>
  );
}
