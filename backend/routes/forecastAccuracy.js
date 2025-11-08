/**
 * Forecast Accuracy Routes
 * 
 * Routes for forecast accuracy tracking and parameter optimization
 * Part of Objective 3.3: Adaptive Learning & User Feedback - Phase 2
 */

import express from "express";
import {
  createForecastRecord,
  submitActualValue,
  getPendingForecasts,
  getForecastHistory,
  getOptimizedParameters,
  getAccuracyStatistics,
  getForecastsNeedingReminders,
  markReminderSent,
  deleteForecast
} from "../controllers/forecastAccuracyController.js";
import { authMiddleware } from "../middleware/authMiddleware.js";

const router = express.Router();

// Create forecast record (called by Flask - no auth needed for inter-service communication)
// POST /api/forecast-accuracy/create
router.post("/create", createForecastRecord);

// Submit actual value for a forecast
// POST /api/forecast-accuracy/submit-actual
router.post("/submit-actual", authMiddleware, submitActualValue);

// Get pending forecasts (waiting for actual values)
// GET /api/forecast-accuracy/pending
router.get("/pending", authMiddleware, getPendingForecasts);

// Get forecast history
// GET /api/forecast-accuracy/history?forecastType=sales&domain=sales&status=completed&limit=50
router.get("/history", authMiddleware, getForecastHistory);

// Get optimized parameters for forecasting
// GET /api/forecast-accuracy/optimized-parameters?forecastType=sales&domain=sales
router.get("/optimized-parameters", authMiddleware, getOptimizedParameters);

// Get accuracy statistics
// GET /api/forecast-accuracy/statistics
router.get("/statistics", authMiddleware, getAccuracyStatistics);

// Get forecasts needing reminders
// GET /api/forecast-accuracy/reminders?daysThreshold=30
router.get("/reminders", authMiddleware, getForecastsNeedingReminders);

// Mark reminder as sent
// POST /api/forecast-accuracy/mark-reminder-sent
router.post("/mark-reminder-sent", authMiddleware, markReminderSent);

// Delete a forecast record
// DELETE /api/forecast-accuracy/:id
router.delete("/:id", authMiddleware, deleteForecast);

export default router;

