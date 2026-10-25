export type Priority = "Low" | "Medium" | "High" | "Critical";
export type Status = "Open" | "In Progress" | "Pending Customer" | "Resolved" | "Closed";

export const STATUSES: Status[] = ["Open", "In Progress", "Pending Customer", "Resolved", "Closed"];
export const PRIORITIES: Priority[] = ["Low", "Medium", "High", "Critical"];
export const CATEGORIES = ["Technical issue", "Billing inquiry", "Refund request", "Cancellation request", "Product inquiry"];
export const DEPARTMENTS = ["Technical Support", "Billing Support", "Account Security", "Logistics", "Retention Team", "Sales & Product", "General Support"];
export const CHANNELS = ["Web form", "Email", "Chat", "Phone", "Social media"];

export interface Alternative { label: string; confidence: number }

export interface Prediction {
  category: string; category_confidence: number; category_alternatives: Alternative[];
  priority: string; priority_confidence: number; priority_reason: string;
  topic: string; topic_confidence: number;
  sentiment: string; sentiment_score: number;
  department: string; needs_review: boolean; model_version: string;
}

export interface Ticket {
  id: number; code: string; customer_name: string; customer_email: string | null; product: string | null;
  channel: string; subject: string; description: string;
  category: string; category_confidence: number;
  priority: string; priority_confidence: number; priority_reason: string | null;
  topic: string; topic_confidence: number;
  sentiment: string; sentiment_score: number;
  department: string; needs_review: boolean; model_version: string;
  status: string; suggested_reply: string | null; reply_source: string | null;
  created_at: string; updated_at: string;
}

export interface TicketList { items: Ticket[]; total: number; limit: number; offset: number }
export interface Count { label: string; count: number }
export interface Analytics {
  total: number; open: number; urgent_open: number; needs_review: number;
  by_category: Count[]; by_priority: Count[]; by_sentiment: Count[]; by_department: Count[]; by_status: Count[];
  daily: { date: string; count: number }[];
}
export interface TaskMetrics {
  target_column: string; classes: string[]; best_model: string;
  val_macro_f1: number; test_macro_f1: number; test_accuracy: number;
  baseline_macro_f1: number; baseline_accuracy: number; above_chance: boolean;
}
export interface ModelInfo {
  ready: boolean; version: string;
  metrics: { trained_at?: string; sklearn_version?: string; rows?: Record<string, number>; tasks?: Record<string, TaskMetrics> };
}
export interface Health { status: string; models_loaded: boolean; model_version: string }
