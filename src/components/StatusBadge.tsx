/**
 * Semantic status badge wrapping the base Badge UI component.
 */
import { Badge } from "@/components/ui/badge";

type Status = "success" | "warning" | "error" | "info" | "default";

interface Props {
  status: Status;
  label: string;
}

const variantMap: Record<Status, string> = {
  success: "bg-emerald-100 text-emerald-800 border-emerald-200",
  warning: "bg-amber-100 text-amber-800 border-amber-200",
  error:   "bg-red-100 text-red-800 border-red-200",
  info:    "bg-blue-100 text-blue-800 border-blue-200",
  default: "bg-slate-100 text-slate-800 border-slate-200",
};

export function StatusBadge({ status, label }: Props) {
  return (
    <Badge className={`border ${variantMap[status]}`} variant="outline">
      {label}
    </Badge>
  );
}
