import ChartFeedback from "../models/ChartFeedback.js";
import { analyzeSentiment, detectMismatch } from "../services/sentimentAnalysisService.js";

/**
 * Submit feedback for a specific chart
 * POST /api/feedback/chart
 */
export const submitChartFeedback = async (req, res) => {
  try {
    const { datasetId, chartId, chartTitle, rating, comment } = req.body;
    const userId = req.user.id;

    // Validate input
    if (!datasetId || !chartId || !chartTitle || !rating) {
      return res.status(400).json({
        success: false,
        message: "Required fields missing: datasetId, chartId, chartTitle, rating",
      });
    }

    if (rating < 1 || rating > 5) {
      return res.status(400).json({
        success: false,
        message: "Rating must be between 1 and 5",
      });
    }

    // Comment is optional, but if provided, must be at least 5 characters
    if (comment && comment.trim().length > 0 && comment.trim().length < 5) {
      return res.status(400).json({
        success: false,
        message: "Comment must be at least 5 characters long if provided",
      });
    }

    // Perform sentiment analysis
    console.log("🧠 Analyzing sentiment for feedback...");
    const sentimentAnalysis = await analyzeSentiment(comment);
    console.log("✅ Sentiment analysis complete:", sentimentAnalysis);

    // Detect rating/sentiment mismatch
    const mismatch = detectMismatch(rating, sentimentAnalysis.sentiment, sentimentAnalysis.score);
    console.log("🔍 Mismatch detection:", mismatch);

    // Create feedback record
    const feedback = await ChartFeedback.create({
      userId,
      datasetId,
      chartId,
      chartTitle,
      rating,
      comment,
      sentiment: sentimentAnalysis.sentiment,
      sentimentScore: sentimentAnalysis.score,
      mismatchDetected: mismatch.mismatchDetected,
      mismatchSeverity: mismatch.severity,
    });

    // Log mismatch for admin review
    if (mismatch.mismatchDetected) {
      console.log(`⚠️ Sentiment mismatch detected! Rating: ${rating}, Sentiment: ${sentimentAnalysis.sentiment}, Severity: ${mismatch.severity}`);
    }

    res.status(201).json({
      success: true,
      message: "Thank you for your feedback!",
      data: feedback,
      sentiment: {
        detected: sentimentAnalysis.sentiment,
        score: sentimentAnalysis.score,
        mismatch: mismatch.mismatchDetected,
        mismatchSeverity: mismatch.severity,
      },
    });
  } catch (error) {
    console.error("❌ Error submitting chart feedback:", error);
    res.status(500).json({
      success: false,
      message: "Failed to submit feedback",
      error: error.message,
    });
  }
};

/**
 * Get all feedback for a user (with date filter)
 * GET /api/feedback/my-feedback?startDate=2024-01-01&endDate=2024-12-31
 */
export const getMyFeedback = async (req, res) => {
  try {
    const userId = req.user.id;
    const { startDate, endDate } = req.query;

    // Build query
    const query = { userId };

    // Add date filter if provided
    if (startDate || endDate) {
      query.createdAt = {};
      if (startDate) {
        query.createdAt.$gte = new Date(startDate);
      }
      if (endDate) {
        const endDateTime = new Date(endDate);
        endDateTime.setHours(23, 59, 59, 999);
        query.createdAt.$lte = endDateTime;
      }
    }

    const feedbacks = await ChartFeedback.find(query)
      .populate("datasetId", "fileName uploadDate")
      .sort({ createdAt: -1 });

    // Group by sentiment for stats
    const stats = {
      total: feedbacks.length,
      byRating: {
        5: feedbacks.filter((f) => f.rating === 5).length,
        4: feedbacks.filter((f) => f.rating === 4).length,
        3: feedbacks.filter((f) => f.rating === 3).length,
        2: feedbacks.filter((f) => f.rating === 2).length,
        1: feedbacks.filter((f) => f.rating === 1).length,
      },
      bySentiment: {
        positive: feedbacks.filter((f) => f.sentiment === "positive").length,
        neutral: feedbacks.filter((f) => f.sentiment === "neutral").length,
        negative: feedbacks.filter((f) => f.sentiment === "negative").length,
      },
      mismatches: {
        total: feedbacks.filter((f) => f.mismatchDetected).length,
        major: feedbacks.filter((f) => f.mismatchSeverity === "major").length,
        minor: feedbacks.filter((f) => f.mismatchSeverity === "minor").length,
      },
      averageRating: feedbacks.length > 0 
        ? (feedbacks.reduce((sum, f) => sum + f.rating, 0) / feedbacks.length).toFixed(2)
        : 0,
    };

    res.status(200).json({
      success: true,
      data: feedbacks,
      stats,
    });
  } catch (error) {
    console.error("❌ Error fetching feedback:", error);
    res.status(500).json({
      success: false,
      message: "Failed to fetch feedback",
      error: error.message,
    });
  }
};

/**
 * Get feedback for a specific chart
 * GET /api/feedback/chart/:chartId
 */
export const getFeedbackForChart = async (req, res) => {
  try {
    const { chartId } = req.params;
    const userId = req.user.id;

    const feedbacks = await ChartFeedback.find({
      userId,
      chartId,
    })
      .populate("datasetId", "fileName uploadDate")
      .sort({ createdAt: -1 });

    res.status(200).json({
      success: true,
      data: feedbacks,
    });
  } catch (error) {
    console.error("❌ Error fetching chart feedback:", error);
    res.status(500).json({
      success: false,
      message: "Failed to fetch chart feedback",
      error: error.message,
    });
  }
};

/**
 * Admin: Get all feedback with advanced filtering
 * GET /api/admin/feedback?startDate=...&endDate=...&sentiment=...&mismatchOnly=true
 */
export const getAllFeedback = async (req, res) => {
  try {
    const { startDate, endDate, sentiment, mismatchOnly, chartId, rating, search } = req.query;

    // Build query
    const query = {};

    // Date filter
    if (startDate || endDate) {
      query.createdAt = {};
      if (startDate) {
        query.createdAt.$gte = new Date(startDate);
      }
      if (endDate) {
        const endDateTime = new Date(endDate);
        endDateTime.setHours(23, 59, 59, 999);
        query.createdAt.$lte = endDateTime;
      }
    }

    // Sentiment filter
    if (sentiment) {
      query.sentiment = sentiment;
    }

    // Mismatch filter
    if (mismatchOnly === "true") {
      query.mismatchDetected = true;
    }

    // Chart filter
    if (chartId) {
      query.chartId = chartId;
    }

    // Rating filter
    if (rating) {
      query.rating = parseInt(rating);
    }

    // Search filter (chart title)
    if (search) {
      query.chartTitle = { $regex: search, $options: 'i' };
    }

    const feedbacks = await ChartFeedback.find(query)
      .populate("userId", "fullName businessName email")
      .populate("datasetId", "fileName uploadDate")
      .sort({ createdAt: -1 });

    // Calculate comprehensive stats
    const stats = {
      total: feedbacks.length,
      byRating: {
        5: feedbacks.filter((f) => f.rating === 5).length,
        4: feedbacks.filter((f) => f.rating === 4).length,
        3: feedbacks.filter((f) => f.rating === 3).length,
        2: feedbacks.filter((f) => f.rating === 2).length,
        1: feedbacks.filter((f) => f.rating === 1).length,
      },
      bySentiment: {
        positive: feedbacks.filter((f) => f.sentiment === "positive").length,
        neutral: feedbacks.filter((f) => f.sentiment === "neutral").length,
        negative: feedbacks.filter((f) => f.sentiment === "negative").length,
      },
      mismatches: {
        total: feedbacks.filter((f) => f.mismatchDetected).length,
        major: feedbacks.filter((f) => f.mismatchSeverity === "major").length,
        minor: feedbacks.filter((f) => f.mismatchSeverity === "minor").length,
      },
      averageRating: feedbacks.length > 0 
        ? (feedbacks.reduce((sum, f) => sum + f.rating, 0) / feedbacks.length).toFixed(2)
        : 0,
      chartBreakdown: getChartBreakdown(feedbacks),
    };

    res.status(200).json({
      success: true,
      data: feedbacks,
      stats,
    });
  } catch (error) {
    console.error("❌ Error fetching all feedback:", error);
    res.status(500).json({
      success: false,
      message: "Failed to fetch feedback",
      error: error.message,
    });
  }
};

/**
 * Helper: Get feedback breakdown by chart type
 */
const getChartBreakdown = (feedbacks) => {
  const breakdown = {};

  feedbacks.forEach((f) => {
    if (!breakdown[f.chartId]) {
      breakdown[f.chartId] = {
        chartTitle: f.chartTitle,
        count: 0,
        averageRating: 0,
        totalRating: 0,
        sentiments: { positive: 0, neutral: 0, negative: 0 },
      };
    }

    breakdown[f.chartId].count++;
    breakdown[f.chartId].totalRating += f.rating;
    breakdown[f.chartId].sentiments[f.sentiment]++;
  });

  // Calculate averages
  Object.keys(breakdown).forEach((chartId) => {
    breakdown[chartId].averageRating = (
      breakdown[chartId].totalRating / breakdown[chartId].count
    ).toFixed(2);
  });

  return breakdown;
};

/**
 * Delete feedback (user's own feedback only)
 * DELETE /api/feedback/:id
 */
export const deleteChartFeedback = async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;

    const feedback = await ChartFeedback.findOne({ _id: id, userId });

    if (!feedback) {
      return res.status(404).json({
        success: false,
        message: "Feedback not found or you don't have permission to delete it",
      });
    }

    await ChartFeedback.findByIdAndDelete(id);

    res.status(200).json({
      success: true,
      message: "Feedback deleted successfully",
    });
  } catch (error) {
    console.error("❌ Error deleting feedback:", error);
    res.status(500).json({
      success: false,
      message: "Failed to delete feedback",
      error: error.message,
    });
  }
};

