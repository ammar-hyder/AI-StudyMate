export default function NotesForm({
  notes,
  email,
  hasResult,
  isGenerating,
  isSending,
  onNotesChange,
  onEmailChange,
  onGenerate,
  onSendEmail,
}) {
  return (
    <form className="notes-panel" onSubmit={onGenerate}>
      <label htmlFor="notes">Study notes</label>
      <textarea
        id="notes"
        value={notes}
        onChange={(event) => onNotesChange(event.target.value)}
        placeholder="Paste at least 20 characters of lecture notes, textbook notes, or revision content..."
        rows={12}
      />

      <label htmlFor="email">Email address</label>
      <input
        id="email"
        type="email"
        value={email}
        onChange={(event) => onEmailChange(event.target.value)}
        placeholder="student@example.com"
      />

      <div className="actions">
        <button type="submit" disabled={isGenerating || isSending}>
          {isGenerating ? "Generating..." : "Generate Study Material"}
        </button>
        <button
          type="button"
          className="secondary-button"
          disabled={!hasResult || isGenerating || isSending}
          onClick={onSendEmail}
        >
          {isSending ? "Sending..." : "Send Result to Email"}
        </button>
      </div>
    </form>
  );
}
