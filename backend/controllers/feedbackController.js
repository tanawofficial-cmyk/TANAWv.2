import Feedback from "../models/Feedback.js";

// Submit feedback
export const submitFeedback = async (req, res) => {
  try {
    const { message, rating, type } = req.body;
    
    const feedback = new Feedback({
      userId: req.user.id,
      message,
      rating: rating || 5, // Default to 5 if not provided
      type: type || 'user_feedback',
    });

    await feedback.save();

    res.status(201).json({ success: true, message: "Feedback submitted successfully", feedback });
  } catch (err) {
    res.status(500).json({ success: false, message: "Server error", error: err.message });
  }
};

// Get all feedback
export const getAllFeedback = async (req, res) => {
  try {
    const feedbacks = await Feedback.find().populate("userId", "fullName email");
    res.json({ success: true, data: feedbacks });
  } catch (err) {
    res.status(500).json({ success: false, message: "Server error", error: err.message });
  }
};
