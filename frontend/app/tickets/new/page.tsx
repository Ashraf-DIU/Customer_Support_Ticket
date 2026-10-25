"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import { CHANNELS, type Prediction } from "@/lib/types";
import PredictionPanel from "@/components/PredictionPanel";

const EXAMPLES = [
  { label: "Payment problem", product: "GoPro Hero", subject: "Payment deducted but order cancelled", message: "My payment was deducted but my order was cancelled. I have contacted support twice and nobody has resolved this issue." },
  { label: "Won't turn on", product: "Dell XPS", subject: "Laptop will not boot", message: "My laptop shows a black screen after the logo and restarts. I already tried a hard reset and nothing changed." },
  { label: "Cancel plan", product: "", subject: "Cancel my subscription", message: "Please cancel my subscription before the next billing date and confirm by email." },
  { label: "Pre-sale question", product: "Sony Xperia", subject: "Is this compatible with my headset?", message: "Does this phone support Bluetooth 5.2 headsets with aptX? I want to be sure before I buy." },
];

export default function NewTicket() {
  const router = useRouter();
  const [f, setF] = useState({ customer_name: "", customer_email: "", product: "", channel: "Web form", subject: "", message: "" });
  const [pred, setPred] = useState<Prediction | null>(null);
  const [busy, setBusy] = useState<"" | "analyze" | "submit">("");
  const [error, setError] = useState("");

  const set = (k: keyof typeof f) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setF({ ...f, [k]: e.target.value }); setPred(null);
  };
  const valid = f.subject.trim().length >= 3 && f.message.trim().length >= 10;

  const analyze = async () => {
    setBusy("analyze"); setError("");
    try { setPred(await api.predict({ subject: f.subject, message: f.message })); }
    catch (e) { setError((e as Error).message); } finally { setBusy(""); }
  };
  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setBusy("submit"); setError("");
    try {
      const t = await api.createTicket({ ...f, customer_name: f.customer_name.trim() || "Customer", customer_email: f.customer_email || undefined, product: f.product || undefined });
      router.push(`/tickets/${t.id}`);
    } catch (err) { setError((err as Error).message); setBusy(""); }
  };

  return (
    <>
      <header className="page-head"><div><h1>New ticket</h1><p className="muted">Describe the issue. You can preview the AI triage before submitting.</p></div></header>
      <div className="grid-3-2">
        <form className="panel form" onSubmit={submit}>
          <div className="chips" aria-label="Fill with an example">
            <span className="muted small">Try an example</span>
            {EXAMPLES.map((x) => (
              <button type="button" key={x.label} className="chip" onClick={() => { setF({ ...f, subject: x.subject, message: x.message, product: x.product }); setPred(null); }}>{x.label}</button>
            ))}
          </div>
          <div className="two-col">
            <label>Customer name<input value={f.customer_name} onChange={set("customer_name")} placeholder="Maya Chen" /></label>
            <label>Email<input type="email" value={f.customer_email} onChange={set("customer_email")} placeholder="maya@example.com" /></label>
            <label>Product<input value={f.product} onChange={set("product")} placeholder="Dell XPS" /></label>
            <label>Channel<select value={f.channel} onChange={set("channel")}>{CHANNELS.map((c) => <option key={c}>{c}</option>)}</select></label>
          </div>
          <label>Subject<input required minLength={3} maxLength={200} value={f.subject} onChange={set("subject")} placeholder="Short summary of the problem" /></label>
          <label>Message<textarea required minLength={10} maxLength={5000} rows={7} value={f.message} onChange={set("message")} placeholder="What happened, what you tried, and what you expect." />
            <span className="muted small">{f.message.length}/5000</span></label>
          {error && <p className="notice error" role="alert">{error}</p>}
          <div className="row-gap">
            <button type="button" className="btn" disabled={!valid || busy !== ""} onClick={analyze}>{busy === "analyze" ? "Analyzing…" : "Preview AI triage"}</button>
            <button type="submit" className="btn primary" disabled={!valid || busy !== ""}>{busy === "submit" ? "Submitting…" : "Submit ticket"}</button>
          </div>
        </form>
        <div>
          {pred ? <PredictionPanel data={pred} /> : (
            <div className="panel"><h2>AI triage</h2><p className="muted">Fill in the subject and message, then choose Preview AI triage to see the category, priority, sentiment and team it would be routed to.</p></div>
          )}
        </div>
      </div>
    </>
  );
}
