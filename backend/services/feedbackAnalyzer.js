/**
 * Feedback Analyzer Service
 * 
 * Analyzes user feedback patterns to improve AI recommendations
 * Part of Objective 3.3: Adaptive Learning & User Feedback
 */

import ChartFeedback from "../models/ChartFeedback.js";

class FeedbackAnalyzer {
  /**
   * Analyze feedback patterns for a specific domain (sales, inventory, finance, customer, product)
   * Returns insights about what users prefer in recommendations
   * 
   * @param {String} domain - "sales" | "inventory" | "finance" | "customer" | "product" | "all"
   * @param {Number} minFeedbackCount - Minimum feedback entries needed for reliable analysis (default: 10)
   * @returns {Object} - Patterns and preferences extracted from feedback
   */
  async analyzeFeedbackPatterns(domain = "all", minFeedbackCount = 1) {
    try {
      console.log(`📊 Analyzing feedback patterns for domain: ${domain}`);

      // Build query filter
      const query = {};
      if (domain !== "all") {
        // Filter by chart titles that contain domain keywords
        const domainKeywords = this._getDomainKeywords(domain);
        query.chartTitle = { $regex: domainKeywords.join("|"), $options: "i" };
      }

      // Fetch all feedback entries
      const feedbacks = await ChartFeedback.find(query)
        .sort({ createdAt: -1 })
        .limit(200) // Limit to recent 200 for performance
        .lean();

      if (feedbacks.length < minFeedbackCount) {
        console.log(`⚠️ Insufficient feedback data: ${feedbacks.length} entries (need ${minFeedbackCount})`);
        return {
          hasEnoughData: false,
          feedbackCount: feedbacks.length,
          minRequired: minFeedbackCount,
          patterns: null
        };
      }

      console.log(`✅ Found ${feedbacks.length} feedback entries for analysis`);

      // Analyze patterns
      const patterns = {
        // Rating distribution
        ratingDistribution: this._analyzeRatingDistribution(feedbacks),
        
        // Sentiment analysis
        sentimentAnalysis: this._analyzeSentimentPatterns(feedbacks),
        
        // Chart-specific patterns
        chartTypePreferences: this._analyzeChartPreferences(feedbacks),
        
        // Comment keyword analysis (what users mention most)
        commonKeywords: this._extractCommonKeywords(feedbacks),
        
        // High-rated patterns (what works well)
        highRatedPatterns: this._analyzeHighRatedFeedback(feedbacks),
        
        // Low-rated patterns (what to avoid)
        lowRatedPatterns: this._analyzeLowRatedFeedback(feedbacks),
        
        // Mismatch insights (rating vs sentiment conflicts)
        mismatchInsights: this._analyzeMismatches(feedbacks),
        
        // Overall statistics
        statistics: {
          totalFeedback: feedbacks.length,
          averageRating: this._calculateAverageRating(feedbacks),
          positiveFeedbackPercentage: this._calculatePositivePercentage(feedbacks),
          domain: domain,
          analyzedAt: new Date()
        }
      };

      console.log(`✅ Feedback analysis complete: Avg rating ${patterns.statistics.averageRating}/5`);

      return {
        hasEnoughData: true,
        feedbackCount: feedbacks.length,
        patterns: patterns
      };

    } catch (error) {
      console.error(`❌ Error analyzing feedback patterns: ${error.message}`);
      throw error;
    }
  }

  /**
   * Generate prompt enhancement guidelines based on feedback patterns
   * This is the key method that translates feedback into actionable prompt improvements
   */
  generatePromptEnhancements(patterns) {
    if (!patterns || !patterns.hasEnoughData) {
      return null;
    }

    const { patterns: data } = patterns;
    const enhancements = [];

    // 1. High-rated patterns -> Emphasize these
    if (data.highRatedPatterns.commonThemes.length > 0) {
      enhancements.push({
        type: "emphasis",
        instruction: `Users highly value recommendations that include: ${data.highRatedPatterns.commonThemes.join(", ")}`,
        priority: "high"
      });
    }

    // 2. Low-rated patterns -> Avoid these
    if (data.lowRatedPatterns.commonThemes.length > 0) {
      enhancements.push({
        type: "avoidance",
        instruction: `Avoid recommendations that are: ${data.lowRatedPatterns.commonThemes.join(", ")}`,
        priority: "high"
      });
    }

    // 3. Common keywords in positive feedback
    if (data.commonKeywords.positive.length > 0) {
      enhancements.push({
        type: "keyword_emphasis",
        instruction: `Include these concepts when relevant: ${data.commonKeywords.positive.slice(0, 5).join(", ")}`,
        priority: "medium"
      });
    }

    // 4. Chart-specific preferences
    const topCharts = data.chartTypePreferences.topRated.slice(0, 3);
    if (topCharts.length > 0) {
      enhancements.push({
        type: "chart_focus",
        instruction: `Users find these chart types most valuable: ${topCharts.map(c => c.chartType).join(", ")}`,
        priority: "low"
      });
    }

    // 5. Sentiment-based insights
    if (data.sentimentAnalysis.positivePercentage < 0.5) {
      enhancements.push({
        type: "tone_adjustment",
        instruction: "Users prefer more actionable, specific recommendations with clear next steps",
        priority: "high"
      });
    }

    return {
      enhancements,
      summary: this._generateEnhancementSummary(enhancements),
      confidence: this._calculateConfidence(patterns.feedbackCount),
      appliedAt: new Date()
    };
  }

  // ============================================
  // PRIVATE HELPER METHODS
  // ============================================

  _getDomainKeywords(domain) {
    const keywords = {
      sales: ["sales", "revenue", "product comparison", "regional sales"],
      inventory: ["stock", "inventory", "reorder", "turnover"],
      finance: ["profit", "expense", "cash flow", "margin"],
      customer: ["customer", "segment", "retention", "lifetime"],
      product: ["product performance", "quantity", "demand"]
    };
    return keywords[domain] || [];
  }

  _analyzeRatingDistribution(feedbacks) {
    const distribution = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
    feedbacks.forEach(f => {
      distribution[f.rating] = (distribution[f.rating] || 0) + 1;
    });
    return distribution;
  }

  _analyzeSentimentPatterns(feedbacks) {
    const sentiments = { positive: 0, neutral: 0, negative: 0 };
    feedbacks.forEach(f => {
      sentiments[f.sentiment] = (sentiments[f.sentiment] || 0) + 1;
    });
    const total = feedbacks.length;
    return {
      counts: sentiments,
      positivePercentage: sentiments.positive / total,
      neutralPercentage: sentiments.neutral / total,
      negativePercentage: sentiments.negative / total
    };
  }

  _analyzeChartPreferences(feedbacks) {
    const chartStats = {};
    
    feedbacks.forEach(f => {
      const chartType = f.chartTitle;
      if (!chartStats[chartType]) {
        chartStats[chartType] = {
          chartType,
          count: 0,
          totalRating: 0,
          avgRating: 0,
          sentiments: { positive: 0, neutral: 0, negative: 0 }
        };
      }
      chartStats[chartType].count++;
      chartStats[chartType].totalRating += f.rating;
      chartStats[chartType].sentiments[f.sentiment]++;
    });

    // Calculate averages
    Object.values(chartStats).forEach(stat => {
      stat.avgRating = stat.totalRating / stat.count;
    });

    // Sort by average rating
    const sorted = Object.values(chartStats).sort((a, b) => b.avgRating - a.avgRating);

    return {
      topRated: sorted.slice(0, 5),
      lowRated: sorted.slice(-5),
      all: sorted
    };
  }

  _extractCommonKeywords(feedbacks) {
    const positiveKeywords = {};
    const negativeKeywords = {};

    feedbacks.forEach(f => {
      if (!f.comment || f.comment.length < 5) return;

      const words = f.comment
        .toLowerCase()
        .replace(/[^\w\s]/g, '')
        .split(/\s+/)
        .filter(w => w.length > 3); // Only words longer than 3 chars

      const target = f.rating >= 4 ? positiveKeywords : negativeKeywords;
      
      words.forEach(word => {
        // Skip common stop words
        if (this._isStopWord(word)) return;
        target[word] = (target[word] || 0) + 1;
      });
    });

    return {
      positive: this._topKeywords(positiveKeywords, 10),
      negative: this._topKeywords(negativeKeywords, 10)
    };
  }

  _analyzeHighRatedFeedback(feedbacks) {
    const highRated = feedbacks.filter(f => f.rating >= 4);
    
    const themes = [];
    const commentPatterns = [];

    // Extract common themes from high-rated comments
    highRated.forEach(f => {
      if (f.comment && f.comment.length > 10) {
        const lower = f.comment.toLowerCase();
        
        // Detect common positive themes
        if (lower.includes("specific") || lower.includes("detailed")) {
          themes.push("specific");
        }
        if (lower.includes("actionable") || lower.includes("useful")) {
          themes.push("actionable");
        }
        if (lower.includes("clear") || lower.includes("understand")) {
          themes.push("clear");
        }
        if (lower.includes("number") || lower.includes("data")) {
          themes.push("data-driven");
        }
        if (lower.includes("timeline") || lower.includes("when")) {
          themes.push("timeline-oriented");
        }
      }
    });

    // Get unique themes and count occurrences
    const themeCounts = {};
    themes.forEach(theme => {
      themeCounts[theme] = (themeCounts[theme] || 0) + 1;
    });

    const sortedThemes = Object.entries(themeCounts)
      .sort((a, b) => b[1] - a[1])
      .map(([theme]) => theme);

    return {
      count: highRated.length,
      commonThemes: sortedThemes,
      averageRating: this._calculateAverageRating(highRated),
      examples: highRated.slice(0, 3).map(f => f.comment).filter(c => c && c.length > 10)
    };
  }

  _analyzeLowRatedFeedback(feedbacks) {
    const lowRated = feedbacks.filter(f => f.rating <= 2);
    
    const themes = [];

    lowRated.forEach(f => {
      if (f.comment && f.comment.length > 10) {
        const lower = f.comment.toLowerCase();
        
        // Detect common negative themes
        if (lower.includes("vague") || lower.includes("unclear")) {
          themes.push("too vague");
        }
        if (lower.includes("generic") || lower.includes("general")) {
          themes.push("too generic");
        }
        if (lower.includes("wrong") || lower.includes("inaccurate")) {
          themes.push("inaccurate");
        }
        if (lower.includes("confusing") || lower.includes("confused")) {
          themes.push("confusing");
        }
        if (lower.includes("not helpful") || lower.includes("useless")) {
          themes.push("not actionable");
        }
      }
    });

    const themeCounts = {};
    themes.forEach(theme => {
      themeCounts[theme] = (themeCounts[theme] || 0) + 1;
    });

    const sortedThemes = Object.entries(themeCounts)
      .sort((a, b) => b[1] - a[1])
      .map(([theme]) => theme);

    return {
      count: lowRated.length,
      commonThemes: sortedThemes,
      averageRating: this._calculateAverageRating(lowRated),
      examples: lowRated.slice(0, 3).map(f => f.comment).filter(c => c && c.length > 10)
    };
  }

  _analyzeMismatches(feedbacks) {
    const mismatches = feedbacks.filter(f => f.mismatchDetected);
    
    return {
      count: mismatches.length,
      percentage: mismatches.length / feedbacks.length,
      majorMismatches: mismatches.filter(f => f.mismatchSeverity === "major").length,
      minorMismatches: mismatches.filter(f => f.mismatchSeverity === "minor").length,
      examples: mismatches.slice(0, 3).map(f => ({
        rating: f.rating,
        sentiment: f.sentiment,
        comment: f.comment
      }))
    };
  }

  _calculateAverageRating(feedbacks) {
    if (feedbacks.length === 0) return 0;
    const sum = feedbacks.reduce((acc, f) => acc + f.rating, 0);
    return (sum / feedbacks.length).toFixed(2);
  }

  _calculatePositivePercentage(feedbacks) {
    const positive = feedbacks.filter(f => f.sentiment === "positive").length;
    return ((positive / feedbacks.length) * 100).toFixed(1);
  }

  _topKeywords(keywordMap, limit = 10) {
    return Object.entries(keywordMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
      .map(([word]) => word);
  }

  _isStopWord(word) {
    const stopWords = ["this", "that", "with", "from", "have", "more", "been", 
                       "were", "they", "than", "some", "very", "will", "just"];
    return stopWords.includes(word);
  }

  _generateEnhancementSummary(enhancements) {
    const high = enhancements.filter(e => e.priority === "high").length;
    const medium = enhancements.filter(e => e.priority === "medium").length;
    const low = enhancements.filter(e => e.priority === "low").length;

    return `Generated ${enhancements.length} prompt enhancements (${high} high priority, ${medium} medium, ${low} low)`;
  }

  _calculateConfidence(feedbackCount) {
    // Confidence increases with more feedback, caps at 0.95
    if (feedbackCount < 10) return 0.3;
    if (feedbackCount < 30) return 0.5;
    if (feedbackCount < 50) return 0.7;
    if (feedbackCount < 100) return 0.85;
    return 0.95;
  }
}

export default new FeedbackAnalyzer();

