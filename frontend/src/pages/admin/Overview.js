import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  Users,
  FileText,
  MessageSquare,
  TrendingUp,
} from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function Overview() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // Fetch both admin stats and analytics data
        const [adminStatsRes, analyticsRes] = await Promise.all([
          axios.get("/api/admin/stats"),
          axios.get("/api/analytics/data?range=7d")
        ]);
        
        // Merge the data
        const mergedStats = {
          ...adminStatsRes.data.data,
          analytics: analyticsRes.data.success ? analyticsRes.data.data : null
        };
        
        console.log("📊 Merged admin stats:", mergedStats);
        setStats(mergedStats);
      } catch (err) {
        console.error("Error fetching admin stats:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="p-6 text-center text-gray-500">Loading overview...</div>
    );
  }

  if (!stats) {
    return (
      <div className="p-6 text-center text-red-500">
        Failed to load admin stats.
      </div>
    );
  }

  // Data for chart
  const chartsGenerated = stats.analytics?.overview?.chartsGenerated?.value || 0;
  const totalDatasets = stats.analytics?.overview?.totalDatasets?.value || stats.uploads.totalUploads || 0;
  
  const chartData = [
    { name: "Users", count: stats.users.totalUsers },
    { name: "Uploads", count: totalDatasets },
    { name: "Charts", count: chartsGenerated },
    { name: "Feedback", count: stats.feedback.positiveFeedback + stats.feedback.negativeFeedback },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-2xl blur-3xl"></div>
        <div className="relative">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Admin Overview
          </h1>
          <p className="text-gray-600 mt-2 text-lg">
            Summary of the TANAW platform performance and usage.
          </p>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Users */}
        <div className="group relative p-6 bg-white/80 backdrop-blur-sm shadow-lg rounded-2xl border border-gray-200/50 hover:shadow-xl transition-all duration-300 transform hover:scale-105">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div className="relative flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full blur-sm opacity-20 group-hover:opacity-30 transition-opacity"></div>
              <div className="relative p-3 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full">
                <Users className="text-blue-600" size={24} />
              </div>
            </div>
            <div>
              <h2 className="text-sm text-gray-600 font-medium">Total Users</h2>
              <p className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {stats.users.totalUsers}
              </p>
            </div>
          </div>
        </div>

        {/* Total Uploads */}
        <div className="group relative p-6 bg-white/80 backdrop-blur-sm shadow-lg rounded-2xl border border-gray-200/50 hover:shadow-xl transition-all duration-300 transform hover:scale-105">
          <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-emerald-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div className="relative flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full blur-sm opacity-20 group-hover:opacity-30 transition-opacity"></div>
              <div className="relative p-3 bg-gradient-to-br from-green-100 to-emerald-100 rounded-full">
                <FileText className="text-green-600" size={24} />
              </div>
            </div>
            <div>
              <h2 className="text-sm text-gray-600 font-medium">Total Uploads</h2>
              <p className="text-2xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                {totalDatasets}
              </p>
            </div>
          </div>
        </div>

        {/* Charts Generated */}
        <div className="group relative p-6 bg-white/80 backdrop-blur-sm shadow-lg rounded-2xl border border-gray-200/50 hover:shadow-xl transition-all duration-300 transform hover:scale-105">
          <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div className="relative flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full blur-sm opacity-20 group-hover:opacity-30 transition-opacity"></div>
              <div className="relative p-3 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full">
                <TrendingUp className="text-purple-600" size={24} />
              </div>
            </div>
            <div>
              <h2 className="text-sm text-gray-600 font-medium">Charts Generated</h2>
              <p className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                {chartsGenerated}
              </p>
              {stats.analytics?.overview?.chartsGenerated?.change && (
                <p className={`text-xs mt-1 font-medium ${stats.analytics.overview.chartsGenerated.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                  {stats.analytics.overview.chartsGenerated.change > 0 ? '+' : ''}{stats.analytics.overview.chartsGenerated.change}% vs last period
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Average Feedback Rating */}
        <div className="group relative p-6 bg-white/80 backdrop-blur-sm shadow-lg rounded-2xl border border-gray-200/50 hover:shadow-xl transition-all duration-300 transform hover:scale-105">
          <div className="absolute inset-0 bg-gradient-to-br from-yellow-500/5 to-orange-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div className="relative flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-full blur-sm opacity-20 group-hover:opacity-30 transition-opacity"></div>
              <div className="relative p-3 bg-gradient-to-br from-yellow-100 to-orange-100 rounded-full">
                <MessageSquare className="text-yellow-600" size={24} />
              </div>
            </div>
            <div>
              <h2 className="text-sm text-gray-600 font-medium">Avg. Feedback Rating</h2>
              <p className="text-2xl font-bold bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent">
                {stats.feedback.avgRating.toFixed(1)} ⭐
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Chart Section */}
      <div className="group relative bg-white/80 backdrop-blur-sm p-8 shadow-lg rounded-2xl border border-gray-200/50 hover:shadow-xl transition-all duration-300">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div className="relative">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full blur-sm opacity-20"></div>
                <div className="relative p-2 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full">
                  <TrendingUp className="text-blue-600" size={20} />
                </div>
              </div>
              <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Platform Summary
              </h2>
            </div>
            <p className="text-sm text-gray-600 font-medium">Overview of key statistics</p>
          </div>

          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.3} />
              <XAxis 
                dataKey="name" 
                tick={{ fontSize: 12, fill: '#6b7280' }}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <YAxis 
                tick={{ fontSize: 12, fill: '#6b7280' }}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #e5e7eb',
                  borderRadius: '12px',
                  boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Bar 
                dataKey="count" 
                fill="url(#gradient)" 
                radius={[12, 12, 0, 0]}
                className="hover:opacity-80 transition-opacity"
              />
              <defs>
                <linearGradient id="gradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#8b5cf6" />
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
