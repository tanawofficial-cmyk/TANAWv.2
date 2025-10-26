// Analytics tracking service for TANAW
class AnalyticsService {
  constructor() {
    this.events = [];
    this.sessionStart = Date.now();
    this.userId = this.getUserId();
    this.sessionId = this.getSessionId();
  }

  getUserId() {
    // Try to get the actual authenticated user ID from localStorage first
    const userData = localStorage.getItem('user');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        if (user.id) {
          return user.id;
        }
      } catch (e) {
        console.warn('Failed to parse user data from localStorage');
      }
    }
    
    // Fallback to analytics user ID if no authenticated user
    let userId = localStorage.getItem('analytics_user_id');
    if (!userId) {
      userId = 'user_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('analytics_user_id', userId);
    }
    return userId;
  }
  
  // Update user ID when user logs in
  setUserId(userId) {
    this.userId = userId;
  }

  getSessionId() {
    let sessionId = sessionStorage.getItem('analytics_session_id');
    if (!sessionId) {
      sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
      sessionStorage.setItem('analytics_session_id', sessionId);
    }
    return sessionId;
  }

  // Track page views
  trackPageView(page) {
    const event = {
      type: 'page_view',
      page,
      timestamp: new Date().toISOString(),
      userId: this.userId,
      sessionId: this.sessionId,
      userAgent: navigator.userAgent,
      referrer: document.referrer
    };
    
    this.events.push(event);
    this.sendEvent(event);
  }

  // Track user actions
  trackAction(action, details = {}) {
    const event = {
      type: 'action',
      action,
      details,
      timestamp: new Date().toISOString(),
      userId: this.userId,
      sessionId: this.sessionId
    };
    
    this.events.push(event);
    this.sendEvent(event);
  }

  // Track file uploads
  trackFileUpload(fileName, fileSize, fileType) {
    const event = {
      type: 'file_upload',
      fileName,
      fileSize,
      fileType,
      timestamp: new Date().toISOString(),
      userId: this.userId,
      sessionId: this.sessionId
    };
    
    this.events.push(event);
    this.sendEvent(event);
  }

  // Track chart generation
  trackChartGeneration(chartType, datasetSize) {
    const event = {
      type: 'chart_generation',
      chartType,
      datasetSize,
      timestamp: new Date().toISOString(),
      userId: this.userId,
      sessionId: this.sessionId
    };
    
    this.events.push(event);
    this.sendEvent(event);
  }

  // Track downloads
  trackDownload(downloadType, fileName) {
    const event = {
      type: 'download',
      downloadType,
      fileName,
      timestamp: new Date().toISOString(),
      userId: this.userId,
      sessionId: this.sessionId
    };
    
    this.events.push(event);
    this.sendEvent(event);
  }

  // Send event to backend
  async sendEvent(event) {
    try {
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
      const response = await fetch(`${API_BASE_URL}/analytics/track`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(event)
      });
      
      if (!response.ok) {
        console.warn('Analytics tracking failed:', response.status);
      }
    } catch (error) {
      console.warn('Analytics tracking error:', error);
    }
  }

  // Get analytics data for admin dashboard
  async getAnalyticsData(timeRange = '7d', specificDate = null) {
    try {
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
      let url = `${API_BASE_URL}/analytics/data?range=${timeRange}`;
      
      // Add specific date parameter for historical data filtering
      if (specificDate) {
        url += `&date=${specificDate}`;
        console.log(`📅 Fetching analytics data for specific date: ${specificDate}`);
      }
      
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        console.log(`📊 Analytics data fetched:`, data);
        return data;
      }
    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
    }
    return null;
  }

  // Get user metrics
  async getUserMetrics() {
    try {
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
      const response = await fetch(`${API_BASE_URL}/analytics/users`);
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('Failed to fetch user metrics:', error);
    }
    return null;
  }
}

// Create singleton instance
const analytics = new AnalyticsService();

export default analytics;
