"use client";

import { useCallback, useEffect, useState } from "react";
import {
  RefreshCw,
  Loader2,
  Ticket,
  PlusCircle,
  ArrowDown,
  ArrowUp,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { TicketTable } from "@/components/ticket-table";
import {
  TicketFilterSidebar,
  type TicketFilters,
} from "@/components/ticket-filters";
import { getTickets } from "@/lib/api";
import type { Ticket as TicketType } from "@/lib/api";

const REFRESH_INTERVAL = 30_000;
const PAGE_SIZE = 45;
const KNOWN_AGENTS = ["agent_alice", "agent_bob", "agent_carlos"];

export default function TicketsPage() {
  const [tickets, setTickets] = useState<TicketType[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [sortOrder, setSortOrder] = useState<"desc" | "asc">("desc");

  // Pagination state — cursor history for back navigation
  const [currentPage, setCurrentPage] = useState(0);
  const [cursorHistory, setCursorHistory] = useState<(string | null)[]>([null]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);

  const [filters, setFilters] = useState<TicketFilters>({
    status: "",
    severity: "",
    category: "",
    assigned_to: "",
  });

  const fetchPage = useCallback(
    async (cursor: string | null) => {
      try {
        const params: Record<string, string | number> = {
          limit: PAGE_SIZE,
          order: sortOrder,
        };
        if (filters.status) params.status = filters.status;
        if (filters.severity) params.severity = filters.severity;
        if (filters.category) params.category = filters.category;
        if (filters.assigned_to) params.assigned_to = filters.assigned_to;
        if (cursor) params.after = cursor;

        const data = await getTickets(params);

        setTickets(data.tickets);
        setTotal(data.total);
        setNextCursor(data.next_cursor);
        setHasMore(data.has_more);
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load tickets");
      }
    },
    [filters, sortOrder]
  );

  // Initial load and filter/sort changes — reset to page 1
  useEffect(() => {
    setIsLoading(true);
    setCurrentPage(0);
    setCursorHistory([null]);
    fetchPage(null).finally(() => setIsLoading(false));
  }, [fetchPage]);

  // Auto-refresh current page
  useEffect(() => {
    const interval = setInterval(async () => {
      setIsRefreshing(true);
      await fetchPage(cursorHistory[currentPage]);
      setIsRefreshing(false);
    }, REFRESH_INTERVAL);

    return () => clearInterval(interval);
  }, [fetchPage, cursorHistory, currentPage]);

  async function handleRefresh() {
    setIsRefreshing(true);
    await fetchPage(cursorHistory[currentPage]);
    setIsRefreshing(false);
  }

  async function handleOlder() {
    if (!hasMore || !nextCursor) return;
    setIsLoading(true);

    const newPage = currentPage + 1;
    // Store the cursor for this new page so we can come back
    const newHistory = [...cursorHistory];
    newHistory[newPage] = nextCursor;
    setCursorHistory(newHistory);
    setCurrentPage(newPage);

    await fetchPage(nextCursor);
    setIsLoading(false);
    // Scroll to top of table
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleNewer() {
    if (currentPage <= 0) return;
    setIsLoading(true);

    const newPage = currentPage - 1;
    setCurrentPage(newPage);

    await fetchPage(cursorHistory[newPage]);
    setIsLoading(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function toggleSortOrder() {
    setSortOrder((prev) => (prev === "desc" ? "asc" : "desc"));
  }

  // Calculate range display: "1–45 of 110"
  const rangeStart = total === 0 ? 0 : currentPage * PAGE_SIZE + 1;
  const rangeEnd = Math.min(rangeStart + tickets.length - 1, total);
  const hasPrev = currentPage > 0;
  const hasNext = hasMore;

  return (
    <div className="flex flex-col gap-6 h-full">
      {/* Header */}
      <div className="flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-3xl font-bold">Tickets</h1>
          <p className="text-muted-foreground">
            View and manage all support tickets
          </p>
        </div>
        <Link href="/submit">
          <Button size="sm" className="transition-colors hover:bg-blue-600 hover:text-white">
            <PlusCircle className="mr-2 h-4 w-4" />
            New Ticket
          </Button>
        </Link>
      </div>

      {/* Main content: Filters + Table */}
      <div className="flex gap-6 flex-1 min-h-0">
        {/* Sticky filter sidebar */}
        <div className="shrink-0 self-start sticky top-0">
          <TicketFilterSidebar
            filters={filters}
            onChange={setFilters}
            agents={KNOWN_AGENTS}
          />
        </div>

        {/* Table area */}
        <div className="flex-1 space-y-4">
          {/* Toolbar: refresh left, sort + pagination right */}
          {!isLoading && !error && tickets.length > 0 && (
            <div className="flex items-center justify-between sticky top-0 z-10 bg-background py-2">
              <Button variant="outline" size="sm" onClick={handleRefresh}>
                <RefreshCw
                  className={`mr-2 h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`}
                />
                Refresh
              </Button>

              <div className="flex items-center gap-3">
                {isRefreshing && (
                  <span className="text-xs text-muted-foreground">Refreshing...</span>
                )}

                <Button
                  variant="outline"
                  size="sm"
                  onClick={toggleSortOrder}
                  className="gap-2"
                >
                  {sortOrder === "desc" ? (
                    <>
                      <ArrowDown className="h-3.5 w-3.5" />
                      Newest First
                    </>
                  ) : (
                    <>
                      <ArrowUp className="h-3.5 w-3.5" />
                      Oldest First
                    </>
                  )}
                </Button>

                <span className="text-sm text-muted-foreground">
                  <span className="font-medium text-foreground">
                    {rangeStart}–{rangeEnd}
                  </span>
                  {" "}of{" "}
                  <span className="font-medium text-foreground">{total}</span>
                </span>
                <div className="flex items-center">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={handleNewer}
                    disabled={!hasPrev}
                    title="Newer"
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={handleOlder}
                    disabled={!hasNext}
                    title="Older"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Loading state */}
          {isLoading && (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          )}

          {/* Error state */}
          {error && !isLoading && (
            <div className="rounded-lg border border-destructive p-6 text-center">
              <p className="text-destructive">{error}</p>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                className="mt-3"
              >
                Try Again
              </Button>
            </div>
          )}

          {/* Empty state */}
          {!isLoading && !error && tickets.length === 0 && (
            <div className="rounded-lg border-2 border-dashed p-12 text-center">
              <Ticket className="mx-auto h-10 w-10 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-medium">No tickets found</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                {Object.values(filters).some((v) => v !== "")
                  ? "No tickets match your current filters. Try adjusting or clearing them."
                  : "No tickets have been submitted yet. Create one to get started."}
              </p>
              {Object.values(filters).some((v) => v !== "") ? (
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-4"
                  onClick={() =>
                    setFilters({
                      status: "",
                      severity: "",
                      category: "",
                      assigned_to: "",
                    })
                  }
                >
                  Clear Filters
                </Button>
              ) : (
                <Link href="/submit">
                  <Button size="sm" className="mt-4">
                    <PlusCircle className="mr-2 h-4 w-4" />
                    Submit a Ticket
                  </Button>
                </Link>
              )}
            </div>
          )}

          {/* Table */}
          {!isLoading && !error && tickets.length > 0 && (
            <>
              <TicketTable tickets={tickets} />

              {/* Bottom pagination (mirrors top for convenience) */}
              <div className="flex items-center justify-end py-2">
                <div className="flex items-center gap-3">
                  <span className="text-sm text-muted-foreground">
                    <span className="font-medium text-foreground">
                      {rangeStart}–{rangeEnd}
                    </span>
                    {" "}of{" "}
                    <span className="font-medium text-foreground">{total}</span>
                  </span>
                  <div className="flex items-center">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={handleNewer}
                      disabled={!hasPrev}
                      title="Newer"
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={handleOlder}
                      disabled={!hasNext}
                      title="Older"
                    >
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}