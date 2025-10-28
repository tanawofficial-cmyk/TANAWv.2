import Analytics from "../models/Analytics.js";
import User from "../models/User.js";

// Track analytics events
export const trackEvent = async (req, res) => {
  try {
    const event = req.body;
    
    // Store the event in database
    const analyticsEvent = new Analytics({
      type: event.type,
      action: event.action || null,
      page: event.page || null,
      userId: event.userId,
      sessionId: event.sessionId,
      timestamp: new Date(event.timestamp),
      details: event.details || {},
      metadata: {
        userAgent: event.userAgent,
        referrer: event.referrer,
        fileName: event.fileName,
        fileSize: event.fileSize,
        fileType: event.fileType,
        chartType: event.chartType,
        datasetSize: event.datasetSize,
        downloadType: event.downloadType
      }
    });

    await analyticsEvent.save();
    
    res.status(200).json({ success: true });
  } catch (error) {
    console.error("Analytics tracking error:", error);
    res.status(500).json({ success: false, error: error.message });
  }
};

// Get analytics data for admin dashboard
export const getAnalyticsData = async (req, res) => {
  try {
    const { range = '7d', date } = req.query;
    
    // Calculate date range
    const now = new Date();
    let startDate, endDate;
    
    // If specific date is provided, filter for that single day only
    if (date) {
      startDate = new Date(date);
      startDate.setHours(0, 0, 0, 0);
      
      endDate = new Date(date);
      endDate.setHours(23, 59, 59, 999);
      
      console.log(`📅 Filtering analytics for specific date: ${date}`);
      console.log(`   Start: ${startDate.toISOString()}`);
      console.log(`   End: ${endDate.toISOString()}`);
    } else {
      // Normal range filtering
      switch (range) {
        case '1d':
          startDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
          break;
        case '7d':
          startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          break;
        case '30d':
          startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
          break;
        default:
          startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      }
      endDate = now;
    }

    // Build query based on whether we have a specific date or range
    const timestampQuery = date 
      ? { $gte: startDate, $lte: endDate }  // Specific date
      : { $gte: startDate };                 // Range from startDate to now

    // Get total datasets (file uploads)
    const totalDatasets = await Analytics.countDocuments({
      type: 'file_upload',
      timestamp: timestampQuery
    });

    // Get charts generated
    const chartsGenerated = await Analytics.countDocuments({
      type: 'chart_generation',
      timestamp: timestampQuery
    });

    // Get registered users from User model
    const registeredUsers = await User.countDocuments();
    
    // Get new users this month
    const startOfMonth = new Date();
    startOfMonth.setDate(1);
    startOfMonth.setHours(0, 0, 0, 0);
    const newUsersThisMonth = await User.countDocuments({
      createdAt: { $gte: startOfMonth }
    });

    // Get active users (users who have uploaded at least one dataset)
    const activeUsers = await User.find({ datasetCount: { $gt: 0 } }).select('_id');

    // Get downloads
    const downloads = await Analytics.countDocuments({
      type: 'download',
      timestamp: timestampQuery
    });

    // Calculate real growth rates by comparing with previous period
    const previousStartDate = new Date(startDate.getTime() - (now.getTime() - startDate.getTime()));
    const previousEndDate = new Date(startDate.getTime() - 1);
    
    // Get previous period data
    const previousDatasets = await Analytics.countDocuments({
      type: 'file_upload',
      timestamp: { $gte: previousStartDate, $lte: previousEndDate }
    });
    
    const previousCharts = await Analytics.countDocuments({
      type: 'chart_generation',
      timestamp: { $gte: previousStartDate, $lte: previousEndDate }
    });
    
    const previousUsers = await User.countDocuments({
      createdAt: { $gte: previousStartDate, $lte: previousEndDate }
    });
    
    // Get previous active users (users who had datasets in the previous period)
    // Note: This is an approximation since we can't easily track historical datasetCount
    const previousActiveUsers = await User.find({ 
      datasetCount: { $gt: 0 },
      createdAt: { $lte: previousEndDate }
    }).select('_id');
    
    // Calculate percentage changes
    const datasetsGrowth = previousDatasets > 0 ? ((totalDatasets - previousDatasets) / previousDatasets) * 100 : 0;
    const chartsGrowth = previousCharts > 0 ? ((chartsGenerated - previousCharts) / previousCharts) * 100 : 0;
    const usersGrowth = previousUsers > 0 ? ((registeredUsers - previousUsers) / previousUsers) * 100 : 0;
    const activeUsersGrowth = previousActiveUsers.length > 0 ? ((activeUsers.length - previousActiveUsers.length) / previousActiveUsers.length) * 100 : 0;
    
    // Debug logging for real calculations
    console.log("📊 Real Analytics Calculations:");
    console.log(`   Current Period (${startDate.toISOString().split('T')[0]} to ${now.toISOString().split('T')[0]}):`);
    console.log(`     Datasets: ${totalDatasets}, Charts: ${chartsGenerated}, Users: ${registeredUsers}, Active: ${activeUsers.length}`);
    console.log(`   Previous Period (${previousStartDate.toISOString().split('T')[0]} to ${previousEndDate.toISOString().split('T')[0]}):`);
    console.log(`     Datasets: ${previousDatasets}, Charts: ${previousCharts}, Users: ${previousUsers}, Active: ${previousActiveUsers.length}`);
    console.log(`   Growth Rates:`);
    console.log(`     Datasets: ${datasetsGrowth.toFixed(2)}%, Charts: ${chartsGrowth.toFixed(2)}%, Users: ${usersGrowth.toFixed(2)}%, Active: ${activeUsersGrowth.toFixed(2)}%`);

    // Calculate average charts per dataset
    const avgChartsPerDataset = totalDatasets > 0 ? Math.round(chartsGenerated / totalDatasets) : 0;

    // Get breakdown for charts
    // If specific date, show HOURLY breakdown; otherwise show last 7 DAYS
    const dailyDatasets = [];
    const dailyCharts = [];
    const dailyActiveUsers = [];
    const timeLabels = [];
    
    if (date) {
      // For specific date, return HOURLY breakdown (24 hours: 00:00 to 23:00)
      console.log(`📊 Generating hourly breakdown for ${date}`);
      
      for (let hour = 0; hour < 24; hour++) {
        const hourStart = new Date(startDate);
        hourStart.setHours(hour, 0, 0, 0);
        
        const hourEnd = new Date(startDate);
        hourEnd.setHours(hour, 59, 59, 999);
        
        const datasetsCount = await Analytics.countDocuments({
          type: 'file_upload',
          timestamp: { $gte: hourStart, $lte: hourEnd }
        });
        
        const chartsCount = await Analytics.countDocuments({
          type: 'chart_generation',
          timestamp: { $gte: hourStart, $lte: hourEnd }
        });
        
        const activeUsersCount = await Analytics.distinct('userId', {
          timestamp: { $gte: hourStart, $lte: hourEnd }
        });
        
        dailyDatasets.push(datasetsCount);
        dailyCharts.push(chartsCount);
        dailyActiveUsers.push(activeUsersCount.length);
        
        // Format hour label (e.g., "00:00", "01:00", "14:00")
        timeLabels.push(`${String(hour).padStart(2, '0')}:00`);
      }
    } else {
      // Normal 7-day DAILY breakdown
      for (let i = 6; i >= 0; i--) {
        const dayStart = new Date(now);
        dayStart.setDate(dayStart.getDate() - i);
        dayStart.setHours(0, 0, 0, 0);
        
        const dayEnd = new Date(dayStart);
        dayEnd.setHours(23, 59, 59, 999);
        
        const datasetsCount = await Analytics.countDocuments({
          type: 'file_upload',
          timestamp: { $gte: dayStart, $lte: dayEnd }
        });
        
        const chartsCount = await Analytics.countDocuments({
          type: 'chart_generation',
          timestamp: { $gte: dayStart, $lte: dayEnd }
        });
        
        const activeUsersCount = await Analytics.distinct('userId', {
          timestamp: { $gte: dayStart, $lte: dayEnd }
        });
        
        dailyDatasets.push(datasetsCount);
        dailyCharts.push(chartsCount);
        dailyActiveUsers.push(activeUsersCount.length);
        
        // Format date label (e.g., "Oct 21", "Oct 22")
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        timeLabels.push(`${monthNames[dayStart.getMonth()]} ${dayStart.getDate()}`);
      }
    }

    const analyticsData = {
      overview: {
        totalDatasets: { 
          value: totalDatasets, 
          change: parseFloat(datasetsGrowth.toFixed(2)), 
          trend: datasetsGrowth >= 0 ? 'up' : 'down' 
        },
        chartsGenerated: { 
          value: chartsGenerated, 
          change: parseFloat(chartsGrowth.toFixed(2)), 
          trend: chartsGrowth >= 0 ? 'up' : 'down' 
        },
        registeredUsers: { 
          value: registeredUsers, 
          change: parseFloat(usersGrowth.toFixed(2)), 
          trend: usersGrowth >= 0 ? 'up' : 'down' 
        },
        activeUsers: { 
          value: activeUsers.length, 
          change: parseFloat(activeUsersGrowth.toFixed(2)), 
          trend: activeUsersGrowth >= 0 ? 'up' : 'down' 
        }
      },
      detailed: {
        totalUsers: registeredUsers,
        newUsersThisMonth: newUsersThisMonth,
        totalDatasets: totalDatasets,
        avgChartsPerDataset: avgChartsPerDataset
      },
      activities: {
        fileUploads: totalDatasets,
        chartGenerations: chartsGenerated,
        downloads: downloads
      },
      timeSeries: {
        dailyDatasets: dailyDatasets,
        dailyCharts: dailyCharts,
        dailyActiveUsers: dailyActiveUsers,
        labels: timeLabels, // NEW: Dynamic labels (hourly for specific date, daily for range)
        isHourlyView: !!date // NEW: Flag to indicate if it's hourly or daily view
      }
    };

    res.json({ success: true, data: analyticsData });
  } catch (error) {
    console.error("Analytics data error:", error);
    res.status(500).json({ success: false, error: error.message });
  }
};

// Get user metrics
export const getUserMetrics = async (req, res) => {
  try {
    // Get total registered users
    const totalUsers = await User.countDocuments();
    
    // Get active users (logged in within last 30 days)
    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
    const activeUsers = await User.countDocuments({
      lastLogin: { $gte: thirtyDaysAgo }
    });

    // Get new users this month
    const startOfMonth = new Date();
    startOfMonth.setDate(1);
    startOfMonth.setHours(0, 0, 0, 0);
    
    const newUsersThisMonth = await User.countDocuments({
      createdAt: { $gte: startOfMonth }
    });

    res.json({
      success: true,
      data: {
        totalUsers,
        activeUsers,
        newUsersThisMonth
      }
    });
  } catch (error) {
    console.error("User metrics error:", error);
    res.status(500).json({ success: false, error: error.message });
  }
};