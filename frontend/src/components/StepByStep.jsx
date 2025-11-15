import { useState } from 'react';
import '../styles/StepByStep.css';

function StepByStep({ steps, isExpanded: initialExpanded = false }) {
  const [isExpanded, setIsExpanded] = useState(initialExpanded);

  if (!steps || steps.length === 0) return null;

  // Parse steps if it's a string
  const stepsList = typeof steps === 'string' 
    ? steps.split('\n').filter(s => s.trim())
    : steps;

  return (
    <div className="step-by-step-container">
      <button 
        className="step-toggle-button"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
        aria-label={isExpanded ? "Hide solution steps" : "Show solution steps"}
      >
        <span className="step-toggle-icon">{isExpanded ? '▼' : '▶'}</span>
        <strong>Step-by-Step Solution</strong>
        <span className="step-count">({stepsList.length} steps)</span>
      </button>

      {isExpanded && (
        <div className="steps-content fade-in">
          <div className="steps-list">
            {stepsList.map((step, index) => (
              <div key={index} className="step-item">
                <div className="step-number">Step {index + 1}</div>
                <div className="step-content tex2jax_process">
                  {step}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default StepByStep;
