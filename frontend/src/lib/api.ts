
// --- Types matching your backend Pydantic schemas ---

export interface Ticket {
  id: string;
  title: string;
  description: string;
  status: string;
  source: string;
  submitter_email: string | null;
  assigned_to: string | null;
  created_at: string;
  updated_at: string;
}

export interface Enrichment {
  id: string;
  severity: string;
  category: string;
  summary: string;
  suggested_response: string;
  confidence: number;
  model_used: string;
  prompt_version: string;
  tokens_in: number;
  tokens_out: number;
  estimated_cost: number;
  raw_response: string | null;
  created_at: string;
}

export interface TicketDetail extends Ticket {
  enrichment: Enrichment | null;
}

export interface TicketListResponse {
  tickets: Ticket[];
  next_cursor: string | null;
  has_more: boolean;
}

export interface DashboardSummary {
  total_tickets: number;
  open_tickets: number;
  critical_high_count: number;
  ai_accuracy_rate: number;
  avg_enrichment_cost: number;
  total_enrichment_cost: number;
  total_enriched: number;
}

export interface TicketsByField {
  label: string;
  count: number;
}

export interface OverrideBreakdown {
  field: string;
  override_count: number;
  total_enriched: number;
  accuracy_rate: number;
}

export interface DashboardCharts {
  by_severity: TicketsByField[];
  by_category: TicketsByField[];
  by_status: TicketsByField[];
  override_breakdown: OverrideBreakdown[];
}

// --- API Client ---

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail?.message || error.detail || `API error: ${res.status}`);
  }

  return res.json();
}

// --- Ticket endpoints ---

export async function getTickets(params?: {
  status?: string;
  severity?: string;
  category?: string;
  assigned_to?: string;
  after?: string;
  limit?: number;
}): Promise<TicketListResponse> {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        searchParams.set(key, String(value));
      }
    });
  }
  const query = searchParams.toString();
  return fetchAPI<TicketListResponse>(
    `/api/tickets${query ? `?${query}` : ""}`
  );
}

export async function getTicketById(id: string): Promise<TicketDetail> {
  return fetchAPI<TicketDetail>(`/api/tickets/${id}`);
}

export async function createTicket(data: {
  title: string;
  description: string;
  submitter_email?: string;
}): Promise<Ticket> {
  return fetchAPI<Ticket>("/api/tickets", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateTicket(
  id: string,
  data: { status?: string; assigned_to?: string; agent_id?: string }
): Promise<Ticket> {
  return fetchAPI<Ticket>(`/api/tickets/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function overrideEnrichment(
  ticketId: string,
  data: { field: string; new_value: string; agent_id: string }
): Promise<{ ticket_id: string; field: string; old_value: string; new_value: string }> {
  return fetchAPI(`/api/tickets/${ticketId}/override`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// --- Dashboard endpoints ---

export async function getDashboardSummary(): Promise<DashboardSummary> {
  return fetchAPI<DashboardSummary>("/api/dashboard/summary");
}

export async function getDashboardCharts(): Promise<DashboardCharts> {
  return fetchAPI<DashboardCharts>("/api/dashboard/charts");
}