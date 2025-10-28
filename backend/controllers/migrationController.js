// migrationController.js - One-time data fixes
import User from "../models/User.js";
import Dataset from "../models/Dataset.js";

/**
 * @desc    Recalculate and fix user dataset/chart counts
 * @route   POST /api/admin/migrate/fix-user-counts
 * @access  Private (Admin only)
 */
export const fixUserCounts = async (req, res) => {
  try {
    console.log('🔧 Starting user counts migration...');
    
    const users = await User.find({});
    let fixed = 0;
    
    for (const user of users) {
      // Count actual datasets owned by this user
      const datasetCount = await Dataset.countDocuments({ ownerId: user._id });
      
      // Count total charts from all their datasets
      const datasets = await Dataset.find({ ownerId: user._id });
      const chartsGenerated = datasets.reduce((sum, dataset) => {
        return sum + (dataset.visualizationData?.length || 0);
      }, 0);
      
      // Update user counts if different
      if (user.datasetCount !== datasetCount || user.chartsGenerated !== chartsGenerated) {
        await User.findByIdAndUpdate(user._id, {
          datasetCount,
          chartsGenerated
        });
        console.log(`✅ Fixed user ${user.email}: ${datasetCount} datasets, ${chartsGenerated} charts`);
        fixed++;
      }
    }
    
    console.log(`✅ Migration complete! Fixed ${fixed} users`);
    
    res.json({
      success: true,
      message: `Migration complete! Fixed ${fixed} users`,
      totalUsers: users.length,
      fixedUsers: fixed
    });
  } catch (error) {
    console.error('❌ Migration error:', error);
    res.status(500).json({
      success: false,
      message: 'Migration failed',
      error: error.message
    });
  }
};

/**
 * @desc    Clean up orphaned files (files without database records)
 * @route   POST /api/admin/migrate/cleanup-orphaned-files
 * @access  Private (Admin only)
 */
export const cleanupOrphanedFiles = async (req, res) => {
  try {
    console.log('🧹 Starting orphaned files cleanup...');
    
    const fs = require('fs');
    const path = require('path');
    
    // Get all datasets from database
    const datasets = await Dataset.find({});
    const validFiles = new Set(datasets.map(d => d.filePath));
    
    // Read uploads directory
    const uploadsDir = path.join(process.cwd(), 'uploads');
    if (!fs.existsSync(uploadsDir)) {
      return res.json({ success: true, message: 'No uploads directory found' });
    }
    
    const files = fs.readdirSync(uploadsDir);
    let deletedCount = 0;
    
    for (const file of files) {
      const filePath = path.join(uploadsDir, file);
      
      // Skip if it's a valid dataset file
      if (!validFiles.has(filePath)) {
        try {
          fs.unlinkSync(filePath);
          console.log(`🧹 Deleted orphaned file: ${file}`);
          deletedCount++;
        } catch (err) {
          console.error(`⚠️ Failed to delete ${file}:`, err.message);
        }
      }
    }
    
    console.log(`✅ Cleanup complete! Deleted ${deletedCount} orphaned files`);
    
    res.json({
      success: true,
      message: `Cleanup complete! Deleted ${deletedCount} orphaned files`,
      totalFiles: files.length,
      deletedFiles: deletedCount
    });
  } catch (error) {
    console.error('❌ Cleanup error:', error);
    res.status(500).json({
      success: false,
      message: 'Cleanup failed',
      error: error.message
    });
  }
};

