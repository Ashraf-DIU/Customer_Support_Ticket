"use client";
import { api } from "@/lib/api";
import { useLoad } from "@/lib/hooks";
import { pct } from "@/lib/format";
import { Donut, HBar, Trend } from "@/components/AnalyticsCharts";
import { ErrorState, Loading } from "@/components/StateViews";

export default function AnalyticsPage() {
  const a = useLoad(() => api.analytics());
  const m = useLoad(() => api.modelInfo());

  if (a.loading && !a.data) return <Loading label="Loading analytics" />;
  if (a.error) return <ErrorState message={a.error} onRetry={a.reload} />;
  const d = a.data!;
  const tasks = m.data?.metrics.tasks;

  return (
    <>
      <header className="page-head"><div><h1>Analytics</h1><p className="muted">{d.total} tickets triaged so far.</p></div></header>
      {d.total === 0 ? <div className="state"><strong>No data yet</strong><p className="muted">Create a few tickets and the charts will fill in.</p></div> : (
        <div className="grid-2">
          <div className="panel"><h2>Tickets by category</h2><HBar data={d.by_category} /></div>
          <div className="panel"><h2>Tickets by team</h2><HBar data={d.by_department} /></div>
          <div className="panel"><h2>Priority mix</h2><Donut data={d.by_priority} kind="priority" /></div>
          <div className="panel"><h2>Customer sentiment</h2><Donut data={d.by_sentiment} kind="sentiment" /></div>
          <div className="panel wide"><h2>Tickets created, last 14 days</h2><Trend data={d.daily} /></div>
        </div>
      )}

      <div className="panel flush" style={{ marginTop: 20 }}>
        <div className="panel-head"><h2>Model quality</h2><span className="muted small">{m.data ? `Version ${m.data.version}` : ""}</span></div>
        {tasks ? (
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Task</th><th>Predicts</th><th>Best model</th><th>Test macro-F1</th><th>Random guessing</th><th>Result</th></tr></thead>
              <tbody>
                {Object.entries(tasks).map(([name, t]) => (
                  <tr key={name}>
                    <td>{name}</td><td>{t.target_column}</td><td>{t.best_model}</td>
                    <td>{t.test_macro_f1.toFixed(2)} <span className="muted small">(acc {pct(t.test_accuracy)})</span></td>
                    <td>{t.baseline_macro_f1.toFixed(2)}</td>
                    <td><span className={`badge ${t.above_chance ? "s-resolved" : "p-medium"}`}>{t.above_chance ? "Learns signal" : "Near chance"}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="state"><p className="muted">No trained models loaded. The API is using keyword rules. Run the Colab notebook and copy the files into backend/artifacts.</p></div>}
        {tasks && Object.values(tasks).some((t) => !t.above_chance) && (
          <p className="notice" style={{ margin: 16 }}>
            A result near random guessing means the labels in the training data do not depend on the ticket text. This is common with synthetic datasets. Urgency rules and the agent review flag keep routing safe in that case.
          </p>
        )}
      </div>
    </>
  );
}
