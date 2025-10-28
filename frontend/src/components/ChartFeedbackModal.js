import React, { useState } from "react";
import ReactDOM from "react-dom";
import api from "../api";
import toast from "react-hot-toast";

const ChartFeedbackModal = ({ isOpen, onClose, chart, datasetId, onFeedbackSubmitted }) => {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (rating === 0) {
      toast.error("Please select a rating");
      return;
    }

    // Comment is optional, but if provided, must be at least 5 characters
    if (comment && comment.trim().length > 0 && comment.trim().length < 5) {
      toast.error("Comment must be at least 5 characters if provided");
      return;
    }

    setIsSubmitting(true);

    try {
      // Generate chartId from title if not available
      const chartId = chart.id || chart.title?.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
      
      // Debug: Log what we're sending
      console.log("📤 Submitting feedback:", {
        datasetId,
        chartId,
        chartTitle: chart.title,
        rating,
        hasComment: !!comment,
        chart,
      });
      
      const response = await api.post("/feedback/chart", {
        datasetId,
        chartId,
        chartTitle: chart.title,
        rating,
        comment: comment.trim() || "", // Empty string if no comment
      });

      if (response.success) {
        // Always show success - mismatch detection is for admin analytics only
        toast.success("✅ Thank you for your feedback!");
        
        // Reset form
        setRating(0);
        setComment("");
        
        // Notify parent
        if (onFeedbackSubmitted) {
          onFeedbackSubmitted(response.data);
        }
        
        // Close modal after short delay
        setTimeout(() => {
          onClose();
        }, 1000);
      }
    } catch (error) {
      console.error("❌ Error submitting feedback:", error);
      toast.error(error.message || "Failed to submit feedback");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setRating(0);
    setComment("");
    onClose();
  };

  return ReactDOM.createPortal(
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-[9999] p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                💬 Rate This Chart
              </h2>
              <p className="text-sm text-gray-600">
                <span className="font-semibold text-blue-600">{chart?.title || "Chart"}</span>
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Your feedback helps us improve analytics quality
              </p>
            </div>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600 transition p-2 rounded-lg hover:bg-gray-100"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Rating Section */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                How would you rate this chart's usefulness?
              </label>
              <div className="flex items-center gap-2 mb-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    onMouseEnter={() => setHoveredRating(star)}
                    onMouseLeave={() => setHoveredRating(0)}
                    className="transition-transform hover:scale-110 focus:outline-none"
                  >
                    <svg
                      className={`w-12 h-12 ${
                        star <= (hoveredRating || rating)
                          ? "text-yellow-400 fill-current"
                          : "text-gray-300"
                      } transition-colors`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="1"
                        d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                      />
                    </svg>
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-500">
                {rating === 0 && "Click to rate"}
                {rating === 1 && "1⭐ - Not useful at all"}
                {rating === 2 && "2⭐ - Somewhat useful"}
                {rating === 3 && "3⭐ - Moderately useful"}
                {rating === 4 && "4⭐ - Very useful"}
                {rating === 5 && "5⭐ - Extremely useful"}
              </p>
            </div>

            {/* Comment Section */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Share your thoughts about this chart
              </label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Tell us what you think about this chart's accuracy, clarity, or usefulness... (Optional)"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                rows="5"
                maxLength={1000}
              />
              <div className="flex items-center justify-between mt-2">
                <p className="text-xs text-gray-500">
                  Optional (minimum 5 characters if provided)
                </p>
                <p className="text-xs text-gray-500">
                  {comment.length}/1000
                </p>
              </div>
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <span className="text-2xl">🤖</span>
                <div className="flex-1">
                  <h4 className="text-sm font-semibold text-blue-900 mb-1">
                    AI-Powered Sentiment Analysis
                  </h4>
                  <p className="text-xs text-blue-700">
                    We use AI to analyze your feedback sentiment and detect potential rating/comment mismatches. 
                    This helps maintain feedback quality and authenticity.
                  </p>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 pt-4">
              <button
                type="button"
                onClick={handleClose}
                disabled={isSubmitting}
                className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting || rating === 0 || (comment.trim().length > 0 && comment.trim().length < 5)}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
              >
                {isSubmitting ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Submitting...
                  </span>
                ) : (
                  "Submit Feedback"
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>,
    document.body
  );
};

export default ChartFeedbackModal;

