//backend/route/user.js
import express from "express";
import { getAllUsers, getMe, updateProfile, changePassword, verifyEmailChange } from "../controllers/userController.js";
import { authMiddleware } from "../middleware/authMiddleware.js";

const router = express.Router();

// GET /api/users -> get all users (admin only, still needs role check later)
router.get("/", authMiddleware, getAllUsers);

// GET /api/users/me -> get current logged-in user profile
router.get("/me", authMiddleware, getMe);

// PUT /api/users/me -> update current user profile
router.put("/me", authMiddleware, updateProfile);

// PUT /api/users/change-password -> change current user password
router.put("/change-password", authMiddleware, changePassword);

// GET /api/users/verify-email/:token -> verify email change
router.get("/verify-email/:token", verifyEmailChange);

export default router;
