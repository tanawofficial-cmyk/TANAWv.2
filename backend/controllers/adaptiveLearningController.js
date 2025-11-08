/**
 * Adaptive Learning Controller
 * 
 * Handles endpoints for adaptive learning features:
 * - Feedback pattern analysis
 * - Prompt enhancement recommendations
 * - Forecast accuracy tracking
 * 
 * Part of Objective 3.3: Adaptive Learning & User Feedback
 */

import feedbackAnalyzer from "../services/feedbackAnalyzer.js";

/**
 * Get feedback patterns for a specific domain
 * GET /api/adaptive-learning/feedback-patterns
 * Query params: domain (optional) = "sales" | "inventory" | "finance" | "customer" | "product" | "all"
 */
export const getFeedbackPatterns = async (req, res) => {
  try {
    const { domain = "all" } = req.query;

    console.log(`📊 Request: Analyze feedback patterns for domain: ${domain}`);

    // Analyze feedback patterns
    const result = await feedbackAnalyzer.analyzeFeedbackPatterns(domain);

    if (!result.hasEnoughData) {
      return res.status(200).json({
        success: false,
        message: `Insufficient feedback data. Need at least ${result.minRequired} entries, found ${result.feedbackCount}.`,
        data: {
          hasEnoughData: false,
          feedbackCount: result.feedbackCount,
          minRequired: result.minRequired
        }
      });
    }

    console.log(`✅ Feedback analysis complete: ${result.feedbackCount} entries analyzed`);

    res.status(200).json({
      success: true,
      message: "Feedback patterns analyzed successfully",
      data: result
    });

  } catch (error) {
    console.error(`❌ Error analyzing feedback patterns: ${error.message}`);
    res.status(500).json({
      success: false,
      message: "Failed to analyze feedback patterns",
      error: error.message
    });
  }
};

/**
 * Get prompt enhancement recommendations based on feedback
 * GET /api/adaptive-learning/prompt-enhancements
 * Query params: domain (optional)
 */
export const getPromptEnhancements = async (req, res) => {
  try {
    const { domain = "all" } = req.query;

    console.log(`🧠 Request: Generate prompt enhancements for domain: ${domain}`);

    // Get feedback patterns
    const patterns = await feedbackAnalyzer.analyzeFeedbackPatterns(domain);

    if (!patterns.hasEnoughData) {
      return res.status(200).json({
        success: false,
        message: "Not enough feedback data to generate enhancements",
        data: {
          hasEnoughData: false,
          feedbackCount: patterns.feedbackCount
        }
      });
    }

    // Generate prompt enhancements
    const enhancements = feedbackAnalyzer.generatePromptEnhancements(patterns);

    console.log(`✅ Generated ${enhancements.enhancements.length} prompt enhancements`);

    res.status(200).json({
      success: true,
      message: "Prompt enhancements generated successfully",
      data: enhancements
    });

  } catch (error) {
    console.error(`❌ Error generating prompt enhancements: ${error.message}`);
    res.status(500).json({
      success: false,
      message: "Failed to generate prompt enhancements",
      error: error.message
    });
  }
};

/**
 * Get learning statistics (for admin dashboard)
 * GET /api/adaptive-learning/statistics
 */
export const getLearningStatistics = async (req, res) => {
  try {
    console.log(`📈 Request: Get adaptive learning statistics`);

    // Analyze patterns for all domains
    const domains = ["sales", "inventory", "finance", "customer", "product"];
    const statistics = {};

    for (const domain of domains) {
      const patterns = await feedbackAnalyzer.analyzeFeedbackPatterns(domain, 5); // Lower threshold for stats
      
      if (patterns.hasEnoughData) {
        statistics[domain] = {
          feedbackCount: patterns.feedbackCount,
          averageRating: patterns.patterns.statistics.averageRating,
          positivePercentage: patterns.patterns.statistics.positiveFeedbackPercentage,
          hasLearningData: true
        };
      } else {
        statistics[domain] = {
          feedbackCount: patterns.feedbackCount,
          hasLearningData: false
        };
      }
    }

    // Overall statistics
    const allPatterns = await feedbackAnalyzer.analyzeFeedbackPatterns("all", 1);
    
    const overallStats = {
      totalFeedback: allPatterns.feedbackCount,
      averageRating: allPatterns.hasEnoughData 
        ? allPatterns.patterns.statistics.averageRating 
        : "N/A",
      learningEnabled: allPatterns.feedbackCount >= 10,
      byDomain: statistics,
      lastAnalyzed: new Date()
    };

    console.log(`✅ Learning statistics retrieved: ${overallStats.totalFeedback} total feedback`);

    res.status(200).json({
      success: true,
      message: "Learning statistics retrieved successfully",
      data: overallStats
    });

  } catch (error) {
    console.error(`❌ Error getting learning statistics: ${error.message}`);
    res.status(500).json({
      success: false,
      message: "Failed to get learning statistics",
      error: error.message
    });
  }
};

/**
 * Test endpoint to see if learning is working
 * GET /api/adaptive-learning/test
 */
export const testAdaptiveLearning = async (req, res) => {
  try {
    console.log(`🧪 Test: Adaptive learning system`);

    // Test feedback analysis
    const patterns = await feedbackAnalyzer.analyzeFeedbackPatterns("all", 1);
    
    // Test prompt enhancement generation
    let enhancements = null;
    if (patterns.hasEnoughData) {
      enhancements = feedbackAnalyzer.generatePromptEnhancements(patterns);
    }

    const result = {
      system: "Adaptive Learning System",
      status: "operational",
      feedbackData: {
        available: patterns.feedbackCount > 0,
        count: patterns.feedbackCount,
        sufficientForLearning: patterns.hasEnoughData
      },
      promptEnhancements: {
        available: enhancements !== null,
        count: enhancements ? enhancements.enhancements.length : 0,
        confidence: enhancements ? enhancements.confidence : 0
      },
      recommendations: enhancements 
        ? enhancements.enhancements.slice(0, 3) 
        : ["Not enough data yet - need at least 10 feedback entries"],
      testedAt: new Date()
    };

    console.log(`✅ Adaptive learning test complete`);

    res.status(200).json({
      success: true,
      message: "Adaptive learning system is operational",
      data: result
    });

  } catch (error) {
    console.error(`❌ Adaptive learning test failed: ${error.message}`);
    res.status(500).json({
      success: false,
      message: "Adaptive learning test failed",
      error: error.message
    });
  }
};

