import express from "express";
import { submitFeedback, getAllFeedback } from "../controllers/feedbackController.js";
import { authMiddleware } from "../middleware/authMiddleware.js";


const router = express.Router();

// POST feedback (protected)
router.post("/", authMiddleware, submitFeedback);

// GET all feedback (admin only, protected)
router.get("/", authMiddleware, getAllFeedback);

export default router; // ✅ This is required for default import
