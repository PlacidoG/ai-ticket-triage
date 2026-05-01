
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const statusConfig: Record<string, { label: string; className: string }> = {
  new: {
    label: "New",
    className: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  },
  triaged: {
    label: "Triaged",
    className: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  },
  in_progress: {
    label: "In Progress",
    className: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  },
  waiting_on_customer: {
    label: "Waiting",
    className: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  },
  resolved: {
    label: "Resolved",
    className: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  },
  closed: {
    label: "Closed",
    className: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  },
};

export function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status] || { label: status, className: "" };
  return (
    <Badge variant="secondary" className={cn("text-xs", config.className)}>
      {config.label}
    </Badge>
  );
}