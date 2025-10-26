// fileController.js

import Dataset from "../models/Dataset.js";
import Analytics from "../models/Analytics.js";
import ApiUsage from "../models/ApiUsage.js";
import XLSX from "xlsx";
import axios from "axios";
import FormData from "form-data";
import fs from "fs";

// Flask service base URL - use environment variable for production
const FLASK_BASE_URL = process.env.FLASK_ANALYTICS_URL || "http://127.0.0.1:5002";

// =============== UPLOAD FILE ===============
const uploadFile = async (req, res) => {
  try {
    console.log("📂 Incoming upload...");
    console.log("req.file:", req.file);
    console.log("req.user:", req.user);

    if (!req.file) {
      return res.status(400).json({ success: false, message: "⚠️ No file uploaded" });
    }

    // === Parse dataset locally for validation ===
    let jsonData = [];
    try {
      const workbook = XLSX.readFile(req.file.path);
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      jsonData = XLSX.utils.sheet_to_json(sheet, { defval: null });
    } catch (parseErr) {
      console.error("❌ Failed to parse file:", parseErr.message);
      return res.status(400).json({
        success: false,
        message: "Invalid or unreadable file format.",
      });
    }

    if (jsonData.length === 0) {
      return res.status(400).json({
        success: false,
        message: "⚠️ Uploaded file is empty.",
      });
    }

    // === Send file to Flask analytics microservice ===
    const formData = new FormData();
    formData.append("file", fs.createReadStream(req.file.path));

    let flaskRes;
    try {
      flaskRes = await axios.post(`${FLASK_BASE_URL}/api/files/upload-clean`, formData, {
        headers: formData.getHeaders(),
      });
      // 🧠 Safety check — prevent undefined responses
    if (!flaskRes || !flaskRes.data) {
      console.error("⚠️ Flask returned no data.");
      return res.status(500).json({
        success: false,
        message: "Flask returned no data. Please check analytics service.",
      });
    }

    } catch (flaskErr) {
      console.error("❌ Flask service error:", flaskErr.message);
      if (flaskErr.response) {
        console.error("Flask error response:", flaskErr.response.data);
      }
      return res.status(500).json({
        success: false,
        message: "Flask analytics service error",
        errors: flaskErr.response?.data || null,
      });
    }

    // 🧠 Safety check — prevent undefined responses
    if (!flaskRes || !flaskRes.data) {
      console.error("⚠️ Flask returned no data.");
      return res.status(500).json({
        success: false,
        message: "Flask returned no data. Please check analytics service.",
      });
    }

    const flaskData = flaskRes.data || {};
    console.log("🔍 Flask response:", flaskData);

    // 📊 Log API usage for OpenAI calls made by Flask service
    try {
      // Estimate OpenAI API usage based on Flask response
      // This is a rough estimate since Flask service doesn't return exact token counts
      const estimatedTokens = Math.max(100, (flaskData.columns?.length || 0) * 50); // Rough estimate
      const estimatedCost = (estimatedTokens / 1000) * 0.002; // Rough cost estimate
      
      await ApiUsage.logApiUsage({
        service: 'openai',
        endpoint: '/api/files/upload-clean',
        method: 'POST',
        tokensUsed: estimatedTokens,
        tokensPrompt: Math.floor(estimatedTokens * 0.7),
        tokensCompletion: Math.floor(estimatedTokens * 0.3),
        model: 'gpt-3.5-turbo',
        estimatedCost: estimatedCost,
        responseTime: flaskRes.headers['x-response-time'] || 0,
        statusCode: flaskRes.status,
        success: true,
        userId: req.user.id
      });
      
      console.log(`📊 Logged OpenAI API usage: ${estimatedTokens} tokens, $${estimatedCost.toFixed(4)} cost`);
    } catch (apiLogError) {
      console.error('❌ Failed to log API usage:', apiLogError);
      // Don't fail the upload if API logging fails
    }

    // === Safely extract columns ===
    const safeColumns = Array.isArray(flaskData.columns) ? flaskData.columns : [];
    const analyzedColumns = safeColumns.map((col) => ({
      name: col.column || col.name || "Unknown",
      detectedType: col.detectedType || col.type || "Unknown",
      confidence: col.confidence || 0,
      method: col.method || "ml",
    }));

    // === Check for uncertain or missing columns ===
    let uncertainCols = flaskData.cleaningReport?.uncertain_columns || [];
    const missingCols = flaskData.datasetInfo?.missing_columns || [];

    // 🧠 Normalize uncertain columns to always have details
    if (Array.isArray(uncertainCols)) {
      uncertainCols = uncertainCols.map((col) => {
        if (typeof col === "string") {
          // Match with analyzedColumns if exists
          const match = analyzedColumns.find(
            (c) => c.name.toLowerCase() === col.toLowerCase()
          );
          return {
            column: col,
            detectedType: match?.detectedType || "Unknown",
            confidence: match?.confidence || "?",
          };
        }
        return col;
      });
    }


    // === Save dataset in MongoDB ===
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: "Unauthorized: Please log in.",
      });
    }

    const dataset = new Dataset({
      ownerId: req.user.id,
      fileName: req.file.filename,
      originalName: req.file.originalname,
      filePath: req.file.path,
      rowCount: flaskData.rowCount || jsonData.length,
      missingValues: jsonData
        .flatMap((r) => Object.values(r))
        .filter((v) => v === null || v === "").length,
      columns: analyzedColumns,
      datasetType: flaskData.datasetInfo?.dataset_type || "unknown",
      datasetConfidence: flaskData.datasetInfo?.confidence || 0,
      suggestedAnalytics: flaskData.datasetInfo?.suggested_analytics || [],
      status: "uploaded",
      // ✅ Store Flask analysis ID for linking
      flaskAnalysisId: flaskData.analysis_id || null,
      // ✅ Store analysis results if available
      analysisData: flaskData.analysis || null,
      visualizationData: flaskData.analysis?.charts || [],
    });

    await dataset.save();

    // 📊 Track chart generation analytics
    const charts = flaskData.analysis?.charts || [];
    if (charts.length > 0) {
      try {
        // Track each chart generation as a separate event
        for (const chart of charts) {
          await Analytics.create({
            userId: req.user.id,
            type: 'chart_generation',
            details: {
              chartType: chart.type || 'unknown',
              chartTitle: chart.title || chart.name || 'Untitled',
              datasetId: dataset._id,
              datasetName: req.file.originalname,
              timestamp: new Date()
            }
          });
        }
        console.log(`📊 Tracked ${charts.length} chart generation events`);
        
        // 📊 Log additional API usage for chart generation
        const chartTokens = charts.length * 200; // Estimate tokens per chart
        const chartCost = (chartTokens / 1000) * 0.002;
        
        await ApiUsage.logApiUsage({
          service: 'openai',
          endpoint: '/api/files/upload-clean',
          method: 'POST',
          tokensUsed: chartTokens,
          tokensPrompt: Math.floor(chartTokens * 0.6),
          tokensCompletion: Math.floor(chartTokens * 0.4),
          model: 'gpt-3.5-turbo',
          estimatedCost: chartCost,
          responseTime: 0,
          statusCode: 200,
          success: true,
          userId: req.user.id
        });
        
        console.log(`📊 Logged chart generation API usage: ${chartTokens} tokens, $${chartCost.toFixed(4)} cost`);
      } catch (analyticsError) {
        console.error('Failed to track chart generation:', analyticsError);
        // Don't fail the upload if analytics tracking fails
      }
    }

    // === If columns are uncertain, request user confirmation ===
      if (uncertainCols.length > 0 || missingCols.length > 0) {
    console.log("⚠️ Missing/uncertain columns detected:", [
      ...uncertainCols,
      ...missingCols,
    ]);

    // 🧩 Normalize missing columns too
      const missingDetails = missingCols.map((col) => ({
        column: col,
        detectedType: "Unknown",
        confidence: "?",
      }));

      // 🧹 Auto-cleanup: Delete uploaded file (mapping required case)
      if (req.file && req.file.path) {
        try {
          fs.unlink(req.file.path, (err) => {
            if (err) console.error("⚠️ Failed to delete uploaded file:", err.message);
            else console.log("🧹 Cleaned up uploaded file:", req.file.filename);
          });
        } catch (cleanupErr) {
          console.error("⚠️ Cleanup error:", cleanupErr.message);
        }
      }

      return res.status(200).json({
        success: true,
        nextStep: "mapping_required",
        processed: {
          uncertainColumns: [...uncertainCols, ...missingDetails],
          columns: analyzedColumns,
          datasetInfo: flaskData.datasetInfo,
          cleaningReport: flaskData.cleaningReport,
        },
        datasetId: dataset._id,
      });
    }


    // ✅ If dataset is complete, flatten nested "processed" keys
      const processedData = flaskData.processed || flaskData;

      const responsePayload = {
        success: true,
        nextStep: flaskData.nextStep || "processing_complete",
        processed: {
          charts: processedData.charts || [],
          cleaningReport: processedData.cleaningReport || {},
          datasetInfo: processedData.datasetInfo || {},
          insights: processedData.insights || [],
        },
        datasetId: dataset._id,
      };

      // 🧩 Debug logs
      console.log("📊 Flask returned charts:", (processedData.charts || []).length);
      console.log("💡 Flask insights:", processedData.insights);
      console.log("🚀 Sending final response to frontend:", responsePayload);

      // 🧹 Auto-cleanup: Delete uploaded file after successful processing
      if (req.file && req.file.path) {
        try {
          fs.unlink(req.file.path, (err) => {
            if (err) {
              console.error("⚠️ Failed to delete uploaded file:", err.message);
            } else {
              console.log("🧹 Cleaned up uploaded file:", req.file.filename);
            }
          });
        } catch (cleanupErr) {
          console.error("⚠️ Cleanup error:", cleanupErr.message);
        }
      }

      return res.status(200).json(responsePayload);

  } catch (err) {
    console.error("❌ File upload & analysis error:", err);
    
    // 🧹 Cleanup file on error too
    if (req.file && req.file.path) {
      try {
        fs.unlinkSync(req.file.path);
        console.log("🧹 Cleaned up failed upload:", req.file.filename);
      } catch (cleanupErr) {
        console.error("⚠️ Failed to cleanup after error:", cleanupErr.message);
      }
    }
    
    return res.status(500).json({
      success: false,
      message: "Server error during file upload",
      error: err.message,
    });
  }
};

// =============== CONFIRM MAPPING ===============
const confirmMapping = async (req, res) => {
  try {
    const { mappings, fileName, analysis_id } = req.body;

    if (!mappings) {
      return res
        .status(400)
        .json({ success: false, message: "Mappings are required" });
    }

    let requestBody = {
      mappings: mappings,
      analysis_id: analysis_id
    };

    // If no analysis_id, we need file_path
    if (!analysis_id) {
      if (!fileName) {
        return res
          .status(400)
          .json({ success: false, message: "Either analysis_id or fileName is required" });
      }

      const filePath = `uploads/${fileName}`;
      if (!fs.existsSync(filePath)) {
        return res.status(404).json({ success: false, message: "File not found" });
      }

      requestBody.file_path = filePath;
    }

    // Call the new Flask confirm-mapping endpoint
    let flaskRes;
    try {
      flaskRes = await axios.post(`${FLASK_BASE_URL}/confirm-mapping`, requestBody, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
    } catch (flaskErr) {
      console.error("❌ Flask service error (confirm-mapping):", flaskErr.message);
      return res.status(500).json({
        success: false,
        message: "Error confirming mappings",
        errors: flaskErr.response?.data || null,
      });
    }

    // 📊 Log API usage for OpenAI calls made by Flask service
    try {
      const estimatedTokens = Math.max(50, (requestBody.column_mappings?.length || 0) * 30); // Rough estimate
      const estimatedCost = (estimatedTokens / 1000) * 0.002; // Rough cost estimate
      
      await ApiUsage.logApiUsage({
        service: 'openai',
        endpoint: '/confirm-mapping',
        method: 'POST',
        tokensUsed: estimatedTokens,
        tokensPrompt: Math.floor(estimatedTokens * 0.7),
        tokensCompletion: Math.floor(estimatedTokens * 0.3),
        model: 'gpt-3.5-turbo',
        estimatedCost: estimatedCost,
        responseTime: flaskRes.headers['x-response-time'] || 0,
        statusCode: flaskRes.status,
        success: true,
        userId: req.user.id
      });
      
      console.log(`📊 Logged OpenAI API usage: ${estimatedTokens} tokens, $${estimatedCost.toFixed(4)} cost`);
    } catch (apiLogError) {
      console.error('❌ Failed to log API usage:', apiLogError);
      // Don't fail the upload if API logging fails
    }

    // Return the Flask response directly
    return res.json(flaskRes.data);
  } catch (err) {
    console.error("❌ confirmMapping error:", err);
    return res.status(500).json({
      success: false,
      message: "Server error during confirm mapping",
      error: err.message,
    });
  }
};

// =============== UPLOAD CLEAN (Flask Integration) ===============
const uploadClean = async (req, res) => {
  try {
    console.log("📂 Incoming upload-clean...");
    console.log("req.file:", req.file);
    console.log("req.user:", req.user);

    if (!req.file) {
      return res.status(400).json({ success: false, message: "⚠️ No file uploaded" });
    }

    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: "Unauthorized: Please log in."
      });
    }

    // === Send file to Flask analytics microservice ===
    const formData = new FormData();
    formData.append("file", fs.createReadStream(req.file.path));

    let flaskRes;
    try {
      flaskRes = await axios.post(`${FLASK_BASE_URL}/api/files/upload-clean`, formData, {
        headers: formData.getHeaders(),
      });
    } catch (flaskErr) {
      console.error("❌ Flask service error:", flaskErr.message);
      return res.status(500).json({
        success: false,
        message: "Flask analytics service error",
        errors: flaskErr.response?.data || null,
      });
    }

    const flaskData = flaskRes.data || {};
    console.log("🔍 Flask response:", flaskData);

    // 📊 Log API usage for OpenAI calls made by Flask service
    try {
      // Estimate OpenAI API usage based on Flask response
      const estimatedTokens = Math.max(100, (flaskData.columns?.length || 0) * 50); // Rough estimate
      const estimatedCost = (estimatedTokens / 1000) * 0.002; // Rough cost estimate
      
      await ApiUsage.logApiUsage({
        service: 'openai',
        endpoint: '/api/files/upload-clean',
        method: 'POST',
        tokensUsed: estimatedTokens,
        tokensPrompt: Math.floor(estimatedTokens * 0.7),
        tokensCompletion: Math.floor(estimatedTokens * 0.3),
        model: 'gpt-3.5-turbo',
        estimatedCost: estimatedCost,
        responseTime: flaskRes.headers['x-response-time'] || 0,
        statusCode: flaskRes.status,
        success: true,
        userId: req.user.id
      });
      
      console.log(`📊 Logged OpenAI API usage: ${estimatedTokens} tokens, $${estimatedCost.toFixed(4)} cost`);
    } catch (apiLogError) {
      console.error('❌ Failed to log API usage:', apiLogError);
      // Don't fail the upload if API logging fails
    }

    // === Parse dataset locally for validation ===
    let jsonData = [];
    try {
      const workbook = XLSX.readFile(req.file.path);
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      jsonData = XLSX.utils.sheet_to_json(sheet, { defval: null });
    } catch (parseErr) {
      console.error("❌ Failed to parse file:", parseErr.message);
      return res.status(400).json({
        success: false,
        message: "Invalid or unreadable file format.",
      });
    }

    // === Safely extract columns ===
    const safeColumns = Array.isArray(flaskData.columns) ? flaskData.columns : [];
    const analyzedColumns = safeColumns.map((col) => ({
      name: col.column || col.name || "Unknown",
      detectedType: col.detectedType || col.type || "Unknown",
      confidence: col.confidence || 0,
      method: col.method || "ml",
    }));

    // === Save dataset in MongoDB ===
    const dataset = new Dataset({
      ownerId: req.user.id,
      fileName: req.file.filename,
      originalName: req.file.originalname,
      filePath: req.file.path,
      rowCount: flaskData.rowCount || jsonData.length,
      missingValues: jsonData
        .flatMap((r) => Object.values(r))
        .filter((v) => v === null || v === "").length,
      columns: analyzedColumns,
      datasetType: flaskData.datasetInfo?.dataset_type || "unknown",
      datasetConfidence: flaskData.datasetInfo?.confidence || 0,
      suggestedAnalytics: flaskData.datasetInfo?.suggested_analytics || [],
      status: "processed", // ✅ Mark as processed since Flask already analyzed it
      // ✅ Store Flask analysis ID for linking
      flaskAnalysisId: flaskData.analysis_id || null,
      // ✅ Store analysis results from Flask
      analysisData: flaskData.analysis || null,
      visualizationData: flaskData.analysis?.charts || [],
    });

    await dataset.save();
    console.log(`✅ Saved dataset ${dataset._id} to MongoDB`);

    // === Return Flask response with MongoDB dataset ID ===
    const responsePayload = {
      ...flaskData, // Return all Flask data
      datasetId: dataset._id, // Add MongoDB dataset ID
      mongoId: dataset._id, // Alternative field name
    };

    console.log("🚀 Sending response to frontend:", responsePayload);

    return res.status(200).json(responsePayload);

  } catch (err) {
    console.error("❌ Upload-clean error:", err);
    return res.status(500).json({
      success: false,
      message: "Server error during upload-clean",
      error: err.message,
    });
  }
};

// =============== SAVE ANALYSIS RESULTS ===============
const saveAnalysisResults = async (req, res) => {
  try {
    const { analysisId, analysisData, visualizationData } = req.body;
    
    console.log("💾 Save analysis request:", { analysisId, hasAnalysisData: !!analysisData, hasVisualizationData: !!visualizationData });
    
    if (!analysisId) {
      return res.status(400).json({
        success: false,
        message: "Analysis ID is required"
      });
    }

    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: "Unauthorized: Please log in."
      });
    }

    // 🔍 Find the dataset by Flask analysis ID
    const dataset = await Dataset.findOne({ 
      flaskAnalysisId: analysisId,
      ownerId: req.user.id 
    });

    if (!dataset) {
      console.log("❌ No dataset found for Flask analysis ID:", analysisId, "user:", req.user.id);
      return res.status(404).json({
        success: false,
        message: "Dataset not found for this analysis"
      });
    }

    console.log("📊 Found dataset:", dataset._id, "for Flask analysis ID:", analysisId);

    // Update the dataset with analysis results
    dataset.analysisData = analysisData;
    dataset.visualizationData = visualizationData || [];
    dataset.status = "processed";
    
    await dataset.save();

    console.log(`✅ Updated dataset ${dataset._id} with analysis results`);

    return res.json({
      success: true,
      message: "Analysis results saved successfully"
    });

  } catch (err) {
    console.error("❌ Error saving analysis results:", err);
    return res.status(500).json({
      success: false,
      message: "Server error saving analysis results",
      error: err.message
    });
  }
};

// =============== GET USER'S DATASETS ===============
const getUserDatasets = async (req, res) => {
  try {
    console.log("📂 Fetching user datasets...");
    console.log("req.user:", req.user);

    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: "Unauthorized: Please log in.",
      });
    }

    // Find all datasets owned by the user
    const datasets = await Dataset.find({ ownerId: req.user.id })
      .sort({ uploadDate: -1 }) // Most recent first
      .select('-filePath') // Exclude file path for security
      .lean();

    console.log(`📂 Found ${datasets.length} datasets for user ${req.user.id}`);

    // Transform datasets for frontend
    const transformedDatasets = datasets.map(dataset => ({
      id: dataset._id.toString(),
      analysisId: dataset._id.toString(), // Use dataset ID as analysis ID
      name: dataset.originalName || dataset.fileName,
      fileName: dataset.fileName,
      uploadDate: dataset.uploadDate,
      uploadTime: new Date(dataset.uploadDate).toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit', 
        hour12: true 
      }),
      rowCount: dataset.rowCount,
      missingValues: dataset.missingValues,
      columns: dataset.columns,
      datasetType: dataset.datasetType,
      datasetConfidence: dataset.datasetConfidence,
      suggestedAnalytics: dataset.suggestedAnalytics,
      status: dataset.status,
      // ✅ Include actual analysis data from database
      visualizationData: dataset.visualizationData || [],
      analysisData: dataset.analysisData || null
    }));

    return res.json({
      success: true,
      message: "Datasets retrieved successfully",
      data: {
        datasets: transformedDatasets,
        count: transformedDatasets.length
      }
    });

  } catch (err) {
    console.error("❌ Error fetching user datasets:", err);
    return res.status(500).json({
      success: false,
      message: "Server error",
      error: err.message
    });
  }
};

// 🗑️ Delete Dataset
const deleteDataset = async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;

    console.log(`🗑️ Deleting dataset ${id} for user ${userId}`);

    // Find and delete the dataset
    const dataset = await Dataset.findOneAndDelete({
      _id: id,
      ownerId: userId
    });

    if (!dataset) {
      return res.status(404).json({
        success: false,
        message: "Dataset not found or you don't have permission to delete it"
      });
    }

    console.log(`✅ Dataset deleted: ${dataset.originalName || dataset.fileName}`);

    return res.json({
      success: true,
      message: "Dataset deleted successfully",
      deletedDataset: {
        id: dataset._id,
        name: dataset.originalName || dataset.fileName
      }
    });

  } catch (err) {
    console.error("❌ Error deleting dataset:", err);
    return res.status(500).json({
      success: false,
      message: "Server error",
      error: err.message
    });
  }
};

export {
  uploadFile,
  confirmMapping,
  getUserDatasets,
  saveAnalysisResults,
  uploadClean,
  deleteDataset
};