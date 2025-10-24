// scripts/clearDatasets.js
// ⚠️ This script will DELETE ALL datasets from the database
// Use with caution!

import mongoose from "mongoose";
import dotenv from "dotenv";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import Dataset from "../models/Dataset.js";

// Load environment variables
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
dotenv.config({ path: join(__dirname, "../.env") });

async function clearAllDatasets() {
  try {
    // Connect to MongoDB
    console.log("🔌 Connecting to MongoDB...");
    await mongoose.connect(process.env.MONGO_URI);
    console.log("✅ Connected to MongoDB");

    // Count datasets before deletion
    const countBefore = await Dataset.countDocuments();
    console.log(`📊 Found ${countBefore} datasets in database`);

    if (countBefore === 0) {
      console.log("✅ Database is already empty");
      process.exit(0);
    }

    // Confirm deletion
    console.log("⚠️  WARNING: About to delete ALL datasets!");
    console.log("⏳ Deleting in 3 seconds... Press Ctrl+C to cancel");
    
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Delete all datasets
    const result = await Dataset.deleteMany({});
    console.log(`✅ Deleted ${result.deletedCount} datasets from database`);

    // Verify deletion
    const countAfter = await Dataset.countDocuments();
    console.log(`📊 Datasets remaining: ${countAfter}`);

    if (countAfter === 0) {
      console.log("🎉 Database successfully cleared!");
    } else {
      console.log("⚠️  Warning: Some datasets may still remain");
    }

    // Close connection
    await mongoose.connection.close();
    console.log("🔌 Disconnected from MongoDB");
    process.exit(0);

  } catch (error) {
    console.error("❌ Error clearing datasets:", error);
    process.exit(1);
  }
}

// Run the script
clearAllDatasets();

