import '../styles/LoadingAnimation.css';

function LoadingAnimation({ stage = 'routing' }) {
  const stages = {
    routing: {
      text: 'Routing your query...',
      icon: '🧭',
      gradient: 'linear-gradient(135deg, #667eea, #764ba2)'
    },
    thinking: {
      text: 'Thinking...',
      icon: '🤔',
      gradient: 'linear-gradient(135deg, #f093fb, #f5576c)'
    },
    searching: {
      text: 'Searching knowledge base...',
      icon: '🔍',
      gradient: 'linear-gradient(135deg, #4facfe, #00f2fe)'
    },
    solving: {
      text: 'Solving problem...',
      icon: '⚡',
      gradient: 'linear-gradient(135deg, #43e97b, #38f9d7)'
    }
  };

  const currentStage = stages[stage] || stages.routing;

  return (
    <div className="loading-animation-container">
      <div className="loading-content">
        <div className="loading-icon" style={{ background: currentStage.gradient }}>
          <span className="icon-emoji">{currentStage.icon}</span>
        </div>
        
        <div className="loading-text">
          {currentStage.text}
        </div>

        <div className="loading-dots">
          <span className="dot" style={{ background: currentStage.gradient }}></span>
          <span className="dot" style={{ background: currentStage.gradient }}></span>
          <span className="dot" style={{ background: currentStage.gradient }}></span>
        </div>

        <div className="shimmer-bar">
          <div className="shimmer-fill" style={{ background: currentStage.gradient }}></div>
        </div>
      </div>
    </div>
  );
}

export default LoadingAnimation;
