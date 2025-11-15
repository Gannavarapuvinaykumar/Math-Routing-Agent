// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
const API_TIMEOUT = 30000; // 30 seconds

export const endpoints = {
  agentRoute: `${API_BASE_URL}/api/agent_route`,
  feedback: `${API_BASE_URL}/api/feedback`
};

export { API_TIMEOUT };
