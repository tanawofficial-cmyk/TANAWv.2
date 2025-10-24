import express from "express";
import { trackEvent, getAnalyticsData, getUserMetrics } from "../controllers/analyticsController.js";

const router = express.Router();

// Track analytics events
router.post("/track", trackEvent);

// Get analytics data for admin dashboard
router.get("/data", getAnalyticsData);

// Get user metrics
router.get("/users", getUserMetrics);

export default router;
