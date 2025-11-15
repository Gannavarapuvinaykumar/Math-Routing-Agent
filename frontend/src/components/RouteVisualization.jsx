import '../styles/RouteVisualization.css';

const ROUTES = [
  { id: 'KB', name: 'Knowledge Base', icon: '📚', color: '#28a745' },
  { id: 'Web', name: 'Web Search', icon: '🌐', color: '#007bff' },
  { id: 'AI', name: 'AI Solver', icon: '🤖', color: '#9b59b6' },
  { id: 'Human', name: 'Human Expert', icon: '👨‍🏫', color: '#ffc107' }
];

function RouteVisualization({ selectedRoute, routeExplanation }) {
  if (!selectedRoute) return null;

  return (
    <div className="route-visualization-container">
      <div className="route-header">
        🧠 <strong>Routes Checked</strong>
      </div>

      <div className="routes-grid">
        {ROUTES.map((route) => {
          const isSelected = route.id === selectedRoute;
          return (
            <div
              key={route.id}
              className={`route-card ${isSelected ? 'selected' : 'not-selected'}`}
              style={{
                borderColor: isSelected ? route.color : '#e0e0e0',
                background: isSelected 
                  ? `linear-gradient(135deg, ${route.color}15, ${route.color}08)`
                  : 'rgba(250, 250, 250, 0.5)'
              }}
            >
              <div className="route-status">
                {isSelected ? '✔' : '○'}
              </div>
              <div className="route-icon">{route.icon}</div>
              <div className="route-name">{route.name}</div>
              {isSelected && (
                <div className="selected-badge" style={{ background: route.color }}>
                  SELECTED
                </div>
              )}
            </div>
          );
        })}
      </div>

      {routeExplanation && (
        <div className="route-explanation">
          <div className="explanation-header">
            💡 <strong>Why this route?</strong>
          </div>
          <div className="explanation-content">
            {routeExplanation}
          </div>
        </div>
      )}
    </div>
  );
}

export default RouteVisualization;
