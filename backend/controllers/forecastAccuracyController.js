/**
 * Forecast Accuracy Controller
 * 
 * Handles forecast accuracy tracking and parameter optimization
 * Part of Objective 3.3: Adaptive Learning & User Feedback - Phase 2
 */

import ForecastAccuracy from "../models/ForecastAccuracy.js";
import parameterOptimizer from "../services/parameterOptimizer.js";

/**
 * Create forecast accuracy record (called by Flask)
 * POST /api/forecast-accuracy/create
 */
export const createForecastRecord = async (req, res) => {
  try {
    const {
      userId,
      datasetId,
      chartId,
      chartTitle,
      forecastType,
      domain,
      forecastDate,
      forecastPeriod,
      targetDate,
      predictedValue,
      predictedLower,
      predictedUpper,
      modelParameters,
      status
    } = req.body;

    // Create forecast record
    const forecast = await ForecastAccuracy.create({
      userId,
      datasetId,
      chartId,
      chartTitle,
      forecastType,
      domain,
      forecastDate,
      forecastPeriod,
      targetDate,
      predictedValue,
      predictedLower,
      predictedUpper,
      modelParameters,
      status: status || "pending"
    });

    res.status(201).json({
      success: true,
      message: "Forecast record created successfully",
      data: {
        forecastId: forecast._id
      }
    });

  } catch (error) {
    console.error(`❌ Error creating forecast record: ${error.message}`);
    res.status(500).json({
      success: false,
      message: "Failed to create forecast record",
      error: error.message
    });
  }
};

/**
 * Submit actual value for a forecast
 * POST /api/forecast-accuracy/submit-actual
 */
export const submitActualValue = async (req, res) => {
  try {
    const { forecastId, actualValue, notes } = req.body;
    const userId = req.user.id;

    if (!forecastId || actualValue === undefined || actualValue === null) {
      return res.status(400).json({
        success: false,
        message: "Required fields missing: forecastId, actualValue"
      });
    }

    // Find forecast
    const forecast = await ForecastAccuracy.findOne({
      _id: forecastId,
      userId
    });

    if (!forecast) {
      return res.status(404).json({
        success: false,
        message: "Forecast not found or you don't have permission"
      });
    }

    if (forecast.status === "completed") {
      return res.status(400).json({
        success: false,
        message: "Actual value already provided for this forecast"
      });
    }

    // Update actual value and calculate accuracy
    forecast.actualValue = actualValue;
    if (notes) forecast.notes = notes;
    
    const accuracyMetrics = forecast.calculateAccuracy();
    await forecast.save();

    console.log(`✅ Actual value submitted for forecast ${forecastId}`);
    console.log(`   Accuracy: ${accuracyMetrics.accuracy.toFixed(1)}%, MAPE: ${accuracyMetrics.mape.toFixed(1)}%`);

    res.status(200).json({
      success: true,
      message: "Actual value submitted successfully",
      data: {
        forecastId: forecast._id,
        predictedValue: forecast.predictedValue,
        actualValue: forecast.actualValue,
        accuracy: accuracyMetrics.accuracy,
        mape: accuracyMetrics.mape,
        absoluteError: accuracyMetrics.absoluteError,
        percentageError: accuracyMetrics.percentageError
      }
    });

  } catch (error) {
    console.error(`❌ Error submitting actual value: ${error.message}`);
    res.status(500).json({
      success: false,
      message: "Failed to submit actual value",
      error: error.message
    });
  }
};

/**
 * Get pending forecasts (waiting for actual values)
 * GET /api/forecast-accuracy/pending
 */
export const getPendingForecasts = async (req, res) => {
  try {
    const userId = req.user.id;

    const forecasts = await ForecastAccuracy.find({
      userId,
      status: "pending"
    })
    .sort({ targetDate: 1 })
    .populate('datasetId', 'fileName originalName')
    .lean();

    // Add days until target for each
    const now = new Date();
    const enrichedForecasts = forecasts.map(f => ({
      ...f,
      daysUntilTarget: Math.ceil((f.targetDate - now) / (1000 * 60 * 60 * 24)),
      daysSinceForecast: Math.ceil((now - f.forecastDate) / (1000 * 60 * 60 * 24))
    }));

    res.status(200).json({
      success: true,
      message: "Pending forecasts retrieved successfully",
      data: {
        count: enrichedForecasts.length,
        forecasts: enrichedForecasts
      }
    });

  } catch (error) {
    console.error(`❌ Error getting pending forecasts: ${error.message}`);
    res.status(500).json({
      success: false,
      message: "Failed to get pending forecasts",
      error: error.message
    });
  }
};

/**
 * Get forecast accuracy history
 * GET /api/forecast-accuracy/history
 */
export const getForecastHistory = async (req, res) => {
  try {
    const userId = req.user.id;
    const { forecastType, domain, status, limit = 50 } = req.query;

    const query = { userId };
    if (forecastType) query.forecastType = forecastType;
    if (domain) query.domain = domain;
    if (status) query.status = status;

    const forecasts = await ForecastAccuracy.find(query)
      .sort({ createdAt: -1 })
      .limit(parseInt(limit))
      .populate('datasetId', 'fileName originalName')
      .lean();

    // Calculate statistics
    const completed = forecasts.filter(f => f.status === "completed");
    const avgAccuracy = completed.length > 0
      ? (completed.reduce((sum, f) => sum + (f.accuracy || 0), 0) / completed.length).toFixed(2)
      : null;

    res.status(200).json({
      success: true,
      message: "Forecast history retrieved successfully",
      data: {
        count: forecasts.length,
        completedCount: completed.length,
        averageAccuracy: avgAccuracy,
        forecasts
      }
    });

  } catch (error) {
    console.error(`❌ Error getting forecast history: ${error.message}`);
    res.status(500).json({
      success: false,
      message: "Failed to get forecast history",
      error: error.message
    });
  }
};

/**
 * Get optimized parameters for forecasting
 * GET /api/forecast-accuracy/optimized-parameters
 */
export const getOptimizedParameters = async (req, res) => {
  try {
    const userId = req.user.id;
    const { forecastType = "sales", domain = "sales" } = req.query;

    console.log(`🔧 Request: Get optimized parameters for ${forecastType}/${domain}`);

    const result = await parameterOptimizer.getOptimizedParameters(
      userId,
      forecastType,
      domain
    );

    res.status(200).json({
      success: true,
      message: result.optimized 
        ? "Optimized parameters generated successfully" 
        : "Using default parameters (insufficient data for optimization)",
      data: result
    });

  } catch (error) {
    console.error(`❌ Error getting optimized parameters: ${error.message}`);
    res.status(500).json({
      success: false,
      message: "Failed to get optimized parameters",
      error: error.message
    });
  }
};

/**
 * Get accuracy statistics
 * GET /api/forecast-accuracy/statistics
 */
export const getAccuracyStatistics = async (req, res) => {
  try {
    const userId = req.user.id;

    const stats = await parameterOptimizer.getOptimizationStatistics(userId);

    res.status(200).json({
      success: true,
      message: "Accuracy statistics retrieved successfully",
      data: stats
    });

  } catch (error) {
    console.error(`❌ Error getting accuracy statistics: ${error.message}`);
    res.status(500).json({
      success: false,
      message: "Failed to get accuracy statistics",
      error: error.message
    });
  }
};

/**
 * Get forecasts needing reminders
 * GET /api/forecast-accuracy/reminders
 */
export const getForecastsNeedingReminders = async (req, res) => {
  try {
    const userId = req.user.id;
    const { daysThreshold = 30 } = req.query;

    const forecasts = await ForecastAccuracy.getPendingForecasts(
      userId,
      parseInt(daysThreshold)
    );

    res.status(200).json({
      success: true,
      message: "Forecasts needing reminders retrieved successfully",
      data: {
        count: forecasts.length,
        forecasts
      }
    });

  } catch (error) {
    console.error(`❌ Error getting forecast reminders: ${error.message}`);
    res.status(500).json({
      success: false,
      message: "Failed to get forecast reminders",
      error: error.message
    });
  }
};

/**
 * Mark reminder as sent
 * POST /api/forecast-accuracy/mark-reminder-sent
 */
export const markReminderSent = async (req, res) => {
  try {
    const { forecastId } = req.body;
    const userId = req.user.id;

    const forecast = await ForecastAccuracy.findOne({
      _id: forecastId,
      userId
    });

    if (!forecast) {
      return res.status(404).json({
        success: false,
        message: "Forecast not found"
      });
    }

    forecast.reminderSent = true;
    forecast.reminderSentAt = new Date();
    await forecast.save();

    res.status(200).json({
      success: true,
      message: "Reminder marked as sent"
    });

  } catch (error) {
    console.error(`❌ Error marking reminder sent: ${error.message}`);
    res.status(500).json({
      success: false,
      message: "Failed to mark reminder sent",
      error: error.message
    });
  }
};

/**
 * Delete forecast record
 * DELETE /api/forecast-accuracy/:id
 */
export const deleteForecast = async (req, res) => {
  try {
    const forecastId = req.params.id;
    const userId = req.user.id;
    const userRole = req.user.role;

    // Allow users to delete their own forecasts, admins can delete any
    const query = userRole === 'admin' ? { _id: forecastId } : { _id: forecastId, userId };
    
    const forecast = await ForecastAccuracy.findOne(query);

    if (!forecast) {
      return res.status(404).json({
        success: false,
        message: "Forecast not found or you don't have permission to delete it"
      });
    }

    await ForecastAccuracy.deleteOne({ _id: forecastId });

    res.status(200).json({
      success: true,
      message: "Forecast deleted successfully",
      deletedForecast: {
        id: forecast._id,
        chartTitle: forecast.chartTitle,
        targetDate: forecast.targetDate
      }
    });

  } catch (error) {
    console.error(`❌ Error deleting forecast: ${error.message}`);
    res.status(500).json({
      success: false,
      message: "Failed to delete forecast",
      error: error.message
    });
  }
};

