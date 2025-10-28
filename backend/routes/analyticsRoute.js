import express from "express";
import { trackEvent, getAnalyticsData, getUserMetrics } from "../controllers/analyticsController.js";
import { authMiddleware, authorizeAdmin } from "../middleware/authMiddleware.js";

const router = express.Router();

// Track analytics events (public - no auth needed for tracking)
router.post("/track", trackEvent);

// Get analytics data for admin dashboard (ADMIN ONLY)
router.get("/data", authMiddleware, authorizeAdmin, getAnalyticsData);

// Get user metrics (ADMIN ONLY)
router.get("/users", authMiddleware, authorizeAdmin, getUserMetrics);

export default router;
