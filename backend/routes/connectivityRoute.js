// routes/connectivityRoute.js

import express from "express";
import {
  getSystemStatus,
  getApiMetrics,
  getDatabaseStats,
  getPerformanceMetrics,
} from "../controllers/connectivityController.js";
import { authMiddleware } from "../middleware/authMiddleware.js";

const router = express.Router();

// Apply authentication middleware to all connectivity routes
router.use(authMiddleware);

/**
 * ===========================
 * System Connectivity Status
 * ===========================
 */

// Get overall system status
// GET /api/admin/connectivity/status
router.get("/status", getSystemStatus);

/**
 * ===========================
 * API Usage Metrics
 * ===========================
 */

// Get API usage metrics
// GET /api/admin/connectivity/api-metrics?period=7d
router.get("/api-metrics", getApiMetrics);

/**
 * ===========================
 * Database Statistics
 * ===========================
 */

// Get database statistics
// GET /api/admin/connectivity/database-stats
router.get("/database-stats", getDatabaseStats);

/**
 * ===========================
 * Performance Metrics
 * ===========================
 */

// Get performance metrics
// GET /api/admin/connectivity/performance
router.get("/performance", getPerformanceMetrics);

export default router;

