import Link from "next/link";
import { PriorityBadge, SentimentTag, StatusBadge } from "./Badges";
import { slug, timeAgo } from "@/lib/format";
import type { Ticket } from "@/lib/types";

export default function TicketTable({ items, compact = false }: { items: Ticket[]; compact?: boolean }) {
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            <th>Ticket</th><th>Category</th><th>Priority</th>
            {!compact && <th>Sentiment</th>}
            {!compact && <th>Route to</th>}
            <th>Status</th><th>Created</th>
          </tr>
        </thead>
        <tbody>
          {items.map((t) => (
            <tr key={t.id} className={`rail rail-${slug(t.priority)}`}>
              <td>
                <Link href={`/tickets/${t.id}`} className="ticket-link">{t.subject}</Link>
                <div className="muted small">{t.code} · {t.customer_name}{t.needs_review ? " · needs review" : ""}</div>
              </td>
              <td>{t.category}</td>
              <td><PriorityBadge value={t.priority} /></td>
              {!compact && <td><SentimentTag value={t.sentiment} /></td>}
              {!compact && <td>{t.department}</td>}
              <td><StatusBadge value={t.status} /></td>
              <td className="muted nowrap">{timeAgo(t.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
