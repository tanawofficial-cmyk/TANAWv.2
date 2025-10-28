import React, { useState, useRef } from "react";
import ReCAPTCHA from "react-google-recaptcha";
import api from "../api";
import logo from "../assets/TANAW-LOGO.png";
import { Link } from "react-router-dom";
import toast, { Toaster } from "react-hot-toast";

const LoginForm = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [captchaToken, setCaptchaToken] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [forgotPasswordEmail, setForgotPasswordEmail] = useState("");
  const [sendingReset, setSendingReset] = useState(false);

  const recaptchaRef = useRef();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleCaptchaChange = (token) => setCaptchaToken(token);
  const toggleShowPassword = () => setShowPassword(!showPassword);

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    if (!forgotPasswordEmail) {
      return toast.error("Please enter your email address");
    }

    setSendingReset(true);
    try {
      const res = await api.post("/auth/forgot-password", {
        email: forgotPasswordEmail,
      });

      if (res.success) {
        toast.success("Password reset link sent! Check your email.");
        setShowForgotPassword(false);
        setForgotPasswordEmail("");
      }
    } catch (err) {
      console.error(err);
      toast.error(err.message || "Failed to send reset email. Please try again.");
    } finally {
      setSendingReset(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!captchaToken) return setErrorMessage("⚠️ Please complete the reCAPTCHA!");
    if (loading) return;

    setLoading(true);
    try {
      const res = await api.post("/auth/login", {
        ...formData,
        captchaToken,
      });

      if (res.success) {
        // 🔒 CRITICAL: Clear ALL session data before storing new session
        localStorage.clear(); // Nuclear option - clear everything to prevent contamination
        
        // Store ONLY the new user session data
        localStorage.setItem("token", res.data.token);
        localStorage.setItem("user", JSON.stringify(res.data.user));
        localStorage.setItem("role", res.data.user?.role || "user");
        
        console.log("✅ Regular user login successful:", {
          email: res.data.user?.email,
          role: res.data.user?.role,
          tokenPreview: res.data.token?.substring(0, 20) + "..."
        });
        
        setErrorMessage("");
        toast.success(res.message || "Login successful! Redirecting...", {
          duration: 2000,
          icon: "🎉",
        });
        
        // Redirect after a short delay to show the success message
        setTimeout(() => {
          // Force a full page reload to clear any cached state
          window.location.replace("/userDashboard");
        }, 1500);
      }
    } catch (err) {
      console.error(err);
      setErrorMessage(err.message); // cleaned up by api.js interceptor
    } finally {
      // Reset captcha for next attempt
      recaptchaRef.current.reset();
      setCaptchaToken(null);
      setLoading(false);
    }
  };

  return (
    <div className="relative flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-blue-900 text-gray-200 overflow-hidden">
      <Toaster position="top-center" toastOptions={{ style: { fontSize: "0.9rem", borderRadius: "8px", padding: "10px 16px" } }} />
      
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-1/2 w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob animation-delay-4000"></div>
      </div>

      <div className="flex flex-col md:flex-row items-stretch justify-center w-full max-w-5xl mx-4 rounded-2xl overflow-hidden shadow-2xl bg-gray-900/80 backdrop-blur-xl border border-white/10">
        
        {/* Branding */}
        <div className="flex-1 flex flex-col items-center justify-center p-8 md:p-12 lg:p-16 bg-gradient-to-br from-gray-800/90 to-gray-900/90 text-center space-y-6 relative overflow-hidden">
          {/* Decorative Elements */}
          <div className="absolute top-10 right-10 w-32 h-32 bg-blue-500 rounded-full filter blur-3xl opacity-20"></div>
          <div className="absolute bottom-10 left-10 w-32 h-32 bg-purple-500 rounded-full filter blur-3xl opacity-20"></div>
          
          <div className="relative z-10 space-y-6">
            <div className="relative inline-block">
              <div className="absolute inset-0 bg-blue-500 rounded-full blur-md opacity-50"></div>
              <img src={logo} alt="TANAW Logo" className="relative w-20 h-20 md:w-24 md:h-24 object-contain rounded-full ring-4 ring-blue-400/30" />
            </div>
            
            <div className="inline-flex items-center space-x-2 bg-blue-500/10 border border-blue-400/30 rounded-full px-4 py-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
              </span>
              <span className="text-xs uppercase tracking-wider text-blue-300 font-medium">See Data Differently</span>
            </div>
            
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white leading-tight">
              <span className="block">Analyze.</span>
              <span className="block">Visualize.</span>
              <span className="block bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Collaborate.</span>
            </h2>
            
            <p className="text-sm md:text-base text-gray-400 max-w-xs mx-auto leading-relaxed">
              The collaborative platform for modern business analytics and data visualization.
            </p>
          </div>
        </div>

        {/* Login Form */}
        <div className="flex-1 p-8 md:p-12 lg:p-16 bg-gray-800/50 backdrop-blur-sm w-full flex flex-col justify-center">
          <div className="mb-8">
            <h1 className="text-2xl md:text-3xl font-bold text-white mb-2">Welcome Back</h1>
            <p className="text-sm text-gray-400">Log in to your TANAW account</p>
          </div>


          {errorMessage && <p className="text-red-400 text-sm mb-2">{errorMessage}</p>}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
              <input
                type="email"
                name="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                  required
                />
                <button
                  type="button"
                  onClick={toggleShowPassword}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white text-sm font-medium transition-colors"
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
            </div>

            <div className="flex justify-end -mt-2">
              <button
                type="button"
                onClick={() => setShowForgotPassword(true)}
                className="text-sm text-blue-400 hover:text-blue-300 transition-colors font-medium"
              >
                Forgot Password?
              </button>
            </div>

            <div className="flex justify-center pt-2">
              <ReCAPTCHA
                ref={recaptchaRef}
                sitekey={process.env.REACT_APP_RECAPTCHA_SITE_KEY}
                onChange={handleCaptchaChange}
                theme="dark"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full text-white py-3.5 rounded-lg font-semibold transition-all duration-300 transform ${
                loading 
                  ? "bg-gray-600 cursor-not-allowed" 
                  : "bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 hover:scale-[1.02] shadow-lg hover:shadow-blue-500/50"
              }`}
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <svg className="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Logging in...</span>
                </div>
              ) : (
                "Log in"
              )}
            </button>
          </form>

          <p className="mt-6 text-sm text-gray-400 text-center">
            Don't have an account?{" "}
            <Link to="/register" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">Sign up</Link>
          </p>
        </div>
      </div>

      {/* Forgot Password Modal */}
      {showForgotPassword && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full border border-white/10 transform transition-all">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-white">
                  🔑 Reset Password
                </h2>
                <button
                  onClick={() => {
                    setShowForgotPassword(false);
                    setForgotPasswordEmail("");
                  }}
                  className="text-gray-400 hover:text-white text-2xl font-bold"
                >
                  ×
                </button>
              </div>
              
              <p className="text-sm text-gray-300 mb-6">
                Enter your email address and we'll send you a link to reset your password.
              </p>

              <form onSubmit={handleForgotPassword} className="space-y-4">
                <input
                  type="email"
                  placeholder="Enter your email"
                  value={forgotPasswordEmail}
                  onChange={(e) => setForgotPasswordEmail(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  required
                />

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowForgotPassword(false);
                      setForgotPasswordEmail("");
                    }}
                    className="flex-1 bg-gray-700 text-white px-4 py-3 rounded-lg hover:bg-gray-600 transition-all font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={sendingReset}
                    className={`flex-1 text-white px-4 py-3 rounded-lg font-medium transition-all ${
                      sendingReset 
                        ? "bg-gray-600 cursor-not-allowed" 
                        : "bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-blue-500/50"
                    }`}
                  >
                    {sendingReset ? "Sending..." : "Send Reset Link"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Custom CSS for animations */}
      <style jsx>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          25% { transform: translate(20px, -50px) scale(1.1); }
          50% { transform: translate(-20px, 20px) scale(0.9); }
          75% { transform: translate(50px, 50px) scale(1.05); }
        }
        .animate-blob {
          animation: blob 20s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
};

export default LoginForm;
