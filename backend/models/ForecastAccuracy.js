/**
 * Forecast Accuracy Model
 * 
 * Tracks actual vs predicted values to improve forecast accuracy over time
 * Part of Objective 3.3: Adaptive Learning & User Feedback - Phase 2
 */

import mongoose from "mongoose";

const forecastAccuracySchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
      index: true
    },
    datasetId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Dataset",
      required: false,  // Allow null initially, will be updated after dataset creation
      index: true
    },
    chartId: {
      type: String,
      required: true,
      index: true,
      // e.g., "sales_forecast", "quantity_forecast", "stock_forecast"
    },
    chartTitle: {
      type: String,
      required: true
      // e.g., "Sales Forecast (Prophet AI)", "Quantity Forecast"
    },
    forecastType: {
      type: String,
      required: true,
      enum: ["sales", "quantity", "stock", "cash_flow"],
      index: true
    },
    domain: {
      type: String,
      required: true,
      enum: ["sales", "inventory", "finance", "product"],
      default: "sales",
      index: true
    },
    
    // Forecast metadata
    forecastDate: {
      type: Date,
      required: true,
      // When the forecast was made
    },
    forecastPeriod: {
      type: Number,
      required: true,
      default: 30,
      // Number of days forecasted (e.g., 30 days)
    },
    targetDate: {
      type: Date,
      required: true,
      // The date being forecasted for
    },
    
    // Prediction data
    predictedValue: {
      type: Number,
      required: true,
      // The predicted value (e.g., ₱50,000 sales)
    },
    predictedLower: {
      type: Number,
      // Lower confidence bound (if available)
    },
    predictedUpper: {
      type: Number,
      // Upper confidence bound (if available)
    },
    
    // Actual data (user-provided)
    actualValue: {
      type: Number,
      default: null,
      // The actual value that occurred (null until user provides it)
    },
    actualProvidedAt: {
      type: Date,
      default: null,
      // When the user provided the actual value
    },
    
    // Accuracy metrics
    accuracy: {
      type: Number,
      default: null,
      // Overall accuracy percentage (0-100)
    },
    mape: {
      type: Number,
      default: null,
      // Mean Absolute Percentage Error
    },
    absoluteError: {
      type: Number,
      default: null,
      // |predicted - actual|
    },
    percentageError: {
      type: Number,
      default: null,
      // ((predicted - actual) / actual) * 100
    },
    
    // Model parameters used for this forecast
    modelParameters: {
      type: mongoose.Schema.Types.Mixed,
      default: {},
      // Stores Prophet parameters or other model configs
      // e.g., { changepoint_prior_scale: 0.05, seasonality_mode: 'multiplicative' }
    },
    
    // Status tracking
    status: {
      type: String,
      enum: ["pending", "completed", "expired"],
      default: "pending",
      index: true
      // "pending": waiting for actual value
      // "completed": actual value provided, accuracy calculated
      // "expired": target date passed, no actual value provided
    },
    
    // Reminder system
    reminderSent: {
      type: Boolean,
      default: false
      // Whether we've sent a reminder to provide actual value
    },
    reminderSentAt: {
      type: Date,
      default: null
    },
    
    // Learning metadata
    usedForOptimization: {
      type: Boolean,
      default: false,
      // Whether this data point was used to optimize model parameters
    },
    optimizationAppliedAt: {
      type: Date,
      default: null
    },
    
    // Additional context
    notes: {
      type: String,
      maxLength: 500,
      // User notes about why forecast was accurate/inaccurate
    },
    
    // Related feedback (if user rated the forecast)
    feedbackId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "ChartFeedback",
      default: null
    }
  },
  { 
    timestamps: true 
  }
);

// Indexes for efficient queries
forecastAccuracySchema.index({ userId: 1, status: 1 });
forecastAccuracySchema.index({ forecastType: 1, domain: 1 });
forecastAccuracySchema.index({ targetDate: 1, status: 1 });
forecastAccuracySchema.index({ createdAt: -1 });
forecastAccuracySchema.index({ userId: 1, forecastType: 1, status: 1 });

// Virtual for days until target
forecastAccuracySchema.virtual('daysUntilTarget').get(function() {
  if (!this.targetDate) return null;
  const now = new Date();
  const diffTime = this.targetDate - now;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
});

// Virtual for days since forecast
forecastAccuracySchema.virtual('daysSinceForecast').get(function() {
  if (!this.forecastDate) return null;
  const now = new Date();
  const diffTime = now - this.forecastDate;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
});

// Method to calculate accuracy when actual value is provided
forecastAccuracySchema.methods.calculateAccuracy = function() {
  if (this.actualValue === null || this.actualValue === undefined) {
    throw new Error("Cannot calculate accuracy: actual value not provided");
  }
  
  if (this.predictedValue === null || this.predictedValue === undefined) {
    throw new Error("Cannot calculate accuracy: predicted value missing");
  }
  
  // Calculate absolute error
  this.absoluteError = Math.abs(this.predictedValue - this.actualValue);
  
  // Calculate percentage error (avoid division by zero)
  if (this.actualValue !== 0) {
    this.percentageError = ((this.predictedValue - this.actualValue) / this.actualValue) * 100;
    
    // Calculate MAPE (Mean Absolute Percentage Error)
    this.mape = Math.abs(this.percentageError);
    
    // Calculate accuracy (100% - MAPE, capped at 0)
    this.accuracy = Math.max(0, 100 - this.mape);
  } else {
    // If actual is 0, use absolute error only
    this.percentageError = this.predictedValue === 0 ? 0 : 100;
    this.mape = this.percentageError;
    this.accuracy = this.predictedValue === 0 ? 100 : 0;
  }
  
  // Check if prediction was within confidence bounds
  if (this.predictedLower !== null && this.predictedUpper !== null) {
    this.withinConfidenceBounds = 
      this.actualValue >= this.predictedLower && 
      this.actualValue <= this.predictedUpper;
  }
  
  // Update status
  this.status = "completed";
  this.actualProvidedAt = new Date();
  
  return {
    accuracy: this.accuracy,
    mape: this.mape,
    absoluteError: this.absoluteError,
    percentageError: this.percentageError
  };
};

// Static method to get average accuracy for a user/type
forecastAccuracySchema.statics.getAverageAccuracy = async function(userId, forecastType = null, domain = null) {
  const query = {
    userId,
    status: "completed"
  };
  
  if (forecastType) query.forecastType = forecastType;
  if (domain) query.domain = domain;
  
  const forecasts = await this.find(query);
  
  if (forecasts.length === 0) {
    return {
      count: 0,
      averageAccuracy: null,
      averageMAPE: null
    };
  }
  
  const totalAccuracy = forecasts.reduce((sum, f) => sum + (f.accuracy || 0), 0);
  const totalMAPE = forecasts.reduce((sum, f) => sum + (f.mape || 0), 0);
  
  return {
    count: forecasts.length,
    averageAccuracy: (totalAccuracy / forecasts.length).toFixed(2),
    averageMAPE: (totalMAPE / forecasts.length).toFixed(2)
  };
};

// Static method to get forecasts needing actual values (for reminders)
forecastAccuracySchema.statics.getPendingForecasts = async function(userId, daysThreshold = 30) {
  const now = new Date();
  const thresholdDate = new Date(now.getTime() + (daysThreshold * 24 * 60 * 60 * 1000));
  
  return await this.find({
    userId,
    status: "pending",
    targetDate: { $lte: thresholdDate },
    reminderSent: false
  }).sort({ targetDate: 1 });
};

// Static method to mark forecasts as expired
forecastAccuracySchema.statics.markExpiredForecasts = async function() {
  const now = new Date();
  const expiryDate = new Date(now.getTime() - (7 * 24 * 60 * 60 * 1000)); // 7 days after target date
  
  const result = await this.updateMany(
    {
      status: "pending",
      targetDate: { $lt: expiryDate }
    },
    {
      $set: { status: "expired" }
    }
  );
  
  return result;
};

const ForecastAccuracy = mongoose.model("ForecastAccuracy", forecastAccuracySchema);

export default ForecastAccuracy;

