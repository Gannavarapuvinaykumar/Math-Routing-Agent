/**
 * Extracts and formats response data
 */
export function parseResponse(data) {
  if (!data) {
    return { error: 'No response received' };
  }

  // If it's already an error
  if (data.error) {
    return {
      error: data.error,
      type: 'error'
    };
  }

  // Backend returns: { route: "KB", result: { answer: "...", steps: "..." } }
  // Or sometimes: { answer: "...", steps: "..." }
  // We need to extract the answer from the nested result object
  let answerData;
  let stepsData;
  
  if (data.result && typeof data.result === 'object') {
    // Extract from nested result object
    answerData = data.result.answer || data.result.message || data.result;
    stepsData = data.result.steps || '';
  } else {
    // Fallback to top-level fields
    answerData = data.answer || data.result || '';
    stepsData = data.steps || '';
  }
  
  // Ensure answer is always a string
  const answerString = typeof answerData === 'string' 
    ? answerData 
    : (typeof answerData === 'object' ? JSON.stringify(answerData) : String(answerData));

  return {
    answer: answerString,
    summary: data.summary || (data.result?.summary) || '',
    steps: stepsData || (data.result?.steps) || '',
    message: data.message || (data.result?.message) || '',
    suggestion: data.suggestion || (data.result?.suggestion) || '',
    disclaimer: data.disclaimer || (data.result?.disclaimer) || '',
    type: 'success'
  };
}

/**
 * Determines the route display text and icon
 */
export function getRouteInfo(route) {
  const routeMap = {
    'KB': { text: '📚 Knowledge Base', color: '#28a745' },
    'Web': { text: '🌐 Web Search (MCP)', color: '#007bff' },
    'AI': { text: '🤖 AI Generation', color: '#9b59b6' },
    'Human': { text: '👨‍🏫 Human Expert', color: '#ffc107' },
    'Error': { text: '❌ Error', color: '#dc3545' }
  };

  return routeMap[route] || { text: route || 'Unknown', color: '#6c757d' };
}

/**
 * Determines if feedback should be shown
 */
export function shouldShowFeedback(data, route) {
  return !data?.error && (data?.result || data?.answer) && route !== 'KB';
}

export default {
  parseResponse,
  getRouteInfo,
  shouldShowFeedback
};
