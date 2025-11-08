/**
 * Forecast Accuracy Tracker Component
 * 
 * Displays pending forecasts and allows users to provide actual values
 * Part of Objective 3.3: Adaptive Learning & User Feedback - Phase 2
 */

import React, { useState, useEffect } from 'react';
import api from '../api';
import toast from 'react-hot-toast';

const ForecastAccuracyTracker = () => {
  const [pendingForecasts, setPendingForecasts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedForecast, setSelectedForecast] = useState(null);
  const [actualValue, setActualValue] = useState('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [deleting, setDeleting] = useState(null); // Track which forecast is being deleted

  useEffect(() => {
    fetchPendingForecasts();
  }, []);

  const fetchPendingForecasts = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      if (!token) {
        console.error('No auth token found');
        toast.error('Please log in to view forecasts');
        setPendingForecasts([]);
        setLoading(false);
        return;
      }

      console.log('Fetching pending forecasts from /forecast-accuracy/pending');
      
      const response = await api.get(
        "/forecast-accuracy/pending",
        {
          headers: { Authorization: `Bearer ${token}` },
          timeout: 10000 // 10 second timeout
        }
      );

      console.log('Pending forecasts response:', response);

      if (response.success) {
        const forecasts = response.data?.forecasts || [];
        setPendingForecasts(forecasts);
        console.log(`✅ Loaded ${forecasts.length} pending forecast(s)`);
      } else {
        setPendingForecasts([]);
        console.log('⚠️ No forecasts in response');
      }
    } catch (error) {
      console.error('❌ Error fetching pending forecasts:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      
      if (error.code === 'ECONNABORTED') {
        toast.error('Request timed out - check if backend is running');
      } else if (error.response?.status === 401) {
        toast.error('Session expired - please log in again');
      } else if (error.response?.status === 404) {
        toast.error('Endpoint not found - check backend routes');
      } else {
        toast.error(`Failed to load forecasts: ${error.message}`);
      }
      
      setPendingForecasts([]); // Set to empty array on error
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitActual = async (e) => {
    e.preventDefault();

    if (!actualValue || isNaN(actualValue)) {
      toast.error('Please enter a valid number');
      return;
    }

    try {
      setSubmitting(true);
      const token = localStorage.getItem('token');

      const response = await api.post(
        "/forecast-accuracy/submit-actual",
        {
          forecastId: selectedForecast._id,
          actualValue: parseFloat(actualValue),
          notes: notes || undefined
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      if (response.success) {
        const accuracy = response.data?.accuracy;
        const hasAccuracy = typeof accuracy === 'number' && !Number.isNaN(accuracy);
        toast.success(
          `✅ Actual value submitted! Accuracy: ${hasAccuracy ? accuracy.toFixed(1) : 'N/A'}%`,
          { autoClose: 5000 }
        );

        // Refresh list and close modal
        fetchPendingForecasts();
        setSelectedForecast(null);
        setActualValue('');
        setNotes('');
      }
    } catch (error) {
      console.error('Error submitting actual value:', error);
      toast.error(error.response?.data?.message || 'Failed to submit actual value');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteForecast = async (forecastId, e) => {
    e.stopPropagation(); // Prevent card click

    if (!window.confirm('Are you sure you want to delete this forecast? This action cannot be undone.')) {
      return;
    }

    try {
      setDeleting(forecastId);
      const token = localStorage.getItem('token');

      const response = await api.delete(
        `/forecast-accuracy/${forecastId}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      if (response.success) {
        toast.success('🗑️ Forecast deleted successfully');
        fetchPendingForecasts(); // Refresh list
      }
    } catch (error) {
      console.error('Error deleting forecast:', error);
      toast.error(error.response?.data?.message || 'Failed to delete forecast');
    } finally {
      setDeleting(null);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-PH', {
      style: 'currency',
      currency: 'PHP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getDaysLabel = (days) => {
    if (days < 0) {
      return `${Math.abs(days)} days overdue`;
    } else if (days === 0) {
      return 'Today';
    } else if (days === 1) {
      return 'Tomorrow';
    } else {
      return `${days} days left`;
    }
  };

  const getDaysColor = (days) => {
    if (days < 0) return 'text-red-600';
    if (days <= 3) return 'text-orange-600';
    if (days <= 7) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getForecastTypeLabel = (type) => {
    const labels = {
      sales: '💰 Sales',
      quantity: '📦 Quantity',
      stock: '📊 Stock',
      cash_flow: '💵 Cash Flow'
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="forecast-accuracy-tracker p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            📊 Forecast Accuracy Tracker
          </h2>
          <p className="text-gray-600 mt-1">
            Help improve predictions by providing actual values
          </p>
        </div>
        <button
          onClick={fetchPendingForecasts}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          🔄 Refresh
        </button>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
          <div className="flex items-center gap-3">
            <span className="text-3xl">⏰</span>
            <div>
              <p className="text-sm text-gray-600">Pending</p>
              <p className="text-2xl font-bold text-gray-800">
                {pendingForecasts.length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg border border-orange-200">
          <div className="flex items-center gap-3">
            <span className="text-3xl">⚠️</span>
            <div>
              <p className="text-sm text-gray-600">Urgent (≤7 days)</p>
              <p className="text-2xl font-bold text-gray-800">
                {pendingForecasts.filter(f => f.daysUntilTarget <= 7).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg border border-red-200">
          <div className="flex items-center gap-3">
            <span className="text-3xl">📅</span>
            <div>
              <p className="text-sm text-gray-600">Overdue</p>
              <p className="text-2xl font-bold text-gray-800">
                {pendingForecasts.filter(f => f.daysUntilTarget < 0).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Forecasts List */}
      {pendingForecasts.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <span className="text-6xl mb-4 block">📊</span>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">
            No Pending Forecasts Yet
          </h3>
          <p className="text-gray-600 mb-4">
            Upload datasets with forecast charts to start tracking accuracy.
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto text-left">
            <p className="text-sm font-semibold text-blue-900 mb-2">📝 How to Generate Forecasts:</p>
            <ol className="text-sm text-gray-700 space-y-1">
              <li>1. Go back to Dashboard</li>
              <li>2. Upload a dataset with Date + Sales/Quantity columns</li>
              <li>3. System will generate forecast charts</li>
              <li>4. Come back here after 30 days</li>
              <li>5. Provide actual values to track accuracy!</li>
            </ol>
          </div>
          <button
            onClick={() => window.location.href = '/dashboard'}
            className="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            📤 Go to Dashboard
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Sort info */}
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">
              Showing {pendingForecasts.length} forecast{pendingForecasts.length !== 1 ? 's' : ''} • Sorted by most recent
            </p>
          </div>

          {pendingForecasts
            .sort((a, b) => new Date(b.forecastDate) - new Date(a.forecastDate)) // Sort by most recent first
            .map((forecast, index) => (
            <div
              key={forecast._id}
              className={`bg-white border-2 rounded-lg p-5 hover:shadow-xl transition-all cursor-pointer relative ${
                index === 0 ? 'border-blue-400 ring-2 ring-blue-100' : 'border-gray-200'
              }`}
              onClick={() => setSelectedForecast(forecast)}
            >
              {/* Latest Indicator */}
              {index === 0 && (
                <div className="absolute -top-3 left-4 px-3 py-1 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-xs font-bold rounded-full shadow-lg flex items-center gap-1">
                  ✨ LATEST FORECAST
                </div>
              )}

              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* Chart Title */}
                  <h3 className="text-lg font-semibold text-gray-800 mb-2 flex items-center gap-2">
                    {forecast.chartTitle}
                    {index === 0 && <span className="text-blue-600 text-sm">(Most Recent)</span>}
                  </h3>

                  {/* Forecast Type Badge */}
                  <div className="flex flex-wrap gap-2 mb-3">
                    <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium flex items-center gap-1">
                      💡 {getForecastTypeLabel(forecast.forecastType)}
                    </span>
                    <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
                      {forecast.domain.charAt(0).toUpperCase() + forecast.domain.slice(1)}
                    </span>
                    {forecast.forecastPeriod && (
                      <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                        📅 {forecast.forecastPeriod}-day forecast
                      </span>
                    )}
                  </div>

                  {/* Forecast Details - Enhanced */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-3">
                    <div>
                      <p className="text-gray-500 mb-1">Forecasted</p>
                      <p className="font-semibold text-gray-800">
                        {forecast.forecastType === 'quantity' 
                          ? `${forecast.predictedValue.toLocaleString()} units`
                          : formatCurrency(forecast.predictedValue)
                        }
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500 mb-1">Target Date</p>
                      <p className="font-semibold text-gray-800">
                        {formatDate(forecast.targetDate)}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500 mb-1">Forecast Made</p>
                      <p className="font-semibold text-gray-800">
                        {formatDate(forecast.forecastDate)}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(forecast.forecastDate).toLocaleTimeString('en-US', { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500 mb-1">Dataset</p>
                      <p className="font-semibold text-gray-800 text-xs truncate" title={forecast.datasetId || 'N/A'}>
                        {forecast.datasetId ? `...${forecast.datasetId.slice(-8)}` : 'Pending'}
                      </p>
                    </div>
                  </div>

                  {/* Additional Info Bar */}
                  <div className="bg-gray-50 rounded-lg p-3 text-xs text-gray-600">
                    <div className="flex items-center gap-4 flex-wrap">
                      <span className="flex items-center gap-1">
                        🔮 <strong>Model:</strong> Prophet AI
                      </span>
                      {forecast.predictedLower && forecast.predictedUpper && (
                        <span className="flex items-center gap-1">
                          📊 <strong>Range:</strong> {forecast.forecastType === 'quantity' 
                            ? `${forecast.predictedLower.toLocaleString()} - ${forecast.predictedUpper.toLocaleString()} units`
                            : `${formatCurrency(forecast.predictedLower)} - ${formatCurrency(forecast.predictedUpper)}`
                          }
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        📍 <strong>Created:</strong> {new Date(forecast.createdAt).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Days Until Target */}
                <div className="ml-4 text-right">
                  <div className={`text-2xl font-bold ${getDaysColor(forecast.daysUntilTarget)}`}>
                    {Math.abs(forecast.daysUntilTarget)}
                  </div>
                  <div className={`text-sm ${getDaysColor(forecast.daysUntilTarget)}`}>
                    {getDaysLabel(forecast.daysUntilTarget)}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-4 pt-4 border-t border-gray-200 flex gap-2">
                <button
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition font-medium disabled:opacity-50"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedForecast(forecast);
                  }}
                  disabled={deleting === forecast._id}
                >
                  Provide Actual Value →
                </button>
                <button
                  className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition font-medium disabled:opacity-50 flex items-center gap-2"
                  onClick={(e) => handleDeleteForecast(forecast._id, e)}
                  disabled={deleting === forecast._id}
                  title="Delete this forecast"
                >
                  {deleting === forecast._id ? (
                    <>
                      <span className="animate-spin">⏳</span>
                      Deleting...
                    </>
                  ) : (
                    <>
                      🗑️ Delete
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal for Entering Actual Value */}
      {selectedForecast && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 rounded-t-xl">
              <h3 className="text-xl font-bold mb-2">
                Update Actual Value
              </h3>
              <p className="text-blue-100 text-sm">
                {selectedForecast.chartTitle}
              </p>
            </div>

            {/* Modal Body */}
            <form onSubmit={handleSubmitActual} className="p-6">
              {/* Forecast Summary */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500 mb-1">Predicted Value</p>
                    <p className="font-bold text-gray-800">
                      {selectedForecast.forecastType === 'quantity'
                        ? `${selectedForecast.predictedValue.toLocaleString()} units`
                        : formatCurrency(selectedForecast.predictedValue)
                      }
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500 mb-1">Target Date</p>
                    <p className="font-bold text-gray-800">
                      {formatDate(selectedForecast.targetDate)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Actual Value Input */}
              <div className="mb-4">
                <label className="block text-gray-700 font-medium mb-2">
                  Actual {selectedForecast.forecastType === 'quantity' ? 'Quantity' : 'Value'} *
                </label>
                <div className="relative">
                  {selectedForecast.forecastType !== 'quantity' && (
                    <span className="absolute left-3 top-3 text-gray-500">₱</span>
                  )}
                  <input
                    type="number"
                    value={actualValue}
                    onChange={(e) => setActualValue(e.target.value)}
                    className={`w-full ${
                      selectedForecast.forecastType !== 'quantity' ? 'pl-8' : 'pl-4'
                    } pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                    placeholder={`Enter actual ${selectedForecast.forecastType === 'quantity' ? 'quantity' : 'value'}`}
                    required
                    step="0.01"
                  />
                  {selectedForecast.forecastType === 'quantity' && (
                    <span className="absolute right-3 top-3 text-gray-500">units</span>
                  )}
                </div>
              </div>

              {/* Notes (Optional) */}
              <div className="mb-6">
                <label className="block text-gray-700 font-medium mb-2">
                  Notes (Optional)
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows="3"
                  placeholder="Any notes about why the forecast was accurate/inaccurate..."
                  maxLength="500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {notes.length}/500 characters
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setSelectedForecast(null);
                    setActualValue('');
                    setNotes('');
                  }}
                  className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={submitting}
                >
                  {submitting ? 'Submitting...' : 'Submit'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ForecastAccuracyTracker;

