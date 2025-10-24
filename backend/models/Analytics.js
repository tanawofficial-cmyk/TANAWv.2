import mongoose from "mongoose";

const analyticsSchema = new mongoose.Schema({
  type: {
    type: String,
    required: true,
    enum: ['page_view', 'action', 'file_upload', 'chart_generation', 'download']
  },
  action: {
    type: String,
    required: function() {
      return this.type === 'action';
    }
  },
  page: {
    type: String,
    required: function() {
      return this.type === 'page_view';
    }
  },
  userId: {
    type: String,
    required: true
  },
  sessionId: {
    type: String,
    required: true
  },
  timestamp: {
    type: Date,
    required: true,
    default: Date.now
  },
  details: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  },
  metadata: {
    userAgent: String,
    referrer: String,
    fileName: String,
    fileSize: Number,
    fileType: String,
    chartType: String,
    datasetSize: Number,
    downloadType: String
  }
}, {
  timestamps: true
});

// Create indexes for better query performance
analyticsSchema.index({ type: 1, timestamp: -1 });
analyticsSchema.index({ userId: 1, timestamp: -1 });
analyticsSchema.index({ sessionId: 1, timestamp: -1 });

const Analytics = mongoose.model("Analytics", analyticsSchema);

export default Analytics;
