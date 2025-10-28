import express from "express";
import { submitFeedback, getAllFeedback } from "../controllers/feedbackController.js";
import {
  submitChartFeedback,
  getMyFeedback,
  getFeedbackForChart,
  getAllFeedback as getAllChartFeedback,
  deleteChartFeedback,
} from "../controllers/chartFeedbackController.js";
import { authMiddleware, authorizeAdmin } from "../middleware/authMiddleware.js";


const router = express.Router();

// General feedback routes (existing)
router.post("/", authMiddleware, submitFeedback);
router.get("/", authMiddleware, getAllFeedback);

// Chart-specific feedback routes (new)
router.post("/chart", authMiddleware, submitChartFeedback);
router.get("/my-feedback", authMiddleware, getMyFeedback);
router.get("/chart/:chartId", authMiddleware, getFeedbackForChart);
router.delete("/chart/:id", authMiddleware, deleteChartFeedback);

// Admin: Chart feedback analytics
router.get("/admin/all", authMiddleware, authorizeAdmin, getAllChartFeedback);

export default router; // ✅ This is required for default import
