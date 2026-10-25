"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useDebounced, useLoad } from "@/lib/hooks";
import { CATEGORIES, PRIORITIES, STATUSES } from "@/lib/types";
import TicketTable from "@/components/TicketTable";
import { Empty, ErrorState, Loading } from "@/components/StateViews";

const PAGE = 12;

export default function TicketsPage() {
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [priority, setPriority] = useState("");
  const [category, setCategory] = useState("");
  const [sort, setSort] = useState("newest");
  const [page, setPage] = useState(0);
  const dq = useDebounced(q);

  useEffect(() => setPage(0), [dq, status, priority, category, sort]);
  const { data, error, loading, reload } = useLoad(
    () => api.listTickets({ q: dq, status, priority, category, sort, limit: PAGE, offset: page * PAGE }),
    [dq, status, priority, category, sort, page],
  );
  const pages = data ? Math.max(1, Math.ceil(data.total / PAGE)) : 1;
  const filtered = Boolean(dq || status || priority || category);

  return (
    <>
      <header className="page-head">
        <div><h1>All tickets</h1><p className="muted">{data ? `${data.total} ticket${data.total === 1 ? "" : "s"}` : " "}</p></div>
        <Link href="/tickets/new" className="btn primary">New ticket</Link>
      </header>

      <div className="filters">
        <input type="search" placeholder="Search subject, message or customer" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search tickets" />
        <select value={status} onChange={(e) => setStatus(e.target.value)} aria-label="Status"><option value="">Any status</option>{STATUSES.map((s) => <option key={s}>{s}</option>)}</select>
        <select value={priority} onChange={(e) => setPriority(e.target.value)} aria-label="Priority"><option value="">Any priority</option>{PRIORITIES.map((s) => <option key={s}>{s}</option>)}</select>
        <select value={category} onChange={(e) => setCategory(e.target.value)} aria-label="Category"><option value="">Any category</option>{CATEGORIES.map((s) => <option key={s}>{s}</option>)}</select>
        <select value={sort} onChange={(e) => setSort(e.target.value)} aria-label="Sort"><option value="newest">Newest first</option><option value="oldest">Oldest first</option><option value="priority">Highest priority</option></select>
      </div>

      <div className="panel flush">
        {error ? <ErrorState message={error} onRetry={reload} /> : loading && !data ? <Loading /> :
          data && data.items.length > 0 ? <TicketTable items={data.items} /> :
          <Empty title={filtered ? "No tickets match these filters" : "No tickets yet"}>
            {!filtered && <Link href="/tickets/new" className="btn primary">Create the first ticket</Link>}
          </Empty>}
      </div>

      {data && data.total > PAGE && (
        <div className="pager">
          <button className="btn" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
          <span className="muted">Page {page + 1} of {pages}</span>
          <button className="btn" disabled={page + 1 >= pages} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      )}
    </>
  );
}
