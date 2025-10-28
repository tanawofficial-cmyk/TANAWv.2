// routes/migrationRoute.js - One-time data migration endpoints

import express from "express";
import { fixUserCounts, cleanupOrphanedFiles } from "../controllers/migrationController.js";
import { authMiddleware, authorizeAdmin } from "../middleware/authMiddleware.js";

const router = express.Router();

// Apply authentication AND admin authorization to all migration routes
router.use(authMiddleware);
router.use(authorizeAdmin);

/**
 * ===========================
 * Data Migration Endpoints
 * ===========================
 * These should only be run once after deploying fixes
 */

// Fix user dataset/chart counts
// POST /api/admin/migrate/fix-user-counts
router.post("/fix-user-counts", fixUserCounts);

// Clean up orphaned files
// POST /api/admin/migrate/cleanup-orphaned-files
router.post("/cleanup-orphaned-files", cleanupOrphanedFiles);

export default router;

