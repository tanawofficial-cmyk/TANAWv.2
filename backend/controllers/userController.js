// backend/controllers/userController.js
import User from "../models/User.js";
import bcrypt from "bcryptjs";
import crypto from "crypto";
import { sendEmailChangeVerificationEmail, sendEmailChangeNotificationEmail } from "../services/emailService.js";

// Get all users (admin use case)
export const getAllUsers = async (req, res) => {
  try {
    const users = await User.find().select("-password");
    res.json({ success: true, data: users });
  } catch (err) {
    res.status(500).json({ success: false, message: "Server error", error: err.message });
  }
};

// Get logged-in user profile
export const getMe = async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select("-password");
    if (!user) {
      return res.status(404).json({ success: false, message: "User not found" });
    }
    res.json({ success: true, data: user });
  } catch (err) {
    res.status(500).json({ success: false, message: "Server error", error: err.message });
  }
};

// Update user profile (fullName and businessName only)
export const updateProfile = async (req, res) => {
  try {
    const { fullName, businessName, email } = req.body;
    const userId = req.user.id;

    // Find the user
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ success: false, message: "User not found" });
    }

    // If email is being changed, handle verification flow
    if (email && email.toLowerCase() !== user.email.toLowerCase()) {
      // Check if new email is already in use
      const existingUser = await User.findOne({ email: email.toLowerCase() });
      if (existingUser) {
        return res.status(400).json({ 
          success: false, 
          message: "Email already in use by another account" 
        });
      }

      // Generate verification token
      const verificationToken = crypto.randomBytes(32).toString('hex');
      const tokenExpiry = Date.now() + 24 * 60 * 60 * 1000; // 24 hours

      // Save pending email and token
      user.pendingEmail = email.toLowerCase();
      user.emailVerificationToken = verificationToken;
      user.emailVerificationExpires = tokenExpiry;

      await user.save();

      // Send verification email
      try {
        await sendEmailChangeVerificationEmail(email, verificationToken, user.fullName || user.businessName);
        
        return res.json({ 
          success: true, 
          message: "Verification email sent! Please check your new email to confirm the change.",
          emailVerificationRequired: true,
          pendingEmail: email
        });
      } catch (emailError) {
        console.error("❌ Error sending verification email:", emailError);
        return res.status(500).json({ 
          success: false, 
          message: "Failed to send verification email. Please try again." 
        });
      }
    }

    // Update other fields (fullName, businessName)
    if (fullName) user.fullName = fullName;
    if (businessName) user.businessName = businessName;

    await user.save();

    // Return updated user without password
    const updatedUser = await User.findById(userId).select("-password");
    
    res.json({ 
      success: true, 
      message: "Profile updated successfully",
      data: updatedUser 
    });
  } catch (err) {
    console.error("❌ Update profile error:", err);
    res.status(500).json({ 
      success: false, 
      message: "Server error", 
      error: err.message 
    });
  }
};

// Verify email change
export const verifyEmailChange = async (req, res) => {
  try {
    const { token } = req.params;

    // Find user with this verification token
    const user = await User.findOne({
      emailVerificationToken: token,
      emailVerificationExpires: { $gt: Date.now() }
    });

    if (!user) {
      return res.status(400).json({ 
        success: false, 
        message: "Invalid or expired verification token" 
      });
    }

    // Store old email for notification
    const oldEmail = user.email;
    const newEmail = user.pendingEmail;

    // Update email
    user.email = newEmail;
    user.pendingEmail = null;
    user.emailVerificationToken = null;
    user.emailVerificationExpires = null;

    await user.save();

    // Send notification to old email
    try {
      await sendEmailChangeNotificationEmail(oldEmail, user.fullName || user.businessName, newEmail);
    } catch (emailError) {
      console.error("⚠️ Failed to send notification to old email:", emailError);
      // Don't fail the request if notification fails
    }

    res.json({ 
      success: true, 
      message: "Email address successfully verified and updated!",
      newEmail: newEmail
    });
  } catch (err) {
    console.error("❌ Email verification error:", err);
    res.status(500).json({ 
      success: false, 
      message: "Server error", 
      error: err.message 
    });
  }
};

// Change password
export const changePassword = async (req, res) => {
  try {
    const { currentPassword, newPassword } = req.body;
    const userId = req.user.id;

    // Validate inputs
    if (!currentPassword || !newPassword) {
      return res.status(400).json({ 
        success: false, 
        message: "Current password and new password are required" 
      });
    }

    if (newPassword.length < 6) {
      return res.status(400).json({ 
        success: false, 
        message: "New password must be at least 6 characters long" 
      });
    }

    // Find user
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ success: false, message: "User not found" });
    }

    // Verify current password
    const isMatch = await bcrypt.compare(currentPassword, user.password);
    if (!isMatch) {
      return res.status(400).json({ 
        success: false, 
        message: "Current password is incorrect" 
      });
    }

    // Hash new password
    const hashedPassword = await bcrypt.hash(newPassword, 10);
    user.password = hashedPassword;
    await user.save();

    res.json({ 
      success: true, 
      message: "Password changed successfully" 
    });
  } catch (err) {
    console.error("❌ Change password error:", err);
    res.status(500).json({ 
      success: false, 
      message: "Server error", 
      error: err.message 
    });
  }
};
