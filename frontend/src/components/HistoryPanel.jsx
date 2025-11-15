import { useState, useEffect } from 'react';
import '../styles/HistoryPanel.css';

function HistoryPanel({ onSelectQuery }) {
  const [history, setHistory] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    // Load history from localStorage
    const savedHistory = localStorage.getItem('mathAgentHistory');
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory));
    }
  }, []);

  const clearHistory = () => {
    if (confirm('Clear all history?')) {
      localStorage.removeItem('mathAgentHistory');
      setHistory([]);
    }
  };

  if (history.length === 0) return null;

  return (
    <div className="history-panel">
      <button
        className="history-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
        aria-label={isExpanded ? "Hide history" : "Show history"}
      >
        <span className="history-icon">📜</span>
        <strong>Recent Questions</strong>
        <span className="history-count">({history.length})</span>
        <span className="toggle-arrow">{isExpanded ? '▼' : '▶'}</span>
      </button>

      {isExpanded && (
        <div className="history-content fade-in">
          <div className="history-list">
            {history.slice(0, 10).map((item, index) => (
              <div
                key={index}
                className="history-item"
                onClick={() => onSelectQuery(item.query)}
                role="button"
                tabIndex={0}
                onKeyPress={(e) => e.key === 'Enter' && onSelectQuery(item.query)}
              >
                <div className="history-number">{history.length - index}</div>
                <div className="history-details">
                  <div className="history-query">{item.query}</div>
                  {item.answer && (
                    <div className="history-answer">→ {item.answer}</div>
                  )}
                  <div className="history-meta">
                    <span className="history-route" style={{ color: getRouteColor(item.route) }}>
                      {getRouteIcon(item.route)} {item.route}
                    </span>
                    <span className="history-time">{formatTime(item.timestamp)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <button className="clear-history-btn" onClick={clearHistory}>
            🗑️ Clear History
          </button>
        </div>
      )}
    </div>
  );
}

function getRouteColor(route) {
  const colors = {
    'KB': '#28a745',
    'Web': '#007bff',
    'AI': '#9b59b6',
    'Human': '#ffc107'
  };
  return colors[route] || '#6c757d';
}

function getRouteIcon(route) {
  const icons = {
    'KB': '📚',
    'Web': '🌐',
    'AI': '🤖',
    'Human': '👨‍🏫'
  };
  return icons[route] || '📍';
}

function formatTime(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;
  
  if (diff < 60000) return 'Just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return date.toLocaleDateString();
}

export function addToHistory(query, answer, route) {
  const history = JSON.parse(localStorage.getItem('mathAgentHistory') || '[]');
  
  // Convert answer to string if it's an object or other type
  const answerText = typeof answer === 'string' 
    ? answer 
    : (typeof answer === 'object' ? JSON.stringify(answer) : String(answer || ''));
  
  history.unshift({
    query,
    answer: answerText.substring(0, 100),
    route,
    timestamp: Date.now()
  });

  // Keep only last 50 items
  const trimmedHistory = history.slice(0, 50);
  localStorage.setItem('mathAgentHistory', JSON.stringify(trimmedHistory));
}

export default HistoryPanel;
