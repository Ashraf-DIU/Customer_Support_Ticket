import type { Analytics, Health, ModelInfo, Prediction, Ticket, TicketList } from "./types";

export const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/+$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, { ...init, headers: { "Content-Type": "application/json", ...(init?.headers || {}) } });
  } catch {
    throw new Error("Cannot reach the API. If it is hosted on a free plan it may be waking up, so retry in about a minute.");
  }
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") msg = body.detail;
      else if (Array.isArray(body.detail)) msg = body.detail.map((d: { loc?: string[]; msg: string }) => `${d.loc?.slice(-1)[0] ?? "input"}: ${d.msg}`).join("; ");
    } catch { /* keep default message */ }
    throw new Error(msg);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

type Params = Record<string, string | number | boolean | undefined>;
const qs = (p: Params) => {
  const s = new URLSearchParams();
  Object.entries(p).forEach(([k, v]) => { if (v !== undefined && v !== "") s.set(k, String(v)); });
  const out = s.toString();
  return out ? `?${out}` : "";
};

export interface NewTicket {
  customer_name: string; customer_email?: string; product?: string; channel: string; subject: string; message: string;
}

export const api = {
  health: () => request<Health>("/api/health"),
  predict: (body: { subject: string; message: string }) => request<Prediction>("/api/predict", { method: "POST", body: JSON.stringify(body) }),
  createTicket: (body: NewTicket) => request<Ticket>("/api/tickets", { method: "POST", body: JSON.stringify(body) }),
  listTickets: (p: Params = {}) => request<TicketList>(`/api/tickets${qs(p)}`),
  getTicket: (id: number | string) => request<Ticket>(`/api/tickets/${id}`),
  updateTicket: (id: number, patch: Partial<Pick<Ticket, "status" | "priority" | "department" | "suggested_reply">>) =>
    request<Ticket>(`/api/tickets/${id}`, { method: "PATCH", body: JSON.stringify(patch) }),
  deleteTicket: (id: number) => request<void>(`/api/tickets/${id}`, { method: "DELETE" }),
  suggestReply: (id: number) => request<Ticket>(`/api/tickets/${id}/suggest-reply`, { method: "POST" }),
  analytics: () => request<Analytics>("/api/analytics"),
  modelInfo: () => request<ModelInfo>("/api/model-info"),
  seedDemo: () => request<{ created: number }>("/api/demo/seed", { method: "POST" }),
};
