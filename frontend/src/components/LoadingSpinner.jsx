export default function LoadingSpinner({ label = "Working" }) {
  return (
    <div className="spinner-row" role="status" aria-live="polite">
      <span className="spinner" />
      <span>{label}</span>
    </div>
  );
}
