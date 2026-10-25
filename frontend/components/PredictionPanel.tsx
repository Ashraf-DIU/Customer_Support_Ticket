import { Confidence, PriorityBadge, SentimentTag } from "./Badges";
import type { Prediction } from "@/lib/types";

type PanelData = Omit<Prediction, "category_alternatives" | "model_version" | "sentiment_score" | "priority_reason"> & {
  category_alternatives?: Prediction["category_alternatives"];
  priority_reason?: string | null;
};

export default function PredictionPanel({ data }: { data: PanelData }) {
  return (
    <div className="panel">
      <h2>AI triage</h2>
      {data.needs_review && (
        <p className="notice">Low confidence. Have an agent confirm the category and priority before routing.</p>
      )}
      <dl className="facts">
        <dt>Category</dt><dd>{data.category} <Confidence value={data.category_confidence} /></dd>
        <dt>Issue topic</dt><dd>{data.topic} <Confidence value={data.topic_confidence} /></dd>
        <dt>Priority</dt>
        <dd>
          <PriorityBadge value={data.priority} />
          {data.priority_confidence > 0 && <Confidence value={data.priority_confidence} />}
          <div className="muted small">{data.priority_reason}</div>
        </dd>
        <dt>Sentiment</dt><dd><SentimentTag value={data.sentiment} /></dd>
        <dt>Route to</dt><dd><strong>{data.department}</strong></dd>
      </dl>
      {data.category_alternatives && data.category_alternatives.length > 1 && (
        <div className="alts">
          <div className="muted small">Other likely categories</div>
          {data.category_alternatives.slice(1).map((a) => (
            <div key={a.label} className="alt"><span>{a.label}</span><Confidence value={a.confidence} /></div>
          ))}
        </div>
      )}
    </div>
  );
}
