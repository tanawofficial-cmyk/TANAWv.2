// backend/controller/authController.js
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import crypto from "crypto";
import User from "../models/User.js"; // 👈 make sure this import is here
import { sendPasswordResetEmail, sendPasswordResetConfirmationEmail } from "../services/emailService.js";

// REGISTER
export const registerUser = async (req, res) => {
  try {
    const { fullName, businessName, email, password, role } = req.body;

    // ✅ Check if user already exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: "User already exists"
      });
    }

    // ✅ Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // ✅ Create new user (admins validated by license key only at login)
    const user = new User({
      fullName,
      businessName,
      email,
      password: hashedPassword,
      role: role || "user"
    });

    await user.save();

    return res.status(201).json({
      success: true,
      message: "User registered successfully",
      data: {
        id: user._id,
        email: user.email,
        fullName: user.fullName,
        role: user.role
      }
    });
  } catch (err) {
    res.status(500).json({
      success: false,
      message: "Server error",
      error: err.message
    });
  }
};

// LOGIN
export const loginUser = async (req, res) => {
  try {
    const { email, password, loginType, licenseKey } = req.body;

    // ✅ Find user
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(400).json({ success: false, message: "Invalid credentials" });
    }

    // ✅ Check password
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(400).json({ success: false, message: "Invalid credentials" });
    }

    // ✅ Check license key if logging in as admin
    if (loginType === "admin") {
      if (licenseKey !== process.env.ADMIN_LICENSE_KEY) {
        return res.status(403).json({ success: false, message: "Invalid admin license key" });
      }
    }

    // ✅ Sign JWT
    const token = jwt.sign(
      { id: user._id, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: "1h" }
    );

    return res.json({
      success: true,
      message: "Login successful",
      data: {
        token,
        id: user._id,
        email: user.email,
        role: loginType === "admin" ? "admin" : "user",
        fullName: user.fullName,
        businessName: user.businessName
      }
    });
  } catch (err) {
    console.error("❌ Login error:", err);
    res.status(500).json({
      success: false,
      message: "Server error",
      error: err.message
    });
  }
};

// FORGOT PASSWORD
export const forgotPassword = async (req, res) => {
  try {
    const { email } = req.body;

    if (!email) {
      return res.status(400).json({
        success: false,
        message: "Email is required"
      });
    }

    // Find user by email
    const user = await User.findOne({ email: email.toLowerCase() });
    
    if (!user) {
      // For security, don't reveal if email exists or not
      return res.json({
        success: true,
        message: "If an account exists with this email, you will receive a password reset link shortly."
      });
    }

    // Generate reset token
    const resetToken = crypto.randomBytes(32).toString("hex");
    
    // Hash token before saving to database
    const hashedToken = crypto.createHash("sha256").update(resetToken).digest("hex");
    
    // Set token and expiry (1 hour from now)
    user.resetPasswordToken = hashedToken;
    user.resetPasswordExpires = Date.now() + 3600000; // 1 hour
    
    await user.save();

    // Send email with reset token
    try {
      await sendPasswordResetEmail(user.email, resetToken, user.businessName);
      
      console.log(`✅ Password reset token generated for: ${user.email}`);
      
      return res.json({
        success: true,
        message: "If an account exists with this email, you will receive a password reset link shortly."
      });
    } catch (emailError) {
      // If email fails, remove the token
      user.resetPasswordToken = null;
      user.resetPasswordExpires = null;
      await user.save();
      
      console.error("❌ Failed to send reset email:", emailError);
      return res.status(500).json({
        success: false,
        message: "Failed to send password reset email. Please try again later."
      });
    }
  } catch (err) {
    console.error("❌ Forgot password error:", err);
    res.status(500).json({
      success: false,
      message: "Server error",
      error: err.message
    });
  }
};

// RESET PASSWORD
export const resetPassword = async (req, res) => {
  try {
    const { token } = req.params;
    const { password } = req.body;

    if (!password) {
      return res.status(400).json({
        success: false,
        message: "New password is required"
      });
    }

    if (password.length < 6) {
      return res.status(400).json({
        success: false,
        message: "Password must be at least 6 characters long"
      });
    }

    // Hash the token from URL to compare with database
    const hashedToken = crypto.createHash("sha256").update(token).digest("hex");

    // Find user with valid token that hasn't expired
    const user = await User.findOne({
      resetPasswordToken: hashedToken,
      resetPasswordExpires: { $gt: Date.now() }
    });

    if (!user) {
      return res.status(400).json({
        success: false,
        message: "Password reset token is invalid or has expired"
      });
    }

    // Hash new password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Update password and clear reset token fields
    user.password = hashedPassword;
    user.resetPasswordToken = null;
    user.resetPasswordExpires = null;
    
    await user.save();

    // Send confirmation email
    try {
      await sendPasswordResetConfirmationEmail(user.email, user.businessName);
    } catch (emailError) {
      console.error("❌ Failed to send confirmation email:", emailError);
      // Continue anyway, password was successfully reset
    }

    console.log(`✅ Password successfully reset for: ${user.email}`);

    return res.json({
      success: true,
      message: "Password has been reset successfully. You can now log in with your new password."
    });
  } catch (err) {
    console.error("❌ Reset password error:", err);
    res.status(500).json({
      success: false,
      message: "Server error",
      error: err.message
    });
  }
};
