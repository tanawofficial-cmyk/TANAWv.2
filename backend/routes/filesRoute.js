// routes/filesRoute.js
import express from "express";
import multer from "multer";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { uploadFile, uploadClean, confirmMapping, getUserDatasets, saveAnalysisResults, deleteDataset } from "../controllers/fileController.js";
import { authMiddleware } from "../middleware/authMiddleware.js";

const router = express.Router();

// === Fix for ESM (Node.js 22+) ===
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// === Ensure uploads folder exists ===
const uploadDir = path.join(__dirname, "../uploads");
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
  console.log("📂 Created uploads directory:", uploadDir);
}

// === Multer setup ===
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
    cb(null, uniqueSuffix + "-" + file.originalname);
  },
});

const upload = multer({
  storage,
  fileFilter: (req, file, cb) => {
    const allowedTypes = [
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", // .xlsx
      "application/vnd.ms-excel", // .xls
      "text/csv", // .csv
    ];
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error("Only .xlsx, .xls, or .csv files are allowed!"), false);
    }
  },
});

// === Upload Route ===
router.post(
  "/upload",
  authMiddleware,
  (req, res, next) => {
    upload.single("file")(req, res, (err) => {
      if (err) {
        console.error("❌ Multer error:", err.message);
        return res.status(400).json({ success: false, message: err.message });
      }
      next();
    });
  },
  uploadFile
);

// === Upload Clean Route (Flask Integration) ===
router.post(
  "/upload-clean",
  authMiddleware,
  (req, res, next) => {
    upload.single("file")(req, res, (err) => {
      if (err) {
        console.error("❌ Multer error:", err.message);
        return res.status(400).json({ success: false, message: err.message });
      }
      next();
    });
  },
  uploadClean
);

// === Confirm Mapping Route ===
router.post("/confirm-mapping", authMiddleware, confirmMapping);

// === Get User's Datasets Route ===
router.get("/datasets", authMiddleware, getUserDatasets);

// === Save Analysis Results Route ===
router.post("/save-analysis", authMiddleware, saveAnalysisResults);

// === Delete Dataset Route ===
router.delete("/datasets/:id", authMiddleware, deleteDataset);

// ✅ Export as default (important!)
export default router;
