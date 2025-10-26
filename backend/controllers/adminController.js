// controllers/adminController.js

import User from "../models/User.js";
import Upload from "../models/Upload.js";
import Feedback from "../models/Feedback.js";
import Dataset from "../models/Dataset.js";
import { sendAccountDeletionEmail } from "../services/emailService.js";

/**
 * @desc    Get aggregated admin statistics for dashboard
 * @route   GET /api/admin/stats
 * @access  Private (Admin only)
 */
export const getAdminStats = async (req, res) => {
  try {
    // === USER STATISTICS ===
    const totalUsers = await User.countDocuments();
    const adminUsers = await User.countDocuments({ role: "admin" });
    const regularUsers = await User.countDocuments({ role: "user" });

    // === UPLOAD STATISTICS ===
    const totalUploads = await Upload.countDocuments();

    // === FEEDBACK STATISTICS ===
    const positiveFeedback = await Feedback.countDocuments({ type: "Positive" });
    const negativeFeedback = await Feedback.countDocuments({ type: "Negative" });
    const neutralFeedback = await Feedback.countDocuments({ type: "Neutral" });

    const avgRatingData = await Feedback.aggregate([
      { $group: { _id: null, avgRating: { $avg: "$rating" } } },
    ]);
    const avgRating = avgRatingData[0]?.avgRating || 0;

    // === FINAL STRUCTURED RESPONSE ===
    res.status(200).json({
      success: true,
      data: {
        users: {
          total: totalUsers,
          admins: adminUsers,
          regular: regularUsers,
        },
        uploads: {
          total: totalUploads,
        },
        feedback: {
          positive: positiveFeedback,
          neutral: neutralFeedback,
          negative: negativeFeedback,
          avgRating: parseFloat(avgRating.toFixed(2)),
        },
      },
    });
  } catch (error) {
    console.error("❌ Error fetching admin stats:", error);
    res.status(500).json({
      success: false,
      message: "Server Error: Unable to fetch admin stats",
      error: error.message,
    });
  }
};

/**
 * @desc    Get all users for Active Users page
 * @route   GET /api/admin/users
 * @access  Private (Admin only)
 */
export const getAllUsers = async (req, res) => {
  try {
    const users = await User.find().select("-password").sort({ createdAt: -1 });
    
    // Get dataset count for each user
    const usersWithDatasetCount = await Promise.all(
      users.map(async (user) => {
        const datasetCount = await Dataset.countDocuments({ ownerId: user._id });
        return {
          ...user.toObject(),
          datasetCount
        };
      })
    );
    
    res.status(200).json({ success: true, data: usersWithDatasetCount });
  } catch (error) {
    console.error("❌ Error fetching users:", error);
    res.status(500).json({ success: false, message: "Server Error" });
  }
};


/**
 * @desc    Delete user account
 * @route   DELETE /api/admin/users/:id
 * @access  Private (Admin only)
 */
export const deleteUser = async (req, res) => {
  try {
    const { id } = req.params;
    const user = await User.findById(id);

    if (!user) {
      return res.status(404).json({ success: false, message: "User not found" });
    }

    // Store user info before deletion for email
    const userEmail = user.email;
    const userName = user.fullName || user.businessName;

    // Delete the user
    await User.findByIdAndDelete(id);

    // Send notification email to deleted user
    try {
      await sendAccountDeletionEmail(userEmail, userName);
      console.log(`✅ Account deletion notification sent to: ${userEmail}`);
    } catch (emailError) {
      console.error("⚠️ Failed to send deletion notification email:", emailError);
      // Don't fail the request if email fails
    }

    res.status(200).json({
      success: true,
      message: "User deleted successfully and notification sent",
    });
  } catch (error) {
    console.error("❌ Error deleting user:", error);
    res.status(500).json({ success: false, message: "Server Error" });
  }
};

/**
 * @desc    Get all feedback for Feedback Analytics page
 * @route   GET /api/admin/feedback
 * @access  Private (Admin only)
 */
export const getAllFeedback = async (req, res) => {
  try {
    const feedback = await Feedback.find()
      .populate('userId', 'fullName email businessName')
      .sort({ date: -1 })
      .limit(100); // limit to recent 100 entries for performance
    res.status(200).json({ success: true, data: feedback });
  } catch (error) {
    console.error("❌ Error fetching feedback:", error);
    res.status(500).json({ success: false, message: "Server Error" });
  }
};

/**
 * @desc    Delete feedback entry
 * @route   DELETE /api/admin/feedback/:id
 * @access  Private (Admin only)
 */
export const deleteFeedback = async (req, res) => {
  try {
    const { id } = req.params;
    const deletedFeedback = await Feedback.findByIdAndDelete(id);

    if (!deletedFeedback) {
      return res.status(404).json({ success: false, message: "Feedback not found" });
    }

    res.status(200).json({
      success: true,
      message: "Feedback deleted successfully",
    });
  } catch (error) {
    console.error("❌ Error deleting feedback:", error);
    res.status(500).json({ success: false, message: "Server Error" });
  }
};
