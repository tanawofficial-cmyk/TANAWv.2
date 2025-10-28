import mongoose from "mongoose";

const chartFeedbackSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
    },
    datasetId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Dataset",
      required: true,
    },
    chartId: {
      type: String,
      required: true, // e.g., "product_comparison_analysis", "sales_forecast"
    },
    chartTitle: {
      type: String,
      required: true, // e.g., "Product Comparison by Sales"
    },
    rating: {
      type: Number,
      required: true,
      min: 1,
      max: 5,
    },
    comment: {
      type: String,
      required: false, // Optional - users can submit rating-only feedback
      default: "",
      maxLength: 1000,
    },
    sentiment: {
      type: String,
      enum: ["positive", "neutral", "negative"],
      required: true,
    },
    sentimentScore: {
      type: Number, // -1 to 1 (negative to positive)
      required: true,
    },
    mismatchDetected: {
      type: Boolean,
      default: false, // True if rating and sentiment don't match
    },
    mismatchSeverity: {
      type: String,
      enum: ["none", "minor", "major"],
      default: "none",
    },
  },
  { timestamps: true }
);

// Index for efficient queries
chartFeedbackSchema.index({ userId: 1, datasetId: 1 });
chartFeedbackSchema.index({ chartId: 1 });
chartFeedbackSchema.index({ createdAt: -1 });
chartFeedbackSchema.index({ sentiment: 1 });
chartFeedbackSchema.index({ mismatchDetected: 1 });

const ChartFeedback = mongoose.model("ChartFeedback", chartFeedbackSchema);

export default ChartFeedback;

