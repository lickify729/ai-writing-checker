import type { WritingFeedback, WritingStyle } from "./types";
import "./App.css";
import { useState, useEffect } from "react";

export default function App() {
  const [text, setText] = useState("");
  const [style, setStyle] = useState<WritingStyle>("academic");
  const [feedback, setFeedback] = useState<WritingFeedback | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Count words (simple: split on whitespace, ignore empty strings)
  const wordCount = text.trim() === "" ? 0 : text.trim().split(/\s+/).length;
  const charCount = text.length;
  const overLimit = charCount > 8000;

    const handleAnalyze = async () => {
    if (text.trim().length === 0) {
      setError("Please enter some text to analyze.");
      setFeedback(null);
      return;
    }
    if (text.length > 8000) {
      setError("Text is too long (max 8,000 characters).");
      setFeedback(null);
      return;
    }

    setError(null);
    setIsLoading(true);
    setFeedback(null);

    try {
      const response = await fetch("http://localhost:8001/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, style }),
      });

      if (!response.ok) {
        // Server returned an error (4xx or 5xx)
        const errBody = await response.json().catch(() => ({}));
        const message =
          errBody.detail ||
          `Server error (${response.status}). Please try again.`;
        setError(message);
        return;
      }

      const data: WritingFeedback = await response.json();
      setFeedback(data);
    } catch (err) {
      // Network failure, CORS issue, or backend not running
      setError(
        "Could not reach the server. Make sure the backend is running on port 8001."
      );
    } finally {
      setIsLoading(false);
      // On small screens, bring the (now-loaded) feedback into view
      if (window.innerWidth < 768) {
        document.querySelector(".feedback-panel")?.scrollIntoView({ behavior: "smooth" });
      }
    }
  };

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === "Enter") {
        handleAnalyze();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [text, style, isLoading]);

  return (
    <div>
      {/* ===== Header ===== */}
      <header className="app-header">
        <h1>AI Writing Checker</h1>
        <p>
          Paste your writing below and get feedback on grammar, clarity,
          conciseness, and tone.
        </p>
      </header>

      {/* ===== Two-Column Workspace ===== */}
      <main className="workspace">
        {/* --- Left: Editor --- */}
        <section className="editor-panel" aria-label="Text editor">
          <label className="editor-label" htmlFor="writing-input">
            Your Writing
          </label>

          <textarea
            id="writing-input"
            className="text-editor"
            placeholder="Paste or type your paragraph or essay here…"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />

          <div className="editor-footer">
            <span className={"word-count" + (overLimit ? " word-count--over" : "")} aria-live="polite">
              {wordCount} {wordCount === 1 ? "word" : "words"} · {charCount.toLocaleString()} / 8,000
            </span>

            <div className="controls-row">
              <select
                className="style-select"
                value={style}
                onChange={(e) => setStyle(e.target.value as WritingStyle)}
                aria-label="Writing style"
              >
                <option value="academic">Academic</option>
                <option value="professional">Professional</option>
                <option value="casual">Casual</option>
              </select>

              <button
                className="analyze-btn"
                onClick={handleAnalyze}
                disabled={isLoading}
              >
                {isLoading ? "Analyzing…" : "Analyze Writing"}
              </button>

              <span className="kbd-hint" style={{ fontSize: "var(--text-xs, 0.75rem)", color: "var(--color-text-muted)" }}>
                Ctrl+Enter
              </span>
            </div>
          </div>
        </section>

        {/* --- Right: Feedback --- */}
        <section
          className="feedback-panel"
          aria-label="Feedback"
          aria-live="polite"
          aria-busy={isLoading}
        >
          {/* Empty state */}
          {!isLoading && !feedback && !error && (
            <div className="feedback-empty">
              <p>
                Your feedback will appear here after you click{" "}
                <strong>Analyze Writing</strong>.
              </p>
              <button
                className="sample-btn"
                style={{ marginTop: "var(--space-md)" }}
                onClick={() =>
                  setText(
                    "In the event that a student decides to participate in the extracurricular activity, they must complete the registration form no later than the last day. Also, its important to actually really note that we of learned a lot."
                  )
                }
              >
                Try a sample paragraph
              </button>
            </div>
          )}

          {/* Loading state */}
          {isLoading && (
            <div className="feedback-loading" role="status">
              <div className="spinner" aria-hidden="true" />
              <p>Analyzing your writing…</p>
            </div>
          )}

          {/* Error state */}
          {error && (
            <div className="feedback-error" role="alert">
              {error}
            </div>
          )}

          {/* Feedback content */}
          {feedback && !isLoading && !error && (
            <>
              {/* Summary */}
              <div className="feedback-summary">
                <strong>Summary:</strong> {feedback.summary}
              </div>

              {/* Grammar */}
              <FeedbackSection
                title="Grammar"
                icon="📝"
                issues={feedback.grammar}
              />

              {/* Clarity */}
              <FeedbackSection
                title="Clarity"
                icon="💡"
                issues={feedback.clarity}
              />

              {/* Conciseness */}
              <FeedbackSection
                title="Conciseness"
                icon="✂️"
                issues={feedback.conciseness}
              />

              {/* Tone */}
              <div className="feedback-section">
                <h3>
                  <span className="section-icon" aria-hidden="true">
                    🎯
                  </span>
                  Tone
                </h3>
                <p
                  style={{
                    fontSize: "var(--text-sm)",
                    marginTop: "var(--space-sm)",
                  }}
                >
                  <strong>Detected:</strong> {feedback.tone.detected}
                  <br />
                  <strong>Consistency:</strong> {feedback.tone.consistency}
                  <br />
                  <strong>Note:</strong> {feedback.tone.note}
                </p>
              </div>

              {/* Strengths */}
              <div className="feedback-section">
                <h3>
                  <span className="section-icon" aria-hidden="true">
                    ⭐
                  </span>
                  What Went Well
                </h3>
                <ul className="strengths-list">
                  {feedback.strengths.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}

/* ===== Sub-component: renders a list of issues ===== */
function FeedbackSection({
  title,
  icon,
  issues,
}: {
  title: string;
  icon: string;
  issues: WritingFeedback["grammar"];
}) {
  return (
    <div className="feedback-section">
      <h3>
        <span className="section-icon" aria-hidden="true">
          {icon}
        </span>
        {title}
        {issues.length === 0 && (
          <span
            style={{
              marginLeft: "auto",
              fontSize: "var(--text-sm)",
              color: "var(--color-low)",
              fontWeight: 500,
            }}
          >
            No issues found ✓
          </span>
        )}
      </h3>

      {issues.map((issue, i) => (
        <div key={i} className={`issue-card severity-${issue.severity}`}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "baseline",
            }}
          >
            <span className="issue-original">{issue.original}</span>
            <span className={`severity-badge ${issue.severity}`}>
              {issue.severity}
            </span>
          </div>
          <p className="issue-suggestion">→ {issue.suggestion}</p>
          <p className="issue-explanation">{issue.explanation}</p>
        </div>
      ))}
    </div>
  );
}

