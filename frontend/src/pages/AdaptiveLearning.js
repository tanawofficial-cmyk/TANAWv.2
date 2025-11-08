/**
 * Adaptive Learning Page
 * 
 * Main page for forecast accuracy tracking and learning features
 * Part of Objective 3.3: Adaptive Learning & User Feedback
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import api from '../api';
import StickyHeader from '../components/StickyHeader';
import ForecastAccuracyTracker from '../components/ForecastAccuracyTracker';
import AccuracyDashboard from '../components/AccuracyDashboard';

const AdaptiveLearning = () => {
  const [activeTab, setActiveTab] = useState('tracker'); // 'tracker' or 'dashboard'
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Check authentication and load user data on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    // Fetch user profile from API (same as Dashboard.js does)
    api.get("/users/me", { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => {
        const userData = res?.data || res;
        console.log("✅ Adaptive Learning - User profile loaded:", { email: userData?.email, role: userData?.role });
        setUser(userData);
        if (userData) {
          localStorage.setItem('user', JSON.stringify(userData));
        }
        setLoading(false);
      })
      .catch((error) => {
        console.error("❌ Failed to load user profile:", error);
        // Fallback to localStorage if API fails
        const storedUser = localStorage.getItem('user');
        if (storedUser && storedUser !== 'undefined' && storedUser !== 'null') {
          try {
            setUser(JSON.parse(storedUser));
          } catch (e) {
            console.error('Failed to parse user data:', e);
          }
        }
        setLoading(false);
      });
  }, [navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />

      <StickyHeader 
        user={user}
        onUserUpdate={(updatedUser) => setUser(updatedUser)}
        onLogout={() => {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          localStorage.removeItem('role');
          navigate('/login');
        }}
      />

      <div className="container mx-auto px-4 py-8 mt-20">
        {/* Page Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-800 mb-4 transition"
          >
            ← Back to Dashboard
          </button>

          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg">
              <span className="text-white text-3xl">🧠</span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-800">
                Adaptive Learning
              </h1>
              <p className="text-gray-600 mt-1">
                Track forecast accuracy and help improve predictions
              </p>
            </div>
          </div>

          {/* Info Card */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 mt-4">
            <div className="flex items-start gap-3">
              <span className="text-2xl mt-1 flex-shrink-0">🧠</span>
              <div>
                <h3 className="font-semibold text-gray-800 mb-1">
                  How Adaptive Learning Works
                </h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  TANAW learns from your feedback! By providing actual values for forecasts, 
                  the system automatically optimizes its prediction algorithms to become more 
                  accurate for your specific business patterns. The more data you provide, 
                  the better the predictions become.
                </p>
                <div className="mt-2 flex flex-wrap gap-2">
                  <span className="px-2 py-1 bg-white border border-blue-200 rounded text-xs text-blue-700">
                    Self-Improving AI
                  </span>
                  <span className="px-2 py-1 bg-white border border-blue-200 rounded text-xs text-blue-700">
                    Personalized for Your Business
                  </span>
                  <span className="px-2 py-1 bg-white border border-blue-200 rounded text-xs text-blue-700">
                    Quantifiable Accuracy
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6 bg-white p-2 rounded-lg border border-gray-200 shadow-sm">
          <button
            onClick={() => setActiveTab('tracker')}
            className={`flex-1 px-6 py-3 rounded-lg font-medium transition ${
              activeTab === 'tracker'
                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            📝 Update Forecasts
          </button>
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex-1 px-6 py-3 rounded-lg font-medium transition ${
              activeTab === 'dashboard'
                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            📊 View Statistics
          </button>
        </div>

        {/* Content */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-200">
          {activeTab === 'tracker' ? (
            <ForecastAccuracyTracker />
          ) : (
            <AccuracyDashboard />
          )}
        </div>
      </div>
    </div>
  );
};

export default AdaptiveLearning;



