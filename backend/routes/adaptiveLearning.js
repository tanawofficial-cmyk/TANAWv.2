/**
 * Adaptive Learning Routes
 * 
 * Routes for adaptive learning and feedback analysis features
 * Part of Objective 3.3: Adaptive Learning & User Feedback
 */

import express from "express";
import { 
  getFeedbackPatterns, 
  getPromptEnhancements, 
  getLearningStatistics,
  testAdaptiveLearning
} from "../controllers/adaptiveLearningController.js";
import { authMiddleware } from "../middleware/authMiddleware.js";

const router = express.Router();

// Get feedback patterns for a domain
// GET /api/adaptive-learning/feedback-patterns?domain=sales
router.get("/feedback-patterns", authMiddleware, getFeedbackPatterns);

// Get prompt enhancement recommendations
// GET /api/adaptive-learning/prompt-enhancements?domain=sales
router.get("/prompt-enhancements", authMiddleware, getPromptEnhancements);

// Get learning statistics (admin)
// GET /api/adaptive-learning/statistics
router.get("/statistics", authMiddleware, getLearningStatistics);

// Test adaptive learning system
// GET /api/adaptive-learning/test
router.get("/test", authMiddleware, testAdaptiveLearning);

export default router;

