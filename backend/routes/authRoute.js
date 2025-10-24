//backend/route/authRoutes.js
import express from "express";
import { registerUser, loginUser, forgotPassword, resetPassword } from "../controllers/authController.js";
import axios from "axios";

const router = express.Router();

// REGISTER with reCAPTCHA
router.post("/register", async (req, res) => {
  const { fullName, businessName, email, password, role, licenseKey, captchaToken } = req.body;

  if (!captchaToken) {
    return res.status(400).json({ success: false, message: "No captcha token provided" });
  }

  try {
    const params = new URLSearchParams();
    params.append("secret", process.env.RECAPTCHA_SECRET_KEY);
    params.append("response", captchaToken);

    const { data } = await axios.post(
      "https://www.google.com/recaptcha/api/siteverify",
      params.toString(),
      { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
    );

    console.log("reCAPTCHA verify response (register):", data);

    if (!data.success) {
      return res.status(400).json({ success: false, message: "Captcha verification failed", errors: data["error-codes"] });
    }

    return registerUser(req, res);

  } catch (err) {
    res.status(500).json({ success: false, message: "Server error", error: err.message });
  }
});

// LOGIN with reCAPTCHA
router.post("/login", async (req, res) => {
  const { captchaToken } = req.body;

  if (!captchaToken) {
    return res.status(400).json({ success: false, message: "No captcha token provided" });
  }

  try {
    const params = new URLSearchParams();
    params.append("secret", process.env.RECAPTCHA_SECRET_KEY);
    params.append("response", captchaToken);

    const { data } = await axios.post(
      "https://www.google.com/recaptcha/api/siteverify",
      params.toString(),
      { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
    );

    console.log("reCAPTCHA verify response (login):", data);

    if (!data.success) {
      return res.status(400).json({
        success: false,
        message: "Captcha verification failed",
        errors: data["error-codes"]
      });
    }

    return loginUser(req, res);
  } catch (err) {
    res.status(500).json({
      success: false,
      message: "Server error",
      error: err.message
    });
  }
});

// FORGOT PASSWORD (no captcha needed)
router.post("/forgot-password", forgotPassword);

// ADMIN LOGIN (no captcha needed)
router.post("/admin-login", async (req, res) => {
  const { email, password, licenseKey } = req.body;

  // Validate license key
  if (!licenseKey || licenseKey !== process.env.ADMIN_LICENSE_KEY) {
    return res.status(400).json({ 
      success: false, 
      message: "Invalid admin license key" 
    });
  }

  // Add role to request body for admin login
  req.body.role = "admin";
  
  return loginUser(req, res);
});

// RESET PASSWORD (no captcha needed)
router.post("/reset-password/:token", resetPassword);

export default router;
