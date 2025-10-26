import mongoose from 'mongoose';
import ApiUsage from '../models/ApiUsage.js';
import User from '../models/User.js';
import Dataset from '../models/Dataset.js';
import Feedback from '../models/Feedback.js';
import Analytics from '../models/Analytics.js';
import axios from 'axios';

/**
 * @desc    Get overall system connectivity status
 * @route   GET /api/admin/connectivity/status
 * @access  Private (Admin only)
 */
export const getSystemStatus = async (req, res) => {
  try {
    const status = {
      mongodb: {
        status: 'disconnected',
        responseTime: 0,
        host: null,
        database: null,
        uptime: 0
      },
      flaskService: {
        status: 'offline',
        responseTime: 0,
        url: process.env.FLASK_ANALYTICS_URL || 'http://localhost:5002',
        lastCheck: new Date()
      },
      openaiApi: {
        status: 'unknown',
        configured: !!process.env.OPENAI_API_KEY,
        lastUsed: null
      }
    };

    // Check MongoDB Connection
    const mongoStartTime = Date.now();
    try {
      if (mongoose.connection.readyState === 1) {
        await mongoose.connection.db.admin().ping();
        status.mongodb.status = 'connected';
        status.mongodb.responseTime = Date.now() - mongoStartTime;
        status.mongodb.host = mongoose.connection.host;
        status.mongodb.database = mongoose.connection.name;
        status.mongodb.uptime = Math.floor((Date.now() - mongoose.connection._connectTime) / 1000);
      }
    } catch (error) {
      console.error('MongoDB health check failed:', error);
      status.mongodb.status = 'error';
    }

    // Check Flask Analytics Service
    const flaskStartTime = Date.now();
    try {
      const flaskUrl = process.env.FLASK_ANALYTICS_URL || 'http://localhost:5002';
      let flaskResponse;
      let healthCheckPassed = false;
      
      // Try the root endpoint first (most reliable)
      try {
        flaskResponse = await axios.get(`${flaskUrl}/`, { 
          timeout: 3000,
          validateStatus: (status) => status < 500 // Accept 2xx, 3xx, 4xx as "service is running"
        });
        
        // If we get any response (even 404), the service is running
        if (flaskResponse.status < 500) {
          healthCheckPassed = true;
        }
      } catch (err) {
        // If root fails, try upload endpoint as fallback
        try {
          flaskResponse = await axios.get(`${flaskUrl}/api/files/upload-clean`, { 
            timeout: 3000,
            validateStatus: (status) => status < 500
          });
          
          if (flaskResponse.status < 500) {
            healthCheckPassed = true;
          }
        } catch (fallbackErr) {
          // Service is likely offline
          healthCheckPassed = false;
        }
      }
      
      if (healthCheckPassed) {
        status.flaskService.status = 'online';
        status.flaskService.responseTime = Date.now() - flaskStartTime;
      } else {
        status.flaskService.status = 'offline';
        status.flaskService.responseTime = Date.now() - flaskStartTime;
      }
    } catch (error) {
      // If Flask service is not available, mark as offline but don't spam logs
      status.flaskService.status = 'offline';
      status.flaskService.responseTime = Date.now() - flaskStartTime;
    }

    // Check OpenAI API Status (check last successful call)
    try {
      const lastOpenAICall = await ApiUsage.findOne({ 
        service: 'openai',
        success: true 
      }).sort({ timestamp: -1 }).limit(1);
      
      if (lastOpenAICall) {
        status.openaiApi.status = 'active';
        status.openaiApi.lastUsed = lastOpenAICall.timestamp;
      } else {
        status.openaiApi.status = 'inactive';
      }
    } catch (error) {
      console.error('OpenAI status check failed:', error);
      status.openaiApi.status = 'unknown';
    }

    res.status(200).json({ success: true, data: status });
  } catch (error) {
    console.error('❌ Error checking system status:', error);
    res.status(500).json({ success: false, message: 'Failed to check system status' });
  }
};

/**
 * @desc    Get API usage metrics
 * @route   GET /api/admin/connectivity/api-metrics
 * @access  Private (Admin only)
 */
export const getApiMetrics = async (req, res) => {
  try {
    const { period = '7d' } = req.query;
    
    // Calculate date ranges
    const now = new Date();
    let startDate;
    
    switch (period) {
      case '24h':
        startDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        break;
      case '7d':
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case '30d':
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      case 'all':
        startDate = new Date(0);
        break;
      default:
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    }

    // Get OpenAI metrics
    const openaiMetrics = await ApiUsage.getTotalTokens(startDate, now);

    // Get endpoint breakdown
    const endpointBreakdown = await ApiUsage.getEndpointBreakdown(startDate, now);

    // Get daily timeline
    const dailyTimeline = await ApiUsage.getDailyTimeline(startDate, now);

    // Get success rate by service
    const serviceStats = await ApiUsage.aggregate([
      {
        $match: {
          timestamp: { $gte: startDate, $lte: now }
        }
      },
      {
        $group: {
          _id: '$service',
          totalCalls: { $sum: 1 },
          successfulCalls: {
            $sum: { $cond: ['$success', 1, 0] }
          },
          avgResponseTime: { $avg: '$responseTime' }
        }
      }
    ]);

    // Format service stats
    const formattedServiceStats = {};
    serviceStats.forEach(stat => {
      formattedServiceStats[stat._id] = {
        totalCalls: stat.totalCalls,
        successfulCalls: stat.successfulCalls,
        successRate: ((stat.successfulCalls / stat.totalCalls) * 100).toFixed(2),
        avgResponseTime: Math.round(stat.avgResponseTime)
      };
    });

    res.status(200).json({
      success: true,
      data: {
        period,
        openai: openaiMetrics,
        services: formattedServiceStats,
        endpoints: endpointBreakdown,
        timeline: dailyTimeline
      }
    });
  } catch (error) {
    console.error('❌ Error fetching API metrics:', error);
    res.status(500).json({ success: false, message: 'Failed to fetch API metrics' });
  }
};

/**
 * @desc    Get database statistics
 * @route   GET /api/admin/connectivity/database-stats
 * @access  Private (Admin only)
 */
export const getDatabaseStats = async (req, res) => {
  try {
    // Get collection stats
    const collections = {
      users: {
        name: 'Users',
        count: await User.countDocuments(),
        icon: '👥'
      },
      datasets: {
        name: 'Datasets',
        count: await Dataset.countDocuments(),
        icon: '📊'
      },
      feedback: {
        name: 'Feedback',
        count: await Feedback.countDocuments(),
        icon: '💬'
      },
      analytics: {
        name: 'Analytics',
        count: await Analytics.countDocuments(),
        icon: '📈'
      },
      apiUsage: {
        name: 'API Usage Logs',
        count: await ApiUsage.countDocuments(),
        icon: '🔌'
      }
    };

    // Get database size and stats
    let databaseStats = {
      size: 0,
      dataSize: 0,
      indexSize: 0,
      collections: 0
    };

    try {
      const stats = await mongoose.connection.db.stats();
      databaseStats = {
        size: (stats.dataSize / (1024 * 1024)).toFixed(2), // Convert to MB
        dataSize: (stats.dataSize / (1024 * 1024)).toFixed(2),
        indexSize: (stats.indexSize / (1024 * 1024)).toFixed(2),
        collections: stats.collections,
        indexes: stats.indexes,
        avgObjSize: stats.avgObjSize
      };
    } catch (error) {
      console.error('Error getting database stats:', error);
    }

    // Get recent activity (last 24 hours)
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
    const recentActivity = {
      newUsers: await User.countDocuments({ createdAt: { $gte: oneDayAgo } }),
      newDatasets: await Dataset.countDocuments({ uploadDate: { $gte: oneDayAgo } }),
      newFeedback: await Feedback.countDocuments({ date: { $gte: oneDayAgo } }),
      apiCalls: await ApiUsage.countDocuments({ timestamp: { $gte: oneDayAgo } })
    };

    res.status(200).json({
      success: true,
      data: {
        collections,
        databaseStats,
        recentActivity
      }
    });
  } catch (error) {
    console.error('❌ Error fetching database stats:', error);
    res.status(500).json({ success: false, message: 'Failed to fetch database stats' });
  }
};

/**
 * @desc    Get performance metrics
 * @route   GET /api/admin/connectivity/performance
 * @access  Private (Admin only)
 */
export const getPerformanceMetrics = async (req, res) => {
  try {
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);

    // Get slowest endpoints
    const slowestEndpoints = await ApiUsage.aggregate([
      {
        $match: {
          timestamp: { $gte: oneDayAgo }
        }
      },
      {
        $group: {
          _id: { service: '$service', endpoint: '$endpoint' },
          avgResponseTime: { $avg: '$responseTime' },
          maxResponseTime: { $max: '$responseTime' },
          count: { $sum: 1 }
        }
      },
      {
        $sort: { avgResponseTime: -1 }
      },
      {
        $limit: 10
      }
    ]);

    // Get error rate by endpoint
    const errorRates = await ApiUsage.aggregate([
      {
        $match: {
          timestamp: { $gte: oneDayAgo }
        }
      },
      {
        $group: {
          _id: { service: '$service', endpoint: '$endpoint' },
          totalCalls: { $sum: 1 },
          errors: {
            $sum: { $cond: ['$success', 0, 1] }
          }
        }
      },
      {
        $project: {
          service: '$_id.service',
          endpoint: '$_id.endpoint',
          totalCalls: 1,
          errors: 1,
          errorRate: {
            $multiply: [
              { $divide: ['$errors', '$totalCalls'] },
              100
            ]
          }
        }
      },
      {
        $match: {
          errors: { $gt: 0 }
        }
      },
      {
        $sort: { errorRate: -1 }
      }
    ]);

    // Get peak usage times
    const peakUsage = await ApiUsage.aggregate([
      {
        $match: {
          timestamp: { $gte: oneDayAgo }
        }
      },
      {
        $group: {
          _id: { $hour: '$timestamp' },
          count: { $sum: 1 }
        }
      },
      {
        $sort: { count: -1 }
      },
      {
        $limit: 5
      }
    ]);

    res.status(200).json({
      success: true,
      data: {
        slowestEndpoints,
        errorRates,
        peakUsage
      }
    });
  } catch (error) {
    console.error('❌ Error fetching performance metrics:', error);
    res.status(500).json({ success: false, message: 'Failed to fetch performance metrics' });
  }
};

/**
 * @desc    Log API usage (helper function for middleware)
 * @route   N/A (internal use)
 * @access  N/A
 */
export const logApiUsage = async (usageData) => {
  try {
    const apiUsage = new ApiUsage(usageData);
    await apiUsage.save();
  } catch (error) {
    console.error('❌ Error logging API usage:', error);
  }
};

