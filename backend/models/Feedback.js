import mongoose from "mongoose";

const feedbackSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  message: { type: String, required: true },
  rating: { type: Number, min: 1, max: 5, required: true },
  type: { type: String, enum: ['user_feedback', 'bug_report', 'feature_request'], default: 'user_feedback' },
  date: { type: Date, default: Date.now },
});

export default mongoose.model("Feedback", feedbackSchema); // ✅ default export
