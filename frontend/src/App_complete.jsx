import { useState } from 'react';

function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [route, setRoute] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackData, setFeedbackData] = useState({ rating: 3, feedback: '' });
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [traceId, setTraceId] = useState(null);

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
          route: route
        })
      });
      
      const feedbackResult = await response.json();
      if (response.ok) {
        setFeedbackSubmitted(true);
        setTimeout(() => setShowFeedback(false), 2000);
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
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <div style={{ 
        maxWidth: 800, 
        margin: '0 auto', 
        background: 'white',
        borderRadius: '20px',
        padding: '40px',
        boxShadow: '0 20px 40px rgba(0,0,0,0.1)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h1 style={{ 
            color: '#2c3e50', 
            fontSize: '2.5em', 
            marginBottom: '10px',
            background: 'linear-gradient(45deg, #667eea, #764ba2)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            🧮 Math Routing Agent
          </h1>
          <p style={{ color: '#7f8c8d', fontSize: '1.1em' }}>
            AI-powered math solver with KB, MCP web search, AI generation, and human feedback loop
          </p>
        </div>

        <div style={{ marginBottom: '30px' }}>
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask any math question (e.g., 'Solve x² - 5x + 6 = 0')"
            style={{ 
              width: '100%', 
              padding: '16px 20px', 
              fontSize: '16px',
              border: '2px solid #e9ecef',
              borderRadius: '12px',
              outline: 'none',
              transition: 'border-color 0.3s',
              boxSizing: 'border-box'
            }}
            onFocus={e => e.target.style.borderColor = '#667eea'}
            onBlur={e => e.target.style.borderColor = '#e9ecef'}
          />
          <button 
            onClick={handleSearch} 
            disabled={loading || !query}
            style={{ 
              width: '100%',
              marginTop: '16px',
              padding: '16px',
              fontSize: '16px',
              fontWeight: '600',
              border: 'none',
              borderRadius: '12px',
              background: loading || !query ? '#95a5a6' : 'linear-gradient(45deg, #667eea, #764ba2)',
              color: 'white',
              cursor: loading || !query ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s',
              boxShadow: loading || !query ? 'none' : '0 4px 15px rgba(102, 126, 234, 0.4)'
            }}
          >
            {loading ? '🔍 Searching...' : '🚀 Solve Problem'}
          </button>
        </div>

        {route && (
          <div style={{ 
            marginBottom: '20px',
            padding: '12px 20px',
            background: `${getRouteColor(route)}15`,
            border: `2px solid ${getRouteColor(route)}`,
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <span style={{ 
              fontWeight: '600', 
              color: getRouteColor(route),
              fontSize: '14px',
              textTransform: 'uppercase',
              letterSpacing: '1px'
            }}>
              📍 Source: {route === 'KB' ? '📚 Knowledge Base' : route === 'Web' ? '🌐 Web Search (MCP)' : route === 'AI' ? '🤖 AI Model' : route === 'Human' ? '👨‍🏫 Human Expert' : '❌ Error'}
            </span>
          </div>
        )}

        {result && (
          <div style={{ 
            background: '#f8f9fa',
            border: '1px solid #e9ecef',
            borderRadius: '15px',
            padding: '30px',
            marginTop: '20px'
          }}>
            {result.error ? (
              <div style={{ 
                color: '#dc3545', 
                background: '#f8d7da',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '16px',
                fontWeight: 'bold',
                textAlign: 'center',
                border: '1px solid #dc3545'
              }}>
                ⚠️ {result.error}
              </div>
            ) : (
              <>
                {result.answer && (
                  <div style={{ fontSize: '1.2em', marginBottom: '12px', color: '#2c3e50' }}>
                    <strong>Answer:</strong> {result.answer}
                  </div>
                )}
                {result.summary && (
                  <div style={{ fontSize: '1em', marginBottom: '12px', color: '#34495e' }}>
                    <strong>Summary:</strong> {result.summary}
                  </div>
                )}
                {result.steps && (
                  <div style={{ fontSize: '1em', color: '#34495e' }}>
                    <strong>Steps:</strong>
                    <pre style={{ background: '#eef2f7', padding: '12px', borderRadius: '8px', marginTop: '8px' }}>{result.steps}</pre>
                  </div>
                )}
                {result.message && (
                  <div style={{ 
                    background: '#f8f9fa',
                    color: '#495057',
                    padding: '15px',
                    borderRadius: '8px',
                    margin: '0',
                    border: '1px solid #dee2e6',
                    fontSize: '16px'
                  }}>
                    {result.message}
                  </div>
                )}
                {result.suggestion && (
                  <div style={{ 
                    background: '#e7f3ff',
                    color: '#0056b3',
                    padding: '12px',
                    borderRadius: '8px',
                    marginTop: '10px',
                    border: '1px solid #b3d7ff',
                    fontSize: '14px',
                    fontStyle: 'italic'
                  }}>
                    💡 <strong>Suggestion:</strong> {result.suggestion}
                  </div>
                )}
                {result.disclaimer && (
                  <div style={{ 
                    background: '#fff3cd',
                    color: '#856404',
                    padding: '10px',
                    borderRadius: '8px',
                    marginTop: '10px',
                    border: '1px solid #ffeaa7',
                    fontSize: '12px',
                    fontStyle: 'italic'
                  }}>
                    ⚠️ {result.disclaimer}
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {showFeedback && (
          <div style={{ 
            background: '#f0f8ff',
            border: '2px solid #0056b3',
            borderRadius: '15px',
            padding: '20px',
            marginTop: '20px'
          }}>
            {!feedbackSubmitted ? (
              <>
                <h3 style={{ color: '#0056b3', marginBottom: '15px' }}>
                  🔄 Was this solution helpful?
                </h3>
                
                <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', justifyContent: 'center' }}>
                  <button 
                    onClick={() => handleFeedbackSubmit('👍')}
                    style={{ 
                      padding: '12px 24px',
                      background: '#28a745',
                      color: 'white',
                      border: 'none',
                      borderRadius: '25px',
                      cursor: 'pointer',
                      fontWeight: 'bold',
                      fontSize: '16px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}
                    title="This solution was helpful"
                  >
                    👍 Helpful
                  </button>
                  <button 
                    onClick={() => handleFeedbackSubmit('👎')}
                    style={{ 
                      padding: '12px 24px',
                      background: '#dc3545',
                      color: 'white',
                      border: 'none',
                      borderRadius: '25px',
                      cursor: 'pointer',
                      fontWeight: 'bold',
                      fontSize: '16px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}
                    title="This solution needs improvement"
                  >
                    👎 Needs Fix
                  </button>
                </div>
                
                <details style={{ marginBottom: '15px' }}>
                  <summary style={{ 
                    cursor: 'pointer', 
                    fontWeight: 'bold', 
                    color: '#0056b3',
                    marginBottom: '10px'
                  }}>
                    📝 Provide detailed feedback (optional)
                  </summary>
                  
                  <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                      Rate this solution (1-5):
                    </label>
                    <select 
                      value={feedbackData.rating} 
                      onChange={e => setFeedbackData({...feedbackData, rating: parseInt(e.target.value)})}
                      style={{ 
                        padding: '8px', 
                        borderRadius: '5px', 
                        border: '1px solid #ccc',
                        fontSize: '16px'
                      }}
                    >
                      <option value={1}>1 - Poor</option>
                      <option value={2}>2 - Fair</option>
                      <option value={3}>3 - Good</option>
                      <option value={4}>4 - Very Good</option>
                      <option value={5}>5 - Excellent</option>
                    </select>
                  </div>
                  
                  <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                      Your feedback or improved solution:
                    </label>
                    <textarea
                      value={feedbackData.feedback}
                      onChange={e => setFeedbackData({...feedbackData, feedback: e.target.value})}
                      placeholder="Please provide your feedback, corrections, or improved solution..."
                      style={{ 
                        width: '100%', 
                        height: '100px', 
                        padding: '10px',
                        borderRadius: '5px',
                        border: '1px solid #ccc',
                        fontSize: '14px',
                        boxSizing: 'border-box'
                      }}
                    />
                  </div>
                  
                  <button 
                    onClick={handleDetailedFeedbackSubmit}
                    style={{ 
                      padding: '10px 20px',
                      background: '#28a745',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      cursor: 'pointer',
                      fontWeight: 'bold'
                    }}
                  >
                    Submit Detailed Feedback
                  </button>
                </details>
                
                <button 
                  onClick={() => setShowFeedback(false)}
                  style={{ 
                    padding: '8px 16px',
                    background: '#6c757d',
                    color: 'white',
                    border: 'none',
                    borderRadius: '5px',
                    cursor: 'pointer',
                    fontSize: '14px'
                  }}
                >
                  Skip Feedback
                </button>
              </>
            ) : (
              <div style={{ 
                textAlign: 'center', 
                color: '#28a745', 
                fontWeight: 'bold',
                fontSize: '16px'
              }}>
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
