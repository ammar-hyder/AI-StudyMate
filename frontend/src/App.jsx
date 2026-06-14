import { useState } from "react";

import { generateStudyMaterial, sendEmail } from "./api";
import LoadingSpinner from "./components/LoadingSpinner";
import NotesForm from "./components/NotesForm";
import ResultsDisplay from "./components/ResultsDisplay";
import "./styles.css";

function getErrorMessage(error) {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(" ");
  }
  if (typeof detail === "string") {
    return detail;
  }
  return "Something went wrong. Please try again.";
}

export default function App() {
  const [notes, setNotes] = useState("");
  const [email, setEmail] = useState("");
  const [result, setResult] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  async function handleGenerate(event) {
    event.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");
    setIsGenerating(true);

    try {
      const data = await generateStudyMaterial(notes);
      setResult(data);
      setSuccessMessage("Study material generated successfully.");
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleSendEmail() {
    setErrorMessage("");
    setSuccessMessage("");
    setIsSending(true);

    try {
      const data = await sendEmail(email, result);
      setSuccessMessage(data.message || "Email sent successfully.");
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsSending(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Semester DevOps Project</p>
          <h1>AI StudyMate</h1>
          <p className="subtitle">
            Generate summaries, flashcards, MCQs, and revision points from your notes.
          </p>
        </div>
      </header>

      <section className="workspace">
        <NotesForm
          notes={notes}
          email={email}
          hasResult={Boolean(result)}
          isGenerating={isGenerating}
          isSending={isSending}
          onNotesChange={setNotes}
          onEmailChange={setEmail}
          onGenerate={handleGenerate}
          onSendEmail={handleSendEmail}
        />

        <div className="output-panel">
          {isGenerating && <LoadingSpinner label="Generating study material" />}
          {isSending && <LoadingSpinner label="Sending email" />}
          {errorMessage && <div className="alert error">{errorMessage}</div>}
          {successMessage && <div className="alert success">{successMessage}</div>}
          <ResultsDisplay result={result} />
        </div>
      </section>
    </main>
  );
}
