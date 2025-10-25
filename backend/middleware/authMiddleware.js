// backend/middleware/authMiddleware.js
import jwt from "jsonwebtoken";

export const authMiddleware = (req, res, next) => {
  try {
    // 🔑 Get token from Authorization header
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return res.status(401).json({
        success: false,
        message: "Unauthorized: No token provided",
      });
    }

    const token = authHeader.split(" ")[1];

    // 🔑 Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // ✅ Attach user payload to request (so controller can use req.user.id)
    req.user = decoded;

    next();
  } catch (err) {
    console.error("❌ JWT Auth Error:", err.message);
    return res.status(401).json({
      success: false,
      message: "Unauthorized: Invalid or expired token",
    });
  }
};

// Admin authorization middleware
export const authorizeAdmin = (req, res, next) => {
  try {
    // Check if user exists and has admin role
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: "Unauthorized: Authentication required",
      });
    }

    if (req.user.role !== "admin") {
      return res.status(403).json({
        success: false,
        message: "Forbidden: Admin access required",
      });
    }

    next();
  } catch (err) {
    console.error("❌ Admin Authorization Error:", err.message);
    return res.status(403).json({
      success: false,
      message: "Forbidden: Access denied",
    });
  }
};