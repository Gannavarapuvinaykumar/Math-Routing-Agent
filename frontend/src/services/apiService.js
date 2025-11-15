import { endpoints, API_TIMEOUT } from '../config/api';

const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

/**
 * Makes an API request with retry logic and error handling
 */
async function apiCall(url, options = {}, retryCount = 0) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    // Retry on network errors or timeouts
    if (retryCount < MAX_RETRIES && (error.name === 'AbortError' || error instanceof TypeError)) {
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * (retryCount + 1)));
      return apiCall(url, options, retryCount + 1);
    }

    throw error;
  }
}

/**
 * Query the routing agent for a math problem
 */
export async function queryAgent(query) {
  if (!query?.trim()) {
    throw new Error('Query cannot be empty');
  }

  return apiCall(endpoints.agentRoute, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query })
  });
}

/**
 * Submit feedback for a response
 */
export async function submitFeedback(feedbackData) {
  if (!feedbackData?.trace_id) {
    throw new Error('Trace ID is required for feedback');
  }

  return apiCall(endpoints.feedback, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(feedbackData)
  });
}

export default {
  queryAgent,
  submitFeedback
};
