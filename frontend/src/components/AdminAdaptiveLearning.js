/**
 * Admin Adaptive Learning Dashboard
 * 
 * Admin view to monitor system-wide learning, feedback patterns, and accuracy metrics
 * Part of Objective 3.3: Adaptive Learning & User Feedback - Admin Side
 */

import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import api from '../api';

const AdminAdaptiveLearning = () => {
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'feedback', 'forecasts'
  const [loading, setLoading] = useState(true);
  
  // Data states
  const [learningStats, setLearningStats] = useState(null);
  const [feedbackPatterns, setFeedbackPatterns] = useState(null);
  const [accuracyStats, setAccuracyStats] = useState(null);
  const [allFeedback, setAllFeedback] = useState([]);
  const [allForecasts, setAllForecasts] = useState([]);
  
  // Filter states
  const [selectedDomain, setSelectedDomain] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch learning statistics
      const learningRes = await api.get(
        "/adaptive-learning/statistics",
        { headers }
      );

      // Fetch feedback patterns
      const feedbackRes = await api.get(
        "/adaptive-learning/feedback-patterns?domain=all",
        { headers }
      );

      // Fetch accuracy statistics
      const accuracyRes = await api.get(
        "/forecast-accuracy/statistics",
        { headers }
      );

      // Fetch all feedback (admin endpoint)
      const allFeedbackRes = await api.get(
        "/feedback/admin/all",
        { headers }
      );

      if (learningRes.success) {
        setLearningStats(learningRes.data);
      }

      if (feedbackRes.success) {
        setFeedbackPatterns({ ...feedbackRes.data, success: true });
      } else {
        setFeedbackPatterns({ ...(feedbackRes.data || {}), success: false, message: feedbackRes.message });
      }

      if (accuracyRes.success) {
        setAccuracyStats(accuracyRes.data);
      }

      if (allFeedbackRes.success) {
        setAllFeedback(allFeedbackRes.data || []);
      }

    } catch (error) {
      console.error('Error fetching adaptive learning data:', error);
      toast.error('Failed to load adaptive learning data');
    } finally {
      setLoading(false);
    }
  };

  const formatPercentage = (value) => {
    return `${parseFloat(value || 0).toFixed(1)}%`;
  };

  const getStatusColor = (status) => {
    if (status === 'excellent') return 'text-green-600 bg-green-100';
    if (status === 'good') return 'text-blue-600 bg-blue-100';
    if (status === 'fair') return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getLearningStatus = (feedbackCount, completedForecasts) => {
    const hasEnoughFeedback = feedbackCount >= 10;
    const hasEnoughForecasts = completedForecasts >= 10;

    if (hasEnoughFeedback && hasEnoughForecasts) {
      return { label: 'Fully Active', color: 'green', icon: '✅' };
    } else if (hasEnoughFeedback || hasEnoughForecasts) {
      return { label: 'Partially Active', color: 'blue', icon: '🔵' };
    } else {
      return { label: 'Collecting Data', color: 'gray', icon: '⏰' };
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-12">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const learningStatus = getLearningStatus(
    learningStats?.totalFeedback || 0,
    accuracyStats?.completedForecasts || 0
  );

  return (
    <div className="admin-adaptive-learning p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-lg">
            <span className="text-white text-3xl">🧠</span>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-800">
              Adaptive Learning System
            </h1>
            <p className="text-gray-600 mt-1">
              Monitor how the AI learns from user feedback and forecast accuracy
            </p>
          </div>
        </div>

        {/* System Status Banner */}
        <div className={`border-2 rounded-lg p-4 ${
          learningStatus.color === 'green' ? 'bg-green-50 border-green-300' :
          learningStatus.color === 'blue' ? 'bg-blue-50 border-blue-300' :
          'bg-gray-50 border-gray-300'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-3xl">{learningStatus.icon}</span>
              <div>
                <h3 className="font-bold text-gray-800">
                  Learning Status: {learningStatus.label}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  {learningStats?.totalFeedback || 0} feedback entries • {accuracyStats?.completedForecasts || 0} completed forecasts
                </p>
              </div>
            </div>
            <button
              onClick={fetchAllData}
              className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition relative z-10 cursor-pointer"
              style={{ pointerEvents: 'auto' }}
            >
              🔄 Refresh Data
            </button>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-6 bg-white p-2 rounded-lg border border-gray-200 shadow-sm relative z-10">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex-1 px-6 py-3 rounded-lg font-medium transition relative z-10 cursor-pointer ${
            activeTab === 'overview'
              ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md'
              : 'text-gray-700 hover:bg-gray-100'
          }`}
          style={{ pointerEvents: 'auto' }}
        >
          📊 System Overview
        </button>
        <button
          onClick={() => setActiveTab('feedback')}
          className={`flex-1 px-6 py-3 rounded-lg font-medium transition relative z-10 cursor-pointer ${
            activeTab === 'feedback'
              ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md'
              : 'text-gray-700 hover:bg-gray-100'
          }`}
          style={{ pointerEvents: 'auto' }}
        >
          💬 Feedback Analysis
        </button>
        <button
          onClick={() => setActiveTab('forecasts')}
          className={`flex-1 px-6 py-3 rounded-lg font-medium transition relative z-10 cursor-pointer ${
            activeTab === 'forecasts'
              ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md'
              : 'text-gray-700 hover:bg-gray-100'
          }`}
          style={{ pointerEvents: 'auto' }}
        >
          🎯 Forecast Accuracy
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Empty State */}
          {(!learningStats || learningStats.totalFeedback === 0) && (!accuracyStats || accuracyStats.completedForecasts === 0) ? (
            <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
              <span className="text-6xl mb-4 block">🧠</span>
              <h3 className="text-2xl font-bold text-gray-800 mb-2">
                Adaptive Learning System Ready
              </h3>
              <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
                The system is active and waiting for data! As users upload datasets and provide feedback, 
                you'll see learning metrics, patterns, and accuracy statistics appear here.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto text-left">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <h4 className="font-bold text-blue-900 mb-3 flex items-center gap-2">
                    📊 To See Forecast Data:
                  </h4>
                  <ol className="text-sm text-gray-700 space-y-2">
                    <li>1. Users upload datasets with Date + Sales columns</li>
                    <li>2. System generates forecasts automatically</li>
                    <li>3. Users submit actual values in Adaptive Learning page</li>
                    <li>4. Accuracy metrics appear here!</li>
                  </ol>
                </div>
                
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                  <h4 className="font-bold text-purple-900 mb-3 flex items-center gap-2">
                    💬 To See Feedback Data:
                  </h4>
                  <ol className="text-sm text-gray-700 space-y-2">
                    <li>1. Users view AI insights on charts</li>
                    <li>2. Users click 👍 or 👎 buttons</li>
                    <li>3. Users write optional comments</li>
                    <li>4. Feedback patterns appear here!</li>
                  </ol>
                </div>
              </div>

              <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg max-w-2xl mx-auto">
                <p className="text-sm text-yellow-900">
                  💡 <strong>Tip for Demo:</strong> Have users submit 3-5 feedbacks and 1-2 actual forecast values 
                  before the defense to show this dashboard populated with real data!
                </p>
              </div>
            </div>
          ) : (
            <>
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Total Feedback */}
                <div className="bg-white border border-gray-200 rounded-lg p-5">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm text-gray-600">Total Feedback</p>
                    <span className="text-2xl">💬</span>
              </div>
              <p className="text-3xl font-bold text-gray-800">
                {learningStats?.totalFeedback || 0}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                Avg Rating: {learningStats?.averageRating || 'N/A'}
              </p>
            </div>

            {/* Learning Status */}
            <div className="bg-white border border-gray-200 rounded-lg p-5">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">Learning Status</p>
                <span className="text-2xl">🧠</span>
              </div>
              <p className="text-2xl font-bold text-gray-800">
                {learningStatus.label}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                {learningStats?.learningEnabled ? 'AI is learning' : 'Collecting data'}
              </p>
            </div>

            {/* Total Forecasts */}
            <div className="bg-white border border-gray-200 rounded-lg p-5">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">Total Forecasts</p>
                <span className="text-2xl">📈</span>
              </div>
              <p className="text-3xl font-bold text-gray-800">
                {accuracyStats?.totalForecasts || 0}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                {accuracyStats?.completedForecasts || 0} completed
              </p>
            </div>

            {/* Avg Accuracy */}
            <div className="bg-white border border-gray-200 rounded-lg p-5">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">System Accuracy</p>
                <span className="text-2xl">🎯</span>
              </div>
              <p className="text-3xl font-bold text-gray-800">
                {accuracyStats?.accuracyByType?.sales?.averageAccuracy || 'N/A'}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                Average across all users
              </p>
            </div>
          </div>

          {/* Learning by Domain */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              📊 Learning Progress by Domain
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {learningStats?.byDomain && Object.entries(learningStats.byDomain).map(([domain, data]) => (
                <div key={domain} className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-700 capitalize mb-2">
                    {domain === 'sales' && '💰 Sales'}
                    {domain === 'inventory' && '📦 Inventory'}
                    {domain === 'finance' && '💵 Finance'}
                    {domain === 'customer' && '👥 Customer'}
                    {domain === 'product' && '📦 Product'}
                  </h4>
                  <p className="text-2xl font-bold text-gray-800 mb-1">
                    {data.feedbackCount || 0}
                  </p>
                  <p className="text-xs text-gray-600">
                    {data.hasLearningData ? (
                      <span className="text-green-600">✅ Active</span>
                    ) : (
                      <span className="text-gray-500">⏰ Collecting</span>
                    )}
                  </p>
                  {data.averageRating && (
                    <p className="text-sm text-gray-700 mt-2">
                      Avg: {data.averageRating}⭐
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* How Users Are Contributing */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">
              🎯 How Users Are Helping the System Learn
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium text-gray-700 mb-2">💬 Feedback Contribution</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Users rate charts (1-5 stars)</li>
                  <li>• Provide comments on recommendations</li>
                  <li>• System analyzes patterns automatically</li>
                  <li>• OpenAI prompts improve based on feedback</li>
                  <li className="font-medium text-blue-700 mt-2">
                    ✅ {learningStats?.totalFeedback || 0} feedback entries collected
                  </li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-gray-700 mb-2">📈 Forecast Contribution</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Users provide actual values after 30 days</li>
                  <li>• System calculates forecast accuracy (MAPE)</li>
                  <li>• Prophet parameters auto-optimize</li>
                  <li>• Predictions become more accurate</li>
                  <li className="font-medium text-blue-700 mt-2">
                    ✅ {accuracyStats?.completedForecasts || 0} forecasts completed
                  </li>
                </ul>
              </div>
            </div>
          </div>
            </>
          )}
        </div>
      )}

      {activeTab === 'feedback' && (
        <div className="space-y-6">
          {/* Feedback Patterns Analysis */}
          {feedbackPatterns?.hasEnoughData ? (
            <>
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                  📊 Feedback Patterns Analysis
                </h3>
                
                {/* Sentiment Distribution */}
                <div className="mb-6">
                  <h4 className="font-medium text-gray-700 mb-3">Sentiment Distribution</h4>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
                      <p className="text-3xl font-bold text-green-600">
                        {feedbackPatterns.patterns?.sentimentAnalysis?.counts?.positive || 0}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">😊 Positive</p>
                      <p className="text-xs text-gray-500">
                        {formatPercentage(feedbackPatterns.patterns?.sentimentAnalysis?.positivePercentage * 100)}
                      </p>
                    </div>
                    <div className="text-center p-4 bg-gray-50 border border-gray-200 rounded-lg">
                      <p className="text-3xl font-bold text-gray-600">
                        {feedbackPatterns.patterns?.sentimentAnalysis?.counts?.neutral || 0}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">😐 Neutral</p>
                      <p className="text-xs text-gray-500">
                        {formatPercentage(feedbackPatterns.patterns?.sentimentAnalysis?.neutralPercentage * 100)}
                      </p>
                    </div>
                    <div className="text-center p-4 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-3xl font-bold text-red-600">
                        {feedbackPatterns.patterns?.sentimentAnalysis?.counts?.negative || 0}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">😞 Negative</p>
                      <p className="text-xs text-gray-500">
                        {formatPercentage(feedbackPatterns.patterns?.sentimentAnalysis?.negativePercentage * 100)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* What Users Love */}
                <div className="mb-6">
                  <h4 className="font-medium text-gray-700 mb-3">✅ What Users Love (High-Rated Patterns)</h4>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-sm text-gray-700 mb-2">
                      <strong>{feedbackPatterns.patterns?.highRatedPatterns?.count || 0}</strong> high-rated entries (4-5 stars)
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {feedbackPatterns.patterns?.highRatedPatterns?.commonThemes?.map((theme, idx) => (
                        <span key={idx} className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                          ✨ {theme}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* What to Avoid */}
                <div className="mb-6">
                  <h4 className="font-medium text-gray-700 mb-3">❌ What to Avoid (Low-Rated Patterns)</h4>
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-sm text-gray-700 mb-2">
                      <strong>{feedbackPatterns.patterns?.lowRatedPatterns?.count || 0}</strong> low-rated entries (1-2 stars)
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {feedbackPatterns.patterns?.lowRatedPatterns?.commonThemes?.map((theme, idx) => (
                        <span key={idx} className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                          ⚠️ {theme}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Top Rated Chart Types */}
                <div>
                  <h4 className="font-medium text-gray-700 mb-3">🏆 Most Valued Chart Types</h4>
                  <div className="space-y-2">
                    {feedbackPatterns.patterns?.chartTypePreferences?.topRated?.slice(0, 5).map((chart, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-lg">
                        <div>
                          <p className="font-medium text-gray-800">{chart.chartType}</p>
                          <p className="text-xs text-gray-500">{chart.count} feedback entries</p>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold text-blue-600">{chart.avgRating.toFixed(1)}⭐</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* AI Prompt Enhancements Applied */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                  🎯 AI Prompt Enhancements (Auto-Applied)
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Based on user feedback, the system automatically enhances OpenAI prompts with these guidelines:
                </p>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="font-medium text-blue-800 mb-2">Current Enhancements:</p>
                  <ul className="space-y-2 text-sm text-gray-700">
                    {feedbackPatterns.patterns?.highRatedPatterns?.commonThemes?.map((theme, idx) => (
                      <li key={idx}>
                        ✅ <strong>Emphasize:</strong> {theme} recommendations
                      </li>
                    ))}
                    {feedbackPatterns.patterns?.lowRatedPatterns?.commonThemes?.map((theme, idx) => (
                      <li key={idx}>
                        ❌ <strong>Avoid:</strong> {theme} content
                      </li>
                    ))}
                  </ul>
                  <div className="mt-3 pt-3 border-t border-blue-200">
                    <p className="text-xs text-blue-700">
                      🎓 These enhancements are automatically applied to every new analytics generation
                    </p>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
              <span className="text-4xl block mb-3">⏰</span>
              <h3 className="font-semibold text-gray-800 mb-2">
                Collecting Feedback Data
              </h3>
              <p className="text-sm text-gray-600">
                Need at least 10 feedback entries to analyze patterns.
                <br />
                Current: {feedbackPatterns?.feedbackCount || 0} / 10
              </p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'forecasts' && (
        <div className="space-y-6">
          {/* Accuracy Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white border border-gray-200 rounded-lg p-5">
              <p className="text-sm text-gray-600 mb-2">Total Forecasts</p>
              <p className="text-3xl font-bold text-gray-800">
                {accuracyStats?.totalForecasts || 0}
              </p>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-5">
              <p className="text-sm text-gray-600 mb-2">Completed</p>
              <p className="text-3xl font-bold text-green-600">
                {accuracyStats?.completedForecasts || 0}
              </p>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-5">
              <p className="text-sm text-gray-600 mb-2">Pending</p>
              <p className="text-3xl font-bold text-orange-600">
                {accuracyStats?.pendingForecasts || 0}
              </p>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-5">
              <p className="text-sm text-gray-600 mb-2">AI Optimized</p>
              <p className="text-3xl font-bold text-purple-600">
                {accuracyStats?.optimizationRate || 0}%
              </p>
            </div>
          </div>

          {/* Accuracy by Forecast Type */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              🎯 Forecast Accuracy by Type
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {accuracyStats?.accuracyByType && Object.entries(accuracyStats.accuracyByType).map(([type, data]) => (
                <div key={type} className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-700 capitalize mb-2">
                    {type === 'sales' && '💰'} 
                    {type === 'quantity' && '📦'} 
                    {type === 'stock' && '📊'} 
                    {type === 'cash_flow' && '💵'} 
                    {' '}{type}
                  </h4>
                  <p className="text-2xl font-bold text-blue-600 mb-1">
                    {data.averageAccuracy}%
                  </p>
                  <p className="text-xs text-gray-600">
                    Based on {data.count} forecasts
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    MAPE: {data.averageMAPE}%
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* System Improvement Recommendations */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              💡 System Improvement Recommendations
            </h3>
            <div className="space-y-3">
              {accuracyStats?.completedForecasts < 10 ? (
                <div className="flex items-start gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <span className="text-2xl">⚠️</span>
                  <div>
                    <p className="font-medium text-gray-800">Need More Forecast Data</p>
                    <p className="text-sm text-gray-600 mt-1">
                      Encourage users to provide actual values for forecasts. 
                      Need {10 - (accuracyStats?.completedForecasts || 0)} more completed forecasts for parameter optimization.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="flex items-start gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <span className="text-2xl">✅</span>
                  <div>
                    <p className="font-medium text-gray-800">Forecast Learning Active</p>
                    <p className="text-sm text-gray-600 mt-1">
                      System is actively optimizing Prophet AI parameters based on {accuracyStats?.completedForecasts} completed forecasts.
                    </p>
                  </div>
                </div>
              )}

              {learningStats?.totalFeedback < 10 ? (
                <div className="flex items-start gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <span className="text-2xl">⚠️</span>
                  <div>
                    <p className="font-medium text-gray-800">Need More Feedback Data</p>
                    <p className="text-sm text-gray-600 mt-1">
                      Encourage users to rate charts and provide feedback.
                      Need {10 - (learningStats?.totalFeedback || 0)} more feedback entries for prompt optimization.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="flex items-start gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <span className="text-2xl">✅</span>
                  <div>
                    <p className="font-medium text-gray-800">Feedback Learning Active</p>
                    <p className="text-sm text-gray-600 mt-1">
                      System is actively improving recommendations based on {learningStats?.totalFeedback} feedback entries.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminAdaptiveLearning;

