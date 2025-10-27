// backend/server.js
import express from "express";
import mongoose from "mongoose";
import dotenv from "dotenv";
import cors from "cors";

// Routes
import authRoutes from "./routes/authRoute.js";
import fileRoutes from "./routes/filesRoute.js";
import userRoutes from "./routes/users.js";
import analyticsRoutes from "./routes/analyticsRoute.js";
import feedbackRoutes from "./routes/feedback.js";
import adminRoutes from "./routes/adminRoute.js";
import connectivityRoutes from "./routes/connectivityRoute.js";
import contactRoutes from "./routes/contactRoute.js";

dotenv.config();

const app = express();

// CORS Configuration - Allow requests from Hostinger frontend
const corsOptions = {
  origin: function (origin, callback) {
    // Allow requests with no origin (mobile apps, Postman, etc.)
    if (!origin) return callback(null, true);
    
    // List of allowed origins
    const allowedOrigins = [
      'http://localhost:3000', // Local development
      process.env.FRONTEND_URL, // Production Hostinger URL
    ].filter(Boolean); // Remove undefined values
    
    if (allowedOrigins.indexOf(origin) !== -1) {
      callback(null, true);
    } else {
      console.log('⚠️ CORS blocked origin:', origin);
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true, // Allow cookies
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
};

// Middleware
app.use(cors(corsOptions));
app.use(express.json());
app.use("/api/admin", adminRoutes);

// Root route for testing
app.get("/", (req, res) => {
  res.send("✅ TANAW Backend is running!");
});

// Health check endpoint
app.get("/api/health", (req, res) => {
  res.status(200).json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    service: 'TANAW Backend'
  });
});

// API Routes
app.use("/api/auth", authRoutes);
app.use("/api/files", fileRoutes);
app.use("/api/users", userRoutes);
app.use("/api/analytics", analyticsRoutes);
app.use("/api/feedback", feedbackRoutes);
app.use("/api/contact", contactRoutes);
app.use("/api/admin/connectivity", connectivityRoutes);

// Connect MongoDB
mongoose
  .connect(process.env.MONGO_URI)
  .then(() => console.log("✅ MongoDB connected"))
  .catch((err) => console.error("❌ MongoDB connection error:", err));

// Global error handler (prevents crash on unhandled errors)
app.use((err, req, res, next) => {
  console.error("🔥 Server error:", err.stack);
  res.status(500).json({ success: false, message: "Internal Server Error" });
});

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () =>
  console.log(`🚀 Server running at http://localhost:${PORT}`)
);
