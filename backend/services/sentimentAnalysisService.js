import OpenAI from "openai";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

/**
 * Analyze sentiment of feedback comment
 * @param {string} comment - User feedback comment
 * @returns {Object} - { sentiment: 'positive'|'neutral'|'negative', score: -1 to 1, confidence: 0-1 }
 */
export const analyzeSentiment = async (comment) => {
  try {
    if (!comment || comment.trim().length === 0) {
      return {
        sentiment: "neutral",
        score: 0,
        confidence: 0,
      };
    }

    // Use OpenAI for sentiment analysis
    const response = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content: `You are a sentiment analysis expert. Analyze the sentiment of user feedback and respond ONLY with a JSON object in this exact format:
{
  "sentiment": "positive" | "neutral" | "negative",
  "score": <number between -1 and 1>,
  "confidence": <number between 0 and 1>,
  "reasoning": "<brief explanation>"
}

Rules:
- "positive": Comment expresses satisfaction, praise, or positive experience (score: 0.3 to 1.0)
- "neutral": Comment is factual, balanced, or mixed (score: -0.3 to 0.3)
- "negative": Comment expresses dissatisfaction, criticism, or negative experience (score: -1.0 to -0.3)
- Consider context, sarcasm, and nuance
- confidence: How certain you are about the sentiment (0.0 to 1.0)`,
        },
        {
          role: "user",
          content: comment,
        },
      ],
      temperature: 0.3,
      max_tokens: 150,
    });

    const result = JSON.parse(response.choices[0].message.content);

    return {
      sentiment: result.sentiment,
      score: result.score,
      confidence: result.confidence,
      reasoning: result.reasoning,
    };
  } catch (error) {
    console.error("❌ Sentiment analysis error:", error);

    // Fallback: Simple keyword-based sentiment analysis
    return simpleKeywordSentiment(comment);
  }
};

/**
 * Fallback sentiment analysis using keywords
 */
const simpleKeywordSentiment = (comment) => {
  const lowerComment = comment.toLowerCase();

  const positiveKeywords = [
    "good", "great", "excellent", "amazing", "helpful", "useful",
    "accurate", "love", "perfect", "wonderful", "fantastic", "awesome",
    "clear", "easy", "simple", "insightful", "valuable",
  ];

  const negativeKeywords = [
    "bad", "poor", "terrible", "awful", "useless", "wrong",
    "inaccurate", "hate", "confusing", "difficult", "hard",
    "unclear", "misleading", "incorrect", "error", "broken",
  ];

  let positiveCount = 0;
  let negativeCount = 0;

  positiveKeywords.forEach((word) => {
    if (lowerComment.includes(word)) positiveCount++;
  });

  negativeKeywords.forEach((word) => {
    if (lowerComment.includes(word)) negativeCount++;
  });

  const totalWords = comment.split(/\s+/).length;
  const score = (positiveCount - negativeCount) / Math.max(totalWords, 1);

  let sentiment = "neutral";
  if (score > 0.1) sentiment = "positive";
  else if (score < -0.1) sentiment = "negative";

  return {
    sentiment,
    score: Math.max(-1, Math.min(1, score * 5)), // Normalize to -1 to 1
    confidence: 0.6, // Lower confidence for keyword-based
    reasoning: "Fallback keyword-based analysis",
  };
};

/**
 * Detect mismatch between rating and sentiment
 * @param {number} rating - User rating (1-5)
 * @param {string} sentiment - Detected sentiment
 * @param {number} sentimentScore - Sentiment score (-1 to 1)
 * @returns {Object} - { mismatchDetected: boolean, severity: 'none'|'minor'|'major' }
 */
export const detectMismatch = (rating, sentiment, sentimentScore) => {
  // Expected sentiment based on rating
  let expectedSentiment;
  if (rating >= 4) expectedSentiment = "positive";
  else if (rating <= 2) expectedSentiment = "negative";
  else expectedSentiment = "neutral";

  // Check for mismatch
  const mismatchDetected = sentiment !== expectedSentiment;

  if (!mismatchDetected) {
    return { mismatchDetected: false, severity: "none" };
  }

  // Determine severity
  let severity = "minor";

  // Major mismatch: 5-star rating with negative comment
  if (rating === 5 && sentiment === "negative") {
    severity = "major";
  }
  // Major mismatch: 1-star rating with positive comment
  else if (rating === 1 && sentiment === "positive") {
    severity = "major";
  }
  // Major mismatch: 4-5 star with strong negative sentiment
  else if (rating >= 4 && sentimentScore < -0.5) {
    severity = "major";
  }
  // Major mismatch: 1-2 star with strong positive sentiment
  else if (rating <= 2 && sentimentScore > 0.5) {
    severity = "major";
  }

  return { mismatchDetected: true, severity };
};

export default { analyzeSentiment, detectMismatch };

