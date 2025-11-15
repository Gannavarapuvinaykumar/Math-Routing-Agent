import { useState } from 'react';
import '../styles/SearchInput.css';

const EXAMPLES = [
  'Solve quadratic equation x² - 5x + 6 = 0',
  'Find derivative of f(x) = x³ + 2x² - 5x + 1',
  'Compute integral ∫ x² dx',
  'Calculate limit as x approaches 0: sin(x)/x',
  'Solve system: 2x + y = 5, x - y = 1'
];

function SearchInput({
  query,
  onChange,
  onSearch,
  isLoading,
  onKeyPress
}) {
  const [showExamples, setShowExamples] = useState(false);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      if (!e.shiftKey) {
        e.preventDefault();
        onSearch();
      }
    }
    if (onKeyPress) {
      onKeyPress(e);
    }
  };

  const handleExampleClick = (example) => {
    onChange(example);
    setShowExamples(false);
  };

  return (
    <div className="input-section">
      <div className="input-wrapper">
        <input
          type="text"
          value={query}
          onChange={e => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask any math question (e.g., 'Solve x² - 5x + 6 = 0')"
          className="query-input"
          disabled={isLoading}
          aria-label="Math question input"
          autoFocus
        />
        <button
          className="examples-toggle"
          onClick={() => setShowExamples(!showExamples)}
          title="Show example questions"
          aria-label="Toggle example questions"
          type="button"
        >
          💡
        </button>
      </div>

      {showExamples && (
        <div className="examples-dropdown fade-in">
          <div className="examples-header">Example Questions:</div>
          {EXAMPLES.map((example, index) => (
            <button
              key={index}
              className="example-item"
              onClick={() => handleExampleClick(example)}
              type="button"
            >
              {example}
            </button>
          ))}
        </div>
      )}

      <button
        onClick={onSearch}
        disabled={isLoading || !query.trim()}
        className={`search-button ${isLoading ? 'loading' : ''}`}
        aria-label={isLoading ? 'Searching for answer' : 'Search for answer'}
      >
        {isLoading ? '🔍 Searching...' : '🚀 Solve Problem'}
      </button>
    </div>
  );
}

export default SearchInput;
