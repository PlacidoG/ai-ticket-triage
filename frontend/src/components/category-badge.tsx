
import { Badge } from "@/components/ui/badge";

const categoryLabels: Record<string, string> = {
  bug_report: "Bug Report",
  billing: "Billing",
  account_access: "Account Access",
  feature_request: "Feature Request",
  general: "General",
};

export function CategoryBadge({ category }: { category: string | null }) {
  if (!category) return <span className="text-xs text-muted-foreground">—</span>;
  const label = categoryLabels[category] || category;
  return <Badge variant="outline" className="text-xs">{label}</Badge>;
}