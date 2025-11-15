import { convertToLatex } from '../utils/mathRenderer';
import '../styles/ResultsContainer.css';

function ResultsContainer({ result }) {
  if (!result) return null;

  if (result.error) {
    return (
      <div className="results-container fade-in">
        <div className="error-message" role="alert">
          ⚠️ {result.error}
        </div>
      </div>
    );
  }

  return (
    <div className="results-container fade-in" role="region" aria-label="Response results">
      {result.answer && (
        <div className="answer-text">
          <strong>Answer:</strong> <span className="tex2jax_process" dangerouslySetInnerHTML={{ __html: convertToLatex(result.answer) }} />
        </div>
      )}
      {result.summary && (
        <div className="summary-text">
          <strong>Summary:</strong> <span className="tex2jax_process" dangerouslySetInnerHTML={{ __html: convertToLatex(result.summary) }} />
        </div>
      )}
      {result.steps && (
        <div className="steps-container">
          <strong>Steps:</strong>
          <pre className="steps-pre">{result.steps}</pre>
        </div>
      )}
      {result.message && (
        <div className="message-box">
          {result.message}
        </div>
      )}
      {result.suggestion && (
        <div className="suggestion-box">
          💡 <strong>Suggestion:</strong> {result.suggestion}
        </div>
      )}
      {result.disclaimer && (
        <div className="disclaimer-box">
          ⚠️ {result.disclaimer}
        </div>
      )}
    </div>
  );
}

export default ResultsContainer;
