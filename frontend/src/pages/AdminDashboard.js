import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  Users, 
  MessageSquare, 
  TrendingUp, 
  TrendingDown,
  UserPlus,
  Clock,
  Activity,
  Menu,
  X,
  LogOut,
  Database,
  BarChart,
  Star,
  Download,
  Trash2,
  CheckCircle,
  XCircle,
  AlertCircle,
  Zap,
  HardDrive,
  Cpu,
  Server,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import analytics from '../services/analytics';
import AdminCharts from '../components/AdminCharts';
import api from '../api';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  
  // User management state
  const [users, setUsers] = useState([]);
  const [usersLoading, setUsersLoading] = useState(true);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [roleFilter, setRoleFilter] = useState('');
  const [userSearchQuery, setUserSearchQuery] = useState('');
  const [userDateFilter, setUserDateFilter] = useState('');
  const [showUserProfileModal, setShowUserProfileModal] = useState(false);
  const [selectedUserProfile, setSelectedUserProfile] = useState(null);
  const [openDropdownId, setOpenDropdownId] = useState(null);
  const [overviewDateFilter, setOverviewDateFilter] = useState('');
  const [connectivityDateFilter, setConnectivityDateFilter] = useState('');
  const [analyticsData, setAnalyticsData] = useState({
    overview: {
      totalDatasets: { value: 0, change: 0, trend: 'up' },
      chartsGenerated: { value: 0, change: 0, trend: 'up' },
      registeredUsers: { value: 0, change: 0, trend: 'up' },
      activeUsers: { value: 0, change: 0, trend: 'up' }
    },
    detailed: {
      totalUsers: 0,
      newUsersThisMonth: 0,
      totalDatasets: 0,
      avgChartsPerDataset: 0
    }
  });
  const [loading, setLoading] = useState(true);
  
  // Feedback management state
  const [feedbackData, setFeedbackData] = useState([]);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [feedbackStats, setFeedbackStats] = useState({
    averageRating: 0,
    totalFeedback: 0,
    responseRate: 0,
    trend: 0
  });
  const [filteredFeedback, setFilteredFeedback] = useState([]);
  const [ratingFilter, setRatingFilter] = useState('');
  const [feedbackSearchQuery, setFeedbackSearchQuery] = useState('');
  const [dateFilter, setDateFilter] = useState('');
  
  // Connectivity & Usage state
  const [systemStatus, setSystemStatus] = useState({
    mongodb: { status: 'checking', responseTime: 0 },
    flaskService: { status: 'checking', responseTime: 0 },
    openaiApi: { status: 'checking', configured: false }
  });
  const [apiMetrics, setApiMetrics] = useState({
    openai: {
      totalTokens: 0,
      totalPromptTokens: 0,
      totalCompletionTokens: 0,
      totalCalls: 0,
      totalCost: 0,
      avgResponseTime: 0,
      successRate: 0
    },
    services: {},
    endpoints: [],
    timeline: []
  });
  const [databaseStats, setDatabaseStats] = useState({
    collections: {},
    databaseStats: {},
    recentActivity: {}
  });
  const [usagePeriod, setUsagePeriod] = useState('7d');

  // Handle window resize for responsive behavior
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
      // Auto-collapse sidebar on mobile
      if (window.innerWidth < 768) {
        setMobileMenuOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Fetch analytics data on component mount (access already verified by ProtectedRoute)
  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        setLoading(true);
        
        // Track admin dashboard visit
        analytics.trackPageView('admin-dashboard');
        analytics.trackAction('admin_dashboard_visit', { page: 'admin-dashboard' });
        
        const data = await analytics.getAnalyticsData('7d');
        console.log('📊 Analytics data received:', data);
        if (data && data.success) {
          console.log('✅ Setting analytics data:', data.data);
          setAnalyticsData(data.data);
        } else {
          console.error('❌ Analytics data fetch failed or no data:', data);
        }
      } catch (error) {
        console.error('Failed to fetch analytics data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyticsData();
  }, []);

  // Fetch users when activeTab changes to activeUsers
  useEffect(() => {
    if (activeTab === 'activeUsers') {
      console.log('🔄 Active tab changed to activeUsers, fetching users...');
      fetchUsers();
    }
  }, [activeTab]);

  // Filter users based on search and filters
  useEffect(() => {
    let filtered = users;

    if (roleFilter) {
      filtered = filtered.filter(user => user.role === roleFilter);
    }

    if (userSearchQuery) {
      filtered = filtered.filter(user => 
        user.fullName.toLowerCase().includes(userSearchQuery.toLowerCase()) ||
        user.email.toLowerCase().includes(userSearchQuery.toLowerCase()) ||
        user.businessName.toLowerCase().includes(userSearchQuery.toLowerCase())
      );
    }

    // Filter by registration date
    if (userDateFilter) {
      const now = new Date();
      if (userDateFilter === 'today') {
        filtered = filtered.filter(user => {
          const userDate = new Date(user.createdAt);
          return userDate.toDateString() === now.toDateString();
        });
      } else if (userDateFilter === 'week') {
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        filtered = filtered.filter(user => new Date(user.createdAt) >= weekAgo);
      } else if (userDateFilter === 'month') {
        const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        filtered = filtered.filter(user => new Date(user.createdAt) >= monthAgo);
      }
    }

    setFilteredUsers(filtered);
  }, [users, roleFilter, userSearchQuery, userDateFilter]);

  // Fetch feedback when tab changes to userFeedback
  useEffect(() => {
    if (activeTab === 'userFeedback') {
      console.log('💬 Active tab changed to userFeedback, fetching feedback...');
      fetchFeedback();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  // Filter feedback based on rating, date, and search
  useEffect(() => {
    let filtered = [...feedbackData];

    // Filter by rating
    if (ratingFilter) {
      filtered = filtered.filter(f => f.rating === parseInt(ratingFilter));
    }

    // Filter by date
    if (dateFilter) {
      const now = new Date();
      if (dateFilter === 'today') {
        filtered = filtered.filter(f => {
          const feedbackDate = new Date(f.date);
          return feedbackDate.toDateString() === now.toDateString();
        });
      } else if (dateFilter === 'week') {
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        filtered = filtered.filter(f => new Date(f.date) >= weekAgo);
      } else if (dateFilter === 'month') {
        const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        filtered = filtered.filter(f => new Date(f.date) >= monthAgo);
      }
    }

    // Search in message or user details
    if (feedbackSearchQuery) {
      filtered = filtered.filter(f => 
        f.message?.toLowerCase().includes(feedbackSearchQuery.toLowerCase()) ||
        f.userId?.fullName?.toLowerCase().includes(feedbackSearchQuery.toLowerCase()) ||
        f.userId?.email?.toLowerCase().includes(feedbackSearchQuery.toLowerCase()) ||
        f.userId?.businessName?.toLowerCase().includes(feedbackSearchQuery.toLowerCase())
      );
    }

    setFilteredFeedback(filtered);
  }, [feedbackData, ratingFilter, dateFilter, feedbackSearchQuery]);

  // Fetch connectivity data when tab changes
  useEffect(() => {
    if (activeTab === 'connectivity') {
      console.log('🔌 Active tab changed to connectivity, fetching status...');
      fetchConnectivityStatus();
      fetchApiMetrics(usagePeriod);
      fetchDatabaseStats();
      
      // Set up auto-refresh for connectivity status every 2 minutes
      const interval = setInterval(() => {
        fetchConnectivityStatus();
      }, 120000); // 2 minutes instead of 30 seconds
      
      return () => clearInterval(interval);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  // Refetch API metrics when connectivity date filter changes
  useEffect(() => {
    if (activeTab === 'connectivity' && connectivityDateFilter) {
      fetchApiMetrics('7d', connectivityDateFilter); // Pass date as second parameter
      fetchDatabaseStats(connectivityDateFilter); // Also filter database stats
    } else if (activeTab === 'connectivity' && !connectivityDateFilter) {
      fetchApiMetrics('7d'); // Default to 7 days when no filter
      fetchDatabaseStats(); // Fetch all time database stats
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [connectivityDateFilter, activeTab]);

  // Refetch analytics when overview date filter changes
  useEffect(() => {
    if (activeTab === 'overview' && overviewDateFilter) {
      const fetchFilteredAnalytics = async () => {
        try {
          setLoading(true);
          // Fetch data for specific date (you may need to modify backend to support this)
          const data = await analytics.getAnalyticsData('7d', overviewDateFilter);
          if (data && data.success) {
            setAnalyticsData(data.data);
          }
        } catch (error) {
          console.error('Failed to fetch filtered analytics:', error);
        } finally {
          setLoading(false);
        }
      };
      fetchFilteredAnalytics();
    } else if (activeTab === 'overview' && !overviewDateFilter) {
      // Refetch all time data when filter is cleared
      const fetchAnalyticsData = async () => {
        try {
          setLoading(true);
          const data = await analytics.getAnalyticsData('7d');
          if (data && data.success) {
            setAnalyticsData(data.data);
          }
        } catch (error) {
          console.error('Failed to fetch analytics data:', error);
        } finally {
          setLoading(false);
        }
      };
      fetchAnalyticsData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [overviewDateFilter, activeTab]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (openDropdownId && !event.target.closest('.relative')) {
        setOpenDropdownId(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [openDropdownId]);

  // Helper functions
  const handleLogout = () => {
    setShowLogoutModal(false); // Close modal
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    toast.success("👋 Admin logged out successfully! Redirecting to home...");
    // Redirect to landing page
    setTimeout(() => {
      window.location.href = '/';
    }, 1000); // Delay to show the toast
  };



  const toggleSidebar = () => {
    if (isMobile) {
      setMobileMenuOpen(!mobileMenuOpen);
    } else {
      setSidebarCollapsed(!sidebarCollapsed);
    }
  };

  // User management functions
  const fetchUsers = async () => {
    try {
      setUsersLoading(true);
      console.log('🔍 Fetching users from API...');
      console.log('🔑 Token:', localStorage.getItem('token') ? 'Present' : 'Missing');
      
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
      const response = await fetch(`${API_BASE_URL}/admin/users`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('📡 Response status:', response.status);
      console.log('📡 Response headers:', response.headers);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('📊 API Response:', data);
      
      if (data.success) {
        console.log('✅ Users fetched successfully:', data.data.length, 'users');
        console.log('👥 User data structure:', data.data);
        setUsers(data.data);
        setFilteredUsers(data.data);
      } else {
        console.error('❌ API returned error:', data.message);
      }
    } catch (error) {
      console.error('❌ Error fetching users:', error);
    } finally {
      setUsersLoading(false);
    }
  };


  const handleDeleteUser = async (userId) => {
    const userToDelete = users.find(u => u._id === userId);
    const userName = userToDelete?.fullName || userToDelete?.businessName || 'this user';
    const userEmail = userToDelete?.email;
    
    if (window.confirm(`Are you sure you want to delete ${userName}? This action cannot be undone and the user will be notified via email.`)) {
      try {
        const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
        const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        });
        
        const data = await response.json();
        console.log('Delete user response:', data);
        
        if (response.ok && data.success) {
          toast.success(`✅ User deleted! Notification email sent to ${userEmail}`);
          
          // Refetch users to update the list in real-time
          await fetchUsers();
          
          console.log('✅ User list refreshed');
        } else {
          toast.error(data.message || 'Failed to delete user');
        }
      } catch (error) {
        console.error('❌ Error deleting user:', error);
        toast.error(error?.message || 'Failed to delete user. Please try again.');
      }
    }
  };

  // Fetch feedback data
  const fetchFeedback = async () => {
    try {
      setFeedbackLoading(true);
      console.log('💬 Fetching feedback from API...');
      
      const response = await api.get('admin/feedback');
      console.log('📊 Feedback API Response:', response);
      
      if (response && response.success) {
        const feedback = response.data || [];
        console.log('✅ Feedback fetched successfully:', feedback.length, 'entries');
        setFeedbackData(feedback);
        setFilteredFeedback(feedback);
        
        // Calculate feedback stats
        calculateFeedbackStats(feedback);
      }
    } catch (error) {
      console.error('❌ Error fetching feedback:', error);
    } finally {
      setFeedbackLoading(false);
    }
  };

  // Calculate feedback statistics
  const calculateFeedbackStats = (feedback) => {
    if (feedback.length === 0) {
      setFeedbackStats({
        averageRating: 0,
        totalFeedback: 0,
        responseRate: 0,
        trend: 0
      });
      return;
    }

    // Calculate average rating
    const totalRating = feedback.reduce((sum, item) => sum + (item.rating || 0), 0);
    const averageRating = totalRating / feedback.length;

    // Calculate response rate (feedback count / total users * 100)
    const responseRate = users.length > 0 ? (feedback.length / users.length) * 100 : 0;

    // Calculate trend (compare last 7 days vs previous 7 days)
    const now = new Date();
    const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    const fourteenDaysAgo = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);

    const recentFeedback = feedback.filter(f => new Date(f.date) >= sevenDaysAgo);
    const previousFeedback = feedback.filter(f => 
      new Date(f.date) >= fourteenDaysAgo && new Date(f.date) < sevenDaysAgo
    );

    const trend = previousFeedback.length > 0 
      ? ((recentFeedback.length - previousFeedback.length) / previousFeedback.length) * 100 
      : recentFeedback.length > 0 ? 100 : 0;

    setFeedbackStats({
      averageRating: averageRating.toFixed(1),
      totalFeedback: feedback.length,
      responseRate: responseRate.toFixed(1),
      trend: trend.toFixed(1)
    });
  };

  // Delete feedback
  const handleDeleteFeedback = async (feedbackId) => {
    if (window.confirm('Are you sure you want to delete this feedback?')) {
      try {
        await api.delete(`/admin/feedback/${feedbackId}`);
        const updatedFeedback = feedbackData.filter(f => f._id !== feedbackId);
        setFeedbackData(updatedFeedback);
        setFilteredFeedback(updatedFeedback);
        calculateFeedbackStats(updatedFeedback);
      } catch (error) {
        console.error('Error deleting feedback:', error);
        alert('Failed to delete feedback. Please try again.');
      }
    }
  };

  // Export feedback to CSV
  const exportFeedbackToCSV = () => {
    const headers = ['Date', 'User Name', 'Business', 'Email', 'Rating', 'Message'];
    const csvData = filteredFeedback.map(f => [
      new Date(f.date).toLocaleDateString(),
      f.userId?.fullName || 'Unknown',
      f.userId?.businessName || 'N/A',
      f.userId?.email || 'N/A',
      f.rating,
      `"${f.message?.replace(/"/g, '""') || ''}"`
    ]);

    const csvContent = [
      headers.join(','),
      ...csvData.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `tanaw_feedback_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Fetch connectivity status
  const fetchConnectivityStatus = async () => {
    try {
      const response = await api.get('admin/connectivity/status');
      if (response && response.success) {
        setSystemStatus(response.data);
      }
    } catch (error) {
      console.error('❌ Error fetching connectivity status:', error);
    }
  };

  // Fetch API usage metrics
  const fetchApiMetrics = async (period = '7d', specificDate = null) => {
    try {
      let url = `admin/connectivity/api-metrics?period=${period}`;
      
      // Add specific date parameter for historical data filtering
      if (specificDate) {
        url += `&date=${specificDate}`;
        console.log(`📅 Fetching API metrics for specific date: ${specificDate}`);
      }
      
      const response = await api.get(url);
      if (response && response.success) {
        setApiMetrics(response.data);
        console.log(`📊 API metrics fetched for ${specificDate || period}:`, response.data);
      }
    } catch (error) {
      console.error('❌ Error fetching API metrics:', error);
    }
  };

  // Fetch database stats
  const fetchDatabaseStats = async (specificDate = null) => {
    try {
      let url = 'admin/connectivity/database-stats';
      
      // Add specific date parameter for historical data filtering
      if (specificDate) {
        url += `?date=${specificDate}`;
        console.log(`📅 Fetching database stats for specific date: ${specificDate}`);
      }
      
      const response = await api.get(url);
      if (response && response.success) {
        setDatabaseStats(response.data);
        console.log(`📊 Database stats fetched for ${specificDate || 'all time'}:`, response.data);
      }
    } catch (error) {
      console.error('❌ Error fetching database stats:', error);
    }
  };

  // Export usage report
  const exportUsageReport = () => {
    const headers = ['Date', 'Total Tokens', 'API Calls', 'Estimated Cost'];
    const csvData = apiMetrics.timeline.map(day => [
      `${day._id.year}-${String(day._id.month).padStart(2, '0')}-${String(day._id.day).padStart(2, '0')}`,
      day.totalTokens,
      day.totalCalls,
      `$${day.totalCost.toFixed(4)}`
    ]);

    const csvContent = [
      headers.join(','),
      ...csvData.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `tanaw_usage_report_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const sidebarItems = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'activeUsers', label: 'Active Users', icon: Users },
    { id: 'userFeedback', label: 'User Feedback', icon: MessageSquare },
    { id: 'connectivity', label: 'Connectivity & Usage', icon: Activity }
  ];

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Date Filter for Overview */}
      <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <label className="text-sm font-medium text-gray-700">Filter Overview Data:</label>
          </div>
          <input
            type="date"
            value={overviewDateFilter}
            onChange={(e) => setOverviewDateFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
          />
          {overviewDateFilter && (
            <button
              onClick={() => setOverviewDateFilter('')}
              className="px-3 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition text-sm flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
              Clear
            </button>
          )}
          <span className="text-xs text-gray-500 ml-auto">
            {overviewDateFilter ? `Showing data for: ${new Date(overviewDateFilter).toLocaleDateString()}` : 'Showing all time data'}
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Object.entries(analyticsData.overview).map(([key, data]) => {
          const cardConfig = {
            totalDatasets: { 
              label: 'Total Datasets', 
              icon: BarChart3, 
              color: 'text-blue-600',
              bgColor: 'bg-blue-50'
            },
            chartsGenerated: { 
              label: 'Charts Generated', 
              icon: Activity, 
              color: 'text-green-600',
              bgColor: 'bg-green-50'
            },
            registeredUsers: { 
              label: 'Registered Users', 
              icon: Users, 
              color: 'text-purple-600',
              bgColor: 'bg-purple-50'
            },
            activeUsers: { 
              label: 'Active Users', 
              icon: UserPlus, 
              color: 'text-orange-600',
              bgColor: 'bg-orange-50'
            }
          };
          
          const config = cardConfig[key];
          const Icon = config.icon;
          
          return (
            <div key={key} className="group relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 hover:shadow-xl transition-all duration-300 transform hover:scale-105">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
              <div className="relative z-10 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    {config.label}
                  </p>
                  <p className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mt-1">
                    {data.value.toLocaleString()}
                  </p>
                  <div className="flex items-center mt-2">
                    {data.trend === 'up' ? (
                      <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
                    )}
                    <span className={`text-sm font-medium ${
                      data.trend === 'up' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {data.change > 0 ? '+' : ''}{data.change}%
                    </span>
                  </div>
                </div>
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl blur-sm opacity-20 group-hover:opacity-30 transition-opacity"></div>
                  <div className={`relative p-3 ${config.bgColor} rounded-xl`}>
                  <Icon className={`h-6 w-6 ${config.color}`} />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Real Charts */}
      <AdminCharts analyticsData={analyticsData} />

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Object.entries(analyticsData.detailed).map(([key, value]) => {
          const metricConfig = {
            totalUsers: { label: 'Total Users', icon: Users },
            newUsersThisMonth: { label: 'New Users (Month)', icon: UserPlus },
            totalDatasets: { label: 'Total Datasets', icon: BarChart3 },
            avgChartsPerDataset: { label: 'Avg Charts/Dataset', icon: Activity }
          };
          
          const config = metricConfig[key];
          const Icon = config.icon;
          
          return (
            <div key={key} className="group relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 hover:shadow-xl transition-all duration-300 transform hover:scale-105">
              <div className="absolute inset-0 bg-gradient-to-br from-gray-500/5 to-slate-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
              <div className="relative z-10 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    {config.label}
                  </p>
                  <p className="text-2xl font-bold bg-gradient-to-r from-gray-600 to-slate-600 bg-clip-text text-transparent mt-1">
                    {typeof value === 'number' ? value.toLocaleString() : value}
                  </p>
                </div>
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-gray-500 to-slate-500 rounded-xl blur-sm opacity-20 group-hover:opacity-30 transition-opacity"></div>
                  <div className="relative h-16 w-20 bg-gradient-to-t from-gray-100 to-gray-50 rounded-xl flex items-end shadow-lg">
                    <div className="w-full h-3/4 bg-gradient-to-t from-gray-400 to-gray-500 rounded-t-xl"></div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );


  const renderUserFeedback = () => {
    // Calculate rating distribution
    const ratingDistribution = [5, 4, 3, 2, 1].map(rating => ({
      rating,
      count: feedbackData.filter(f => f.rating === rating).length,
      percentage: feedbackData.length > 0 
        ? ((feedbackData.filter(f => f.rating === rating).length / feedbackData.length) * 100).toFixed(0)
        : 0
    }));
    
    // Calculate AI-specific average ratings
    const calculateAIAverages = () => {
      const aiRatings = { charts: [], forecasts: [], insights: [], aiQuality: [] };
      
      feedbackData.forEach(feedback => {
        if (!feedback.message) return;
        
        const chartsMatch = feedback.message.match(/\[Charts: (\d+)\/5\]/);
        const forecastsMatch = feedback.message.match(/\[Forecasts: (\d+)\/5\]/);
        const insightsMatch = feedback.message.match(/\[Insights: (\d+)\/5\]/);
        const aiQualityMatch = feedback.message.match(/\[AI Quality: ([\d.]+)\/5\]/);
        
        if (chartsMatch) aiRatings.charts.push(parseInt(chartsMatch[1]));
        if (forecastsMatch) aiRatings.forecasts.push(parseInt(forecastsMatch[1]));
        if (insightsMatch) aiRatings.insights.push(parseInt(insightsMatch[1]));
        if (aiQualityMatch) aiRatings.aiQuality.push(parseFloat(aiQualityMatch[1]));
      });
      
      return {
        charts: aiRatings.charts.length > 0 ? (aiRatings.charts.reduce((a, b) => a + b, 0) / aiRatings.charts.length).toFixed(1) : 'N/A',
        forecasts: aiRatings.forecasts.length > 0 ? (aiRatings.forecasts.reduce((a, b) => a + b, 0) / aiRatings.forecasts.length).toFixed(1) : 'N/A',
        insights: aiRatings.insights.length > 0 ? (aiRatings.insights.reduce((a, b) => a + b, 0) / aiRatings.insights.length).toFixed(1) : 'N/A',
        aiQuality: aiRatings.aiQuality.length > 0 ? (aiRatings.aiQuality.reduce((a, b) => a + b, 0) / aiRatings.aiQuality.length).toFixed(1) : 'N/A',
        count: aiRatings.charts.length
      };
    };
    
    const aiAverages = calculateAIAverages();

    return (
    <div className="space-y-6">
        {/* AI Quality Analytics (NEW!) */}
        {aiAverages.count > 0 && (
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl shadow-lg border border-purple-200 p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900">AI Analytics Quality Metrics</h3>
                <p className="text-sm text-gray-600">{aiAverages.count} detailed AI feedback submissions</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white/80 rounded-xl p-4 border border-purple-200">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span className="text-xs font-medium text-gray-600">Overall AI Quality</span>
                </div>
                <div className="flex items-center gap-2">
                  <p className="text-2xl font-bold text-purple-600">{aiAverages.aiQuality}</p>
                  <span className="text-sm text-gray-500">/ 5.0</span>
                </div>
              </div>
              <div className="bg-white/80 rounded-xl p-4 border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <span className="text-xs font-medium text-gray-600">Chart Quality</span>
                </div>
                <div className="flex items-center gap-2">
                  <p className="text-2xl font-bold text-blue-600">{aiAverages.charts}</p>
                  <span className="text-sm text-gray-500">/ 5.0</span>
                </div>
              </div>
              <div className="bg-white/80 rounded-xl p-4 border border-green-200">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  <span className="text-xs font-medium text-gray-600">Forecast Accuracy</span>
                </div>
                <div className="flex items-center gap-2">
                  <p className="text-2xl font-bold text-green-600">{aiAverages.forecasts}</p>
                  <span className="text-sm text-gray-500">/ 5.0</span>
                </div>
              </div>
              <div className="bg-white/80 rounded-xl p-4 border border-pink-200">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-4 h-4 text-pink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-xs font-medium text-gray-600">Insights Helpfulness</span>
                </div>
                <div className="flex items-center gap-2">
                  <p className="text-2xl font-bold text-pink-600">{aiAverages.insights}</p>
                  <span className="text-sm text-gray-500">/ 5.0</span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Feedback Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Average Rating Card */}
          <div className="group relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 hover:shadow-xl transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-yellow-500/5 to-orange-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium text-gray-600">Average Rating</p>
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-xl blur-sm opacity-20"></div>
                  <div className="relative p-3 bg-gradient-to-br from-yellow-100 to-orange-100 rounded-xl">
                    <Star className="h-5 w-5 text-yellow-600 fill-yellow-600" />
                  </div>
                </div>
              </div>
              <div className="flex items-baseline gap-2">
                <p className="text-3xl font-bold bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent">
                  {feedbackStats.averageRating}
                </p>
                <p className="text-lg text-gray-500">/ 5.0</p>
              </div>
              <div className="flex items-center gap-1 mt-2">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`h-4 w-4 ${
                      i < Math.round(feedbackStats.averageRating)
                        ? 'text-yellow-400 fill-yellow-400'
                        : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
        </div>
      </div>
      
          {/* Total Feedback Card */}
          <div className="group relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 hover:shadow-xl transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium text-gray-600">Total Feedback</p>
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl blur-sm opacity-20"></div>
                  <div className="relative p-3 bg-gradient-to-br from-blue-100 to-purple-100 rounded-xl">
                    <MessageSquare className="h-5 w-5 text-blue-600" />
                  </div>
                </div>
              </div>
              <p className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {feedbackStats.totalFeedback}
              </p>
              <p className="text-sm text-gray-500 mt-1">submissions</p>
          </div>
        </div>
        
          {/* Response Rate Card */}
          <div className="group relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 hover:shadow-xl transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-emerald-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium text-gray-600">Response Rate</p>
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl blur-sm opacity-20"></div>
                  <div className="relative p-3 bg-gradient-to-br from-green-100 to-emerald-100 rounded-xl">
                    <Users className="h-5 w-5 text-green-600" />
          </div>
        </div>
              </div>
              <div className="flex items-baseline gap-2">
                <p className="text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                  {feedbackStats.responseRate}%
                </p>
              </div>
              <p className="text-sm text-gray-500 mt-1">of users responded</p>
            </div>
          </div>

          {/* Trend Card */}
          <div className="group relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 hover:shadow-xl transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-pink-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium text-gray-600">7-Day Trend</p>
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-indigo-500 to-pink-500 rounded-xl blur-sm opacity-20"></div>
                  <div className="relative p-3 bg-gradient-to-br from-indigo-100 to-pink-100 rounded-xl">
                    {parseFloat(feedbackStats.trend) >= 0 ? (
                      <TrendingUp className="h-5 w-5 text-green-600" />
                    ) : (
                      <TrendingDown className="h-5 w-5 text-red-600" />
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-baseline gap-2">
                <p className={`text-3xl font-bold bg-gradient-to-r ${
                  parseFloat(feedbackStats.trend) >= 0
                    ? 'from-green-600 to-emerald-600'
                    : 'from-red-600 to-rose-600'
                } bg-clip-text text-transparent`}>
                  {parseFloat(feedbackStats.trend) >= 0 ? '+' : ''}{feedbackStats.trend}%
                </p>
              </div>
              <p className="text-sm text-gray-500 mt-1">vs previous week</p>
            </div>
          </div>
        </div>

        {/* Rating Distribution Chart */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <BarChart className="h-5 w-5 text-blue-600" />
              Rating Distribution
            </h3>
          </div>
          <div className="space-y-4">
            {ratingDistribution.map(({ rating, count, percentage }) => (
              <div key={rating} className="flex items-center gap-3">
                <div className="flex items-center gap-1 w-20">
                  <span className="text-sm font-medium text-gray-700">{rating}</span>
                  <Star className="h-4 w-4 text-yellow-400 fill-yellow-400" />
                </div>
                <div className="flex-1 h-8 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-yellow-400 to-orange-500 transition-all duration-500 flex items-center justify-end pr-2"
                    style={{ width: `${percentage}%` }}
                  >
                    {percentage > 0 && (
                      <span className="text-xs font-medium text-white">{percentage}%</span>
                    )}
                  </div>
                </div>
                <span className="text-sm font-medium text-gray-600 w-16 text-right">{count} votes</span>
              </div>
            ))}
          </div>
        </div>

        {/* Feedback Table */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <MessageSquare className="h-5 w-5 text-blue-600" />
                  User Feedback
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  {filteredFeedback.length} of {feedbackData.length} feedback entries
                </p>
              </div>
              <button
                onClick={exportFeedbackToCSV}
                disabled={filteredFeedback.length === 0}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="h-4 w-4" />
                Export CSV
              </button>
            </div>

            {/* Filters */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Filter by Rating</label>
                <select
                  value={ratingFilter}
                  onChange={(e) => setRatingFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Ratings</option>
                  <option value="5">5 Stars</option>
                  <option value="4">4 Stars</option>
                  <option value="3">3 Stars</option>
                  <option value="2">2 Stars</option>
                  <option value="1">1 Star</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Filter by Date</label>
                <select
                  value={dateFilter}
                  onChange={(e) => setDateFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Time</option>
                  <option value="today">Today</option>
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
                <input
                  type="text"
                  placeholder="Search feedback..."
                  value={feedbackSearchQuery}
                  onChange={(e) => setFeedbackSearchQuery(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Feedback Table */}
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">User</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Rating</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Feedback</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Date</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {feedbackLoading ? (
                  <tr>
                    <td colSpan="5" className="px-4 py-8 text-center">
                      <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                        <span className="ml-2 text-gray-600">Loading feedback...</span>
                      </div>
                    </td>
                  </tr>
                ) : filteredFeedback.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-4 py-8 text-center text-gray-500">
                      {feedbackData.length === 0 
                        ? 'No feedback received yet' 
                        : 'No feedback matches your filters'}
                    </td>
                  </tr>
                ) : (
                  filteredFeedback.map((feedback) => {
                    // Parse AI-specific ratings from message
                    const parseAIRatings = (message) => {
                      const ratings = {
                        aiQuality: null,
                        charts: null,
                        forecasts: null,
                        insights: null,
                        dataset: null,
                        cleanMessage: message
                      };
                      
                      if (!message) return ratings;
                      
                      // Extract ratings using regex
                      const aiQualityMatch = message.match(/\[AI Quality: ([\d.]+)\/5\]/);
                      const chartsMatch = message.match(/\[Charts: (\d+)\/5\]/);
                      const forecastsMatch = message.match(/\[Forecasts: (\d+)\/5\]/);
                      const insightsMatch = message.match(/\[Insights: (\d+)\/5\]/);
                      const datasetMatch = message.match(/\[Dataset: ([^\]]+)\]/);
                      
                      if (aiQualityMatch) ratings.aiQuality = parseFloat(aiQualityMatch[1]);
                      if (chartsMatch) ratings.charts = parseInt(chartsMatch[1]);
                      if (forecastsMatch) ratings.forecasts = parseInt(forecastsMatch[1]);
                      if (insightsMatch) ratings.insights = parseInt(insightsMatch[1]);
                      if (datasetMatch) ratings.dataset = datasetMatch[1];
                      
                      // Remove metadata from message
                      ratings.cleanMessage = message
                        .replace(/\[AI Quality: [\d.]+\/5\]/g, '')
                        .replace(/\[Charts: \d+\/5\]/g, '')
                        .replace(/\[Forecasts: \d+\/5\]/g, '')
                        .replace(/\[Insights: \d+\/5\]/g, '')
                        .replace(/\[Dataset: [^\]]+\]/g, '')
                        .trim();
                      
                      return ratings;
                    };
                    
                    const aiRatings = parseAIRatings(feedback.message);
                    const hasAIRatings = aiRatings.aiQuality || aiRatings.charts || aiRatings.forecasts || aiRatings.insights;
                    
                    return (
                    <tr key={feedback._id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
                              <span className="text-white font-semibold text-sm">
                                {feedback.userId?.fullName ? feedback.userId.fullName.split(' ').map(n => n[0]).join('').toUpperCase() : 'U'}
                              </span>
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{feedback.userId?.fullName || 'Unknown User'}</div>
                            <div className="text-sm text-gray-500">{feedback.userId?.email || 'No Email'}</div>
                            <div className="text-xs text-gray-400">{feedback.userId?.businessName || 'No Business'}</div>
                            {aiRatings.dataset && (
                              <div className="text-xs text-blue-600 mt-1 flex items-center gap-1">
                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                {aiRatings.dataset}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="space-y-2">
                          {/* Overall Rating */}
                          <div>
                            <div className="flex items-center gap-1">
                              {[...Array(5)].map((_, i) => (
                                <Star
                                  key={i}
                                  className={`h-4 w-4 ${
                                    i < feedback.rating
                                      ? 'text-yellow-400 fill-yellow-400'
                                      : 'text-gray-300'
                                  }`}
                                />
                              ))}
                              <span className="ml-1 text-sm font-medium text-gray-700">
                                {feedback.rating}.0
                              </span>
                            </div>
                            <span className="text-xs text-gray-500">Overall</span>
                          </div>
                          
                          {/* AI Quality Breakdown */}
                          {hasAIRatings && (
                            <div className="mt-2 pt-2 border-t border-gray-200 space-y-1">
                              {aiRatings.aiQuality && (
                                <div className="flex items-center gap-2">
                                  <svg className="w-3 h-3 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                  </svg>
                                  <span className="text-xs font-medium text-gray-700">AI: {aiRatings.aiQuality.toFixed(1)}/5</span>
                                </div>
                              )}
                              {aiRatings.charts && (
                                <div className="flex items-center gap-2">
                                  <svg className="w-3 h-3 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                  </svg>
                                  <span className="text-xs font-medium text-gray-700">Charts: {aiRatings.charts}/5</span>
                                </div>
                              )}
                              {aiRatings.forecasts && (
                                <div className="flex items-center gap-2">
                                  <svg className="w-3 h-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                  </svg>
                                  <span className="text-xs font-medium text-gray-700">Forecasts: {aiRatings.forecasts}/5</span>
                                </div>
                              )}
                              {aiRatings.insights && (
                                <div className="flex items-center gap-2">
                                  <svg className="w-3 h-3 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                  </svg>
                                  <span className="text-xs font-medium text-gray-700">Insights: {aiRatings.insights}/5</span>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-4">
                        <div className="space-y-2">
                          {aiRatings.cleanMessage && (
                            <p className="text-sm text-gray-900 max-w-md">
                              {aiRatings.cleanMessage}
                            </p>
                          )}
                          {feedback.type === 'ai_analytics_feedback' && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                              🧠 AI Analytics Feedback
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {new Date(feedback.date).toLocaleDateString()}
                        </div>
                        <div className="text-xs text-gray-500">
                          {new Date(feedback.date).toLocaleTimeString()}
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={() => handleDeleteFeedback(feedback._id)}
                          className="text-red-600 hover:text-red-900 transition-colors"
                          title="Delete feedback"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination Info */}
          {filteredFeedback.length > 0 && (
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
              <div className="text-center text-sm text-gray-600">
                Showing <span className="font-medium text-blue-600">{filteredFeedback.length}</span> of{' '}
                <span className="font-medium text-blue-600">{feedbackData.length}</span> feedback entries
                {feedbackSearchQuery && (
                  <span className="ml-2 text-gray-500">(filtered by "{feedbackSearchQuery}")</span>
                )}
              </div>
            </div>
          )}
      </div>
    </div>
  );
  };

  const renderConnectivity = () => {
    const getStatusIcon = (status) => {
      switch(status) {
        case 'connected':
        case 'online':
        case 'active':
          return <CheckCircle className="h-6 w-6 text-green-500" />;
        case 'disconnected':
        case 'offline':
        case 'inactive':
          return <XCircle className="h-6 w-6 text-red-500" />;
        case 'checking':
          return <AlertCircle className="h-6 w-6 text-yellow-500 animate-pulse" />;
        default:
          return <AlertCircle className="h-6 w-6 text-gray-400" />;
      }
    };

    const getStatusColor = (status) => {
      switch(status) {
        case 'connected':
        case 'online':
        case 'active':
          return 'from-green-500 to-emerald-500';
        case 'disconnected':
        case 'offline':
        case 'inactive':
          return 'from-red-500 to-rose-500';
        case 'checking':
          return 'from-yellow-500 to-orange-500';
        default:
          return 'from-gray-500 to-slate-500';
      }
    };

    return (
    <div className="space-y-6">
        {/* Connection Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* MongoDB Status */}
          <div className="group relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 hover:shadow-xl transition-all duration-300">
            <div className={`absolute inset-0 bg-gradient-to-br ${getStatusColor(systemStatus.mongodb?.status)}/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity`}></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  {getStatusIcon(systemStatus.mongodb?.status)}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">MongoDB</h3>
                    <p className="text-sm text-gray-500">Database Connection</p>
                  </div>
                </div>
                <Database className="h-8 w-8 text-gray-400" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Status:</span>
                  <span className={`text-sm font-medium capitalize ${
                    systemStatus.mongodb?.status === 'connected' ? 'text-green-600' :
                    systemStatus.mongodb?.status === 'checking' ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    {systemStatus.mongodb?.status || 'Unknown'}
                  </span>
                </div>
                {systemStatus.mongodb?.responseTime > 0 && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Response Time:</span>
                    <span className="text-sm font-medium text-gray-900">{systemStatus.mongodb.responseTime}ms</span>
                  </div>
                )}
                {systemStatus.mongodb?.database && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Database:</span>
                    <span className="text-sm font-medium text-gray-900">{systemStatus.mongodb.database}</span>
                  </div>
                )}
              </div>
        </div>
      </div>
      
          {/* Flask Service Status */}
          <div className="group relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 hover:shadow-xl transition-all duration-300">
            <div className={`absolute inset-0 bg-gradient-to-br ${getStatusColor(systemStatus.flaskService?.status)}/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity`}></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  {getStatusIcon(systemStatus.flaskService?.status)}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Flask Analytics</h3>
                    <p className="text-sm text-gray-500">Analytics Service</p>
                  </div>
                </div>
                <Server className="h-8 w-8 text-gray-400" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Status:</span>
                  <span className={`text-sm font-medium capitalize ${
                    systemStatus.flaskService?.status === 'online' ? 'text-green-600' :
                    systemStatus.flaskService?.status === 'checking' ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    {systemStatus.flaskService?.status || 'Unknown'}
                  </span>
                </div>
                {systemStatus.flaskService?.responseTime > 0 && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Response Time:</span>
                    <span className="text-sm font-medium text-gray-900">{systemStatus.flaskService.responseTime}ms</span>
                  </div>
                )}
                {systemStatus.flaskService?.url && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 truncate">URL:</span>
                    <span className="text-xs font-medium text-gray-500 truncate max-w-[150px]">{systemStatus.flaskService.url}</span>
                  </div>
                )}
              </div>
          </div>
        </div>
        
          {/* OpenAI API Status */}
          <div className="group relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 hover:shadow-xl transition-all duration-300">
            <div className={`absolute inset-0 bg-gradient-to-br ${getStatusColor(systemStatus.openaiApi?.status)}/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity`}></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  {getStatusIcon(systemStatus.openaiApi?.status)}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">OpenAI API</h3>
                    <p className="text-sm text-gray-500">AI Processing</p>
          </div>
        </div>
                <Cpu className="h-8 w-8 text-gray-400" />
      </div>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Status:</span>
                  <span className={`text-sm font-medium capitalize ${
                    systemStatus.openaiApi?.status === 'active' ? 'text-green-600' :
                    systemStatus.openaiApi?.status === 'checking' ? 'text-yellow-600' :
                    'text-gray-600'
                  }`}>
                    {systemStatus.openaiApi?.status || 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Configured:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {systemStatus.openaiApi?.configured ? 'Yes' : 'No'}
                  </span>
                </div>
                {systemStatus.openaiApi?.lastUsed && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Last Used:</span>
                    <span className="text-xs font-medium text-gray-500">
                      {new Date(systemStatus.openaiApi.lastUsed).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

          {/* API Usage Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-6">
          {/* Total Tokens Card */}
          <div className="group relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 hover:shadow-xl transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium text-gray-600">Total Tokens Used</p>
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl blur-sm opacity-20"></div>
                  <div className="relative p-3 bg-gradient-to-br from-blue-100 to-purple-100 rounded-xl">
                    <Zap className="h-5 w-5 text-blue-600" />
                  </div>
                </div>
              </div>
              <p className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {(apiMetrics.openai?.totalTokens || 0).toLocaleString()}
              </p>
              <p className="text-sm text-gray-500 mt-1">tokens ({usagePeriod})</p>
            </div>
          </div>

          {/* Total API Calls Card */}
          <div className="group relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 hover:shadow-xl transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-emerald-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium text-gray-600">Total API Calls</p>
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl blur-sm opacity-20"></div>
                  <div className="relative p-3 bg-gradient-to-br from-green-100 to-emerald-100 rounded-xl">
                    <Activity className="h-5 w-5 text-green-600" />
                  </div>
                </div>
              </div>
              <p className="text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                {(apiMetrics.openai?.totalCalls || 0).toLocaleString()}
              </p>
              <p className="text-sm text-gray-500 mt-1">requests ({usagePeriod})</p>
            </div>
          </div>

          {/* Estimated Cost Card */}
          <div className="group relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 hover:shadow-xl transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-yellow-500/5 to-orange-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium text-gray-600">Estimated Cost</p>
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-xl blur-sm opacity-20"></div>
                  <div className="relative p-3 bg-gradient-to-br from-yellow-100 to-orange-100 rounded-xl">
                    <span className="text-xl font-bold text-yellow-600">$</span>
                  </div>
                </div>
              </div>
              <p className="text-3xl font-bold bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent">
                ${(apiMetrics.openai?.totalCost || 0).toFixed(4)}
              </p>
              <p className="text-sm text-gray-500 mt-1">USD ({usagePeriod})</p>
            </div>
          </div>

          {/* Avg Response Time Card */}
          <div className="group relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 hover:shadow-xl transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-pink-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-indigo-500 to-pink-500 rounded-xl blur-sm opacity-20"></div>
                  <div className="relative p-3 bg-gradient-to-br from-indigo-100 to-pink-100 rounded-xl">
                    <Clock className="h-5 w-5 text-indigo-600" />
                  </div>
                </div>
              </div>
              <p className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-pink-600 bg-clip-text text-transparent">
                {Math.round(apiMetrics.openai?.avgResponseTime || 0)}
              </p>
              <p className="text-sm text-gray-500 mt-1">milliseconds</p>
            </div>
          </div>

          {/* Success Rate Card */}
          <div className="group relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 hover:shadow-xl transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-teal-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium text-gray-600">Success Rate</p>
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-xl blur-sm opacity-20"></div>
                  <div className="relative p-3 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-xl">
                    <CheckCircle className="h-5 w-5 text-emerald-600" />
                  </div>
                </div>
              </div>
              <p className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                {((apiMetrics.openai?.successRate || 0) * 100).toFixed(1)}%
              </p>
              <p className="text-sm text-gray-500 mt-1">API calls successful</p>
            </div>
          </div>

          {/* Prompt Tokens Card */}
          <div className="group relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 hover:shadow-xl transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium text-gray-600">Prompt Tokens</p>
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-xl blur-sm opacity-20"></div>
                  <div className="relative p-3 bg-gradient-to-br from-cyan-100 to-blue-100 rounded-xl">
                    <span className="text-lg font-bold text-cyan-600">P</span>
                  </div>
                </div>
              </div>
              <p className="text-3xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
                {(apiMetrics.openai?.totalPromptTokens || 0).toLocaleString()}
              </p>
              <p className="text-sm text-gray-500 mt-1">tokens ({usagePeriod})</p>
            </div>
          </div>
        </div>

        {/* Date Filter & Export for Usage Analytics */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <BarChart className="h-5 w-5 text-blue-600" />
                Usage Analytics
              </h3>
              <p className="text-sm text-gray-500 mt-1">Monitor API usage and system performance</p>
            </div>
            <div className="flex items-center gap-3">
              {/* Date Picker (Replaced dropdown) */}
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <input
                  type="date"
                  value={connectivityDateFilter}
                  onChange={(e) => setConnectivityDateFilter(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                />
              </div>
              {connectivityDateFilter && (
                <button
                  onClick={() => setConnectivityDateFilter('')}
                  className="px-3 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition text-sm flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  Clear
                </button>
              )}
              <button
                onClick={exportUsageReport}
                disabled={!apiMetrics.timeline || apiMetrics.timeline.length === 0}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="h-4 w-4" />
                Export Report
              </button>
            </div>
          </div>
          {connectivityDateFilter && (
            <div className="mt-3 text-xs text-gray-600 flex items-center gap-2">
              <span className="text-blue-600 font-medium">📅 Showing data for: {new Date(connectivityDateFilter).toLocaleDateString()}</span>
            </div>
          )}
        </div>

        {/* API Endpoint Breakdown */}
        {apiMetrics.endpoints && apiMetrics.endpoints.length > 0 && (
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
              <Activity className="h-5 w-5 text-blue-600" />
              API Endpoint Breakdown
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Service</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Endpoint</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-600">Calls</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-600">Avg Response</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-600">Success Rate</th>
                  </tr>
                </thead>
                <tbody>
                  {apiMetrics.endpoints.map((endpoint, index) => (
                    <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {endpoint._id.service}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-sm text-gray-600">
                        {endpoint._id.endpoint || 'N/A'}
                      </td>
                      <td className="py-3 px-4 text-right font-medium">
                        {endpoint.count.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right text-gray-600">
                        {Math.round(endpoint.avgResponseTime)}ms
                      </td>
                      <td className="py-3 px-4 text-right">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          endpoint.successRate >= 0.9 
                            ? 'bg-green-100 text-green-800' 
                            : endpoint.successRate >= 0.7 
                            ? 'bg-yellow-100 text-yellow-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {(endpoint.successRate * 100).toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Database Statistics */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 relative">
          <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2 relative z-10">
            <HardDrive className="h-5 w-5 text-blue-600" />
            Database Statistics
          </h3>
          
          {/* Collection Stats */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
            {Object.entries(databaseStats.collections || {}).map(([key, collection]) => (
              <div key={key} className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 border border-gray-200">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">{collection.icon}</span>
                  <span className="text-xs font-medium text-gray-600">{collection.name}</span>
                </div>
                <p className="text-2xl font-bold text-gray-900">{collection.count.toLocaleString()}</p>
              </div>
            ))}
          </div>

          {/* Database Health */}
          {databaseStats.databaseStats && Object.keys(databaseStats.databaseStats).length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-6 border-t border-gray-200">
              <div className="text-center">
                <p className="text-sm text-gray-600">Total Size</p>
                <p className="text-xl font-bold text-gray-900">{databaseStats.databaseStats.size} MB</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Data Size</p>
                <p className="text-xl font-bold text-gray-900">{databaseStats.databaseStats.dataSize} MB</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Index Size</p>
                <p className="text-xl font-bold text-gray-900">{databaseStats.databaseStats.indexSize} MB</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Collections</p>
                <p className="text-xl font-bold text-gray-900">{databaseStats.databaseStats.collections}</p>
              </div>
            </div>
          )}
        </div>

        {/* Recent Activity (Last 24h) */}
        {databaseStats.recentActivity && Object.keys(databaseStats.recentActivity).length > 0 && (
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Recent Activity (Last 24 Hours)</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4">
                <p className="text-sm text-gray-600 mb-1">New Users</p>
                <p className="text-3xl font-bold text-blue-600">{databaseStats.recentActivity.newUsers || 0}</p>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4">
                <p className="text-sm text-gray-600 mb-1">New Datasets</p>
                <p className="text-3xl font-bold text-green-600">{databaseStats.recentActivity.newDatasets || 0}</p>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4">
                <p className="text-sm text-gray-600 mb-1">New Feedback</p>
                <p className="text-3xl font-bold text-purple-600">{databaseStats.recentActivity.newFeedback || 0}</p>
              </div>
              <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4">
                <p className="text-sm text-gray-600 mb-1">API Calls</p>
                <p className="text-3xl font-bold text-orange-600">{databaseStats.recentActivity.apiCalls || 0}</p>
              </div>
            </div>
          </div>
        )}
    </div>
  );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 font-sans">
      <div className="flex flex-col md:flex-row">
        {/* Mobile Menu Overlay */}
        {isMobile && mobileMenuOpen && (
          <div 
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            onClick={() => setMobileMenuOpen(false)}
          ></div>
        )}

        {/* Sidebar */}
        <div className={`
          ${isMobile 
            ? `fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-300 ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}`
            : `${sidebarCollapsed ? 'w-16' : 'w-64'} transition-all duration-300`
          } 
          bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-white shadow-2xl
          overflow-hidden flex flex-col
        `}>
          {/* Background Pattern */}
          <div className="absolute inset-0 opacity-5">
            <div className="absolute inset-0" style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
              backgroundSize: '20px 20px'
            }}></div>
          </div>
          
          <div className="p-4 md:p-6 relative z-10">
            <div className="flex items-center justify-between">
              {!sidebarCollapsed && (
                <div className="flex items-center space-x-3 group cursor-pointer">
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl blur-sm opacity-70 group-hover:opacity-90 transition-opacity"></div>
                    <div className="relative w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 transform group-hover:scale-105">
                      <span className="text-xl font-bold text-white">T</span>
                    </div>
                  </div>
                  <div className="flex flex-col">
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent tracking-tight">
                      TANAW
                    </h1>
                    <p className="text-sm text-slate-300 font-medium">Admin Dashboard</p>
                  </div>
                </div>
              )}
              {!isMobile && (
                <button
                  onClick={toggleSidebar}
                  className="p-2 hover:bg-white/10 rounded-lg transition-all duration-200 hover:scale-105"
                >
                  {sidebarCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
                </button>
              )}
            </div>
          </div>
          
          <nav className="mt-8 space-y-2 flex-1 overflow-y-auto px-2">
            {sidebarItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id);
                    if (isMobile) setMobileMenuOpen(false);
                  }}
                  className={`w-full flex items-center ${sidebarCollapsed && !isMobile ? 'px-2 justify-center' : 'px-4'} py-4 text-left transition-all duration-300 transform hover:scale-105 rounded-lg ${
                    activeTab === item.id 
                      ? 'bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-white shadow-lg backdrop-blur-sm border-r-4 border-blue-400' 
                      : 'text-slate-300 hover:bg-white/10 hover:text-white hover:shadow-md'
                  }`}
                  title={sidebarCollapsed && !isMobile ? item.label : ''}
                >
                  <div className="relative">
                    <Icon className="h-5 w-5" />
                    {activeTab === item.id && (
                      <div className="absolute -inset-1 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-lg blur-sm"></div>
                    )}
                  </div>
                  {(!sidebarCollapsed || isMobile) && <span className="ml-3 font-semibold text-sm">{item.label}</span>}
                </button>
              );
            })}
          </nav>

          {/* Admin Actions */}
          <div className="mt-auto p-4 border-t border-white/20 relative z-50">
            <div className="space-y-2">
              <button
                onClick={() => {
                  console.log('🔴 Logout button clicked');
                  setShowLogoutModal(true);
                }}
                className="w-full flex items-center px-4 py-3 text-red-200 hover:bg-red-500/20 hover:text-white transition-all duration-200 rounded-lg cursor-pointer"
                title={sidebarCollapsed && !isMobile ? 'Logout' : ''}
              >
                <LogOut size={20} />
                {(!sidebarCollapsed || isMobile) && <span className="ml-3 font-semibold">Logout</span>}
              </button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-hidden">
          {/* Header */}
          <div className="bg-white/90 backdrop-blur-lg border-b border-gray-200/50 px-4 md:px-6 py-4 md:py-5 shadow-sm relative">
            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-5">
              <div className="absolute inset-0" style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23000000' fill-opacity='0.1'%3E%3Cpath d='M20 20c0-5.5-4.5-10-10-10s-10 4.5-10 10 4.5 10 10 10 10-4.5 10-10zm10 0c0-5.5-4.5-10-10-10s-10 4.5-10 10 4.5 10 10 10 10-4.5 10-10z'/%3E%3C/g%3E%3C/svg%3E")`,
                backgroundSize: '30px 30px'
              }}></div>
            </div>
            
            <div className="flex items-center justify-between gap-2 relative z-10">
              {/* Mobile Menu Button */}
              {isMobile && (
                <button
                  onClick={toggleSidebar}
                  className="p-2 hover:bg-blue-50 rounded-lg transition-all duration-200 hover:scale-105"
                >
                  <Menu size={20} className="text-gray-700" />
                </button>
              )}

              {/* Breadcrumb - Hidden on small mobile */}
              <div className="hidden sm:flex items-center space-x-2 md:space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full animate-pulse" style={{animationDelay: '0.5s'}}></div>
                </div>
                <span className="text-sm md:text-base text-gray-600 font-medium">
                  Dashboard &gt; <span className="font-bold text-gray-800 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    {sidebarItems.find(item => item.id === activeTab)?.label}
                  </span>
                </span>
              </div>
              

              {/* Header Actions */}
              <div className="flex items-center space-x-1 md:space-x-3">
                {/* Admin Avatar */}
                <div className="relative group">
                  <div className="w-7 h-7 md:w-8 md:h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 transform group-hover:scale-105">
                    <span className="text-white text-xs md:text-sm font-bold">A</span>
                  </div>
                  <div className="absolute -top-1 -right-1 w-2.5 h-2.5 md:w-3 md:h-3 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
                </div>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="h-full overflow-y-auto p-3 md:p-6 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="relative">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
                  <div className="absolute inset-0 animate-ping rounded-full h-12 w-12 border border-purple-300 opacity-20"></div>
                </div>
              </div>
            ) : (
              <>
                {activeTab === 'overview' && renderOverview()}
                {activeTab === 'activeUsers' && (
                  <div className="space-y-6">
                    {/* TANAW User Management Header */}
                    <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 relative overflow-hidden">
                      {/* Background Pattern - pointer-events-none to allow clicks through */}
                      <div className="absolute inset-0 opacity-5 pointer-events-none">
                        <div className="absolute inset-0 pointer-events-none" style={{
                          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
                          backgroundSize: '20px 20px'
                        }}></div>
                      </div>
                      <div className="relative z-10 flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
                        <div>
                          <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                            TANAW User Management
                          </h2>
                          <p className="text-gray-600 mt-1">Manage TANAW user accounts and business information</p>
                        </div>
                        
                      </div>
                      
                      {/* TANAW-specific Filters */}
                      <div className="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Role Filter</label>
                          <select 
                            value={roleFilter}
                            onChange={(e) => setRoleFilter(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          >
                            <option value="">All Roles</option>
                            <option value="admin">Admin</option>
                            <option value="user">User</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Registration Date</label>
                          <select 
                            value={userDateFilter}
                            onChange={(e) => setUserDateFilter(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          >
                            <option value="">All Time</option>
                            <option value="today">Today</option>
                            <option value="week">This Week</option>
                            <option value="month">This Month</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
                          <input
                            type="text"
                            placeholder="Search by name, email, or business..."
                            value={userSearchQuery}
                            onChange={(e) => setUserSearchQuery(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                        </div>
                      </div>

                      {/* TANAW User Table */}
                      <div className="relative z-10 overflow-x-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                            <tr>
                              <th className="px-3 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">User</th>
                              <th className="px-3 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider hidden sm:table-cell">Business</th>
                              <th className="px-3 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Role</th>
                              <th className="px-3 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Datasets</th>
                              <th className="px-3 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider hidden md:table-cell">Registered</th>
                              <th className="px-3 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Actions</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {usersLoading ? (
                              <tr>
                                <td colSpan="6" className="px-4 py-8 text-center">
                                  <div className="flex items-center justify-center">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                                    <span className="ml-2 text-gray-600">Loading TANAW users...</span>
                                  </div>
                                </td>
                              </tr>
                            ) : filteredUsers.length === 0 ? (
                              <tr>
                                <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                                  No TANAW users found
                                </td>
                              </tr>
                            ) : (
                              filteredUsers.map((user) => (
                                <tr key={user._id} className="hover:bg-gray-50 transition-all duration-200 hover:shadow-sm">
                                  <td className="px-3 py-4">
                                    <div className="flex items-center">
                                      <div className="flex-shrink-0 h-10 w-10">
                                        <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center shadow-md">
                                          <span className="text-white font-bold text-sm">
                                            {user.fullName ? user.fullName.split(' ').map(n => n[0]).join('').toUpperCase() : 'U'}
                                          </span>
                                        </div>
                                      </div>
                                      <div className="ml-3">
                                        <div className="text-sm font-semibold text-gray-900">{user.fullName || 'No Name'}</div>
                                        <div className="text-xs text-gray-500">{user.email || 'No Email'}</div>
                                      </div>
                                    </div>
                                  </td>
                                  <td className="px-3 py-4 hidden sm:table-cell">
                                    <div className="text-sm text-gray-900 font-medium">{user.businessName || 'No Business'}</div>
                                  </td>
                                  <td className="px-3 py-4">
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${
                                      user.role === 'admin' 
                                        ? 'bg-purple-100 text-purple-800' 
                                        : 'bg-green-100 text-green-800'
                                    }`}>
                                      {user.role === 'admin' ? 'Admin' : user.role === 'user' ? 'User' : 'Unknown'}
                                    </span>
                                  </td>
                                  <td className="px-3 py-4">
                                    <div className="text-sm text-gray-900">
                                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${
                                        user.datasetCount > 0 
                                          ? 'bg-green-100 text-green-800' 
                                          : 'bg-gray-100 text-gray-600'
                                      }`}>
                                        {user.datasetCount || 0} datasets
                                      </span>
                                    </div>
                                  </td>
                                  <td className="px-3 py-4 hidden md:table-cell text-sm text-gray-500">
                                    <div className="flex flex-col">
                                      <span className="font-medium">{user.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'Unknown'}</span>
                                      <span className="text-xs text-gray-400">
                                        {user.createdAt ? new Date(user.createdAt).toLocaleTimeString() : ''}
                                      </span>
                                    </div>
                                  </td>
                                  <td className="px-3 py-4 text-sm font-medium">
                                    <div className="flex items-center space-x-2">
                                      {/* Actions Dropdown - Click-based */}
                                      <div className="relative">
                                        <button 
                                          onClick={() => setOpenDropdownId(openDropdownId === user._id ? null : user._id)}
                                          className="flex items-center px-3 py-2 text-xs bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-all duration-200 hover:scale-105 border border-gray-200"
                                        >
                                          <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                                          </svg>
                                          <span className="hidden sm:inline">Actions</span>
                                          <svg className="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                          </svg>
                                        </button>
                                        
                                        {/* Actions Dropdown Menu - Click-based, now functional! */}
                                        {openDropdownId === user._id && (
                                          <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
                                            <div className="py-1">
                                              <button 
                                                onClick={() => {
                                                  setSelectedUserProfile(user);
                                                  setShowUserProfileModal(true);
                                                  setOpenDropdownId(null);
                                                }}
                                                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 transition-colors"
                                              >
                                                <UserPlus className="w-4 h-4 mr-3 text-blue-600" />
                                                View Profile
                                              </button>
                                              <div className="border-t border-gray-100"></div>
                                              <button 
                                                onClick={() => {
                                                  handleDeleteUser(user._id);
                                                  setOpenDropdownId(null);
                                                }}
                                                className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                                              >
                                                <Trash2 className="w-4 h-4 mr-3" />
                                                Delete User
                                              </button>
                                            </div>
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  </td>
                                </tr>
                              ))
                            )}
                          </tbody>
                        </table>
                      </div>

                      {/* TANAW User Summary */}
                      <div className="relative z-10 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4 mt-6">
                        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-blue-600">{users.length}</div>
                            <div className="text-sm text-gray-600">Total Users</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-purple-600">{users.filter(u => u.role === 'admin').length}</div>
                            <div className="text-sm text-gray-600">Admins</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">{users.filter(u => u.role === 'user').length}</div>
                            <div className="text-sm text-gray-600">Regular Users</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-orange-600">{users.filter(u => (u.datasetCount || 0) > 0).length}</div>
                            <div className="text-sm text-gray-600">Active Users</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-purple-600">{users.reduce((sum, u) => sum + (u.datasetCount || 0), 0)}</div>
                            <div className="text-sm text-gray-600">Total Datasets</div>
                          </div>
                        </div>
                        
                        {/* Additional Real-time Statistics */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-200">
                          <div className="text-center">
                            <div className="text-lg font-bold text-indigo-600">
                              {users.filter(u => {
                                const createdAt = new Date(u.createdAt);
                                const oneWeekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
                                return createdAt >= oneWeekAgo;
                              }).length}
                            </div>
                            <div className="text-xs text-gray-600">New This Week</div>
                          </div>
                          <div className="text-center">
                            <div className="text-lg font-bold text-emerald-600">
                              {users.filter(u => {
                                const createdAt = new Date(u.createdAt);
                                const oneMonthAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
                                return createdAt >= oneMonthAgo;
                              }).length}
                            </div>
                            <div className="text-xs text-gray-600">New This Month</div>
                          </div>
                          <div className="text-center">
                            <div className="text-lg font-bold text-amber-600">
                              {users.filter(u => (u.datasetCount || 0) >= 5).length}
                            </div>
                            <div className="text-xs text-gray-600">Power Users (5+ datasets)</div>
                          </div>
                          <div className="text-center">
                            <div className="text-lg font-bold text-rose-600">
                              {users.filter(u => (u.datasetCount || 0) === 0).length}
                            </div>
                            <div className="text-xs text-gray-600">Inactive Users</div>
                          </div>
                        </div>
                        
                        {/* Real-time User Activity Insights */}
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <h4 className="text-sm font-semibold text-gray-700 mb-3">Real-time User Activity Insights</h4>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="bg-white/60 rounded-lg p-3">
                              <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-600">Avg Datasets per User</span>
                                <span className="text-lg font-bold text-blue-600">
                                  {users.length > 0 ? (users.reduce((sum, u) => sum + (u.datasetCount || 0), 0) / users.length).toFixed(1) : '0'}
                                </span>
                              </div>
                            </div>
                            <div className="bg-white/60 rounded-lg p-3">
                              <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-600">Most Active User</span>
                                <span className="text-lg font-bold text-green-600">
                                  {users.length > 0 ? Math.max(...users.map(u => u.datasetCount || 0)) : '0'} datasets
                                </span>
                              </div>
                            </div>
                            <div className="bg-white/60 rounded-lg p-3">
                              <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-600">User Engagement Rate</span>
                                <span className="text-lg font-bold text-purple-600">
                                  {users.length > 0 ? ((users.filter(u => (u.datasetCount || 0) > 0).length / users.length) * 100).toFixed(1) : '0'}%
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        <div className="mt-4 text-center text-sm text-gray-600">
                          Showing <span className="font-medium text-blue-600">{filteredUsers.length}</span> of <span className="font-medium text-blue-600">{users.length}</span> users
                          {userSearchQuery && (
                            <span className="ml-2 text-gray-500">(filtered by "{userSearchQuery}")</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                {activeTab === 'userFeedback' && renderUserFeedback()}
                {activeTab === 'connectivity' && renderConnectivity()}
              </>
            )}
          </div>
        </div>
      </div>

      {/* User Profile Modal */}
      {showUserProfileModal && selectedUserProfile && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[100] p-4">
          <div className="bg-white rounded-2xl shadow-2xl border border-gray-200/50 p-6 max-w-2xl w-full relative z-[101] max-h-[90vh] overflow-y-auto">
            {/* Close Button */}
            <button
              onClick={() => {
                setShowUserProfileModal(false);
                setSelectedUserProfile(null);
              }}
              className="absolute top-4 right-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X size={20} className="text-gray-500" />
            </button>

            {/* Profile Header */}
            <div className="flex items-center space-x-4 mb-6 pb-6 border-b border-gray-200">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center shadow-lg">
                <span className="text-white text-3xl font-bold">
                  {selectedUserProfile.fullName ? selectedUserProfile.fullName.split(' ').map(n => n[0]).join('').toUpperCase() : 'U'}
                </span>
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-gray-900">
                  {selectedUserProfile.fullName || 'No Name Provided'}
                </h2>
                <p className="text-gray-500">{selectedUserProfile.email}</p>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold mt-2 ${
                  selectedUserProfile.role === 'admin' 
                    ? 'bg-purple-100 text-purple-800' 
                    : 'bg-green-100 text-green-800'
                }`}>
                  {selectedUserProfile.role === 'admin' ? 'Admin' : 'User'}
                </span>
              </div>
            </div>

            {/* Profile Details */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Profile Information</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <label className="text-xs font-semibold text-gray-500 uppercase">Full Name</label>
                  <p className="text-sm font-medium text-gray-900 mt-1">
                    {selectedUserProfile.fullName || 'Not provided'}
                  </p>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <label className="text-xs font-semibold text-gray-500 uppercase">Business Name</label>
                  <p className="text-sm font-medium text-gray-900 mt-1">
                    {selectedUserProfile.businessName || 'Not provided'}
                  </p>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <label className="text-xs font-semibold text-gray-500 uppercase">Email Address</label>
                  <p className="text-sm font-medium text-gray-900 mt-1">
                    {selectedUserProfile.email}
                  </p>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <label className="text-xs font-semibold text-gray-500 uppercase">Role</label>
                  <p className="text-sm font-medium text-gray-900 mt-1">
                    {selectedUserProfile.role === 'admin' ? 'Administrator' : 'User'}
                  </p>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <label className="text-xs font-semibold text-gray-500 uppercase">Datasets</label>
                  <p className="text-sm font-medium text-gray-900 mt-1">
                    {selectedUserProfile.datasetCount || 0} dataset(s)
                  </p>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <label className="text-xs font-semibold text-gray-500 uppercase">Registration Date</label>
                  <p className="text-sm font-medium text-gray-900 mt-1">
                    {selectedUserProfile.createdAt ? new Date(selectedUserProfile.createdAt).toLocaleDateString() : 'Unknown'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {selectedUserProfile.createdAt ? new Date(selectedUserProfile.createdAt).toLocaleTimeString() : ''}
                  </p>
                </div>
              </div>

              {/* Activity Summary */}
              <div className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-200">
                <h4 className="text-sm font-semibold text-gray-900 mb-3">Activity Summary</h4>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-blue-600">
                      {selectedUserProfile.datasetCount || 0}
                    </div>
                    <div className="text-xs text-gray-600">Datasets</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-purple-600">
                      {selectedUserProfile.chartsGenerated || 0}
                    </div>
                    <div className="text-xs text-gray-600">Charts</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-green-600">
                      {selectedUserProfile.role === 'admin' ? 'Admin' : 'Active'}
                    </div>
                    <div className="text-xs text-gray-600">Status</div>
                  </div>
                </div>
              </div>

              {/* User ID (for reference) */}
              <div className="mt-4 p-3 bg-gray-100 rounded-lg">
                <label className="text-xs font-semibold text-gray-500 uppercase">User ID</label>
                <p className="text-xs font-mono text-gray-600 mt-1 break-all">
                  {selectedUserProfile._id}
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end space-x-3 mt-6 pt-6 border-t border-gray-200">
              <button
                onClick={() => {
                  setShowUserProfileModal(false);
                  setSelectedUserProfile(null);
                }}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
              >
                Close
              </button>
              <button
                onClick={() => {
                  handleDeleteUser(selectedUserProfile._id);
                  setShowUserProfileModal(false);
                  setSelectedUserProfile(null);
                }}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-medium flex items-center"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete User
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Logout Modal - Responsive */}
      {showLogoutModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[100] p-4">
          <div className="bg-white rounded-2xl shadow-2xl border border-gray-200/50 p-4 md:p-6 max-w-md w-full relative z-[101]">
            <div className="flex items-center space-x-3 mb-3 md:mb-4">
              <div className="p-2 bg-red-100 rounded-full">
                <LogOut className="text-red-600" size={20} />
              </div>
              <h3 className="text-base md:text-lg font-bold text-gray-800">Confirm Logout</h3>
            </div>
            <p className="text-sm md:text-base text-gray-600 mb-4 md:mb-6">
              Are you sure you want to logout from the admin dashboard? You'll be redirected to the home page.
            </p>
            <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
              <button
                onClick={() => {
                  console.log('❌ Cancel clicked');
                  setShowLogoutModal(false);
                }}
                className="flex-1 px-4 py-2.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm md:text-base font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  console.log('✅ Logout confirmed');
                  handleLogout();
                }}
                className="flex-1 px-4 py-2.5 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm md:text-base font-semibold"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toast Notifications */}
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#4ade80',
              secondary: '#fff',
            },
          },
        }}
      />
    </div>
  );
};

export default AdminDashboard;

