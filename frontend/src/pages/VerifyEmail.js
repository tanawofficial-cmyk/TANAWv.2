// VerifyEmail.js
import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import api from "../api";
import logo from "../assets/TANAW-LOGO.png";
import toast, { Toaster } from "react-hot-toast";

const VerifyEmail = () => {
  const { token } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState("verifying"); // verifying, success, error
  const [message, setMessage] = useState("");
  const [newEmail, setNewEmail] = useState("");

  useEffect(() => {
    verifyEmail();
  }, [token]);

  const verifyEmail = async () => {
    try {
      const response = await api.get(`/users/verify-email/${token}`);
      
      console.log("Email verification response:", response);

      if (response && response.success) {
        setStatus("success");
        setMessage(response.message || "Email verified successfully!");
        setNewEmail(response.newEmail);
        toast.success("✅ Email verified successfully!");
        
        // Redirect to login after 5 seconds
        setTimeout(() => {
          navigate("/login");
        }, 5000);
      } else {
        setStatus("error");
        setMessage(response?.message || "Verification failed");
        toast.error(response?.message || "Verification failed");
      }
    } catch (error) {
      console.error("Email verification error:", error);
      setStatus("error");
      setMessage(error?.message || "Invalid or expired verification link");
      toast.error(error?.message || "Invalid or expired verification link");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-blue-900 flex items-center justify-center p-4">
      <Toaster position="top-center" />
      
      <div className="max-w-md w-full bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl shadow-2xl p-8">
        {/* Logo */}
        <div className="flex justify-center mb-6">
          <div className="relative">
            <div className="absolute inset-0 bg-blue-500 rounded-full blur-md opacity-50"></div>
            <img 
              src={logo} 
              alt="TANAW Logo" 
              className="relative w-20 h-20 object-contain rounded-full ring-4 ring-blue-400/30" 
            />
          </div>
        </div>

        {/* Status Messages */}
        {status === "verifying" && (
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <svg className="animate-spin h-12 w-12 text-blue-400" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Verifying Your Email...</h2>
            <p className="text-gray-300">Please wait while we verify your email address.</p>
          </div>
        )}

        {status === "success" && (
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">✅ Email Verified!</h2>
            <p className="text-gray-300 mb-4">{message}</p>
            
            {newEmail && (
              <div className="bg-blue-500/10 border border-blue-400/30 rounded-lg p-4 mb-6">
                <p className="text-sm text-gray-300">
                  Your new email address:
                </p>
                <p className="text-lg font-semibold text-blue-400 mt-1">
                  {newEmail}
                </p>
              </div>
            )}
            
            <p className="text-sm text-gray-400 mb-6">
              Redirecting to login in 5 seconds...
            </p>
            
            <Link
              to="/login"
              className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all"
            >
              Go to Login Now
            </Link>
          </div>
        )}

        {status === "error" && (
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">❌ Verification Failed</h2>
            <p className="text-gray-300 mb-6">{message}</p>
            
            <div className="bg-red-500/10 border border-red-400/30 rounded-lg p-4 mb-6">
              <p className="text-sm text-gray-300">
                Common reasons:
              </p>
              <ul className="text-sm text-gray-400 mt-2 space-y-1 text-left">
                <li>• Link has expired (valid for 24 hours)</li>
                <li>• Link has already been used</li>
                <li>• Invalid verification token</li>
              </ul>
            </div>
            
            <div className="space-y-3">
              <Link
                to="/userDashboard"
                className="block bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all"
              >
                Back to Dashboard
              </Link>
              <Link
                to="/support"
                className="block bg-white/10 border border-white/20 text-white px-6 py-3 rounded-lg font-semibold hover:bg-white/20 transition-all"
              >
                Contact Support
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VerifyEmail;

