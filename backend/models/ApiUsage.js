import mongoose from "mongoose";

const apiUsageSchema = new mongoose.Schema({
  service: {
    type: String,
    enum: ['openai', 'tanaw_backend', 'flask_analytics'],
    required: true
  },
  endpoint: {
    type: String,
    required: true
  },
  method: {
    type: String,
    enum: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
    default: 'GET'
  },
  // OpenAI specific fields
  tokensUsed: {
    type: Number,
    default: 0
  },
  tokensPrompt: {
    type: Number,
    default: 0
  },
  tokensCompletion: {
    type: Number,
    default: 0
  },
  model: {
    type: String,
    default: null
  },
  estimatedCost: {
    type: Number,
    default: 0
  },
  // Performance metrics
  responseTime: {
    type: Number, // in milliseconds
    default: 0
  },
  statusCode: {
    type: Number,
    default: 200
  },
  success: {
    type: Boolean,
    default: true
  },
  // User context
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    default: null
  },
  // Additional metadata
  errorMessage: {
    type: String,
    default: null
  },
  metadata: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  },
  timestamp: {
    type: Date,
    default: Date.now,
    index: true
  }
}, { 
  timestamps: true,
  // Automatically delete old records after 90 days
  expireAfterSeconds: 90 * 24 * 60 * 60
});

// Indexes for efficient querying
apiUsageSchema.index({ service: 1, timestamp: -1 });
apiUsageSchema.index({ userId: 1, timestamp: -1 });
apiUsageSchema.index({ success: 1, timestamp: -1 });

// Static method to log API usage
apiUsageSchema.statics.logApiUsage = async function(data) {
  try {
    const usage = new this(data);
    await usage.save();
    return usage;
  } catch (error) {
    console.error('Error logging API usage:', error);
    throw error;
  }
};

// Static method to calculate total tokens for a period
apiUsageSchema.statics.getTotalTokens = async function(startDate, endDate) {
  const result = await this.aggregate([
    {
      $match: {
        service: 'openai',
        timestamp: { $gte: startDate, $lte: endDate }
      }
    },
    {
      $group: {
        _id: null,
        totalTokens: { $sum: '$tokensUsed' },
        totalPromptTokens: { $sum: '$tokensPrompt' },
        totalCompletionTokens: { $sum: '$tokensCompletion' },
        totalCost: { $sum: '$estimatedCost' },
        totalCalls: { $sum: 1 },
        avgResponseTime: { $avg: '$responseTime' }
      }
    }
  ]);
  return result[0] || {
    totalTokens: 0,
    totalPromptTokens: 0,
    totalCompletionTokens: 0,
    totalCost: 0,
    totalCalls: 0,
    avgResponseTime: 0
  };
};

// Static method to get usage breakdown by endpoint
apiUsageSchema.statics.getEndpointBreakdown = async function(startDate, endDate) {
  return await this.aggregate([
    {
      $match: {
        timestamp: { $gte: startDate, $lte: endDate }
      }
    },
    {
      $group: {
        _id: { service: '$service', endpoint: '$endpoint' },
        count: { $sum: 1 },
        avgResponseTime: { $avg: '$responseTime' },
        successRate: {
          $avg: { $cond: ['$success', 1, 0] }
        }
      }
    },
    {
      $sort: { count: -1 }
    }
  ]);
};

// Static method to get aggregated metrics
apiUsageSchema.statics.getAggregatedMetrics = async function(period = '7d') {
  let matchDate = {};
  const now = new Date();

  if (period === '24h') {
    matchDate = { timestamp: { $gte: new Date(now.getTime() - 24 * 60 * 60 * 1000) } };
  } else if (period === '7d') {
    matchDate = { timestamp: { $gte: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000) } };
  } else if (period === '30d') {
    matchDate = { timestamp: { $gte: new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000) } };
  } // 'all' means no date filter

  const metrics = await this.aggregate([
    { $match: matchDate },
    {
      $group: {
        _id: null,
        totalTokens: { $sum: '$tokensUsed' },
        totalCalls: { $sum: 1 },
        totalCost: { $sum: '$estimatedCost' },
        avgResponseTime: { $avg: '$responseTime' },
        successfulCalls: { $sum: { $cond: ['$success', 1, 0] } },
        failedCalls: { $sum: { $cond: ['$success', 0, 1] } },
      },
    },
    {
      $project: {
        _id: 0,
        totalTokens: 1,
        totalCalls: 1,
        totalCost: 1,
        avgResponseTime: { $round: ['$avgResponseTime', 2] },
        successRate: { $cond: ['$totalCalls', { $multiply: [{ $divide: ['$successfulCalls', '$totalCalls'] }, 100] }, 0] },
      },
    },
  ]);

  const timeline = await this.aggregate([
    { $match: matchDate },
    {
      $group: {
        _id: {
          year: { $year: '$timestamp' },
          month: { $month: '$timestamp' },
          day: { $dayOfMonth: '$timestamp' },
        },
        totalTokens: { $sum: '$tokensUsed' },
        totalCalls: { $sum: 1 },
        totalCost: { $sum: '$estimatedCost' },
      },
    },
    { $sort: { '_id.year': 1, '_id.month': 1, '_id.day': 1 } },
  ]);

  return {
    openai: metrics[0] || { totalTokens: 0, totalCalls: 0, totalCost: 0, avgResponseTime: 0, successRate: 0 },
    timeline,
  };
};

// Static method to get daily usage timeline
apiUsageSchema.statics.getDailyTimeline = async function(startDate, endDate) {
  return await this.aggregate([
    {
      $match: {
        service: 'openai',
        timestamp: { $gte: startDate, $lte: endDate }
      }
    },
    {
      $group: {
        _id: {
          year: { $year: '$timestamp' },
          month: { $month: '$timestamp' },
          day: { $dayOfMonth: '$timestamp' }
        },
        totalTokens: { $sum: '$tokensUsed' },
        totalCalls: { $sum: 1 },
        totalCost: { $sum: '$estimatedCost' }
      }
    },
    {
      $sort: { '_id.year': 1, '_id.month': 1, '_id.day': 1 }
    }
  ]);
};

export default mongoose.model("ApiUsage", apiUsageSchema);

