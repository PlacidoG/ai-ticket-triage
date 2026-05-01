
import { cn } from "@/lib/utils";

export function ConfidenceIndicator({ confidence }: { confidence: number | null }) {
  if (confidence === null) return <span className="text-xs text-muted-foreground">—</span>;

  const percent = Math.round(confidence * 100);
  const color =
    percent >= 80
      ? "text-green-600 dark:text-green-400"
      : percent >= 50
        ? "text-yellow-600 dark:text-yellow-400"
        : "text-red-600 dark:text-red-400";

  return (
    <div className="flex items-center gap-1.5">
      <div className="h-1.5 w-12 rounded-full bg-muted">
        <div
          className={cn(
            "h-1.5 rounded-full",
            percent >= 80
              ? "bg-green-500"
              : percent >= 50
                ? "bg-yellow-500"
                : "bg-red-500"
          )}
          style={{ width: `${percent}%` }}
        />
      </div>
      <span className={cn("text-xs font-medium", color)}>{percent}%</span>
    </div>
  );
}