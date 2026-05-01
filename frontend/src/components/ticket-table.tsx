
"use client";

import { useRouter } from "next/navigation";
import { formatDistanceToNow } from "date-fns";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { SeverityBadge } from "@/components/severity-badge";
import { CategoryBadge } from "@/components/category-badge";
import { StatusBadge } from "@/components/status-badge";
import { ConfidenceIndicator } from "@/components/confidence-indicator";
import type { Ticket } from "@/lib/api";

interface TicketTableProps {
  tickets: Ticket[];
}

export function TicketTable({ tickets }: TicketTableProps) {
  const router = useRouter();

  return (
    <div className="rounded-lg border-2">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[280px]">Title</TableHead>
            <TableHead className="w-[100px]">Status</TableHead>
            <TableHead className="w-[100px]">Severity</TableHead>
            <TableHead className="w-[130px]">Category</TableHead>
            <TableHead className="w-[100px]">Confidence</TableHead>
            <TableHead className="w-[80px]">Source</TableHead>
            <TableHead className="w-[120px]">Created</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {tickets.map((ticket) => (
            <TableRow
              key={ticket.id}
              className="cursor-pointer hover:bg-muted/50"
              onClick={() => router.push(`/tickets/${ticket.id}`)}
            >
              <TableCell className="font-medium">
                <div className="max-w-[280px] truncate">{ticket.title}</div>
                {ticket.assigned_to && (
                  <div className="text-xs text-muted-foreground">
                    → {ticket.assigned_to}
                  </div>
                )}
              </TableCell>
              <TableCell>
                <StatusBadge status={ticket.status} />
              </TableCell>
              <TableCell>
                <SeverityBadge severity={ticket.severity} />
              </TableCell>
              <TableCell>
                <CategoryBadge category={ticket.category} />
              </TableCell>
              <TableCell>
                <ConfidenceIndicator confidence={ticket.confidence} />
              </TableCell>
              <TableCell>
                <span className="text-xs text-muted-foreground">
                  {ticket.source === "web_form" ? "Form" : ticket.source}
                </span>
              </TableCell>
              <TableCell>
                <span className="text-xs text-muted-foreground">
                  {formatDistanceToNow(new Date(ticket.created_at), {
                    addSuffix: true,
                  })}
                </span>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}