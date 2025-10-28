//Dashboard.js 
import React, { useState, useEffect } from "react";
import api, { setSessionExpiredCallback } from "../api";
import analytics from "../services/analytics";
import toast, { Toaster } from "react-hot-toast";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts';
import StickyHeader from "../components/StickyHeader";
import FeedbackModal from "../components/FeedbackModal";
import html2canvas from 'html2canvas';


const UserDashboard = () => {
  // 🧠 Core States
  const [user, setUser] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [dateFilter, setDateFilter] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  
  // 🆕 Dataset-specific states
  const [datasets, setDatasets] = useState([]); // Store multiple datasets
  const [selectedDatasetId, setSelectedDatasetId] = useState(null); // Selected dataset for viewing
  const [selectedDatasetData, setSelectedDatasetData] = useState(null); // Full data of selected dataset
  const [charts, setCharts] = useState([]); // Store fetched charts
  
  // 🔒 Session expiration state
  const [showSessionExpiredModal, setShowSessionExpiredModal] = useState(false);

  // 🗑️ Confirmation modals state
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [datasetToDelete, setDatasetToDelete] = useState(null);
  
  // 🔄 Loading states to prevent duplicate calls
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  // 📊 Chart display mode state
  const [chartDisplayMode, setChartDisplayMode] = useState('single'); // 'single' or 'grid'
  
  // 🔝 Back to top state
  const [showBackToTop, setShowBackToTop] = useState(false);

  // 📥 Download menu state
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);

  // 💬 Feedback modal state
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [uploadCount, setUploadCount] = useState(0);

  // 🔝 Back to top function
  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };

  // 💬 Handle feedback submission
  const handleFeedbackSubmitted = (rating, feedback) => {
    console.log('Feedback submitted:', { rating, feedback });
    // Reset upload count after feedback submission
    setUploadCount(0);
    console.log('🔄 Upload count reset to 0');
  };

  // 🔄 Reset upload count when user changes
  useEffect(() => {
    if (user) {
      console.log('👤 User loaded, resetting upload count to 0');
      setUploadCount(0);
    }
  }, [user]);

  // 🔒 Handle session expiration - redirect to login
  const handleRelogin = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.removeItem("role");
    window.location.href = "/login";
  };

  // ✅ Load user info and datasets
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;
    
    // Track page view and user activity
    analytics.trackPageView('user-dashboard');
    analytics.trackAction('dashboard_visit', { page: 'user-dashboard' });
    
    // Load user profile
    api.get("/users/me", { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => {
        setUser(res);
        // Set the user ID in analytics service for proper tracking
        if (res.id || res._id) {
          analytics.setUserId(res.id || res._id);
          console.log("📊 Analytics user ID set to:", res.id || res._id);
        }
        // Load user's datasets after user is loaded
        loadUserDatasets();
      })
      .catch((error) => {
        console.error("Failed to load user profile:", error);
        toast.error("Failed to load user profile");
      });
    
    // Track periodic activity to keep user "active"
    const activityInterval = setInterval(() => {
      analytics.trackAction('user_activity', { 
        type: 'heartbeat',
        timestamp: new Date().toISOString()
      });
    }, 5 * 60 * 1000); // Every 5 minutes
    
    return () => clearInterval(activityInterval);
  }, []);

  // 📂 Load user's datasets from backend
  const loadUserDatasets = async () => {
    try {
      console.log("📂 Loading user datasets from backend...");
      const response = await api.get("/files/datasets");
      
      console.log("📂 Full API response:", response);
      console.log("📂 Response data:", response.data);
      console.log("📂 Response success:", response.data?.success);
      
      // Handle both response formats (with and without success wrapper)
      let userDatasets;
      if (response.data.success && response.data.data) {
        // Original format: {success: true, data: {datasets: [...]}}
        userDatasets = response.data.data.datasets;
      } else if (response.data.datasets) {
        // Intercepted format: {datasets: [...]}
        userDatasets = response.data.datasets;
      } else {
        console.error("❌ Unexpected response format:", response.data);
        return;
      }
      
      if (userDatasets) {
        console.log(`📂 Loaded ${userDatasets.length} datasets from backend`);
        console.log("📂 Raw datasets:", userDatasets);
        
        // Transform backend datasets to frontend format
        const transformedDatasets = userDatasets.map(dataset => {
          const uploadDate = new Date(dataset.uploadDate);
          
          return {
            id: dataset.id,
            analysisId: dataset.analysisId,
            name: dataset.name,
            fileName: dataset.fileName,
            uploadDate: uploadDate, // Keep as Date object for filtering
            uploadDateString: uploadDate.toLocaleDateString(), // String for display
            uploadTime: uploadDate.toLocaleTimeString(),
            rowCount: dataset.rowCount,
            missingValues: dataset.missingValues,
            columns: dataset.columns,
            datasetType: dataset.datasetType,
            datasetConfidence: dataset.datasetConfidence,
            suggestedAnalytics: dataset.suggestedAnalytics,
            status: dataset.status,
            visualizationData: dataset.visualizationData || [],
            analysisData: dataset.analysisData
          };
        });
        
        console.log("📂 Transformed datasets:", transformedDatasets);
        setDatasets(transformedDatasets);
        console.log("📂 User datasets loaded successfully:", transformedDatasets);
      } else {
        console.error("❌ No datasets found in response");
      }
    } catch (error) {
      console.error("❌ Failed to load user datasets:", error);
      console.error("❌ Error details:", error.response?.data);
      // Don't show error to user as this is a background operation
    }
  };

  // 🔄 Refresh datasets (useful for manual refresh)
  const refreshDatasets = async () => {
    if (isRefreshing) {
      console.log("🔄 Already refreshing, skipping duplicate call");
      return;
    }
    
    setIsRefreshing(true);
    console.log("🔄 Refreshing datasets...");
    await loadUserDatasets();
    toast.success("📂 Datasets refreshed successfully!");
    setIsRefreshing(false);
  };

  // 🔒 Register session expiration callback
  useEffect(() => {
    setSessionExpiredCallback(() => {
      setShowSessionExpiredModal(true);
    });
  }, []);

  // 🔝 Back to top scroll listener
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      setShowBackToTop(scrollTop > 300); // Show button after scrolling 300px
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // 📥 Close download menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showDownloadMenu && !event.target.closest('.download-menu-container')) {
        setShowDownloadMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showDownloadMenu]);

  // ✅ Handle file input with validation
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    
    if (!file) return;
    
    // Validate file type
    const allowedTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];
    
    const allowedExtensions = ['.csv', '.xls', '.xlsx'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
      toast.error('❌ Invalid file type. Please upload CSV or Excel (.csv, .xls, .xlsx) files only.');
      e.target.value = ''; // Clear the input
      return;
    }
    
    // Validate file size (max 10MB for performance)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      toast.error('❌ File too large. Please upload files smaller than 10MB for optimal performance.');
      e.target.value = '';
      return;
    }
    
    setSelectedFile(file);
    toast.success(`✓ File selected: ${file.name}`, { duration: 2000 });
  };


  // ✅ Upload and analyze file
  const handleUpload = async () => {
    if (isUploading) {
      console.log("📤 Already uploading, skipping duplicate call");
      return;
    }
    
    if (!selectedFile) return toast.error("⚠️ Please select a file first.");

    const token = localStorage.getItem("token");
    if (!token) return toast.error("❌ Please log in to upload.");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setIsUploading(true);
      setUploading(true);

      console.log("📤 Uploading file to backend...");

      const res = await api.post("/files/upload-clean", formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      });

      console.log("📥 TANAW Response:", res);
      console.log("📥 Response Type:", typeof res);

      // Track file upload analytics
      analytics.trackFileUpload(
        selectedFile.name,
        selectedFile.size,
        selectedFile.type
      );

      // 🧠 Normalize possible backend responses - Axios returns data in res.data
      // Handle case where response might be a string (needs parsing)
      let data;
      if (typeof res === 'string') {
        console.log("📥 Response is string, parsing JSON...");
        // Replace NaN with null (NaN is not valid JSON) - handle both object properties and array elements
        const cleanedResponse = res.replace(/:\s*NaN/g, ': null').replace(/,\s*NaN/g, ', null').replace(/\[\s*NaN/g, '[null');
        data = JSON.parse(cleanedResponse);
      } else if (res && typeof res === 'object' && 'data' in res) {
        console.log("📥 Response has data property");
        data = res.data;
      } else {
        console.log("📥 Using response as-is");
        data = res;
      }
      
      console.log("📥 Normalized Data:", data);
      console.log("📥 Data Type:", typeof data);
      if (!data) {
        console.error("⚠️ No response from backend");
        return toast.error("Upload failed. No response received.");
      }

      // Check for success indicators - handle both old and new response formats
      // Use loose equality to handle type coercion
      const isSuccess = data.success === true || data.status === 'completed' || data.processed === true;
      console.log("🔍 Success validation:", { 
        success: data.success, 
        successType: typeof data.success,
        status: data.status, 
        statusType: typeof data.status,
        processed: data.processed, 
        processedType: typeof data.processed,
        isSuccess 
      });
      
      if (!isSuccess) {
        console.error("⚠️ Upload failed:", data);
        
        // Handle specific fallback errors with helpful messages
        const fallbackMessages = {
          'empty_dataset': '📋 Your file is empty. Please upload a file with data rows.',
          'no_columns': '📋 No columns detected. Please check your file format.',
          'insufficient_rows': '📋 Too few rows. Please upload a file with at least 2 rows of data.',
          'no_usable_columns': '🤔 We couldn\'t identify any usable columns in your dataset.\n\n💡 Tip: Ensure your file has columns like:\n• Date/Time columns\n• Sales/Amount columns\n• Product/Item names\n• Quantity values',
          'no_valid_data_after_cleaning': '⚠️ Your data contains invalid formats.\n\n📝 Please check for:\n• Valid date formats (e.g., 2024-01-15)\n• Numeric values for sales/amounts (no text)',
          'insufficient_valid_rows': '⚠️ Too few valid rows after data cleaning.\n\n💡 Please check your data quality and formats.',
          'no_charts_generated': `📊 No charts could be generated from your dataset.\n\n${data.suggestion || 'Please ensure your dataset has the required columns for analytics.'}`
        };
        
        const fallbackReason = data.fallback_reason || data.fallbackReason;
        const errorMessage = fallbackMessages[fallbackReason] || data?.message || "Upload failed. Please try again.";
        
        toast.error(errorMessage, { 
          duration: 6000,
          style: {
            maxWidth: '500px',
            whiteSpace: 'pre-line' // Allows \n to create line breaks
          }
        });
        return;
      }

      // 🔧 Normalize snake_case to camelCase
      const nextStep = data.next_step || data.nextStep;
      const processed = data.processed;
      const analysis = data.analysis;
      
      console.log("🔍 Response fields:", {
        nextStep: nextStep,
        processed: processed,
        hasAnalysis: !!analysis,
        dataKeys: Object.keys(data)
      });



      // 🧠 SME-Friendly Auto-Mapping: No confirmation dialog needed
      // The backend now automatically maps all columns and proceeds directly to analytics
      console.log("🤖 SME-Friendly Auto-Mapping: Skipping confirmation dialog");

      // 🎯 Handle complete analysis with visualizations
      if (data.status === "completed" || nextStep === "processing_complete" || nextStep === "analysis_complete") {
        console.log("✅ Completing analysis flow");
        toast.success("✅ File analyzed successfully!");
        
        // 🔄 Refresh datasets from backend (dataset is already saved)
        setTimeout(() => {
          loadUserDatasets();
          // ✅ Clear file selection after successful upload
          setSelectedFile(null);
        }, 1000);

        // 💬 Track uploads and show feedback modal every 3 uploads
        const newUploadCount = uploadCount + 1;
        setUploadCount(newUploadCount);
        console.log(`📊 Upload count: ${newUploadCount}/3`);
        
        // Only trigger modal if it's exactly 3, 6, 9, etc. (every 3 uploads)
        if (newUploadCount > 0 && newUploadCount % 3 === 0) {
          // Show feedback modal after 3 uploads
          console.log('🎯 Triggering feedback modal after 3 uploads');
          setTimeout(() => {
            setShowFeedbackModal(true);
          }, 2000); // Show after 2 seconds to let user see success message
        }
      }
    } catch (err) {
      console.error("❌ Upload failed", err);
      toast.error(err.response?.data?.message || "Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
      setUploading(false);
    }
  };

  // 🔍 Search and Date Filter Functionality (with useMemo to prevent unnecessary re-renders)
  const filteredDatasets = React.useMemo(() => {
    console.log("🔍 Filtering datasets...", { 
      totalDatasets: datasets.length, 
      searchTerm, 
      dateFilter 
    });
    
    const filtered = datasets.filter(dataset => {
      // Search filter - search in name and fileName
      const matchesSearch = !searchTerm || 
        dataset.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        dataset.fileName?.toLowerCase().includes(searchTerm.toLowerCase());
      
      // Date filter - compare dates properly (timezone-safe)
      let matchesDate = true;
      if (dateFilter) {
        try {
          // Parse filter date at midnight local time
          const filterDate = new Date(dateFilter + 'T00:00:00');
          
          // Parse dataset date
          const datasetDate = dataset.uploadDate instanceof Date 
            ? dataset.uploadDate 
            : new Date(dataset.uploadDate);
          
          // Check if dates are valid
          if (isNaN(filterDate.getTime()) || isNaN(datasetDate.getTime())) {
            console.warn("⚠️ Invalid date detected");
            matchesDate = true; // If invalid date, don't filter out
          } else {
            // Compare using local date components (ignores time and timezone)
            const filterYear = filterDate.getFullYear();
            const filterMonth = filterDate.getMonth();
            const filterDay = filterDate.getDate();
            
            const datasetYear = datasetDate.getFullYear();
            const datasetMonth = datasetDate.getMonth();
            const datasetDay = datasetDate.getDate();
            
            // EXACT DATE MATCH - compare year, month, and day separately
            matchesDate = (
              filterYear === datasetYear &&
              filterMonth === datasetMonth &&
              filterDay === datasetDay
            );
            
            console.log("📅 Date comparison:", {
              filterDate: `${filterYear}-${filterMonth + 1}-${filterDay}`,
              datasetDate: `${datasetYear}-${datasetMonth + 1}-${datasetDay}`,
              matchesDate
            });
          }
        } catch (error) {
          console.error("❌ Date comparison error:", error);
          matchesDate = true; // If error, don't filter out
        }
      }
      
      return matchesSearch && matchesDate;
    });
    
    console.log("🔍 Filtered results:", { 
      filteredCount: filtered.length, 
      totalCount: datasets.length 
    });
    
    return filtered;
  }, [datasets, searchTerm, dateFilter]);

  // 🗑️ Delete Dataset Function
  const handleDeleteDataset = async (dataset) => {
    try {
      console.log("🗑️ Deleting dataset:", dataset);
      
      const token = localStorage.getItem("token");
      if (!token) {
        toast.error("❌ Please log in to delete datasets.");
        return;
      }

      // Prevent double-clicks by checking if already deleting
      if (dataset.deleting) {
        console.log("🗑️ Already deleting dataset, skipping duplicate call");
        return;
      }
      
      // Mark as deleting to prevent duplicate calls
      setDatasets(prev => prev.map(d => 
        d.id === dataset.id ? { ...d, deleting: true } : d
      ));

      const response = await api.delete(`/files/datasets/${dataset.id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      console.log("🗑️ Delete response:", response);
      console.log("🗑️ Response message:", response.message);

      // Axios interceptor returns response.data directly, so 'response' IS the data
      // Response format: { success: true, message: "...", deletedDataset: {...} }
      const isSuccess = response.success === true || response.message?.includes("successfully");

      if (isSuccess) {
        toast.success("✅ Dataset deleted successfully!");
        
        // Remove from local state
        setDatasets(prev => prev.filter(d => d.id !== dataset.id));
        
        // If this was the selected dataset, clear selection
        if (selectedDatasetId === dataset.id) {
          setSelectedDatasetId(null);
          setSelectedDatasetData(null);
          setCharts([]);
        }
        
        // Close modal and clear deleting state
        setShowDeleteModal(false);
        setDatasetToDelete(null);
        } else {
        toast.error("❌ Failed to delete dataset");
      }
    } catch (error) {
      console.error("❌ Error deleting dataset:", error);
      toast.error(error.message || "Failed to delete dataset");
      
      // Clear deleting state on error
      setDatasets(prev => prev.map(d => 
        d.id === dataset.id ? { ...d, deleting: false } : d
      ));
    }
  };

  // 🗑️ Confirm Delete Dataset
  const confirmDeleteDataset = (dataset) => {
    // Allow deletion of other datasets, just not the one being uploaded
    if ((uploading || isUploading) && !dataset.analysisData) {
      toast.error("⏳ This dataset is still being processed. Please wait before deleting it.");
      return;
    }
    setDatasetToDelete(dataset);
    setShowDeleteModal(true);
  };

  // 🚪 Confirm Logout
  const confirmLogout = () => {
    setShowLogoutModal(true);
  };

  // 🚪 Handle Logout
  const handleLogout = () => {
    setShowLogoutModal(false); // Close modal
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.removeItem("role");
    toast.success("👋 Logged out successfully! Redirecting to home...");
    // Redirect to landing page
    setTimeout(() => {
      window.location.href = "/";
    }, 1000); // Delay to show the toast
  };

  // 📥 Download Handlers
  const handleDownloadPDF = () => {
    if (!selectedDatasetData) {
      toast.error("No dataset selected");
      return;
    }

    try {
      // Create a comprehensive report content
      const reportContent = generateReportContent(selectedDatasetData, charts);
      
      // Create a new window for printing
      const printWindow = window.open('', '_blank');
      printWindow.document.write(reportContent);
      printWindow.document.close();
      
      // Trigger print dialog (user can save as PDF)
      setTimeout(() => {
        printWindow.print();
      }, 500);
      
      toast.success("📄 Opening print dialog - Save as PDF");
      setShowDownloadMenu(false);
    } catch (error) {
      console.error("Error generating PDF:", error);
      toast.error("Failed to generate PDF");
    }
  };

  const handleDownloadExcel = () => {
    if (!selectedDatasetData) {
      toast.error("No dataset selected");
      return;
    }

    try {
      // Create CSV content (Excel-compatible)
      const csvContent = generateCSVContent(selectedDatasetData, charts);
      
      // Create blob and download
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      
      link.setAttribute('href', url);
      link.setAttribute('download', `TANAW_Analytics_${selectedDatasetData.name}_${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast.success("📊 Excel file downloaded successfully");
      setShowDownloadMenu(false);
    } catch (error) {
      console.error("Error generating Excel:", error);
      toast.error("Failed to generate Excel file");
    }
  };

  // 📷 Download individual chart as image with insights
  const handleDownloadChartImage = async (chartIndex) => {
    try {
      const chart = charts[chartIndex];
      if (!chart) {
        toast.error("Chart not found");
        return;
      }

      toast.loading("📷 Generating chart image...");

      // Get the chart container element
      const chartElement = document.getElementById(`chart-${chartIndex}`);
      if (!chartElement) {
        toast.error("Chart element not found");
        return;
      }

      // Use html2canvas to capture the chart
      const canvas = await html2canvas(chartElement, {
        scale: 2, // Higher quality
        backgroundColor: '#ffffff',
        logging: false,
        useCORS: true
      });

      // Convert to blob and download
      canvas.toBlob((blob) => {
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `TANAW_Chart_${chart.title.replace(/[^a-z0-9]/gi, '_')}_${new Date().toISOString().split('T')[0]}.png`;
        link.click();
        
        toast.dismiss();
        toast.success(`📷 Chart "${chart.title}" downloaded as image!`);
      });
    } catch (error) {
      toast.dismiss();
      console.error("Error downloading chart image:", error);
      toast.error("Failed to download chart image");
    }
  };

  // 📷 Download all charts as images (ZIP would require additional library)
  const handleDownloadAllChartsAsImages = async () => {
    if (!charts || charts.length === 0) {
      toast.error("No charts to download");
      return;
    }

    toast.loading(`📷 Generating ${charts.length} chart images...`);

    try {
      for (let i = 0; i < charts.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 500)); // Delay between downloads
        await handleDownloadChartImage(i);
      }
      
      toast.dismiss();
      toast.success(`📷 Downloaded ${charts.length} chart images successfully!`);
    } catch (error) {
      toast.dismiss();
      console.error("Error downloading all charts:", error);
      toast.error("Failed to download some charts");
    }
  };


  // Helper function to generate HTML report for PDF
  const generateReportContent = (datasetData, chartsData) => {
    const contextDetection = datasetData.analysis?.context_detection;
    const date = new Date().toLocaleDateString();
    
    let chartsHTML = '';
    chartsData.forEach((chart, index) => {
      const insights = chart.narrative_insights;
      chartsHTML += `
        <div style="page-break-inside: avoid; margin-bottom: 30px; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px;">
          <h3 style="color: #1f2937; margin-bottom: 10px;">${index + 1}. ${chart.title}</h3>
          <p style="color: #6b7280; margin-bottom: 15px;">${chart.description || ''}</p>
          
          ${insights ? `
            <div style="background: #f3f4f6; padding: 15px; border-radius: 6px; margin-top: 15px;">
              <h4 style="color: #374151; margin-bottom: 10px;">🧠 Business Intelligence</h4>
              
              <!-- Conversational Insights (New Format) -->
              ${insights.conversational_analysis ? `
                <div style="margin-bottom: 12px; background: #dbeafe; padding: 10px; border-radius: 4px;">
                  <strong style="color: #1f2937;">💬 What I'm Seeing:</strong>
                  <p style="color: #4b5563; margin-top: 5px; font-style: italic;">"${insights.conversational_analysis}"</p>
                </div>
              ` : ''}
              
              ${insights.personalized_insights ? `
                <div style="margin-bottom: 12px; background: #f3e8ff; padding: 10px; border-radius: 4px;">
                  <strong style="color: #1f2937;">🎯 What This Means for Your Business:</strong>
                  <p style="color: #4b5563; margin-top: 5px;">${insights.personalized_insights}</p>
                </div>
              ` : ''}
              
              ${insights.actionable_advice ? `
                <div style="margin-bottom: 12px; background: #dcfce7; padding: 10px; border-radius: 4px;">
                  <strong style="color: #1f2937;">🚀 My Recommendations:</strong>
                  <p style="color: #4b5563; margin-top: 5px;">${insights.actionable_advice}</p>
                </div>
              ` : ''}
              
              ${insights.business_impact ? `
                <div style="margin-bottom: 12px; background: #f0fdfa; padding: 10px; border-radius: 4px;">
                  <strong style="color: #1f2937;">📈 Potential Impact:</strong>
                  <p style="color: #4b5563; margin-top: 5px;">${insights.business_impact}</p>
                </div>
              ` : ''}
              
              <!-- Legacy Insights (Fallback) -->
              ${!insights.conversational_analysis && insights.business_description ? `
                <div style="margin-bottom: 12px;">
                  <strong style="color: #1f2937;">📊 Business Analysis:</strong>
                  <p style="color: #4b5563; margin-top: 5px;">${insights.business_description}</p>
                </div>
              ` : ''}
              
              ${!insights.conversational_analysis && insights.strategic_insight ? `
                <div style="margin-bottom: 12px;">
                  <strong style="color: #1f2937;">🎯 Strategic Insight:</strong>
                  <p style="color: #4b5563; margin-top: 5px;">${insights.strategic_insight}</p>
                </div>
              ` : ''}
              
              ${!insights.conversational_analysis && insights.actionable_recommendations && insights.actionable_recommendations.length > 0 ? `
                <div style="margin-bottom: 12px;">
                  <strong style="color: #1f2937;">🚀 Recommendations:</strong>
                  <ol style="margin-top: 5px; padding-left: 20px;">
                    ${insights.actionable_recommendations.map(rec => `<li style="color: #4b5563; margin-bottom: 5px;">${rec}</li>`).join('')}
                  </ol>
                </div>
              ` : ''}
              
              ${insights.risk_assessment ? `
                <div style="margin-bottom: 12px;">
                  <strong style="color: #1f2937;">⚠️ Risk Assessment:</strong>
                  <p style="color: #4b5563; margin-top: 5px;">${insights.risk_assessment}</p>
                </div>
              ` : ''}
            </div>
          ` : ''}
        </div>
      `;
    });

    return `
      <!DOCTYPE html>
      <html>
      <head>
        <title>TANAW Analytics Report - ${datasetData.name}</title>
        <style>
          @media print {
            body { margin: 0; }
            @page { margin: 2cm; }
          }
          body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
          }
          .header {
            text-align: center;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 20px;
            margin-bottom: 30px;
          }
          .logo {
            font-size: 32px;
            font-weight: bold;
            color: #2563eb;
            margin-bottom: 10px;
          }
          .subtitle {
            color: #6b7280;
            font-size: 14px;
          }
        </style>
      </head>
      <body>
        <div class="header">
          <div class="logo">TANAW</div>
          <h1 style="color: #1f2937; margin: 10px 0;">Analytics Report</h1>
          <p class="subtitle">Dataset: ${datasetData.name}</p>
          <p class="subtitle">Generated: ${date}</p>
          ${contextDetection ? `
            <div style="margin-top: 15px; padding: 10px; background: #dbeafe; border-radius: 6px; display: inline-block;">
              <strong>${contextDetection.user_message?.emoji || '📊'} ${contextDetection.user_message?.title || 'Dataset Analysis'}</strong>
            </div>
          ` : ''}
        </div>
        
        <div style="margin-bottom: 30px;">
          <h2 style="color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">Executive Summary</h2>
          <p style="color: #4b5563;">
            This report contains ${chartsData.length} analytical charts with intelligent business insights and recommendations
            generated by TANAW's AI-powered analytics engine.
          </p>
        </div>

        <div>
          <h2 style="color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; margin-bottom: 20px;">Analytics & Insights</h2>
          ${chartsHTML}
        </div>

        <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #e5e7eb; text-align: center; color: #6b7280; font-size: 12px;">
          <p>Generated by TANAW Analytics Platform</p>
          <p>© ${new Date().getFullYear()} TANAW - Smart Analytics for SMEs</p>
        </div>
      </body>
      </html>
    `;
  };

  // Helper function to generate ASCII chart
  const generateASCIIChart = (data, chartType, title) => {
    if (!data || (!data.x && !Array.isArray(data))) return '';
    
    let chart = `\nVisual Chart:\n`;
    chart += `${'─'.repeat(50)}\n`;
    chart += `${title}\n`;
    chart += `${'─'.repeat(50)}\n`;
    
    if (data.x && data.y) {
      // Bar/Line charts
      const maxValue = Math.max(...data.y);
      const minValue = Math.min(...data.y);
      const range = maxValue - minValue;
      const maxBarLength = 30;
      
      chart += `\n`;
      for (let i = 0; i < data.x.length; i++) {
        const value = data.y[i];
        const barLength = range > 0 ? Math.round((value - minValue) / range * maxBarLength) : 0;
        const bar = '█'.repeat(Math.max(1, barLength));
        const label = String(data.x[i]).substring(0, 15).padEnd(15);
        const valueStr = typeof value === 'number' ? value.toFixed(0) : value;
        
        chart += `${label} │${bar.padEnd(maxBarLength)} ${valueStr}\n`;
      }
    } else if (Array.isArray(data)) {
      // Forecast data
      const maxValue = Math.max(...data.map(d => d.y || d.value || 0));
      const minValue = Math.min(...data.map(d => d.y || d.value || 0));
      const range = maxValue - minValue;
      const maxBarLength = 30;
      
      chart += `\n`;
      data.forEach((point, i) => {
        const value = point.y || point.value || 0;
        const barLength = range > 0 ? Math.round((value - minValue) / range * maxBarLength) : 0;
        const bar = '█'.repeat(Math.max(1, barLength));
        const date = String(point.x || point.date || '').substring(0, 15).padEnd(15);
        const type = point.type || 'actual';
        const valueStr = typeof value === 'number' ? value.toFixed(0) : value;
        
        chart += `${date} │${bar.padEnd(maxBarLength)} ${valueStr} (${type})\n`;
      });
    }
    
    chart += `${'─'.repeat(50)}\n`;
    return chart;
  };

  // Helper function to generate CSV content with chart data and visual charts
  const generateCSVContent = (datasetData, chartsData) => {
    let csv = 'TANAW Analytics Report\n';
    csv += `Dataset: ${datasetData.name}\n`;
    csv += `Generated: ${new Date().toISOString()}\n\n`;
    
    chartsData.forEach((chart, index) => {
      csv += `\n${'='.repeat(80)}\n`;
      csv += `Chart ${index + 1}: ${chart.title}\n`;
      csv += `Type: ${chart.type}\n`;
      csv += `Description: ${chart.description || chart.brief_description || 'N/A'}\n`;
      csv += `${'='.repeat(80)}\n\n`;
      
      // Add visual ASCII chart
      csv += generateASCIIChart(chart.data, chart.type, chart.title);
      
      // Add chart data in CSV format
      csv += `\nChart Data:\n`;
      const data = chart.data;
      
      if (data && data.x && data.y) {
        // Bar/Line charts with x and y data
        const xLabel = data.x_label || 'X';
        const yLabel = data.y_label || 'Y';
        
        csv += `${xLabel},${yLabel}\n`;
        for (let i = 0; i < data.x.length; i++) {
          const xValue = String(data.x[i]).replace(/,/g, ';'); // Replace commas in values
          const yValue = data.y[i];
          csv += `"${xValue}",${yValue}\n`;
        }
      } else if (Array.isArray(data)) {
        // Forecast data
        csv += `Date,Value,Type\n`;
        data.forEach(point => {
          const date = point.x || point.date || '';
          const value = point.y || point.value || '';
          const type = point.type || 'actual';
          csv += `"${date}",${value},${type}\n`;
        });
      }
      
      // Add insights
      const insights = chart.narrative_insights;
      if (insights) {
        csv += `\n\nBusiness Intelligence:\n`;
        csv += `${'-'.repeat(80)}\n`;
        
        // Conversational insights (new format)
        if (insights.conversational_analysis) {
          csv += `\nAnalysis:\n"${insights.conversational_analysis}"\n`;
        }
        if (insights.personalized_insights) {
          csv += `\nKey Insights:\n"${insights.personalized_insights}"\n`;
        }
        if (insights.actionable_advice) {
          csv += `\nRecommendations:\n"${insights.actionable_advice}"\n`;
        }
        if (insights.business_impact) {
          csv += `\nBusiness Impact:\n"${insights.business_impact}"\n`;
        }
        
        // Legacy insights format (fallback)
        if (!insights.conversational_analysis && insights.business_description) {
          csv += `\nBusiness Analysis:\n"${insights.business_description}"\n`;
        }
        if (insights.strategic_insight) {
          csv += `\nStrategic Insight:\n"${insights.strategic_insight}"\n`;
        }
        if (insights.actionable_recommendations && insights.actionable_recommendations.length > 0) {
          csv += `\nRecommendations:\n`;
          insights.actionable_recommendations.forEach((rec, i) => {
            csv += `${i + 1}. "${rec}"\n`;
          });
        }
      }
      
      csv += '\n' + '='.repeat(80) + '\n\n';
    });
    
    return csv;
  };

  // 📁 Dataset History Management (unused - datasets fetched from backend)
  /* const addDatasetToHistory = async (datasetInfo) => {
    console.log("📁 Adding dataset to history:", datasetInfo);
    console.log("📁 Analysis ID from datasetInfo:", datasetInfo.analysis_id);
    console.log("📁 Analysis object:", datasetInfo.analysis);
    console.log("📁 Analysis charts:", datasetInfo.analysis?.charts);
    console.log("📁 Analysis charts length:", datasetInfo.analysis?.charts?.length);
    console.log("📁 Full datasetInfo structure:", Object.keys(datasetInfo));
    console.log("📁 DatasetInfo analysis property:", datasetInfo.analysis);
    console.log("📁 DatasetInfo analysis type:", typeof datasetInfo.analysis);
    console.log("📁 DatasetInfo analysis keys:", datasetInfo.analysis ? Object.keys(datasetInfo.analysis) : 'undefined');
    console.log("📁 AnalysisData object:", datasetInfo.analysisData);
    console.log("📁 AnalysisData analysis:", datasetInfo.analysisData?.analysis);
    console.log("📁 AnalysisData analysis charts:", datasetInfo.analysisData?.analysis?.charts);
    console.log("📁 AnalysisData analysis charts length:", datasetInfo.analysisData?.analysis?.charts?.length);
    
    const newDataset = {
      id: datasetInfo.analysis_id || `dataset_${Date.now()}`,
      analysisId: datasetInfo.analysis_id, // This should be the analysis_id from the response
      name: datasetInfo.fileName || selectedFile?.name || 'Unknown Dataset',
      uploadDate: datasetInfo.uploadDate || new Date().toISOString(),
      sessionId: datasetInfo.session_id,
      analyticsReadiness: datasetInfo.analytics_readiness,
      visualizationData: datasetInfo.analysisData?.analysis?.charts || datasetInfo.analysis?.charts || [],
      status: 'completed',
      // Store the REAL backend payload when available; fallback to wrapper
      analysisData: datasetInfo.analysisData || datasetInfo
    };
    
    console.log("📁 Created dataset object:", newDataset);
    console.log("📁 Dataset analysisId:", newDataset.analysisId);
    
    // 💾 Save analysis results to backend database
    try {
      console.log("💾 Saving analysis results to backend...");
      const saveResponse = await api.post("/files/save-analysis", {
        analysisId: datasetInfo.analysis_id,
        analysisData: datasetInfo.analysisData || datasetInfo,
        visualizationData: datasetInfo.analysisData?.analysis?.charts || datasetInfo.analysis?.charts || []
      });
      
      console.log("💾 Save response:", saveResponse.data);
      
      if (saveResponse.data.success) {
        console.log("✅ Analysis results saved to backend successfully");
      } else {
        console.error("❌ Failed to save analysis results:", saveResponse.data.message);
      }
    } catch (error) {
      console.error("❌ Error saving analysis results:", error);
      // Don't block the UI flow, just log the error
    }
    
    setDatasets(prev => {
      // Check if dataset with this analysisId already exists
      const exists = prev.some(ds => ds.analysisId === datasetInfo.analysis_id);
      if (exists) {
        console.log("📁 Dataset already exists in history, skipping duplicate");
        return prev; // Don't add duplicate
      }
      return [newDataset, ...prev]; // Add new dataset
    });
    
    // 🔄 Refresh datasets from backend to ensure consistency
    // Note: loadUserDatasets() is already called in handleFileUpload, no need to call again
  }; */

  // 📊 Chart Rendering Function - Updated for Analytics Engine
  const renderChart = (chart) => {
    // Handle error states
    if (chart.status === 'error') {
      return (
        <div className="h-full flex items-center justify-center bg-red-50 rounded">
          <div className="text-center">
            <p className="text-red-600 font-medium">{chart.type}</p>
            <p className="text-red-500 text-sm">{chart.error}</p>
          </div>
        </div>
      );
    }

    if (!chart.data || (!chart.config && chart.type !== 'line_forecast')) {
      return (
        <div className="h-full flex items-center justify-center bg-gray-100 rounded">
          <p className="text-gray-500">No chart data available</p>
        </div>
      );
    }

    const data = chart.data;

    // Convert backend data format to Recharts format
    let chartData = [];
    if (data && data.date && data.sales && Array.isArray(data.date) && Array.isArray(data.sales)) {
      // Handle {date: [...], sales: [...]} format
      chartData = data.date.map((date, i) => ({
        x: date,
        y: data.sales[i],
        date: date,
        value: data.sales[i]
      }));
    } else if (data && data.category && data.sales && Array.isArray(data.category) && Array.isArray(data.sales)) {
      // Handle {category: [...], sales: [...]} format
      chartData = data.category.map((category, i) => ({
        x: category,
        y: data.sales[i],
        category: category,
        value: data.sales[i]
      }));
    } else if (data && data.x && data.y && Array.isArray(data.x) && Array.isArray(data.y)) {
      // Handle Smart Analytics Engine format: {x: [...], y: [...], x_label: "...", y_label: "..."}
      chartData = data.x.map((x, i) => ({
        x: x,
        y: data.y[i],
        date: x, // For time series charts
        value: data.y[i], // For value charts
        category: x // For categorical charts
      }));
    } else if (data && data.x && data.lines && Array.isArray(data.x) && typeof data.lines === 'object') {
      // Handle Smart Analytics Engine multi-line format: {x: [...], lines: {...}, x_label: "...", y_label: "..."}
      // Create combined data points with all line values
      chartData = data.x.map((x, i) => {
        const dataPoint = { x, date: x };
        // Add each line's value to the data point
        Object.keys(data.lines).forEach(lineName => {
          dataPoint[lineName] = data.lines[lineName][i] || 0;
        });
        return dataPoint;
      });
    } else if (data && data.historical && data.forecast) {
      // Handle forecast data format
      const historicalData = data.historical.x.map((x, i) => ({
        x: x,
        y: data.historical.y[i],
        date: x,
        value: data.historical.y[i],
        type: 'historical'
      }));
      
      const forecastData = data.forecast.x.map((x, i) => ({
        x: x,
        y: data.forecast.y[i],
        date: x,
        value: data.forecast.y[i],
        type: 'forecast',
        lower: data.forecast.lower_bound ? data.forecast.lower_bound[i] : null,
        upper: data.forecast.upper_bound ? data.forecast.upper_bound[i] : null
      }));
      
      chartData = [...historicalData, ...forecastData];
    } else if (Array.isArray(data)) {
      chartData = data;
    } else if (data && data.data && Array.isArray(data.data)) {
      // Handle line_forecast data structure from backend
      console.log("🔍 Processing line_forecast data:", {
        dataLength: data.data.length,
        firstItem: data.data[0],
        dataType: typeof data.data[0]
      });
      chartData = data.data;
    } else if (data && data.data) {
      // Debug: Check what data.data actually is
      console.log("🔍 Debug line_forecast data:", {
        hasData: !!data.data,
        dataType: typeof data.data,
        isArray: Array.isArray(data.data),
        dataKeys: data.data ? Object.keys(data.data) : 'no data',
        dataValue: data.data
      });
      // Try to use data.data even if it's not an array
      chartData = Array.isArray(data.data) ? data.data : [];
    }
    
    // Determine chart type based on analytics engine chart_type (MOVE THIS UP!)
    const chartType = chart.chart_type || chart.type || 'line';
    
    // Handle multi-series line charts (e.g., Revenue vs Expense)
    const isMultiSeries = data.chart_subtype === 'multi_series' && data.series && Array.isArray(data.series);
    
    // Handle pie chart format with labels and values arrays
    const isPieChart = chartType === 'pie' && data.labels && data.values;
    if (isPieChart && Array.isArray(data.labels) && Array.isArray(data.values)) {
      chartData = data.labels.map((label, index) => ({
        x: label,
        y: data.values[index],
        name: label
      }));
      console.log("📊 Converted pie chart data from labels/values format:", chartData.slice(0, 3));
    }
    
    console.log("📊 Chart data conversion:", {
      originalData: data,
      convertedData: chartData.slice(0, 3),
      dataLength: chartData.length,
      chartDataType: typeof chartData,
      chartDataIsArray: Array.isArray(chartData),
      isMultiSeries: isMultiSeries,
      isPieChart: isPieChart,
      chartType: chartType
    });
    
    // For multi-series charts, validate series data instead
    if (isMultiSeries) {
      if (!data.x || data.x.length === 0 || !data.series || data.series.length === 0) {
        return (
          <div className="h-full flex items-center justify-center bg-gray-100 rounded">
            <p className="text-gray-500">No data points available</p>
          </div>
        );
      }
    } else if (chartData.length === 0) {
      return (
        <div className="h-full flex items-center justify-center bg-gray-100 rounded">
          <p className="text-gray-500">No data points available</p>
        </div>
      );
    }

    console.log(`🔍 Rendering chart: ${chart.title || 'Unknown'} with type: ${chartType}, isMultiSeries: ${isMultiSeries}`);
    
    if (chartType === 'bar') {
      return (
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="x" 
              label={{ value: data.x_label || 'Category', position: 'insideBottom', offset: -5 }}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis 
              label={{ value: data.y_label || 'Value', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip />
            <Bar dataKey="y" fill="#3b82f6" name={data.y_label || 'Value'} />
          </BarChart>
        </ResponsiveContainer>
      );
    } else if (chartType === 'pie') {
      return (
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name || 'Unknown'} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="y"
              nameKey="name"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={`hsl(${index * 60}, 70%, 50%)`} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      );
    } else if (chartType === 'multi_line') {
      // Multi-line chart for demand forecasting with multiple products
      const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];
      const products = chart.products || [];
      
      return (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="x" label={{ value: 'Date', position: 'insideBottom', offset: -5 }} />
            <YAxis label={{ value: 'Demand Units', angle: -90, position: 'insideLeft' }} />
            <Tooltip 
              formatter={(value, name) => {
                if (name.includes('_historical')) {
                  return [value, `${name.replace('_historical', '')} (Historical)`];
                } else if (name.includes('_forecast')) {
                  return [value, `${name.replace('_forecast', '')} (Forecast)`];
                }
                return [value, name];
              }}
            />
            {products.map((product, index) => {
              const color = colors[index % colors.length];
              return (
                <React.Fragment key={product}>
                  {/* Historical line */}
                  <Line
                    type="monotone"
                    dataKey={`${product}_historical`}
                    stroke={color}
                    strokeWidth={3}
                    name={`${product} (Historical)`}
                    dot={{ fill: color, strokeWidth: 2, r: 4 }}
                    connectNulls={false}
                  />
                  {/* Forecast line */}
                  <Line
                    type="monotone"
                    dataKey={`${product}_forecast`}
                    stroke={color}
                    strokeWidth={3}
                    strokeDasharray="5 5"
                    name={`${product} (Forecast)`}
                    dot={{ fill: color, strokeWidth: 2, r: 4 }}
                    connectNulls={false}
                  />
                </React.Fragment>
              );
            })}
          </LineChart>
        </ResponsiveContainer>
      );
    } else if (chartType === 'line_forecast') {
      // Simple line chart for forecast data
      return (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="x" 
              label={{ value: data.x_label || 'Date', position: 'insideBottom', offset: -5 }}
            />
            <YAxis 
              label={{ value: data.y_label || 'Sales Value (₱)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              formatter={(value, name, props) => {
                if (name === 'Confidence Interval') {
                  return [`${props.payload.lower} - ${props.payload.upper}`, 'Confidence Range'];
                }
                return [value, name];
              }}
            />
            
            {/* Single line for all data */}
            <Line 
              type="monotone" 
              dataKey="y" 
              stroke="#3b82f6" 
              strokeWidth={3} 
              name="Sales Forecast"
              dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
              connectNulls={false}
            />
          </LineChart>
        </ResponsiveContainer>
      );
    } else if (isMultiSeries) {
      // Multi-series line chart (e.g., Revenue vs Expense)
      console.log("📊 Rendering multi-series line chart:", data.series);
      
      // Transform data for Recharts
      const multiSeriesData = data.x.map((xValue, index) => {
        const point = { x: xValue };
        data.series.forEach(series => {
          point[series.name] = series.y[index];
        });
        return point;
      });
      
      console.log("📊 Transformed multi-series data:", multiSeriesData.slice(0, 3));
      
      return (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={multiSeriesData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="x" 
              label={{ value: data.x_label || 'Date', position: 'insideBottom', offset: -5 }}
            />
            <YAxis 
              label={{ value: data.y_label || 'Amount', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip />
            <Legend />
            {data.series.map((series, index) => (
              <Line
                key={series.name}
                type="monotone"
                dataKey={series.name}
                stroke={series.color || '#3b82f6'}
                strokeWidth={3}
                name={series.name}
                dot={{ fill: series.color || '#3b82f6', strokeWidth: 2, r: 4 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      );
    } else if (chartType === 'multi_line' || (data && data.lines)) {
      // Multi-line chart for Smart Analytics Engine
      const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4'];
      const lineNames = data && data.lines ? Object.keys(data.lines) : [];
      
      return (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="x" 
              label={{ value: data.x_label || 'Date', position: 'insideBottom', offset: -5 }}
            />
            <YAxis 
              label={{ value: data.y_label || 'Value', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip />
            {lineNames.map((lineName, index) => (
              <Line
                key={lineName}
                type="monotone"
                dataKey={lineName} 
                stroke={colors[index % colors.length]}
                strokeWidth={2}
                name={lineName}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      );
    } else if (chartType === 'components') {
      // Components chart showing trend and seasonality
      return (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="x" label={{ value: 'Date', position: 'insideBottom', offset: -5 }} />
            <YAxis label={{ value: 'Component Value', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Line 
              type="monotone" 
              dataKey="y" 
              stroke="#8b5cf6" 
              strokeWidth={2} 
              name="Trend"
            />
            <Line 
              type="monotone" 
              dataKey="seasonal" 
              stroke="#10b981" 
              strokeWidth={2} 
              strokeDasharray="3 3"
              name="Seasonality"
            />
          </LineChart>
        </ResponsiveContainer>
      );
    } else {
      // Default to line chart
      return (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="x" 
              label={{ value: data.x_label || 'Date', position: 'insideBottom', offset: -5 }}
            />
            <YAxis 
              label={{ value: data.y_label || 'Value', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip />
            <Line type="monotone" dataKey="y" stroke="#3b82f6" strokeWidth={2} name={data.y_label || 'Value'} />
          </LineChart>
        </ResponsiveContainer>
      );
    }
  };

  // 🎯 Handle showing analytics for a specific dataset
  const handleShowAnalytics = async (dataset) => {
    // Allow viewing other datasets while upload is in progress
    // Only prevent viewing the dataset that's currently being uploaded
    if ((uploading || isUploading) && !dataset.analysisData) {
      toast.error("⏳ This dataset is still being analyzed. Please wait a moment.");
      return;
    }
    
    console.log("🎯 Showing analytics for dataset:", dataset);
    console.log("🎯 Dataset analysisId:", dataset.analysisId);
    console.log("🎯 Dataset analysisData:", dataset.analysisData);
    
    setSelectedDatasetId(dataset.id);
    setSelectedDatasetData(dataset.analysisData);

    // Use the analysis data that's already available
    if (dataset.analysisData) {
      console.log("📊 Using existing analysis data:", dataset.analysisData);
      console.log("📊 Analysis object:", dataset.analysisData.analysis);
      console.log("📊 Analysis charts:", dataset.analysisData.analysis?.charts);
      console.log("📊 Visualization object:", dataset.analysisData.visualization);
      console.log("📊 Visualization charts:", dataset.analysisData.visualization?.charts);
      console.log("📊 Dataset visualizationData:", dataset.visualizationData);
      
      // Extract charts from the analysis data - check multiple possible locations
      const charts = dataset.analysisData.analysis?.charts || 
                    dataset.analysisData.visualization?.charts || 
                    dataset.analysisData.charts ||
                    dataset.visualizationData || 
                    [];
      console.log("📊 Found charts:", charts);
      console.log("📊 Charts length:", charts.length);
      setCharts(charts);
      
      // 📊 Success message after charts loaded
      if (charts && charts.length > 0) {
        const domain = dataset.analysis?.domain || dataset.analysis?.context_detection?.detected_context || 'your';
        toast.success(`✅ Loaded ${charts.length} ${domain.toUpperCase()} analytics charts!`, {
          duration: 3000,
          icon: '📊'
        });
      }
      
      // 📊 Track chart generation for each chart loaded
      if (charts && charts.length > 0) {
        charts.forEach((chart) => {
          analytics.trackChartGeneration(
            chart.type || chart.chartType || 'unknown',
            dataset.rowCount || 0
          );
          console.log("📊 Tracked chart generation:", chart.type || chart.chartType);
        });
        console.log(`📊 Tracked ${charts.length} chart generation events`);
      }
      
      toast.success(`📊 Loaded analytics for ${dataset.name}`);
    } else {
      console.error("❌ No analysis data found for dataset:", dataset);
      toast.error("No analysis data available for this dataset.");
      setCharts([]);
    }
  };

  // 🔄 Handle closing analytics dashboard
  const handleCloseAnalytics = () => {
    console.log("🔄 Closing analytics dashboard");
    
    setSelectedDatasetId(null);
    setSelectedDatasetData(null);
    setCharts([]);
    
    // Show feedback modal after viewing analytics
    // 30% chance to avoid overwhelming users
    if (Math.random() < 0.3) {
      setTimeout(() => {
        console.log('🎯 Triggering feedback modal after viewing analytics');
        setShowFeedbackModal(true);
      }, 1500); // Show after 1.5 seconds
    }
  };

  // 📊 Handle chart display mode toggle
  const toggleChartDisplayMode = () => {
    setChartDisplayMode(prev => prev === 'single' ? 'grid' : 'single');
  };

  const renderDatasetHistory = () => {
    if (datasets.length === 0) return null;
    
    // Sort filtered datasets by upload date (newest first)
    const sortedAndFilteredDatasets = [...filteredDatasets].sort((a, b) => 
      b.uploadDate - a.uploadDate
    );
    
    return (
      <div className="mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-3 gap-3">
          <h3 className="text-base sm:text-lg font-semibold text-gray-800 flex items-center gap-2">
          📁 Dataset History
        </h3>
          <div className="flex items-center gap-2">
            <button
              onClick={refreshDatasets}
              disabled={isRefreshing}
              className="flex items-center gap-2 px-3 py-1.5 text-xs sm:text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Refresh datasets from server"
            >
              <svg className="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span className="hidden sm:inline">Refresh</span>
            </button>
          </div>
        </div>
        
        <div className="space-y-4">
          {sortedAndFilteredDatasets.length > 0 ? (
            sortedAndFilteredDatasets.map((dataset) => (
            <div key={dataset.id} className="space-y-3">
              {/* Dataset Card - Responsive */}
              <div
                className={`w-full p-3 sm:p-4 border rounded-lg transition-all duration-200 ${
                selectedDatasetId === dataset.id
                  ? 'border-blue-500 bg-blue-50 shadow-md'
                  : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 sm:gap-3">
                    <div className="w-7 h-7 sm:w-8 sm:h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <svg className="w-3 h-3 sm:w-4 sm:h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-sm sm:text-base text-gray-900 truncate">
                        {dataset.name}
                      </h4>
                      <p className="text-xs sm:text-sm text-gray-500">
                        {dataset.uploadDateString} <span className="hidden sm:inline">at</span> <span className="sm:hidden">•</span> {dataset.uploadTime}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between sm:justify-end gap-2 sm:gap-3">
                  <div className="text-left sm:text-right">
                    <div className="text-xs sm:text-sm text-gray-600">
                        <span className="hidden sm:inline">Charts:</span> {dataset.analysisData?.analysis?.charts?.length || dataset.visualizationData?.length || 0}
                    </div>
                  </div>
                    <div className="flex items-center gap-1 sm:gap-2">
                  <span className={`px-2 py-0.5 sm:py-1 text-xs rounded ${
                    dataset.status === 'completed'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {dataset.status}
                  </span>
                      <button
                        onClick={() => handleShowAnalytics(dataset)}
                        disabled={(uploading || isUploading) && !dataset.analysisData}
                        className={`px-2 sm:px-3 py-1 sm:py-1.5 rounded text-xs transition flex items-center gap-1 ${
                          (uploading || isUploading) && !dataset.analysisData
                            ? 'bg-gray-400 text-gray-200 cursor-not-allowed opacity-60'
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                        title={(uploading || isUploading) && !dataset.analysisData ? "Dataset is being analyzed..." : "View analytics"}
                      >
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                        <span className="hidden sm:inline">
                          {(uploading || isUploading) && !dataset.analysisData ? "Analyzing..." : "Show Analytics"}
                        </span>
                        <span className="sm:hidden">View</span>
                      </button>
                      <button
                        onClick={() => confirmDeleteDataset(dataset)}
                        disabled={(uploading || isUploading) && !dataset.analysisData}
                        className={`px-3 py-1 rounded text-xs transition flex items-center gap-1 ${
                          (uploading || isUploading) && !dataset.analysisData
                            ? 'bg-gray-400 text-gray-200 cursor-not-allowed opacity-60'
                            : 'bg-red-600 text-white hover:bg-red-700'
                        }`}
                        title={(uploading || isUploading) && !dataset.analysisData ? "Dataset is being processed..." : "Delete dataset"}
                      >
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        Delete
                      </button>
                </div>
              </div>
        </div>
      </div>

              {/* Analytics Dashboard - Show inline below the dataset */}
              {selectedDatasetId === dataset.id && selectedDatasetData && (
                <div className="ml-4 p-6 border border-blue-300 bg-blue-50 rounded-lg">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                      📊 Analytics Dashboard - {dataset.name}
                    </h3>
                    <button
                      onClick={handleCloseAnalytics}
                      className="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600 transition flex items-center gap-1"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                      Close
            </button>
           </div>
           
                  {/* Context Detection Banner */}
                  {(() => {
                    // Debug: Log the full structure to find context_detection
                    console.log("🔍 Full selectedDatasetData:", selectedDatasetData);
                    console.log("🔍 selectedDatasetData keys:", selectedDatasetData ? Object.keys(selectedDatasetData) : 'null');
                    
                    // Check multiple possible data paths for context_detection
                    const contextDetection = selectedDatasetData?.analysis?.context_detection || 
                                            selectedDatasetData?.context_detection ||
                                            selectedDatasetData?.analytics_results?.context_detection ||
                                            selectedDatasetData?.analytics_results?.analysis?.context_detection;
                    
                    console.log("🔍 Context detection data:", contextDetection);
                    
                    if (!contextDetection) return null;
                    
                    const userMessage = contextDetection.user_message || {};
                    const confidence = contextDetection.confidence || 0;
                    
                    return (
                      <div className="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 rounded-lg p-5 shadow-sm">
                        <div className="flex items-start gap-4">
                          <div className="text-3xl">
                            {userMessage.emoji || "📊"}
               </div>
                          <div className="flex-1">
                            <h4 className="text-lg font-semibold text-blue-900 mb-2">
                              {userMessage.title || "Dataset Analyzed"}
                            </h4>
                            <p className="text-gray-700 leading-relaxed">
                              {userMessage.message || "We've analyzed your dataset and generated relevant analytics."}
                            </p>
                            {confidence >= 0.7 && (
                              <div className="mt-3 flex items-center gap-2">
                                <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs font-medium">
                                  {contextDetection.detected_context} Dataset
               </div>
                                <div className="text-xs text-gray-600">
                                  Confidence: {(confidence * 100).toFixed(0)}%
                                </div>
               </div>
             )}
           </div>
                    </div>
                      </div>
                    );
                  })()}

                  {/* Download Button */}
                  <div className="flex gap-3 mb-6">
                    {/* Download Button with Dropdown */}
                    <div className="relative download-menu-container">
                      <button 
                        onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                        className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition flex items-center gap-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        Download Results
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                      
                      {/* Download Dropdown Menu */}
                      {showDownloadMenu && (
                        <div className="absolute top-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-50 min-w-[200px]">
                          <button
                            onClick={handleDownloadPDF}
                            className="w-full px-4 py-3 text-left hover:bg-gray-50 transition flex items-center gap-3 border-b border-gray-100"
                          >
                            <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                            </svg>
                            <div>
                              <div className="font-medium text-gray-900">PDF Report</div>
                              <div className="text-xs text-gray-500">Professional format</div>
                            </div>
                          </button>
                          
                          <button
                            onClick={handleDownloadExcel}
                            className="w-full px-4 py-3 text-left hover:bg-gray-50 transition flex items-center gap-3 border-b border-gray-100"
                          >
                            <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                            <div>
                              <div className="font-medium text-gray-900">Excel/CSV</div>
                              <div className="text-xs text-gray-500">Spreadsheet with charts data</div>
                            </div>
                          </button>

                          <button
                            onClick={handleDownloadAllChartsAsImages}
                            className="w-full px-4 py-3 text-left hover:bg-gray-50 transition flex items-center gap-3 rounded-b-lg"
                          >
                            <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            <div>
                              <div className="font-medium text-gray-900">All Charts (PNG)</div>
                              <div className="text-xs text-gray-500">Individual image files ({charts.length} charts)</div>
                            </div>
                          </button>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Diagnostics section removed - cleaner UI for users */}

                  {/* Debug: Log anomaly data (supports nested analytics_results) */}
                  {console.log("🔍 Anomaly data:", selectedDatasetData?.analysis?.anomalies || selectedDatasetData?.analysis?.analytics_results?.anomalies || selectedDatasetData?.anomalies)}
                  {console.log("🔍 Anomaly total_anomalies:", (selectedDatasetData?.analysis?.anomalies || selectedDatasetData?.analysis?.analytics_results?.anomalies || selectedDatasetData?.anomalies)?.total_anomalies)}
                  {console.log("🔍 Anomaly condition check:", !!((selectedDatasetData?.analysis?.anomalies || selectedDatasetData?.analysis?.analytics_results?.anomalies || selectedDatasetData?.anomalies)?.total_anomalies > 0))}
                  
                  {/* Anomaly Alerts */}
                  {(
                    (selectedDatasetData?.analysis && (selectedDatasetData.analysis.anomalies || selectedDatasetData.analysis.analytics_results?.anomalies)) 
                    || selectedDatasetData?.anomalies
                  ) && (
                    <div className="mt-6 mb-6">
                      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-3">
                          <span className="text-xl">🚨</span>
                          <h4 className="text-lg font-semibold text-red-800">Anomaly Detection Alert</h4>
                          <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-sm">
                            {(
                              selectedDatasetData.analysis?.anomalies?.total_anomalies 
                              ?? selectedDatasetData.analysis?.analytics_results?.anomalies?.total_anomalies 
                              ?? selectedDatasetData?.anomalies?.total_anomalies 
                              ?? 0
                            )} Issues Found
                          </span>
                        </div>
                        
                        <div className="space-y-3">
                          {/* Critical Alerts */}
                          {(selectedDatasetData.analysis?.anomalies?.critical_alerts 
                            || selectedDatasetData.analysis?.analytics_results?.anomalies?.critical_alerts 
                            || selectedDatasetData?.anomalies?.critical_alerts) && (selectedDatasetData.analysis?.anomalies?.critical_alerts 
                            || selectedDatasetData.analysis?.analytics_results?.anomalies?.critical_alerts 
                            || selectedDatasetData?.anomalies?.critical_alerts).length > 0 && (
                            <div>
                              <h5 className="font-semibold text-red-700 mb-2">Critical Alerts {(selectedDatasetData.analysis?.anomalies?.critical_alerts || selectedDatasetData?.anomalies?.critical_alerts) ? `(${(selectedDatasetData.analysis?.anomalies?.critical_alerts || selectedDatasetData?.anomalies?.critical_alerts).length})` : ''}</h5>
                              <div className="space-y-2">
                                {(selectedDatasetData.analysis?.anomalies?.critical_alerts 
                                  || selectedDatasetData.analysis?.analytics_results?.anomalies?.critical_alerts 
                                  || selectedDatasetData?.anomalies?.critical_alerts).slice(0, 3).map((alert, index) => (
                                  <div key={index} className="bg-red-100 border-l-4 border-red-500 p-3 rounded">
                                    <p className="text-red-800 text-sm font-medium">{alert.message}</p>
                                    {alert.severity && (
                                      <span className="text-xs text-red-600">Severity: {alert.severity}</span>
                                    )}
                </div>
              ))}
            </div>
          </div>
        )}

                          {/* Warnings */}
                          {(selectedDatasetData.analysis?.anomalies?.warnings 
                            || selectedDatasetData.analysis?.analytics_results?.anomalies?.warnings 
                            || selectedDatasetData?.anomalies?.warnings) && (selectedDatasetData.analysis?.anomalies?.warnings 
                            || selectedDatasetData.analysis?.analytics_results?.anomalies?.warnings 
                            || selectedDatasetData?.anomalies?.warnings).length > 0 && (
                            <div>
                              <h5 className="font-semibold text-orange-700 mb-2">Warnings {(selectedDatasetData.analysis?.anomalies?.warnings || selectedDatasetData?.anomalies?.warnings) ? `(${(selectedDatasetData.analysis?.anomalies?.warnings || selectedDatasetData?.anomalies?.warnings).length})` : ''}</h5>
                              <div className="space-y-2">
                                {(selectedDatasetData.analysis?.anomalies?.warnings 
                                  || selectedDatasetData.analysis?.analytics_results?.anomalies?.warnings 
                                  || selectedDatasetData?.anomalies?.warnings).slice(0, 3).map((warning, index) => (
                                  <div key={index} className="bg-orange-100 border-l-4 border-orange-500 p-3 rounded">
                                    <p className="text-orange-800 text-sm">{warning.message}</p>
            </div>
          ))}
        </div>
                </div>
                          )}
                          
                          {/* Detection Summary */}
                          {(selectedDatasetData.analysis?.anomalies?.detection_summary 
                            || selectedDatasetData.analysis?.analytics_results?.anomalies?.detection_summary 
                            || selectedDatasetData?.anomalies?.detection_summary) && (
                            <div className="bg-white border border-red-200 rounded p-3">
                              <p className="text-gray-700 text-sm mb-2">
                                <strong>Summary:</strong> {(selectedDatasetData.analysis?.anomalies?.detection_summary 
                                  || selectedDatasetData.analysis?.analytics_results?.anomalies?.detection_summary 
                                  || selectedDatasetData?.anomalies?.detection_summary).message}
                              </p>
                              {(selectedDatasetData.analysis?.anomalies?.detection_summary?.recommendations 
                                || selectedDatasetData.analysis?.analytics_results?.anomalies?.detection_summary?.recommendations 
                                || selectedDatasetData?.anomalies?.detection_summary?.recommendations) && (
                                <div>
                                  <p className="text-sm font-medium text-gray-600 mb-1">Recommendations:</p>
                                  <ul className="text-sm text-gray-600 space-y-1">
                                    {(selectedDatasetData.analysis?.anomalies?.detection_summary?.recommendations 
                                      || selectedDatasetData.analysis?.analytics_results?.anomalies?.detection_summary?.recommendations 
                                      || selectedDatasetData?.anomalies?.detection_summary?.recommendations).slice(0, 3).map((rec, index) => (
                                      <li key={index} className="flex items-start gap-2">
                                        <span className="text-blue-500 mt-1">•</span>
                                        <span>{rec}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Predictive Analytics Metrics */}
                  {selectedDatasetData?.analysis?.predictive_metrics && Object.keys(selectedDatasetData.analysis.predictive_metrics).length > 0 && (
                    <div className="mt-6 mb-6">
                      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-4">
                          <span className="text-xl">🔮</span>
                          <h4 className="text-lg font-semibold text-purple-800">Predictive Analytics Insights</h4>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          {/* Sales Forecast Metrics */}
                          {selectedDatasetData.analysis.predictive_metrics.sales_forecast && (
                            <div className="bg-white rounded-lg p-4 border border-purple-100">
                              <h5 className="font-semibold text-purple-700 mb-2 flex items-center gap-2">
                                📈 Sales Forecast
                              </h5>
                              <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                  <span>Accuracy:</span>
                                  <span className={`font-medium ${
                                    selectedDatasetData.analysis.predictive_metrics.sales_forecast.forecast_accuracy === 'High' ? 'text-green-600' :
                                    selectedDatasetData.analysis.predictive_metrics.sales_forecast.forecast_accuracy === 'Medium' ? 'text-yellow-600' : 'text-red-600'
                                  }`}>
                                    {selectedDatasetData.analysis.predictive_metrics.sales_forecast.forecast_accuracy}
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Trend:</span>
                                  <span className={`font-medium ${
                                    selectedDatasetData.analysis.predictive_metrics.sales_forecast.trend === 'Increasing' ? 'text-green-600' :
                                    selectedDatasetData.analysis.predictive_metrics.sales_forecast.trend === 'Decreasing' ? 'text-red-600' : 'text-blue-600'
                                  }`}>
                                    {selectedDatasetData.analysis.predictive_metrics.sales_forecast.trend}
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Growth Rate:</span>
                                  <span className={`font-medium ${
                                    selectedDatasetData.analysis.predictive_metrics.sales_forecast.growth_rate > 0 ? 'text-green-600' : 'text-red-600'
                                  }`}>
                                    {selectedDatasetData.analysis.predictive_metrics.sales_forecast.growth_rate}%
                                  </span>
                                </div>
                              </div>
                            </div>
                          )}
                          
                          {/* Inventory Forecast Metrics */}
                          {selectedDatasetData.analysis.predictive_metrics.inventory_forecast && (
                            <div className="bg-white rounded-lg p-4 border border-purple-100">
                              <h5 className="font-semibold text-purple-700 mb-2 flex items-center gap-2">
                                📦 Inventory Forecast
                              </h5>
                              <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                  <span>Reorder Point:</span>
                                  <span className="font-medium text-blue-600">
                                    {selectedDatasetData.analysis.predictive_metrics.inventory_forecast.reorder_point}
                            </span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Safety Stock:</span>
                                  <span className="font-medium text-orange-600">
                                    {selectedDatasetData.analysis.predictive_metrics.inventory_forecast.safety_stock}
                            </span>
                          </div>
                                <div className="flex justify-between">
                                  <span>Avg Daily Demand:</span>
                                  <span className="font-medium text-gray-600">
                                    {selectedDatasetData.analysis.predictive_metrics.inventory_forecast.average_daily_demand}
                                  </span>
                        </div>
                              </div>
                            </div>
                          )}
                          
                          {/* Cash Flow Forecast Metrics */}
                          {selectedDatasetData.analysis.predictive_metrics.cash_flow_forecast && (
                            <div className="bg-white rounded-lg p-4 border border-purple-100">
                              <h5 className="font-semibold text-purple-700 mb-2 flex items-center gap-2">
                                💰 Cash Flow Forecast
                              </h5>
                              <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                  <span>Health:</span>
                                  <span className={`font-medium ${
                                    selectedDatasetData.analysis.predictive_metrics.cash_flow_forecast.cash_flow_health === 'Healthy' ? 'text-green-600' :
                                    selectedDatasetData.analysis.predictive_metrics.cash_flow_forecast.cash_flow_health === 'Moderate' ? 'text-yellow-600' :
                                    selectedDatasetData.analysis.predictive_metrics.cash_flow_forecast.cash_flow_health === 'Low' ? 'text-orange-600' : 'text-red-600'
                                  }`}>
                                    {selectedDatasetData.analysis.predictive_metrics.cash_flow_forecast.cash_flow_health}
                                </span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Avg Monthly:</span>
                                  <span className={`font-medium ${
                                    selectedDatasetData.analysis.predictive_metrics.cash_flow_forecast.average_monthly > 0 ? 'text-green-600' : 'text-red-600'
                                  }`}>
                                    ${selectedDatasetData.analysis.predictive_metrics.cash_flow_forecast.average_monthly}
                                </span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Min Cash Flow:</span>
                                  <span className={`font-medium ${
                                    selectedDatasetData.analysis.predictive_metrics.cash_flow_forecast.minimum_cash_flow > 0 ? 'text-green-600' : 'text-red-600'
                                  }`}>
                                    ${selectedDatasetData.analysis.predictive_metrics.cash_flow_forecast.minimum_cash_flow}
                                  </span>
                                </div>
                              </div>
                            </div>
                                )}
                              </div>
                                </div>
                              </div>
                  )}

                  {/* Visualizations */}
                  {charts.length > 0 && (
                    <div className="mt-6">
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 sm:mb-6 gap-3">
                        <div className="flex items-center gap-3 sm:gap-4">
                          <h4 className="text-base sm:text-lg font-semibold text-gray-800">
                            📊 Analytics Dashboard
                          </h4>
                            </div>
                        
                        {/* Chart Display Mode Toggle - Responsive */}
                        <div className="flex items-center gap-2">
                          <span className="text-xs sm:text-sm text-gray-600 hidden sm:inline">View:</span>
                          <button
                            onClick={toggleChartDisplayMode}
                            className={`px-2 sm:px-3 py-1 sm:py-1.5 rounded text-xs sm:text-sm font-medium transition ${
                              chartDisplayMode === 'single'
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                            }`}
                          >
                            <span className="hidden sm:inline">Single Column</span>
                            <span className="sm:hidden">Single</span>
                          </button>
                          <button
                            onClick={toggleChartDisplayMode}
                            className={`px-2 sm:px-3 py-1 sm:py-1.5 rounded text-xs sm:text-sm font-medium transition ${
                              chartDisplayMode === 'grid'
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                            }`}
                          >
                            <span className="hidden sm:inline">2x2 Grid</span>
                            <span className="sm:hidden">Grid</span>
                          </button>
                        </div>
                        </div>

                      {/* Dynamic Chart Layout - Responsive */}
                      <div className={chartDisplayMode === 'single' ? 'space-y-6 sm:space-y-8' : 'grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6'}>
                        {charts.map((chart, index) => (
                          <div id={`chart-${index}`} key={chart.id || `chart-${index}`} className="p-4 sm:p-6 rounded-lg shadow-lg bg-blue-50 border-l-4 border-blue-400">
                            <div className="flex items-center justify-between gap-3 sm:gap-4 mb-3 sm:mb-4">
                              <div className="flex items-center gap-3 sm:gap-4 flex-1 min-w-0">
                                <span className="text-2xl sm:text-3xl">{chart.icon || '📊'}</span>
                                <div className="flex-1 min-w-0">
                                  <h5 className="text-base sm:text-xl font-semibold text-gray-800 truncate">{chart.title || chart.type || `Analytics ${index + 1}`}</h5>
                                  <p className="text-xs sm:text-sm text-gray-600 mt-0.5 sm:mt-1 line-clamp-2">{chart.description || 'Analytics visualization'}</p>
                                </div>
                              </div>
                              <button
                                onClick={() => handleDownloadChartImage(index)}
                                className="flex-shrink-0 p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all duration-200 shadow-md hover:shadow-lg"
                                title="Download chart as image"
                              >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                              </button>
                        </div>
                        
                        {/* Brief Description - User-Friendly Explanation */}
                        {chart.brief_description && (
                          <div className="mb-4 p-3 bg-white rounded-lg border-l-2 border-blue-300 shadow-sm">
                            <div className="flex items-start gap-2">
                              <span className="text-blue-600 mt-0.5">📝</span>
                              <p className="text-sm text-gray-700 leading-relaxed">{chart.brief_description}</p>
                            </div>
                          </div>
                        )}

                            {/* Debug: Log chart data */}
                            {console.log(`🔍 Chart ${index + 1}:`, {
                              title: chart.title,
                              type: chart.type,
                              hasNarrativeInsights: !!chart.narrative_insights,
                              narrativeInsights: chart.narrative_insights,
                              dataKeys: Object.keys(chart)
                            })}
                            
                            {/* Conversational Business Insights */}
                            {chart.narrative_insights ? (
                              <div className="mb-6 p-5 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border-l-4 border-blue-500 shadow-lg">
                                <div className="flex items-center gap-2 mb-4">
                                  <span className="text-xl">🗣️</span>
                                  <h6 className="font-bold text-gray-800 text-lg">Business Analyst Consultation</h6>
                                  {chart.narrative_insights.insight_type === 'conversational' && (
                                    <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full font-medium">
                                      AI Analyst
                                    </span>
                                  )}
                                </div>
                                
                                {/* Conversational Analysis */}
                                {chart.narrative_insights.conversational_analysis && (
                                  <div className="mb-4 p-4 bg-white rounded-lg border border-blue-100">
                                    <h7 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                                      💬 What I'm Seeing
                                    </h7>
                                    <p className="text-gray-700 text-sm leading-relaxed italic">
                                      "{chart.narrative_insights.conversational_analysis}"
                                    </p>
                                  </div>
                                )}

                                {/* Personalized Insights */}
                                {chart.narrative_insights.personalized_insights && (
                                  <div className="mb-4 p-4 bg-white rounded-lg border border-purple-100">
                                    <h7 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                                      🎯 What This Means for Your Business
                                    </h7>
                                    <p className="text-gray-700 text-sm leading-relaxed">
                                      {chart.narrative_insights.personalized_insights}
                                    </p>
                                  </div>
                                )}

                                {/* Actionable Advice */}
                                {chart.narrative_insights.actionable_advice && (
                                  <div className="mb-4 p-4 bg-white rounded-lg border border-green-100">
                                    <h7 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                                      🚀 My Recommendations
                                    </h7>
                                    <p className="text-gray-700 text-sm leading-relaxed">
                                      {chart.narrative_insights.actionable_advice}
                                    </p>
                                  </div>
                                )}

                                {/* Business Impact */}
                                {chart.narrative_insights.business_impact && (
                                  <div className="mb-4 p-4 bg-white rounded-lg border border-teal-100">
                                    <h7 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                                      📈 Potential Impact
                                    </h7>
                                    <p className="text-gray-700 text-sm leading-relaxed">
                                      {chart.narrative_insights.business_impact}
                                    </p>
                                  </div>
                                )}

                                {/* Legacy Support - Fallback to old format */}
                                {!chart.narrative_insights.conversational_analysis && chart.narrative_insights.business_description && (
                                  <div className="mb-4 p-3 bg-white rounded-lg border border-blue-100">
                                    <h7 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                                      📊 Business Analysis
                                    </h7>
                                    <p className="text-gray-700 text-sm leading-relaxed">
                                      {chart.narrative_insights.business_description}
                                    </p>
                                  </div>
                                )}

                                {/* Legacy Strategic Insight */}
                                {!chart.narrative_insights.conversational_analysis && chart.narrative_insights.strategic_insight && (
                                  <div className="mb-4 p-3 bg-white rounded-lg border border-purple-100">
                                    <h7 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                                      🎯 Strategic Insight
                                    </h7>
                                    <p className="text-gray-700 text-sm leading-relaxed">
                                      {chart.narrative_insights.strategic_insight}
                                    </p>
                                  </div>
                                )}

                                {/* Legacy Actionable Recommendations */}
                                {!chart.narrative_insights.conversational_analysis && chart.narrative_insights.actionable_recommendations && chart.narrative_insights.actionable_recommendations.length > 0 && (
                                  <div className="mb-4 p-3 bg-white rounded-lg border border-green-100">
                                    <h7 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                                      🚀 Actionable Recommendations
                                    </h7>
                                    <div className="space-y-2">
                                      {chart.narrative_insights.actionable_recommendations.map((recommendation, recIndex) => (
                                        <div key={recIndex} className="flex items-start gap-3 p-2 bg-gray-50 rounded">
                                          <span className="text-green-600 mt-1 font-bold text-sm">
                                            {recIndex + 1}.
                                          </span>
                                          <span className="text-sm text-gray-700 leading-relaxed">
                                            {recommendation}
                                          </span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Legacy Support - Fallback to old format */}
                                {!chart.narrative_insights.business_description && chart.narrative_insights.insights && (
                                  <div className="mb-4 p-3 bg-white rounded-lg border border-blue-100">
                                    <h7 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                                      💡 AI Insights
                                    </h7>
                                    <p className="text-gray-700 text-sm leading-relaxed mb-3">
                                      {chart.narrative_insights.insights}
                                    </p>
                                    {chart.narrative_insights.key_points && chart.narrative_insights.key_points.length > 0 && (
                                      <ul className="text-sm text-gray-600 space-y-1">
                                        {chart.narrative_insights.key_points.map((point, pointIndex) => (
                                          <li key={pointIndex} className="flex items-start gap-2">
                                            <span className="text-blue-500 mt-1">•</span>
                                            <span>{point}</span>
                                          </li>
                                        ))}
                                      </ul>
                                    )}
                                  </div>
                                )}

                                {/* Confidence Level */}
                                {chart.narrative_insights.confidence && (
                                  <div className="flex items-center gap-2 text-xs text-gray-500">
                                    <span>Confidence:</span>
                                    <span className={`font-medium ${
                                      chart.narrative_insights.confidence > 0.8 ? 'text-green-600' :
                                      chart.narrative_insights.confidence > 0.6 ? 'text-yellow-600' : 'text-orange-600'
                                    }`}>
                                      {Math.round(chart.narrative_insights.confidence * 100)}%
                                    </span>
                                  </div>
                                )}
                              </div>
                            ) : chart.insights && chart.insights !== "AI insights are not available due to processing limitations." ? (
                              <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border-l-4 border-blue-500 shadow-sm">
                                <div className="flex items-center gap-2 mb-3">
                                  <span className="text-lg">🧠</span>
                                  <h6 className="font-semibold text-gray-800">Smart Analytics Insights</h6>
                                  {chart.meta && chart.meta.openai_recommended && (
                                    <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                                      AI Recommended
                                    </span>
                        )}
                      </div>
                                <div className="text-gray-700 text-sm leading-relaxed whitespace-pre-line">
                                  {typeof chart.insights === 'string' ? chart.insights : JSON.stringify(chart.insights, null, 2)}
                                </div>
                                {chart.meta && chart.meta.business_value && (
                                  <div className="mt-3 p-2 bg-white rounded border-l-2 border-green-400">
                                    <p className="text-xs text-gray-600 font-medium">Business Value:</p>
                                    <p className="text-sm text-gray-700">{chart.meta.business_value}</p>
                  </div>
                )}
                              </div>
                            ) : (
                              <div className="mb-6 p-4 bg-yellow-50 rounded-lg border-l-4 border-yellow-400 shadow-sm">
                                <div className="flex items-center gap-2 mb-3">
                                  <span className="text-lg">⚠️</span>
                                  <h6 className="font-semibold text-gray-800">Insights Not Available</h6>
                                </div>
                                <p className="text-gray-700 text-sm leading-relaxed">
                                  AI insights for this chart are not available. This might be due to insufficient data or API limitations.
                                </p>
                                <div className="mt-2 text-xs text-gray-500">
                                  Chart: {chart.title || 'Unknown'} | Type: {chart.type || 'Unknown'}
                                </div>
                              </div>
                            )}
                            
                            <div className={chartDisplayMode === 'single' ? 'h-64 sm:h-80 md:h-96 w-full' : 'h-56 sm:h-64 md:h-80 w-full'}>
                              {renderChart(chart)}
                      </div>
                    </div>
                  ))}
                </div>
                    </div>
                  )}
                  
                  {charts.length === 0 && (
                    <div className="mt-6 bg-white p-8 rounded-lg shadow text-center">
                      <h4 className="text-lg font-semibold text-gray-800 mb-2">DISPLAY PERFORMABLE ANALYTICS HERE</h4>
                      <p className="text-gray-500">Charts will appear here once generated.</p>
                    </div>
                              )}
                            </div>
              )}
                          </div>
          ))
          ) : (
            <div className="text-center py-8">
              <div className="flex flex-col items-center justify-center space-y-3">
                <svg className="w-16 h-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-gray-500 text-lg font-medium">No datasets found</p>
                <p className="text-gray-400 text-sm">
                  {(searchTerm || dateFilter)
                    ? (
                      <>
                        No datasets match your filters
                        {searchTerm && ` "${searchTerm}"`}
                        {searchTerm && dateFilter && " and "}
                        {dateFilter && ` on ${new Date(dateFilter).toLocaleDateString()}`}.
                        <br />
                        Try adjusting your search or filters.
                      </>
                    )
                    : datasets.length === 0
                      ? "Upload a dataset to get started with analytics."
                      : "No datasets available."}
                </p>
                {(searchTerm || dateFilter) && (
                  <button
                    onClick={() => {
                      setSearchTerm("");
                      setDateFilter("");
                    }}
                    className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                  >
                    Clear All Filters
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

   return (
     <div className="min-h-screen bg-gray-50 font-sans text-gray-800">
       <Toaster position="top-center" toastOptions={{ style: { fontSize: "0.9rem", borderRadius: "8px", padding: "10px 16px" } }} />

       {/* Sticky Header */}
       <StickyHeader 
         user={user?.data || user} 
         onUserUpdate={(updatedUser) => setUser({ data: updatedUser })}
         onLogout={confirmLogout}
         onSearch={(searchQuery) => {
           setSearchTerm(searchQuery);
         }}
         onDateFilter={(dateQuery) => {
           setDateFilter(dateQuery);
         }}
       />

       {/* Upload Progress Banner */}
       {(uploading || isUploading) && (
         <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-4 shadow-lg">
           <div className="max-w-7xl mx-auto flex items-center justify-between">
             <div className="flex items-center gap-3">
               <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
               <div>
                 <p className="font-semibold text-sm">Uploading and analyzing dataset...</p>
                 <p className="text-xs opacity-90">You can continue viewing other datasets while we process this one</p>
               </div>
             </div>
             <div className="text-xs bg-white/20 px-3 py-1 rounded-full">
               Processing...
             </div>
           </div>
         </div>
       )}

       {/* Main Content - Responsive Container */}
       <div className="flex flex-col px-3 sm:px-6 md:px-8 lg:px-12 py-4 sm:py-6 md:py-8 overflow-y-auto max-w-7xl mx-auto w-full">


        {/* Active Filters Indicator */}
        {(searchTerm || dateFilter) && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <span className="text-sm font-medium text-blue-800">Active Filters:</span>
                {searchTerm && (
                  <span className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    🔍 "{searchTerm}"
                    <button
                      onClick={() => setSearchTerm("")}
                      className="ml-1 text-blue-600 hover:text-blue-800"
                    >
                      ×
                    </button>
                  </span>
                )}
                {dateFilter && (
                  <span className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    📅 On {new Date(dateFilter).toLocaleDateString()}
                    <button
                      onClick={() => setDateFilter("")}
                      className="ml-1 text-blue-600 hover:text-blue-800"
                    >
                      ×
                    </button>
                  </span>
                )}
              </div>
              <button
                onClick={() => {
                  setSearchTerm("");
                  setDateFilter("");
                }}
                className="text-xs text-blue-600 hover:text-blue-800 font-medium"
              >
                Clear All Filters
              </button>
            </div>
          </div>
        )}

        {/* 🔒 Session Expired Modal */}
        {showSessionExpiredModal && (
          <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-2xl max-w-md w-full mx-4">
              <div className="p-6">
                <div className="flex items-center justify-center mb-4">
                  <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                    <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                </div>
                
                <h2 className="text-xl font-bold text-gray-900 mb-3 text-center">
                  Session Expired
                </h2>
                
                <p className="text-sm text-gray-600 mb-6 text-center">
                  Your session has expired due to inactivity. Please log in again to continue using TANAW.
                </p>

                <button
                  onClick={handleRelogin}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg text-sm font-medium hover:from-blue-700 hover:to-purple-700 transition shadow-lg"
                >
                  🔑 Log In Again
                </button>
              </div>
            </div>
          </div>
        )}


        {/* 📤 Upload Section - Always at the top */}
        <main className="flex-1 mb-8">
          <div className="bg-white p-6 sm:p-8 rounded-xl shadow-md border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-6 flex items-center gap-2">
              📤 Upload New Dataset
            </h2>
            
            {/* Upload - Responsive */}
            <div className="flex flex-col items-center justify-center py-8 sm:py-10 md:py-12 bg-gray-50 rounded-lg border border-dashed border-gray-300 text-center px-4">
              <div className="mb-4 w-full max-w-md">
                <input 
                  type="file" 
                  accept=".csv,.xlsx,.xls" 
                  onChange={handleFileChange} 
                  className="hidden" 
                  id="file-upload"
                />
                <label 
                  htmlFor="file-upload" 
                  className="inline-block bg-white border border-gray-300 rounded-lg px-4 sm:px-6 py-2 sm:py-2.5 cursor-pointer hover:bg-gray-50 transition text-sm sm:text-base"
                >
                  Choose File
                </label>
                <p className="text-xs sm:text-sm text-gray-500 mt-2 truncate px-2">
                  {selectedFile ? selectedFile.name : "No file chosen"}
                            </p>
                          </div>
              <button
                onClick={handleUpload} 
                disabled={uploading || !selectedFile} 
                className={`w-full sm:w-auto bg-blue-600 text-white px-6 sm:px-8 py-3 sm:py-3.5 rounded-lg font-medium text-sm sm:text-base hover:bg-blue-700 transition ${(uploading || !selectedFile) ? "opacity-50 cursor-not-allowed" : ""}`}
              >
                {uploading ? (
                  <div className="flex items-center space-x-2">
                    <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24">
                      <circle cx="12" cy="12" r="10" stroke="white" strokeWidth="4" fill="none" />
                    </svg>
                    <span>Processing...</span>
                  </div>
                ) : "Upload & Analyze"}
              </button>
              
              {/* 💡 Important Reminders - Compact Version */}
              <div className="mt-4 pt-3 border-t border-gray-200">
                <div className="max-w-3xl mx-auto">
                  <p className="text-[10px] text-gray-400 mb-2 flex items-center gap-1.5 justify-center">
                    <span className="text-xs">💡</span>
                    <span className="font-medium">Important Reminders</span>
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1">
                    <div className="flex items-start gap-1.5">
                      <span className="text-[10px] text-gray-300 mt-0.5">•</span>
                      <p className="text-[10px] text-gray-400 leading-tight">
                        <span className="font-medium text-gray-500">AI Insights:</span> May not be 100% accurate.
                      </p>
                    </div>
                    <div className="flex items-start gap-1.5">
                      <span className="text-[10px] text-gray-300 mt-0.5">•</span>
                      <p className="text-[10px] text-gray-400 leading-tight">
                        <span className="font-medium text-gray-500">Processing:</span> Depends on file size (seconds to 2 min).
                      </p>
                    </div>
                    <div className="flex items-start gap-1.5">
                      <span className="text-[10px] text-gray-300 mt-0.5">•</span>
                      <p className="text-[10px] text-gray-400 leading-tight">
                        <span className="font-medium text-gray-500">Optimized:</span> Best for retail (Sales & Inventory).
                      </p>
                    </div>
                    <div className="flex items-start gap-1.5">
                      <span className="text-[10px] text-gray-300 mt-0.5">•</span>
                      <p className="text-[10px] text-gray-400 leading-tight">
                        <span className="font-medium text-gray-500">Formats:</span> CSV, XLSX, XLS (max 10MB).
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
                </div>
        </main>

        {/* 📁 Dataset History */}
        {renderDatasetHistory()}

                </div>


      {/* 🗑️ Delete Dataset Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-2xl max-w-md w-full mx-4">
            <div className="p-6">
              <div className="flex items-center justify-center mb-4">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </div>
              </div>
              
              <h2 className="text-xl font-bold text-gray-900 mb-3 text-center">
                Delete Dataset
              </h2>
              
              <p className="text-sm text-gray-600 mb-6 text-center">
                Are you sure you want to delete <strong>"{datasetToDelete?.name}"</strong>? This action cannot be undone and will permanently remove all analytics and charts associated with this dataset.
              </p>

              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => {
                    setShowDeleteModal(false);
                    setDatasetToDelete(null);
                  }}
                  className="flex-1 bg-gray-600 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-gray-700 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleDeleteDataset(datasetToDelete)}
                  disabled={datasetToDelete?.deleting}
                  className="flex-1 bg-red-600 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {datasetToDelete?.deleting ? "Deleting..." : "Delete Dataset"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 🚪 Logout Confirmation Modal */}
      {showLogoutModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-2xl max-w-md w-full mx-4">
            <div className="p-6">
              <div className="flex items-center justify-center mb-4">
                <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                </div>
              </div>
              
              <h2 className="text-xl font-bold text-gray-900 mb-3 text-center">
                Confirm Logout
              </h2>
              
              <p className="text-sm text-gray-600 mb-6 text-center">
                Are you sure you want to logout? You'll be redirected to the home page.
              </p>

              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => setShowLogoutModal(false)}
                  className="flex-1 bg-gray-600 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-gray-700 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleLogout}
                  className="flex-1 bg-orange-600 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-orange-700 transition"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Back to Top Button */}
      {showBackToTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-6 right-6 bg-blue-600 text-white p-3 rounded-full shadow-lg hover:bg-blue-700 transition-all duration-300 z-50 flex items-center justify-center"
          title="Back to top"
        >
          <svg 
            className="w-6 h-6" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M5 10l7-7m0 0l7 7m-7-7v18" 
            />
          </svg>
        </button>
      )}

      {/* 💬 Feedback Modal */}
      <FeedbackModal
        isOpen={showFeedbackModal}
        onClose={() => setShowFeedbackModal(false)}
        onFeedbackSubmitted={handleFeedbackSubmitted}
        datasetName={selectedDatasetData?.name || datasets.find(d => d.id === selectedDatasetId)?.name}
      />
    </div>
  );
};

export default UserDashboard;
