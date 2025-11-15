import { getRouteInfo } from '../utils/responseParser';
import '../styles/RouteDisplay.css';

function RouteDisplay({ route }) {
  if (!route) return null;

  const routeInfo = getRouteInfo(route);

  return (
    <div 
      className="route-display"
      style={{ 
        background: `${routeInfo.color}15`,
        border: `2px solid ${routeInfo.color}`
      }}
      role="status"
      aria-live="polite"
      aria-label={`Response source: ${routeInfo.text}`}
    >
      <span 
        className="route-text"
        style={{ color: routeInfo.color }}
      >
        📍 Source: {routeInfo.text}
      </span>
    </div>
  );
}

export default RouteDisplay;
