"use client";
import Link from "next/link";
import { useState } from "react";
import { api } from "@/lib/api";
import { useLoad } from "@/lib/hooks";
import TicketTable from "@/components/TicketTable";
import { Empty, ErrorState, Loading } from "@/components/StateViews";

export default function Dashboard() {
  const stats = useLoad(() => api.analytics());
  const queue = useLoad(() => api.listTickets({ open_only: true, sort: "priority", limit: 8 }));
  const [seeding, setSeeding] = useState(false);

  const seed = async () => {
    setSeeding(true);
    try { await api.seedDemo(); stats.reload(); queue.reload(); } finally { setSeeding(false); }
  };

  if (stats.loading && !stats.data) return <Loading label="Loading queue" />;
  if (stats.error) return <ErrorState message={stats.error} onRetry={() => { stats.reload(); queue.reload(); }} />;
  const s = stats.data!;
  const maxDept = Math.max(1, ...s.by_department.map((d) => d.count));

  return (
    <>
      <header className="page-head">
        <div><h1>Support queue</h1><p className="muted">Open tickets, most urgent first.</p></div>
        <Link href="/tickets/new" className="btn primary">New ticket</Link>
      </header>

      <section className="stats">
        <div className="stat"><div className="stat-n">{s.open}</div><div>Open tickets</div></div>
        <div className="stat urgent"><div className="stat-n">{s.urgent_open}</div><div>High or critical, still open</div></div>
        <div className="stat"><div className="stat-n">{s.needs_review}</div><div>Need an agent to confirm</div></div>
        <div className="stat"><div className="stat-n">{s.total}</div><div>Tickets in total</div></div>
      </section>

      {s.total === 0 ? (
        <Empty title="No tickets yet">
          <p className="muted">Submit a ticket to see it triaged, or load a few sample tickets.</p>
          <div className="row-gap">
            <Link href="/tickets/new" className="btn primary">Create a ticket</Link>
            <button className="btn" onClick={seed} disabled={seeding}>{seeding ? "Loading…" : "Load sample tickets"}</button>
          </div>
        </Empty>
      ) : (
        <div className="grid-2-1">
          <div className="panel flush">
            <div className="panel-head"><h2>Needs attention</h2><Link href="/tickets" className="link">View all tickets</Link></div>
            {queue.loading && !queue.data ? <Loading /> : queue.error ? <ErrorState message={queue.error} onRetry={queue.reload} /> :
              queue.data && queue.data.items.length > 0 ? <TicketTable items={queue.data.items} compact /> : <Empty title="Queue is clear" />}
          </div>
          <div className="panel">
            <h2>Workload by team</h2>
            <ul className="bars">
              {s.by_department.map((d) => (
                <li key={d.label}>
                  <div className="bar-label"><span>{d.label}</span><span>{d.count}</span></div>
                  <div className="bar-track"><div style={{ width: `${(d.count / maxDept) * 100}%` }} /></div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </>
  );
}
