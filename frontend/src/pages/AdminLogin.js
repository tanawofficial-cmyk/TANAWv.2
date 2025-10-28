import React, { useState } from "react";
import api from "../api";
import logo from "../assets/TANAW-LOGO.png";
import { Link } from "react-router-dom";
import toast, { Toaster } from "react-hot-toast";

const AdminLoginForm = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    licenseKey: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const toggleShowPassword = () => setShowPassword(!showPassword);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage("");
    
    // Validate license key is provided
    if (!formData.licenseKey || formData.licenseKey.trim() === "") {
      setErrorMessage("🔑 Admin license key is required");
      toast.error("🔑 Admin license key is required");
      return;
    }
    
    setLoading(true);

    try {
      const res = await api.post("/auth/admin-login", {
        email: formData.email,
        password: formData.password,
        licenseKey: formData.licenseKey,
      });

      if (res.success && res.data.role === "admin") {
        // 🔒 CRITICAL: Clear ALL session data before storing new admin session
        localStorage.clear(); // Nuclear option - clear everything to prevent contamination
        
        // Store ONLY the new admin session data
        localStorage.setItem("token", res.data.token);
        localStorage.setItem("user", JSON.stringify(res.data.user));
        localStorage.setItem("role", "admin");
        
        console.log("✅ Admin login successful:", {
          email: res.data.user?.email,
          role: res.data.role,
          tokenPreview: res.data.token?.substring(0, 20) + "..."
        });
        
        toast.success("Welcome back, Admin!", {
          duration: 2000,
        });
        
        // Redirect to admin dashboard
        setTimeout(() => {
          // Force a full page reload to clear any cached state
          window.location.replace("/admin-dashboard");
        }, 1500);
      }
    } catch (err) {
      console.error("Login error:", err);
      const errorMsg = err.response?.data?.message || "Login failed. Please try again.";
      setErrorMessage(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <Toaster position="top-right" />
      
      <div className="w-full max-w-md">
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
              <img src={logo} alt="TANAW" className="w-10 h-10" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">TANAW</h1>
          <div className="inline-flex items-center gap-2 bg-red-500/20 text-red-400 px-3 py-1 rounded-full text-sm font-medium border border-red-500/30">
            🔒 ADMIN ACCESS
          </div>
          <p className="text-gray-400 mt-4">Secure admin authentication required</p>
        </div>

        {/* Login Form */}
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Field */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Admin Email
              </label>
              <input
                type="email"
                name="email"
                placeholder="admin@tanawofficial.com"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all duration-300"
                required
              />
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Admin Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  placeholder="Enter admin password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all duration-300 pr-12"
                  required
                />
                <button
                  type="button"
                  onClick={toggleShowPassword}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
            </div>

            {/* License Key Field */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Admin License Key
              </label>
              <input
                type="text"
                name="licenseKey"
                placeholder="Enter admin license key"
                value={formData.licenseKey}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all duration-300"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                🔑 License key required for admin access
              </p>
            </div>


            {/* Error Message */}
            {errorMessage && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-lg text-sm">
                {errorMessage}
              </div>
            )}

            {/* Login Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 disabled:from-gray-600 disabled:to-gray-700 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-300 transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed shadow-lg"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Authenticating...
                </div>
              ) : (
                "🔐 Access Admin Dashboard"
              )}
            </button>
          </form>

          {/* Back to User Login */}
          <div className="mt-6 text-center">
            <Link
              to="/login"
              className="text-gray-400 hover:text-white transition-colors text-sm flex items-center justify-center gap-2"
            >
              ← Back to User Login
            </Link>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-gray-500 text-sm">
            © 2025 TANAW - Admin Access Only
          </p>
          <p className="text-gray-600 text-xs mt-1">
            Unauthorized access is prohibited
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminLoginForm;
