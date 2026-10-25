"use client";
import { ArrowLeft, Copy, RefreshCw, Trash2 } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { fullDate } from "@/lib/format";
import { useLoad } from "@/lib/hooks";
import { DEPARTMENTS, PRIORITIES, STATUSES, type Ticket } from "@/lib/types";
import { PriorityBadge, StatusBadge } from "@/components/Badges";
import PredictionPanel from "@/components/PredictionPanel";
import { ErrorState, Loading } from "@/components/StateViews";

export default function TicketDetail() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { data, error, loading, reload } = useLoad(() => api.getTicket(id), [id]);
  const [t, setT] = useState<Ticket | null>(null);
  const [reply, setReply] = useState("");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => { if (data) { setT(data); setReply(data.suggested_reply ?? ""); } }, [data]);
  const flash = (m: string) => { setMsg(m); setTimeout(() => setMsg(""), 2500); };

  const patch = async (p: Parameters<typeof api.updateTicket>[1], label: string) => {
    if (!t) return;
    setBusy(true);
    try { const u = await api.updateTicket(t.id, p); setT(u); flash(label); } catch (e) { flash((e as Error).message); } finally { setBusy(false); }
  };
  const regenerate = async () => {
    if (!t) return;
    setBusy(true);
    try { const u = await api.suggestReply(t.id); setT(u); setReply(u.suggested_reply ?? ""); flash("New draft ready"); } catch (e) { flash((e as Error).message); } finally { setBusy(false); }
  };
  const remove = async () => {
    if (!t || !window.confirm(`Delete ${t.code}? This cannot be undone.`)) return;
    await api.deleteTicket(t.id); router.push("/tickets");
  };
  const copy = async () => { await navigator.clipboard.writeText(reply); flash("Copied to clipboard"); };

  if (loading && !t) return <Loading label="Loading ticket" />;
  if (error) return <ErrorState message={error} onRetry={reload} />;
  if (!t) return null;

  return (
    <>
      <Link href="/tickets" className="back"><ArrowLeft size={16} aria-hidden />All tickets</Link>
      <header className="page-head">
        <div>
          <h1>{t.subject}</h1>
          <p className="muted">{t.code} · opened {fullDate(t.created_at)} · {t.channel}</p>
        </div>
        <div className="row-gap"><PriorityBadge value={t.priority} /><StatusBadge value={t.status} /></div>
      </header>
      {msg && <div className="toast" role="status">{msg}</div>}

      <div className="grid-3-2">
        <div className="stack">
          <div className="panel">
            <h2>Customer message</h2>
            <p className="meta">{t.customer_name}{t.customer_email ? ` · ${t.customer_email}` : ""}{t.product ? ` · ${t.product}` : ""}</p>
            <p className="message">{t.description}</p>
          </div>

          <div className="panel">
            <div className="panel-head">
              <h2>Reply draft</h2>
              <span className="tag">{t.reply_source === "llm" ? "Written by LLM" : "Template draft"}</span>
            </div>
            <p className="muted small">AI-generated draft. An agent must review and edit it before sending.</p>
            <textarea rows={10} value={reply} onChange={(e) => setReply(e.target.value)} aria-label="Reply draft" />
            <div className="row-gap">
              <button className="btn" onClick={regenerate} disabled={busy}><RefreshCw size={15} aria-hidden />Regenerate</button>
              <button className="btn" onClick={() => patch({ suggested_reply: reply }, "Draft saved")} disabled={busy || reply === (t.suggested_reply ?? "")}>Save edits</button>
              <button className="btn" onClick={copy} disabled={!reply}><Copy size={15} aria-hidden />Copy</button>
            </div>
          </div>
        </div>

        <div className="stack">
          <PredictionPanel data={t} />
          <div className="panel">
            <h2>Handling</h2>
            <div className="form">
              <label>Status<select value={t.status} disabled={busy} onChange={(e) => patch({ status: e.target.value }, "Status updated")}>{STATUSES.map((s) => <option key={s}>{s}</option>)}</select></label>
              <label>Priority<select value={t.priority} disabled={busy} onChange={(e) => patch({ priority: e.target.value }, "Priority updated")}>{PRIORITIES.map((s) => <option key={s}>{s}</option>)}</select></label>
              <label>Team<select value={t.department} disabled={busy} onChange={(e) => patch({ department: e.target.value }, "Team updated")}>{Array.from(new Set([...DEPARTMENTS, t.department])).map((s) => <option key={s}>{s}</option>)}</select></label>
            </div>
            <p className="muted small">Last updated {fullDate(t.updated_at)} · model {t.model_version}</p>
            <button className="btn danger" onClick={remove}><Trash2 size={15} aria-hidden />Delete ticket</button>
          </div>
        </div>
      </div>
    </>
  );
}
