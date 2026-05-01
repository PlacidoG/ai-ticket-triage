
"use client";

import { X, Filter, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";

export interface TicketFilters {
  status: string;
  severity: string;
  category: string;
  assigned_to: string;
}

interface TicketFilterSidebarProps {
  filters: TicketFilters;
  onChange: (filters: TicketFilters) => void;
  agents: string[];
}

const ALL_VALUE = "__all__";

export function TicketFilterSidebar({
  filters,
  onChange,
  agents,
}: TicketFilterSidebarProps) {
  const activeCount = Object.values(filters).filter((v) => v !== "").length;

  function updateFilter(key: keyof TicketFilters, value: string) {
    onChange({ ...filters, [key]: value === ALL_VALUE ? "" : value });
  }

  function clearAll() {
    onChange({ status: "", severity: "", category: "", assigned_to: "" });
  }

  return (
    <div className="w-56 shrink-0 space-y-4 rounded-lg border-2 bg-card p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4" />
          <span className="text-sm font-semibold">Filters</span>
          {activeCount > 0 && (
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground">
              {activeCount}
            </span>
          )}
        </div>
        {activeCount > 0 && (
          <Button variant="ghost" size="sm" onClick={clearAll} className="h-7 px-2">
            <RotateCcw className="mr-1 h-3 w-3" />
            Clear
          </Button>
        )}
      </div>

      <Separator />

      {/* Status */}
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Status
        </label>
        <Select
          value={filters.status || ALL_VALUE}
          onValueChange={(v) => updateFilter("status", v)}
        >
          <SelectTrigger className="h-8 text-xs border-2">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL_VALUE}>All Statuses</SelectItem>
            <SelectItem value="new">New</SelectItem>
            <SelectItem value="triaged">Triaged</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="waiting_on_customer">Waiting</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
            <SelectItem value="closed">Closed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Severity */}
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Severity
        </label>
        <Select
          value={filters.severity || ALL_VALUE}
          onValueChange={(v) => updateFilter("severity", v)}
        >
          <SelectTrigger className="h-8 text-xs border-2">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL_VALUE}>All Severities</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="low">Low</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Category */}
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Category
        </label>
        <Select
          value={filters.category || ALL_VALUE}
          onValueChange={(v) => updateFilter("category", v)}
        >
          <SelectTrigger className="h-8 text-xs border-2">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL_VALUE}>All Categories</SelectItem>
            <SelectItem value="bug_report">Bug Report</SelectItem>
            <SelectItem value="billing">Billing</SelectItem>
            <SelectItem value="account_access">Account Access</SelectItem>
            <SelectItem value="feature_request">Feature Request</SelectItem>
            <SelectItem value="general">General</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Assigned To */}
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Assigned To
        </label>
        <Select
          value={filters.assigned_to || ALL_VALUE}
          onValueChange={(v) => updateFilter("assigned_to", v)}
        >
          <SelectTrigger className="h-8 text-xs border-2">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL_VALUE}>Anyone</SelectItem>
            {agents.map((agent) => (
              <SelectItem key={agent} value={agent}>
                {agent}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}