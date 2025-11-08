/**
 * Parameter Optimizer Service
 * 
 * Analyzes forecast accuracy history and recommends optimal Prophet parameters
 * Part of Objective 3.3: Adaptive Learning & User Feedback - Phase 2
 */

import ForecastAccuracy from "../models/ForecastAccuracy.js";

class ParameterOptimizer {
  /**
   * Get optimized Prophet parameters based on historical accuracy data
   * 
   * @param {String} userId - User ID
   * @param {String} forecastType - "sales" | "quantity" | "stock" | "cash_flow"
   * @param {String} domain - "sales" | "inventory" | "finance" | "product"
   * @param {Number} minSamples - Minimum accuracy samples needed (default: 10)
   * @returns {Object} Optimized parameters or default parameters
   */
  async getOptimizedParameters(userId, forecastType, domain, minSamples = 10) {
    try {
      console.log(`🔧 Parameter Optimizer: Analyzing ${forecastType} forecasts for user ${userId}`);

      // Get completed forecasts with accuracy data
      const forecasts = await ForecastAccuracy.find({
        userId,
        forecastType,
        domain,
        status: "completed"
      }).sort({ createdAt: -1 }).limit(50); // Analyze last 50 forecasts

      if (forecasts.length < minSamples) {
        console.log(`ℹ️ Insufficient data for optimization: ${forecasts.length}/${minSamples} samples`);
        return {
          optimized: false,
          reason: `Not enough data (${forecasts.length}/${minSamples} samples needed)`,
          parameters: this._getDefaultParameters(forecastType),
          confidence: 0,
          sampleCount: forecasts.length
        };
      }

      // Analyze parameter performance
      const parameterAnalysis = this._analyzeParameterPerformance(forecasts);

      // Generate optimized parameters
      const optimizedParams = this._generateOptimizedParameters(
        parameterAnalysis,
        forecastType
      );

      // Calculate confidence based on sample size and consistency
      const confidence = this._calculateConfidence(
        forecasts.length,
        parameterAnalysis.variance
      );

      console.log(`✅ Generated optimized parameters with ${confidence}% confidence`);
      console.log(`   Samples: ${forecasts.length}, Avg Accuracy: ${parameterAnalysis.avgAccuracy.toFixed(1)}%`);

      return {
        optimized: true,
        parameters: optimizedParams,
        confidence,
        sampleCount: forecasts.length,
        analysis: {
          averageAccuracy: parameterAnalysis.avgAccuracy,
          averageMAPE: parameterAnalysis.avgMAPE,
          bestAccuracy: parameterAnalysis.bestAccuracy,
          worstAccuracy: parameterAnalysis.worstAccuracy,
          variance: parameterAnalysis.variance
        },
        recommendations: this._generateRecommendations(parameterAnalysis)
      };

    } catch (error) {
      console.error(`❌ Error optimizing parameters: ${error.message}`);
      throw error;
    }
  }

  /**
   * Analyze performance of different parameter combinations
   */
  _analyzeParameterPerformance(forecasts) {
    const accuracies = forecasts.map(f => f.accuracy || 0);
    const mapes = forecasts.map(f => f.mape || 0);

    // Calculate statistics
    const avgAccuracy = accuracies.reduce((a, b) => a + b, 0) / accuracies.length;
    const avgMAPE = mapes.reduce((a, b) => a + b, 0) / mapes.length;
    const bestAccuracy = Math.max(...accuracies);
    const worstAccuracy = Math.min(...accuracies);

    // Calculate variance (measures consistency)
    const mean = avgAccuracy;
    const squareDiffs = accuracies.map(value => Math.pow(value - mean, 2));
    const variance = squareDiffs.reduce((a, b) => a + b, 0) / squareDiffs.length;

    // Group forecasts by parameter values
    const parameterGroups = this._groupByParameters(forecasts);

    // Find best-performing parameter combinations
    const bestParameters = this._findBestParameters(parameterGroups);

    return {
      avgAccuracy,
      avgMAPE,
      bestAccuracy,
      worstAccuracy,
      variance,
      parameterGroups,
      bestParameters
    };
  }

  /**
   * Group forecasts by their parameter combinations
   */
  _groupByParameters(forecasts) {
    const groups = {};

    forecasts.forEach(forecast => {
      if (!forecast.modelParameters) return;

      const params = forecast.modelParameters;
      const key = JSON.stringify({
        changepoint: params.changepoint_prior_scale,
        seasonality: params.seasonality_mode,
        yearly: params.yearly_seasonality,
        weekly: params.weekly_seasonality
      });

      if (!groups[key]) {
        groups[key] = {
          parameters: params,
          forecasts: [],
          accuracies: [],
          avgAccuracy: 0
        };
      }

      groups[key].forecasts.push(forecast);
      groups[key].accuracies.push(forecast.accuracy || 0);
    });

    // Calculate average accuracy for each group
    Object.values(groups).forEach(group => {
      group.avgAccuracy = 
        group.accuracies.reduce((a, b) => a + b, 0) / group.accuracies.length;
    });

    return groups;
  }

  /**
   * Find best-performing parameters
   */
  _findBestParameters(parameterGroups) {
    const groups = Object.values(parameterGroups);

    if (groups.length === 0) return null;

    // Sort by average accuracy
    groups.sort((a, b) => b.avgAccuracy - a.avgAccuracy);

    return groups[0]; // Return best group
  }

  /**
   * Generate optimized parameters based on analysis
   */
  _generateOptimizedParameters(analysis, forecastType) {
    const defaultParams = this._getDefaultParameters(forecastType);

    // If we have best-performing parameters, use them as base
    if (analysis.bestParameters && analysis.bestParameters.forecasts.length >= 3) {
      const bestParams = analysis.bestParameters.parameters;

      return {
        changepoint_prior_scale: bestParams.changepoint_prior_scale || defaultParams.changepoint_prior_scale,
        seasonality_mode: bestParams.seasonality_mode || defaultParams.seasonality_mode,
        seasonality_prior_scale: bestParams.seasonality_prior_scale || defaultParams.seasonality_prior_scale,
        yearly_seasonality: bestParams.yearly_seasonality !== undefined 
          ? bestParams.yearly_seasonality 
          : defaultParams.yearly_seasonality,
        weekly_seasonality: bestParams.weekly_seasonality !== undefined
          ? bestParams.weekly_seasonality
          : defaultParams.weekly_seasonality,
        daily_seasonality: false,
        holidays_prior_scale: bestParams.holidays_prior_scale || defaultParams.holidays_prior_scale
      };
    }

    // Otherwise, adjust based on overall performance
    const adjustedParams = { ...defaultParams };

    // If accuracy is low, try more flexible model
    if (analysis.avgAccuracy < 70) {
      adjustedParams.changepoint_prior_scale = Math.min(
        defaultParams.changepoint_prior_scale * 1.5,
        0.5
      );
      console.log(`   Adjustment: Increased changepoint flexibility for low accuracy`);
    }

    // If variance is high, try more stable model
    if (analysis.variance > 100) {
      adjustedParams.changepoint_prior_scale = Math.max(
        defaultParams.changepoint_prior_scale * 0.5,
        0.001
      );
      console.log(`   Adjustment: Decreased changepoint flexibility for high variance`);
    }

    return adjustedParams;
  }

  /**
   * Get default Prophet parameters by forecast type
   */
  _getDefaultParameters(forecastType) {
    const defaults = {
      sales: {
        changepoint_prior_scale: 0.05,
        seasonality_mode: 'multiplicative',
        seasonality_prior_scale: 10.0,
        yearly_seasonality: true,
        weekly_seasonality: true,
        daily_seasonality: false,
        holidays_prior_scale: 10.0
      },
      quantity: {
        changepoint_prior_scale: 0.05,
        seasonality_mode: 'additive',
        seasonality_prior_scale: 10.0,
        yearly_seasonality: true,
        weekly_seasonality: true,
        daily_seasonality: false,
        holidays_prior_scale: 10.0
      },
      stock: {
        changepoint_prior_scale: 0.05,
        seasonality_mode: 'multiplicative',
        seasonality_prior_scale: 10.0,
        yearly_seasonality: true,
        weekly_seasonality: true,
        daily_seasonality: false,
        holidays_prior_scale: 10.0
      },
      cash_flow: {
        changepoint_prior_scale: 0.05,
        seasonality_mode: 'additive',
        seasonality_prior_scale: 10.0,
        yearly_seasonality: true,
        weekly_seasonality: true,
        daily_seasonality: false,
        holidays_prior_scale: 10.0
      }
    };

    return defaults[forecastType] || defaults.sales;
  }

  /**
   * Calculate confidence based on sample size and consistency
   */
  _calculateConfidence(sampleCount, variance) {
    // Base confidence on sample count (0-70%)
    let confidence = Math.min((sampleCount / 30) * 70, 70);

    // Adjust based on variance (lower variance = higher confidence)
    const variancePenalty = Math.min(variance / 10, 30);
    confidence = Math.max(confidence - variancePenalty, 0);

    return Math.round(confidence);
  }

  /**
   * Generate recommendations based on analysis
   */
  _generateRecommendations(analysis) {
    const recommendations = [];

    if (analysis.avgAccuracy < 70) {
      recommendations.push({
        type: "low_accuracy",
        message: "Average forecast accuracy is below 70%. Consider collecting more diverse historical data.",
        priority: "high"
      });
    }

    if (analysis.variance > 100) {
      recommendations.push({
        type: "high_variance",
        message: "High variance detected in forecast accuracy. Model parameters have been adjusted for more stability.",
        priority: "medium"
      });
    }

    if (analysis.bestAccuracy > 90) {
      recommendations.push({
        type: "excellent_accuracy",
        message: "Excellent forecast accuracy achieved! Continue providing actual values to maintain model quality.",
        priority: "low"
      });
    }

    if (recommendations.length === 0) {
      recommendations.push({
        type: "normal",
        message: "Forecast accuracy is within normal range. System will continue learning from new data.",
        priority: "low"
      });
    }

    return recommendations;
  }

  /**
   * Get optimization statistics for admin dashboard
   */
  async getOptimizationStatistics(userId = null) {
    try {
      const query = userId ? { userId } : {};

      const totalForecasts = await ForecastAccuracy.countDocuments(query);
      const completedForecasts = await ForecastAccuracy.countDocuments({
        ...query,
        status: "completed"
      });
      const pendingForecasts = await ForecastAccuracy.countDocuments({
        ...query,
        status: "pending"
      });

      const optimizedForecasts = await ForecastAccuracy.countDocuments({
        ...query,
        usedForOptimization: true
      });

      // Get average accuracy by type
      const forecastTypes = ["sales", "quantity", "stock", "cash_flow"];
      const accuracyByType = {};

      for (const type of forecastTypes) {
        const forecasts = await ForecastAccuracy.find({
          ...query,
          forecastType: type,
          status: "completed"
        });

        if (forecasts.length > 0) {
          const avgAccuracy = forecasts.reduce((sum, f) => sum + (f.accuracy || 0), 0) / forecasts.length;
          const avgMAPE = forecasts.reduce((sum, f) => sum + (f.mape || 0), 0) / forecasts.length;

          accuracyByType[type] = {
            count: forecasts.length,
            averageAccuracy: avgAccuracy.toFixed(2),
            averageMAPE: avgMAPE.toFixed(2)
          };
        }
      }

      return {
        totalForecasts,
        completedForecasts,
        pendingForecasts,
        optimizedForecasts,
        optimizationRate: totalForecasts > 0 
          ? ((optimizedForecasts / totalForecasts) * 100).toFixed(1) 
          : 0,
        accuracyByType,
        userId: userId || "all"
      };

    } catch (error) {
      console.error(`❌ Error getting optimization statistics: ${error.message}`);
      throw error;
    }
  }
}

export default new ParameterOptimizer();

