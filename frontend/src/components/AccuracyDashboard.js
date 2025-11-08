/**
 * Accuracy Dashboard Component
 * 
 * Displays forecast accuracy statistics and history
 * Part of Objective 3.3: Adaptive Learning & User Feedback - Phase 2
 */

import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import api from '../api';

const AccuracyDashboard = () => {
  const [statistics, setStatistics] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState('all');

  useEffect(() => {
    fetchData();
  }, [selectedType]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');

      // Fetch statistics
      const statsResponse = await api.get(
        "/forecast-accuracy/statistics",
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Fetch history
      const historyParams = selectedType !== 'all' ? `?forecastType=${selectedType}&status=completed` : '?status=completed';
      const historyResponse = await api.get(
        `/forecast-accuracy/history${historyParams}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (statsResponse.success) {
        setStatistics(statsResponse.data);
      }

      if (historyResponse.success) {
        setHistory(historyResponse.data?.forecasts || []);
      }
    } catch (error) {
      console.error('Error fetching accuracy data:', error);
      toast.error('Failed to load accuracy data');
    } finally {
      setLoading(false);
    }
  };

  const getAccuracyColor = (accuracy) => {
    if (accuracy >= 90) return 'text-green-600';
    if (accuracy >= 80) return 'text-blue-600';
    if (accuracy >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getAccuracyBgColor = (accuracy) => {
    if (accuracy >= 90) return 'bg-green-50 border-green-200';
    if (accuracy >= 80) return 'bg-blue-50 border-blue-200';
    if (accuracy >= 70) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const getAccuracyLabel = (accuracy) => {
    if (accuracy >= 90) return 'Excellent';
    if (accuracy >= 80) return 'Good';
    if (accuracy >= 70) return 'Fair';
    return 'Needs Improvement';
  };

  const getAccuracyIcon = (accuracy) => {
    if (accuracy >= 90) return <span className="text-green-600">🏆</span>;
    if (accuracy >= 80) return <span className="text-blue-600">✅</span>;
    if (accuracy >= 70) return <span className="text-yellow-600">⏰</span>;
    return <span className="text-red-600">⚠️</span>;
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

  // Prepare chart data
  const prepareChartData = () => {
    const sortedHistory = [...history].sort((a, b) => 
      new Date(a.targetDate) - new Date(b.targetDate)
    );

    return sortedHistory.slice(-10).map(forecast => ({
      date: formatDate(forecast.targetDate),
      accuracy: parseFloat(forecast.accuracy) || 0,
      mape: parseFloat(forecast.mape) || 0,
      type: forecast.forecastType
    }));
  };

  // Prepare forecast type breakdown
  const prepareTypeBreakdown = () => {
    if (!statistics?.accuracyByType) return [];

    return Object.entries(statistics.accuracyByType).map(([type, data]) => ({
      type: type.charAt(0).toUpperCase() + type.slice(1),
      accuracy: parseFloat(data.averageAccuracy) || 0,
      count: data.count
    }));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="accuracy-dashboard p-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          📊 Forecast Accuracy Dashboard
        </h2>
        <p className="text-gray-600 mt-1">
          Track and improve your forecast accuracy over time
        </p>
      </div>

      {/* Overall Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {/* Total Forecasts */}
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Total Forecasts</p>
            <span className="text-xl">📊</span>
          </div>
          <p className="text-3xl font-bold text-gray-800">
            {statistics?.totalForecasts || 0}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {statistics?.completedForecasts || 0} completed
          </p>
        </div>

        {/* Pending */}
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Pending</p>
            <span className="text-xl">⏰</span>
          </div>
          <p className="text-3xl font-bold text-gray-800">
            {statistics?.pendingForecasts || 0}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Awaiting actual values
          </p>
        </div>

        {/* Optimized */}
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">AI Optimized</p>
            <span className="text-xl">🧠</span>
          </div>
          <p className="text-3xl font-bold text-gray-800">
            {statistics?.optimizedForecasts || 0}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {statistics?.optimizationRate || 0}% optimized
          </p>
        </div>

        {/* Learning Status */}
        <div className={`border rounded-lg p-5 ${
          (statistics?.completedForecasts || 0) >= 10
            ? 'bg-gradient-to-br from-green-50 to-green-100 border-green-200'
            : 'bg-gradient-to-br from-gray-50 to-gray-100 border-gray-200'
        }`}>
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Learning Status</p>
            <span className="text-xl">
              {(statistics?.completedForecasts || 0) >= 10 ? '✅' : '⏰'}
            </span>
          </div>
          <p className={`text-lg font-bold ${
            (statistics?.completedForecasts || 0) >= 10 ? 'text-green-700' : 'text-gray-700'
          }`}>
            {(statistics?.completedForecasts || 0) >= 10 ? 'Active' : 'Collecting Data'}
          </p>
          <p className="text-xs text-gray-600 mt-1">
            {(statistics?.completedForecasts || 0) >= 10
              ? 'System is learning!'
              : `${10 - (statistics?.completedForecasts || 0)} more needed`
            }
          </p>
        </div>
      </div>

      {/* Forecast Type Filter */}
      <div className="flex flex-wrap gap-2 mb-6">
        <button
          onClick={() => setSelectedType('all')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            selectedType === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All Types
        </button>
        <button
          onClick={() => setSelectedType('sales')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            selectedType === 'sales'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          💰 Sales
        </button>
        <button
          onClick={() => setSelectedType('quantity')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            selectedType === 'quantity'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          📦 Quantity
        </button>
        <button
          onClick={() => setSelectedType('stock')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            selectedType === 'stock'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          📊 Stock
        </button>
        <button
          onClick={() => setSelectedType('cash_flow')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            selectedType === 'cash_flow'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          💵 Cash Flow
        </button>
      </div>

      {/* Charts Row */}
      {history.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Accuracy Trend Chart */}
          <div className="bg-white border border-gray-200 rounded-lg p-5">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Accuracy Trend
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={prepareChartData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="accuracy"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  name="Accuracy %"
                  dot={{ fill: '#3B82F6', r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Forecast Type Breakdown */}
          <div className="bg-white border border-gray-200 rounded-lg p-5">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Accuracy by Type
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={prepareTypeBreakdown()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="accuracy" fill="#8B5CF6" name="Avg Accuracy %" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Forecast History Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="p-5 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800">
            Recent Forecasts
          </h3>
        </div>

        {history.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <p>No completed forecasts yet.</p>
            <p className="text-sm mt-1">
              Provide actual values for your forecasts to see accuracy data here.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Chart
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Predicted
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Actual
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Accuracy
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {history.slice(0, 10).map((forecast) => (
                  <tr key={forecast._id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <p className="text-sm font-medium text-gray-800">
                        {forecast.chartTitle}
                      </p>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                        {forecast.forecastType}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {forecast.forecastType === 'quantity'
                        ? `${forecast.predictedValue.toLocaleString()} units`
                        : formatCurrency(forecast.predictedValue)
                      }
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {forecast.forecastType === 'quantity'
                        ? `${forecast.actualValue.toLocaleString()} units`
                        : formatCurrency(forecast.actualValue)
                      }
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {getAccuracyIcon(forecast.accuracy)}
                        <span className={`text-sm font-bold ${getAccuracyColor(forecast.accuracy)}`}>
                          {forecast.accuracy.toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {formatDate(forecast.targetDate)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AccuracyDashboard;

