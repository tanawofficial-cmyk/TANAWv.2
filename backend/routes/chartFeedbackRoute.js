import express from "express";
import {
  submitChartFeedback,
  getMyFeedback,
  getFeedbackForChart,
  getAllFeedback,
  deleteChartFeedback,
} from "../controllers/chartFeedbackController.js";
import { authMiddleware, authorizeAdmin } from "../middleware/authMiddleware.js";

const router = express.Router();

// User routes (require authentication)
router.post("/chart", authMiddleware, submitChartFeedback);
router.get("/my-feedback", authMiddleware, getMyFeedback);
router.get("/chart/:chartId", authMiddleware, getFeedbackForChart);
router.delete("/:id", authMiddleware, deleteChartFeedback);

// Admin routes (require authentication AND admin authorization)
router.get("/all", authMiddleware, authorizeAdmin, getAllFeedback);

export default router;

