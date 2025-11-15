import '../styles/ErrorMessage.css';

const ERROR_TYPES = {
  network: {
    title: 'Connection Error',
    icon: '🔌',
    color: '#dc3545'
  },
  invalid: {
    title: 'Invalid Input',
    icon: '⚠️',
    color: '#ffc107'
  },
  harmful: {
    title: 'Blocked Request',
    icon: '🛡️',
    color: '#e74c3c'
  },
  timeout: {
    title: 'Request Timeout',
    icon: '⏱️',
    color: '#ff6b6b'
  },
  server: {
    title: 'Server Error',
    icon: '🔧',
    color: '#e67e22'
  },
  general: {
    title: 'Error',
    icon: '❌',
    color: '#dc3545'
  }
};

function ErrorMessage({ error, type = 'general', onRetry }) {
  if (!error) return null;

  const errorConfig = ERROR_TYPES[type] || ERROR_TYPES.general;

  const getSuggestion = () => {
    switch(type) {
      case 'network':
        return 'Please check your internet connection and try again.';
      case 'invalid':
        return 'Please provide a valid mathematical problem or question.';
      case 'harmful':
        return 'This request was blocked by our content safety filters.';
      case 'timeout':
        return 'The request took too long. Please try a simpler problem or try again.';
      case 'server':
        return 'Our servers are experiencing issues. Please try again in a moment.';
      default:
        return 'Something went wrong. Please try again.';
    }
  };

  return (
    <div 
      className="error-message-container"
      style={{ 
        background: `linear-gradient(135deg, ${errorConfig.color}15, ${errorConfig.color}08)`,
        borderColor: errorConfig.color 
      }}
      role="alert"
    >
      <div className="error-icon" style={{ color: errorConfig.color }}>
        {errorConfig.icon}
      </div>
      
      <div className="error-content">
        <div className="error-title" style={{ color: errorConfig.color }}>
          {errorConfig.title}
        </div>
        <div className="error-description">
          {error}
        </div>
        <div className="error-suggestion">
          💡 {getSuggestion()}
        </div>
      </div>

      {onRetry && (
        <button 
          className="retry-button"
          onClick={onRetry}
          style={{ 
            background: errorConfig.color,
            boxShadow: `0 4px 12px ${errorConfig.color}40`
          }}
        >
          🔄 Retry
        </button>
      )}
    </div>
  );
}

export default ErrorMessage;
