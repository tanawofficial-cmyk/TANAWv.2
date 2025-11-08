// models/Dataset.js
import mongoose from "mongoose";

const ColumnSchema = new mongoose.Schema({
  name: { type: String, required: true },
  detectedType: { type: String, required: true }, // ✅ allow any string, no enum restriction
  confidence: { type: Number },                   // ✅ optional confidence score
  method: { type: String },                       // ✅ fuzzy | ml
});

const DatasetSchema = new mongoose.Schema({
  ownerId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  fileName: { type: String, required: true },
  originalName: { type: String }, // ✅ Add original filename
  filePath: { type: String, required: true },
  uploadDate: { type: Date, default: Date.now },
  columns: [ColumnSchema],
  rowCount: { type: Number },
  missingValues: { type: Number },
  datasetType: { type: String, default: "unknown" },      // ✅ optional
  datasetConfidence: { type: Number, default: 0 },        // ✅ optional
  suggestedAnalytics: { type: [String], default: [] },    // ✅ optional
  status: { type: String, enum: ["uploaded", "processed"], default: "uploaded" },
  // ✅ Add Flask analysis ID for linking
  flaskAnalysisId: { type: String, default: null }, // Store Flask analysis_id
  // ✅ Add analysis results
  analysisData: { type: mongoose.Schema.Types.Mixed, default: null }, // Store full analysis results
  visualizationData: { type: [mongoose.Schema.Types.Mixed], default: [] }, // Store charts
  // 🎯 Add generation mode and category
  generationMode: { type: String, enum: ["auto", "manual"], default: "auto" }, // auto or manual mode
  selectedCategory: { type: String, default: null }, // sales, inventory, finance, customer, product
});

export default mongoose.model("Dataset", DatasetSchema);
