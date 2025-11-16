import '../styles/SearchInput.css';

function SearchInput({
  query,
  onChange,
  onSearch,
  isLoading,
  onKeyPress
}) {
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
      </div>

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
