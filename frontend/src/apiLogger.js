/**
 * Comprehensive API Logger for Browser Console
 * Logs ALL API requests, responses, AI analysis, and errors
 */

// Styling for console logs
const styles = {
  request: 'background: #0066cc; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;',
  response: 'background: #00cc66; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;',
  error: 'background: #cc0000; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;',
  ai: 'background: #9933ff; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;',
  warning: 'background: #ff9900; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;',
};

export const logRequest = (method, url, data = null) => {
  const timestamp = new Date().toLocaleTimeString();
  console.log(`%c[${timestamp}] API REQUEST → ${method}`, styles.request);
  console.log('URL:', url);
  if (data) {
    console.log('Request Data:', data);
  }
  console.log('---');
};

export const logResponse = (method, url, response) => {
  const timestamp = new Date().toLocaleTimeString();
  console.log(`%c[${timestamp}] API RESPONSE ← ${method}`, styles.response);
  console.log('URL:', url);
  console.log('Response Data:', response.data);

  // Check for AI analysis in the response
  if (response.data) {
    checkForAIAnalysis(response.data);
  }

  console.log('---');
  return response;
};

export const logError = (method, url, error) => {
  const timestamp = new Date().toLocaleTimeString();
  console.error(`%c[${timestamp}] API ERROR ✖ ${method}`, styles.error);
  console.error('URL:', url);
  console.error('Error Message:', error.message);

  if (error.response) {
    console.error('Status:', error.response.status);
    console.error('Response Data:', error.response.data);
  } else if (error.request) {
    console.error('No response received');
    console.error('Request:', error.request);
  } else {
    console.error('Error Details:', error);
  }
  console.error('---');
  throw error;
};

const checkForAIAnalysis = (data) => {
  // Check if there's AI analysis in the response
  if (data.ai_analysis) {
    logAIAnalysis(data.ai_analysis, 'Response contains AI Analysis');
  }

  // Check in opportunity object
  if (data.opportunity && data.opportunity.ai_analysis) {
    logAIAnalysis(data.opportunity.ai_analysis, `AI Analysis for ${data.opportunity.symbol}`);
  }

  // Check in opportunities array
  if (data.opportunities && Array.isArray(data.opportunities)) {
    data.opportunities.forEach((opp, index) => {
      if (opp.ai_analysis) {
        logAIAnalysis(opp.ai_analysis, `AI Analysis for ${opp.symbol}`);
      }
    });
  }

  // Check in portfolio positions
  if (data.portfolio && data.portfolio.positions) {
    data.portfolio.positions.forEach(pos => {
      if (pos.ai_analysis) {
        logAIAnalysis(pos.ai_analysis, `AI Analysis for ${pos.symbol}`);
      }
    });
  }
};

export const logAIAnalysis = (analysis, context = '') => {
  const timestamp = new Date().toLocaleTimeString();
  console.log(`%c[${timestamp}] 🤖 AI ANALYSIS`, styles.ai);
  if (context) {
    console.log('Context:', context);
  }
  console.log('═══════════════════════════════════════');
  console.log('Should Trade:', analysis.should_trade ? '✅ YES' : '❌ NO');
  console.log('Confidence:', `${(analysis.confidence * 100).toFixed(0)}%`);
  console.log('Risk Assessment:', analysis.risk_assessment.toUpperCase());
  console.log('Reasoning:', analysis.reasoning);
  console.log('═══════════════════════════════════════');
  console.log('---');
};

export const logWarning = (message, data = null) => {
  const timestamp = new Date().toLocaleTimeString();
  console.warn(`%c[${timestamp}] ⚠ WARNING`, styles.warning);
  console.warn(message);
  if (data) {
    console.warn('Data:', data);
  }
  console.warn('---');
};

// Create axios wrapper with automatic logging
export const createLoggedAxios = (axios) => {
  // Intercept requests
  axios.interceptors.request.use(
    (config) => {
      logRequest(config.method.toUpperCase(), config.url, config.data);
      return config;
    },
    (error) => {
      console.error('Request setup error:', error);
      return Promise.reject(error);
    }
  );

  // Intercept responses
  axios.interceptors.response.use(
    (response) => {
      logResponse(response.config.method.toUpperCase(), response.config.url, response);
      return response;
    },
    (error) => {
      if (error.config) {
        logError(error.config.method?.toUpperCase() || 'UNKNOWN', error.config.url, error);
      } else {
        console.error('Unexpected error:', error);
      }
      return Promise.reject(error);
    }
  );

  return axios;
};

// Export a function to enable/disable logging
let loggingEnabled = true;

export const setLoggingEnabled = (enabled) => {
  loggingEnabled = enabled;
  console.log(`%c API Logging ${enabled ? 'ENABLED' : 'DISABLED'}`,
    enabled ? styles.response : styles.warning);
};

export const isLoggingEnabled = () => loggingEnabled;
