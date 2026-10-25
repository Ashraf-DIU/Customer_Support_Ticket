export function Loading({ label = "Loading" }: { label?: string }) {
  return <div className="state" role="status"><span className="spinner" />{label}…</div>;
}
export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="state error" role="alert">
      <p>{message}</p>
      {onRetry && <button className="btn" onClick={onRetry}>Retry</button>}
    </div>
  );
}
export function Empty({ title, children }: { title: string; children?: React.ReactNode }) {
  return <div className="state"><strong>{title}</strong>{children}</div>;
}
