import React, { useState } from 'react';
import { X, Star, TrendingUp, BarChart3, Brain, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../api';

const FeedbackModal = ({ isOpen, onClose, onFeedbackSubmitted, datasetName }) => {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // AI-specific quality ratings
  const [chartQuality, setChartQuality] = useState(0);
  const [forecastAccuracy, setForecastAccuracy] = useState(0);
  const [insightsHelpfulness, setInsightsHelpfulness] = useState(0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (rating === 0) {
      toast.error('Please provide an overall rating');
      return;
    }

    setIsSubmitting(true);
    
    try {
      // Calculate average AI quality score
      const aiQualityScore = chartQuality > 0 || forecastAccuracy > 0 || insightsHelpfulness > 0
        ? ((chartQuality + forecastAccuracy + insightsHelpfulness) / 
           [chartQuality, forecastAccuracy, insightsHelpfulness].filter(r => r > 0).length)
        : 0;
      
      // Enhanced feedback with AI-specific metrics
      const enhancedMessage = feedback.trim() + 
        (datasetName ? `\n[Dataset: ${datasetName}]` : '') +
        (aiQualityScore > 0 ? `\n[AI Quality: ${aiQualityScore.toFixed(1)}/5]` : '') +
        (chartQuality > 0 ? `\n[Charts: ${chartQuality}/5]` : '') +
        (forecastAccuracy > 0 ? `\n[Forecasts: ${forecastAccuracy}/5]` : '') +
        (insightsHelpfulness > 0 ? `\n[Insights: ${insightsHelpfulness}/5]` : '');
      
      const response = await api.post('/feedback', {
        rating,
        message: enhancedMessage,
        type: 'ai_analytics_feedback'
      });

      console.log('📤 Feedback API response:', response);
      console.log('📤 Success check:', response?.success);

      if (response && response.success === true) {
        console.log('✅ Feedback submitted successfully');
        toast.success('Thank you for your valuable feedback! 🙏', {
          duration: 3000,
          icon: '✨'
        });
        onFeedbackSubmitted?.(rating, feedback);
        handleClose();
      } else {
        console.error('❌ Feedback API error:', response);
        toast.error('Failed to submit feedback. Please try again.');
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      toast.error('Failed to submit feedback. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setRating(0);
    setHoveredRating(0);
    setFeedback('');
    setChartQuality(0);
    setForecastAccuracy(0);
    setInsightsHelpfulness(0);
    onClose();
  };

  const handleStarClick = (starRating) => {
    setRating(starRating);
  };

  const handleStarHover = (starRating) => {
    setHoveredRating(starRating);
  };

  const handleStarLeave = () => {
    setHoveredRating(0);
  };

  if (!isOpen) return null;

  const RatingStars = ({ value, onChange, label, icon: Icon, color }) => (
    <div className="mb-4">
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`w-4 h-4 ${color}`} />
        <label className="text-sm font-medium text-gray-700">
          {label}
        </label>
      </div>
      <div className="flex space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => onChange(star)}
            className="focus:outline-none transition-transform hover:scale-110"
          >
            <Star
              className={`w-6 h-6 transition-colors ${
                star <= value
                  ? 'text-orange-400 fill-current'
                  : 'text-gray-300'
              }`}
            />
          </button>
        ))}
      </div>
      {value > 0 && (
        <p className="text-xs text-gray-500 mt-1">
          {value === 1 && 'Poor'} {value === 2 && 'Fair'} 
          {value === 3 && 'Good'} {value === 4 && 'Very Good'} 
          {value === 5 && 'Excellent'}
        </p>
      )}
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl relative my-8">
        {/* Close Button */}
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 p-2 hover:bg-gray-100 rounded-full transition-colors z-10"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>

        {/* Header */}
        <div className="p-6 pb-4 bg-gradient-to-r from-purple-600 to-blue-600 rounded-t-2xl">
          <div className="flex items-center gap-3 mb-2">
            <Brain className="w-8 h-8 text-white" />
            <h2 className="text-2xl font-bold text-white">
              Rate Our AI Analytics
            </h2>
          </div>
          <p className="text-purple-100 text-sm">
            Help us improve TANAW by sharing your experience
            {datasetName && ` with "${datasetName}"`}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="px-6 pb-6">
          {/* Overall Rating Section */}
          <div className="mb-6 pt-6">
            <label className="block text-base font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              Overall Experience
            </label>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex space-x-2 mb-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => handleStarClick(star)}
                    onMouseEnter={() => handleStarHover(star)}
                    onMouseLeave={handleStarLeave}
                    className="focus:outline-none transition-transform hover:scale-110"
                  >
                    <Star
                      className={`w-10 h-10 transition-colors ${
                        star <= (hoveredRating || rating)
                          ? 'text-orange-400 fill-current'
                          : 'text-gray-300'
                      }`}
                    />
                  </button>
                ))}
              </div>
              {rating > 0 && (
                <p className="text-sm text-gray-600 font-medium">
                  {rating === 1 && '⭐ Poor - Needs major improvement'}
                  {rating === 2 && '⭐⭐ Fair - Some issues to address'}
                  {rating === 3 && '⭐⭐⭐ Good - Meets expectations'}
                  {rating === 4 && '⭐⭐⭐⭐ Very Good - Exceeds expectations'}
                  {rating === 5 && '⭐⭐⭐⭐⭐ Excellent - Outstanding quality'}
                </p>
              )}
            </div>
          </div>

          {/* AI-Specific Quality Ratings */}
          <div className="mb-6 bg-blue-50 rounded-lg p-4 border border-blue-200">
            <h3 className="text-sm font-semibold text-blue-900 mb-4 flex items-center gap-2">
              <Brain className="w-4 h-4" />
              AI Analytics Quality (Optional)
            </h3>
            
            <RatingStars
              value={chartQuality}
              onChange={setChartQuality}
              label="Chart Relevance & Accuracy"
              icon={BarChart3}
              color="text-blue-600"
            />
            
            <RatingStars
              value={forecastAccuracy}
              onChange={setForecastAccuracy}
              label="Forecast Accuracy (Prophet AI)"
              icon={TrendingUp}
              color="text-green-600"
            />
            
            <RatingStars
              value={insightsHelpfulness}
              onChange={setInsightsHelpfulness}
              label="Business Insights Helpfulness"
              icon={CheckCircle}
              color="text-purple-600"
            />
          </div>

          {/* Text Feedback Section */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Additional Comments (Optional)
            </label>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Tell us more about your experience... What worked well? What could be improved?"
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 resize-none"
            />
            <p className="text-xs text-gray-500 mt-1">
              Your feedback helps us improve TANAW for everyone 🚀
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Maybe Later
            </button>
            <button
              type="submit"
              disabled={rating === 0 || isSubmitting}
              className="flex-1 px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105 font-medium shadow-lg"
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Submitting...
                </span>
              ) : (
                'Submit Feedback'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FeedbackModal;
