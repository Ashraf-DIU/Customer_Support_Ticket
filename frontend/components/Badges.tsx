import { pct, slug } from "@/lib/format";

export function PriorityBadge({ value }: { value: string }) {
  return <span className={`badge p-${slug(value)}`}>{value}</span>;
}
export function StatusBadge({ value }: { value: string }) {
  return <span className={`badge s-${slug(value)}`}>{value}</span>;
}
export function SentimentTag({ value }: { value: string }) {
  return <span className={`sent sent-${slug(value)}`}><i />{value}</span>;
}
export function Confidence({ value }: { value: number }) {
  if (!value) return <span className="muted small">n/a</span>;
  return (
    <span className="conf" title={`Model confidence ${pct(value)}`}>
      <span className="conf-bar"><span className={value < 0.4 ? "low" : ""} style={{ width: pct(value) }} /></span>
      <span className="small">{pct(value)}</span>
    </span>
  );
}
