import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const severityConfig: Record<string, { label: string; className: string }> = {
  critical: {
    label: "Critical",
    className: "bg-red-600 text-white hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800",
  },
  high: {
    label: "High",
    className: "bg-orange-500 text-white hover:bg-orange-600 dark:bg-orange-600 dark:hover:bg-orange-700",
  },
  medium: {
    label: "Medium",
    className: "bg-yellow-500 text-white hover:bg-yellow-600 dark:bg-yellow-600 dark:hover:bg-yellow-700",
  },
  low: {
    label: "Low",
    className: "bg-green-600 text-white hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-800",
  },
};

export function SeverityBadge({ severity }: { severity: string | null }) {
  if (!severity) return <span className="text-xs text-muted-foreground">—</span>;

  const config = severityConfig[severity] || { label: severity, className: "" };
  
  return <Badge className={cn("text-xs", config.className)}>{config.label}</Badge>;

}