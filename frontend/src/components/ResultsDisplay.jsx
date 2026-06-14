export default function ResultsDisplay({ result }) {
  if (!result) {
    return (
      <section className="empty-state">
        <h2>Your study material will appear here</h2>
        <p>Generate a summary, flashcards, MCQs, and revision points from your notes.</p>
      </section>
    );
  }

  return (
    <section className="results">
      <div className="result-section">
        <h2>Summary</h2>
        <p>{result.summary}</p>
      </div>

      <div className="result-section">
        <h2>Flashcards</h2>
        <div className="card-grid">
          {result.flashcards.map((card, index) => (
            <article className="study-card" key={`${card.question}-${index}`}>
              <h3>{card.question}</h3>
              <p>{card.answer}</p>
            </article>
          ))}
        </div>
      </div>

      <div className="result-section">
        <h2>MCQs</h2>
        <div className="mcq-list">
          {result.mcqs.map((mcq, index) => (
            <article className="mcq-card" key={`${mcq.question}-${index}`}>
              <h3>{mcq.question}</h3>
              <ol>
                {mcq.options.map((option) => (
                  <li key={option}>{option}</li>
                ))}
              </ol>
              <p className="answer">Answer: {mcq.answer}</p>
            </article>
          ))}
        </div>
      </div>

      <div className="result-section">
        <h2>Key Revision Points</h2>
        <ul className="revision-list">
          {result.revision_points.map((point) => (
            <li key={point}>{point}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}
