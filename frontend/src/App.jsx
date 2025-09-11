import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [route, setRoute] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackData, setFeedbackData] = useState({ rating: 3, feedback: '' });
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [traceId, setTraceId] = useState(null);
  const [particles, setParticles] = useState([]);

  // Create particle background
  useEffect(() => {
    const createParticles = () => {
      const newParticles = [];
      for (let i = 0; i < 50; i++) {
        newParticles.push({
          id: i,
          x: Math.random() * 100,
          y: Math.random() * 100,
          size: Math.random() * 4 + 2,
          duration: Math.random() * 10 + 10,
          delay: Math.random() * 5,
        });
      }
      setParticles(newParticles);
    };
    createParticles();
  }, []);

  // MathJax rendering effect
  useEffect(() => {
    if (window.MathJax && result) {
      window.MathJax.typesetPromise().catch((err) => console.log(err));
    }
  }, [result]);

  const renderMathContent = (content) => {
    if (typeof content === 'string') {
      // Convert common math notation to LaTeX
      const mathContent = content
        .replace(/\^(\w+)/g, '^{$1}')  // x^2 -> x^{2}
        .replace(/\_(\w+)/g, '_{$1}')  // x_1 -> x_{1}
        .replace(/\bdx\b/g, '\\,dx')   // dx -> \,dx
        .replace(/\bdy\b/g, '\\,dy')   // dy -> \,dy
        .replace(/\\frac/g, '\\frac')  // Keep existing LaTeX
        .replace(/\\int/g, '\\int')    // Keep integral notation
        .replace(/\\sum/g, '\\sum')    // Keep summation notation
        .replace(/\\lim/g, '\\lim');   // Keep limit notation
      
      return <span className="tex2jax_process" dangerouslySetInnerHTML={{ __html: mathContent }} />;
    }
    return content;
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setResult(null);
    setRoute('');
    setShowFeedback(false);
    
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/agent_route`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query })
      });
      
      const data = await response.json();
      setResult(data.result || data);
      setRoute(data.route || '');
      setTraceId(data.trace_id || Date.now().toString());
      setFeedbackSubmitted(false);
      
      // Show feedback for all successful responses except KB responses and errors
      if (!data.error && (data.result || data.answer) && data.route !== 'KB') {
        setShowFeedback(true);
      }
    } catch (error) {
      setResult({ error: 'Failed to connect to backend. Make sure the server is running.' });
    } finally {
      setLoading(false);
    }
  };

  const handleFeedbackSubmit = async (feedbackType, feedbackText = '') => {
    try {
      // Get the response content from result
      const responseContent = result?.answer || result?.message || result?.error || JSON.stringify(result);
      
      const response = await fetch(`http://127.0.0.1:8000/api/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          trace_id: traceId,
          feedback: feedbackType,
          correction: feedbackText,
          query: query,
          route: route,
          response: responseContent  // ✅ Use the correct variable
        })
      });
      
      const feedbackResult = await response.json();
      if (response.ok) {
        setFeedbackSubmitted(true);
        setTimeout(() => setShowFeedback(false), 2000);
        
        // Show success message if stored in KB
        if (feedbackResult.stored_in_kb) {
          alert('✅ Thank you! Your feedback helped improve the knowledge base!');
        }
      } else {
        alert('Failed to submit feedback: ' + feedbackResult.message);
      }
    } catch (error) {
      alert('Error submitting feedback: ' + error.message);
    }
  };

  const handleDetailedFeedbackSubmit = async () => {
    await handleFeedbackSubmit('detailed', feedbackData.feedback);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const getRouteColor = (route) => {
    switch(route) {
      case 'KB': return '#28a745';
      case 'Web': return '#007bff';
      case 'AI': return '#9b59b6';
      case 'Human': return '#ffc107';
      case 'Error': return '#dc3545';
      default: return '#6c757d';
    }
  };

  return (
    <div className="app-container">
      {/* Animated Particle Background */}
      <div className="particles-container">
        {particles.map((particle) => (
          <div
            key={particle.id}
            className="particle"
            style={{
              left: `${particle.x}%`,
              width: `${particle.size}px`,
              height: `${particle.size}px`,
              animationDuration: `${particle.duration}s`,
              animationDelay: `${particle.delay}s`,
            }}
          />
        ))}
      </div>

      <div className="main-content">
        <div className="header">
          <h1>
            🧮 Math Routing Agent
          </h1>
          <p>
            AI-powered math solver with KB, MCP web search, AI generation, and human feedback loop
          </p>
        </div>

        <div className="input-section">
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask any math question (e.g., 'Solve x² - 5x + 6 = 0')"
            className="query-input"
          />
          <button 
            onClick={handleSearch} 
            disabled={loading || !query}
            className={`search-button ${loading ? 'loading' : ''}`}
          >
            {loading ? '🔍 Searching...' : '🚀 Solve Problem'}
          </button>
        </div>

        {route && (
          <div 
            className="route-display"
            style={{ 
              background: `${getRouteColor(route)}15`,
              border: `2px solid ${getRouteColor(route)}`
            }}
          >
            <span 
              className="route-text"
              style={{ color: getRouteColor(route) }}
            >
              📍 Source: {route === 'KB' ? '📚 Knowledge Base' : route === 'Web' ? '🌐 Web Search (MCP)' : route === 'AI' ? '🤖 AI Generation' : route === 'Human' ? '👨‍🏫 Human Expert' : '❌ Error'}
            </span>
          </div>
        )}

        {result && (
          <div className="results-container fade-in">
            {result.error ? (
              <div className="error-message">
                ⚠️ {result.error}
              </div>
            ) : (
              <>
                {result.answer && (
                  <div className="answer-text">
                    <strong>Answer:</strong> {renderMathContent(result.answer)}
                  </div>
                )}
                {result.summary && (
                  <div className="summary-text">
                    <strong>Summary:</strong> {renderMathContent(result.summary)}
                  </div>
                )}
                {result.steps && (
                  <div className="steps-container">
                    <strong>Steps:</strong>
                    <pre className="steps-pre">{renderMathContent(result.steps)}</pre>
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
              </>
            )}
          </div>
        )}

        {showFeedback && (
          <div className="feedback-container fade-in">
            {!feedbackSubmitted ? (
              <>
                <h3 className="feedback-title">
                  🔄 Was this solution helpful?
                </h3>
                
                <div className="quick-feedback-buttons">
                  <button 
                    onClick={() => handleFeedbackSubmit('helpful')}
                    className="feedback-thumb-button thumb-up"
                    title="This solution was helpful"
                  >
                    👍 Helpful
                  </button>
                  <button 
                    onClick={() => handleFeedbackSubmit('👎')}
                    className="feedback-thumb-button thumb-down"
                    title="This solution needs improvement"
                  >
                    👎 Needs Fix
                  </button>
                </div>
                
                <div className="detailed-feedback-section">
                  <details>
                    <summary className="detailed-feedback-toggle">
                      📝 Provide detailed feedback (optional)
                    </summary>
                    
                    <div className="mb-15">
                      <label className="feedback-label">
                        Rate this solution (1-5):
                      </label>
                      <select 
                        value={feedbackData.rating} 
                        onChange={e => setFeedbackData({...feedbackData, rating: parseInt(e.target.value)})}
                        className="rating-select"
                      >
                        <option value={1}>1 - Poor</option>
                        <option value={2}>2 - Fair</option>
                        <option value={3}>3 - Good</option>
                        <option value={4}>4 - Very Good</option>
                        <option value={5}>5 - Excellent</option>
                      </select>
                    </div>
                    
                    <div className="mb-15">
                      <label className="feedback-label">
                        Your feedback or improved solution:
                      </label>
                      <textarea
                        value={feedbackData.feedback}
                        onChange={e => setFeedbackData({...feedbackData, feedback: e.target.value})}
                        placeholder="Please provide your feedback, corrections, or improved solution..."
                        className="feedback-textarea"
                      />
                    </div>
                    
                    <div className="feedback-buttons">
                      <button 
                        onClick={handleDetailedFeedbackSubmit}
                        className="feedback-button feedback-submit"
                      >
                        Submit Detailed Feedback
                      </button>
                    </div>
                  </details>
                </div>
                
                <button 
                  onClick={() => setShowFeedback(false)}
                  className="feedback-skip-button"
                >
                  Skip Feedback
                </button>
              </>
            ) : (
              <div className="feedback-success">
                ✅ Thank you for your feedback! This helps us improve.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
