// routes/adminRoute.js

import express from "express";
import {
  getAdminStats,
  getAllUsers,
  deleteUser,
  getAllFeedback,
  deleteFeedback,
} from "../controllers/adminController.js";
import { authMiddleware } from "../middleware/authMiddleware.js";

const router = express.Router();

// Apply authentication middleware to all admin routes
router.use(authMiddleware);

/**
 * ===========================
 * Admin Overview Dashboard
 * ===========================
 * GET /api/admin/stats
 */
router.get("/stats", getAdminStats);

/**
 * ===========================
 * Active Users Management
 * ===========================
 */

// Get all users
// GET /api/admin/users
router.get("/users", getAllUsers);


// Delete user
// DELETE /api/admin/users/:id
router.delete("/users/:id", deleteUser);

/**
 * ===========================
 * User Feedback Analytics
 * ===========================
 */

// Get all feedback
// GET /api/admin/feedback
router.get("/feedback", getAllFeedback);

// Delete feedback
// DELETE /api/admin/feedback/:id
router.delete("/feedback/:id", deleteFeedback);

export default router;
