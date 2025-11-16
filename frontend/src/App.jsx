import { useState, useEffect } from 'react';
import './App.css';
import backgroundImage from './mathematics-numbers-and-mathematical-data-ftjn425sx2rnifuk.jpg';
import HomePage from './components/HomePage';
import Header from './components/Header';
import SearchInput from './components/SearchInput';
import RouteDisplay from './components/RouteDisplay';
import RouteVisualization from './components/RouteVisualization';
import ResultsContainer from './components/ResultsContainer';
import StepByStep from './components/StepByStep';
import FeedbackContainer from './components/FeedbackContainer';
import ParticleBackground from './components/ParticleBackground';
import LoadingAnimation from './components/LoadingAnimation';
import ErrorMessage from './components/ErrorMessage';
import ExportPanel from './components/ExportPanel';
import { queryAgent, submitFeedback } from './services/apiService';
import { renderMathJax } from './utils/mathRenderer';
import { parseResponse, shouldShowFeedback } from './utils/responseParser';

function App() {
  const [showHomePage, setShowHomePage] = useState(true);
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState('routing');
  const [route, setRoute] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [traceId, setTraceId] = useState(null);
  const [error, setError] = useState(null);
  const [errorType, setErrorType] = useState('general');
  const [steps, setSteps] = useState([]);
  const [routeExplanation, setRouteExplanation] = useState('');

  // MathJax rendering effect
  useEffect(() => {
    if (result && !result.error) {
      renderMathJax();
    }
  }, [result]);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a mathematical question');
      setErrorType('invalid');
      return;
    }
    
    // Basic validation for mathematical content - expanded to include more math terms
    const mathKeywords = [
      // Operations
      'solve', 'calculate', 'find', 'compute', 'simplify', 'evaluate', 'determine',
      // Calculus
      'integrate', 'derivative', 'differentiate', 'limit', 'gradient',
      // Variables & symbols
      'x', 'y', 'z', 'n', '=', '+', '-', '*', '/', '^', 
      // Functions
      'sin', 'cos', 'tan', 'log', 'ln', 'sqrt', 'exp',
      // Topics
      'equation', 'formula', 'theorem', 'proof', 'probability', 'statistics',
      'algebra', 'geometry', 'calculus', 'trigonometry', 'matrix', 'vector',
      // Constants & numbers
      'pi', 'e', 'euler', 'infinity', 'prime', 'fibonacci', 'golden ratio',
      'constant', 'number', 'value',
      // Question words with math context
      'what is', 'how to', 'explain', 'define', 'show', 'prove',
      // Common math terms
      'sum', 'product', 'ratio', 'proportion', 'percentage', 'fraction',
      'decimal', 'integer', 'real', 'complex', 'irrational', 'rational'
    ];
    const hasMathContent = mathKeywords.some(keyword => query.toLowerCase().includes(keyword));
    
    if (!hasMathContent && query.length < 100) {
      setError('This does not look like a mathematical problem. Please provide a valid math query.');
      setErrorType('invalid');
      return;
    }
    
    setLoading(true);
    setLoadingStage('routing');
    setError(null);
    setResult(null);
    setRoute('');
    setSteps([]);
    setRouteExplanation('');
    setShowFeedback(false);
    
    try {
      // Simulate routing stage
      setTimeout(() => setLoadingStage('searching'), 500);
      setTimeout(() => setLoadingStage('thinking'), 1000);
      setTimeout(() => setLoadingStage('solving'), 1500);
      
      const data = await queryAgent(query);
      const parsedData = parseResponse(data);
      
      setResult(parsedData);
      setRoute(data.route || '');
      setTraceId(data.trace_id || Date.now().toString());
      setFeedbackSubmitted(false);
      
      // Extract steps if available
      if (data.steps) {
        const stepsList = typeof data.steps === 'string' 
          ? data.steps.split('\n').filter(s => s.trim())
          : data.steps;
        setSteps(stepsList);
      }
      
      // Generate route explanation
      if (data.route) {
        setRouteExplanation(generateRouteExplanation(data.route, data));
      }
      
      // Show feedback for successful non-KB responses
      if (shouldShowFeedback(data, data.route)) {
        setShowFeedback(true);
      }
    } catch (err) {
      const errorMsg = err.message || 'Failed to connect to backend. Make sure the server is running.';
      
      // Determine error type
      let errType = 'general';
      if (err.name === 'AbortError' || errorMsg.includes('timeout')) {
        errType = 'timeout';
      } else if (errorMsg.includes('network') || errorMsg.includes('connect')) {
        errType = 'network';
      } else if (errorMsg.includes('server') || errorMsg.includes('500')) {
        errType = 'server';
      }
      
      setError(errorMsg);
      setErrorType(errType);
      setResult({ error: errorMsg, type: 'error' });
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateRouteExplanation = (route, data) => {
    switch(route) {
      case 'KB':
        return `Similar solved problem found in knowledge base with high confidence${data.similarity_score ? ` (similarity: ${(data.similarity_score * 100).toFixed(1)}%)` : ''}.`;
      case 'Web':
        return 'No matching solution in knowledge base. Searching web resources via MCP for current information.';
      case 'AI':
        return 'New problem detected. Using AI generation to solve step-by-step.';
      case 'Human':
        return 'Complex problem requiring human expert review and validation.';
      default:
        return `Solution routed through ${route} system.`;
    }
  };

  const handleFeedbackSubmit = async (feedbackType, feedbackText = '') => {
    try {
      const responseContent = result?.answer || result?.message || result?.error || JSON.stringify(result);
      
      const feedbackResult = await submitFeedback({
        trace_id: traceId,
        feedback: feedbackType,
        correction: feedbackText,
        query: query,
        route: route,
        response: responseContent
      });
      
      if (feedbackResult) {
        setFeedbackSubmitted(true);
        setTimeout(() => setShowFeedback(false), 2000);
        
        if (feedbackResult.stored_in_kb) {
          alert('✅ Thank you! Your feedback helped improve the knowledge base!');
        }
      }
    } catch (error) {
      console.error('Feedback error:', error);
      alert('Error submitting feedback: ' + error.message);
    }
  };

  if (showHomePage) {
    return <HomePage onEnter={() => setShowHomePage(false)} />;
  }

  return (
    <div className="app-container" style={{ backgroundImage: `url(${backgroundImage})` }}>
      <ParticleBackground />

      <div className="main-content">
        <Header />

        <SearchInput
          query={query}
          onChange={setQuery}
          onSearch={handleSearch}
          isLoading={loading}
        />

        {loading && <LoadingAnimation stage={loadingStage} />}

        {error && !loading && (
          <ErrorMessage 
            error={error} 
            type={errorType}
            onRetry={handleSearch}
          />
        )}

        {!loading && !error && route && (
          <>
            <RouteDisplay route={route} />
            
            <RouteVisualization 
              selectedRoute={route}
              routeExplanation={routeExplanation}
            />
          </>
        )}

        {!loading && result && !error && (
          <>
            <ResultsContainer result={result} />

            {steps.length > 0 && (
              <StepByStep steps={steps} isExpanded={true} />
            )}

            <ExportPanel 
              query={query}
              result={result}
              steps={steps}
              route={route}
            />
          </>
        )}

        {showFeedback && !loading && (
          <FeedbackContainer
            onFeedbackSubmit={handleFeedbackSubmit}
            onSkip={() => setShowFeedback(false)}
            submitted={feedbackSubmitted}
            isLoading={loading}
          />
        )}
      </div>
    </div>
  );
}

export default App;
