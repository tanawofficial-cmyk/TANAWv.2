import express from "express";
import {
  submitContactForm,
  getAllContactMessages,
  updateContactStatus,
  deleteContactMessage,
  getContactStats
} from "../controllers/contactController.js";
import { authMiddleware, authorizeAdmin } from "../middleware/authMiddleware.js";

const router = express.Router();

// Public route - Submit contact form
router.post("/", submitContactForm);

// Admin routes - Protected
router.get("/", authMiddleware, authorizeAdmin, getAllContactMessages);
router.get("/stats", authMiddleware, authorizeAdmin, getContactStats);
router.put("/:id", authMiddleware, authorizeAdmin, updateContactStatus);
router.delete("/:id", authMiddleware, authorizeAdmin, deleteContactMessage);

export default router;

