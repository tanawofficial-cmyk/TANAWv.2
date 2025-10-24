// UserProfileDropdown.js
import React, { useState, useEffect, useRef } from "react";
import api from "../api";
import toast from "react-hot-toast";

const UserProfileDropdown = ({ user, onUserUpdate, onLogout }) => {
  // Dropdown state
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);


  // Modal states
  const [showEditProfileModal, setShowEditProfileModal] = useState(false);
  const [showChangePasswordModal, setShowChangePasswordModal] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [showAboutModal, setShowAboutModal] = useState(false);

  // Form states
  const [profileForm, setProfileForm] = useState({
    fullName: "",
    businessName: "",
    email: ""
  });

  const [passwordForm, setPasswordForm] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: ""
  });

  // Loading states
  const [isUpdatingProfile, setIsUpdatingProfile] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };

    if (isDropdownOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isDropdownOpen]);

  // Update profile form when user data changes
  useEffect(() => {
    if (user) {
      setProfileForm({
        fullName: user.fullName || user.businessName || "User", // Fallback to businessName if fullName missing
        businessName: user.businessName || "",
        email: user.email || ""
      });
    }
  }, [user]);

  // Toggle dropdown
  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  // Handle edit profile
  const handleEditProfile = async (e) => {
    e.preventDefault();
    setIsUpdatingProfile(true);

    try {
      const response = await api.put("/users/me", profileForm);
      
      if (response.data.success) {
        toast.success("✅ Profile updated successfully!");
        onUserUpdate(response.data.data);
        setShowEditProfileModal(false);
        setIsDropdownOpen(false);
      }
    } catch (error) {
      console.error("❌ Profile update error:", error);
      toast.error(error.response?.data?.message || "Failed to update profile");
    } finally {
      setIsUpdatingProfile(false);
    }
  };

  // Handle change password
  const handleChangePassword = async (e) => {
    e.preventDefault();

    // Validate passwords match
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      toast.error("New passwords do not match!");
      return;
    }

    // Validate password length
    if (passwordForm.newPassword.length < 6) {
      toast.error("Password must be at least 6 characters long!");
      return;
    }

    setIsChangingPassword(true);

    try {
      const response = await api.put("/users/change-password", {
        currentPassword: passwordForm.currentPassword,
        newPassword: passwordForm.newPassword
      });

      if (response.data.success) {
        toast.success("✅ Password changed successfully!");
        setPasswordForm({
          currentPassword: "",
          newPassword: "",
          confirmPassword: ""
        });
        setShowChangePasswordModal(false);
        setIsDropdownOpen(false);
      }
    } catch (error) {
      console.error("❌ Password change error:", error);
      toast.error(error.response?.data?.message || "Failed to change password");
    } finally {
      setIsChangingPassword(false);
    }
  };

  return (
    <>
      {/* User Profile Button */}
      <div className="relative" ref={dropdownRef}>
        <button 
          onClick={toggleDropdown} 
          className="flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-100 transition"
        >
          <div className="w-9 h-9 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold shadow-lg">
            {user?.businessName ? user.businessName.charAt(0).toUpperCase() : (user ? "U" : "S")}
          </div>
          <div className="hidden sm:flex flex-col text-left">
            <span className="text-gray-800 font-medium text-sm">
              {user?.businessName || (user ? "User" : "Loading...")}
            </span>
            <span className="text-gray-500 text-xs">
              {user?.email || (user ? "No email" : "Loading...")}
            </span>
          </div>
          <svg 
            className={`w-4 h-4 text-gray-500 transition-transform ${isDropdownOpen ? "rotate-180" : ""}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* Dropdown Menu */}
        {isDropdownOpen && (
          <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-2xl border border-gray-200 z-50 overflow-hidden">
            {/* Account Overview Section */}
            <div className="bg-gradient-to-br from-purple-50 to-blue-50 p-4 border-b border-gray-200">
              <div className="flex items-center space-x-3 mb-3">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full flex items-center justify-center text-white text-lg font-bold shadow-lg">
                  {user?.businessName ? user.businessName.charAt(0).toUpperCase() : "S"}
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-gray-900">Account Overview</h3>
                  <p className="text-xs text-gray-500">Manage your profile</p>
                </div>
              </div>
              
              <div className="bg-white rounded-lg p-3 space-y-2 shadow-sm">
                <div className="flex items-center space-x-2 text-xs">
                  <span className="text-gray-500">👤</span>
                  <span className="text-gray-700 font-medium">
                    {user?.fullName || user?.businessName || (user ? "User" : "Loading...")}
                  </span>
                </div>
                <div className="flex items-center space-x-2 text-xs">
                  <span className="text-gray-500">🏪</span>
                  <span className="text-gray-700">{user?.businessName || (user ? "Business" : "Loading...")}</span>
                </div>
                <div className="flex items-center space-x-2 text-xs">
                  <span className="text-gray-500">📧</span>
                  <span className="text-gray-700 truncate">{user?.email || (user ? "email@example.com" : "Loading...")}</span>
                </div>
              </div>

              <button
                onClick={() => {
                  setShowEditProfileModal(true);
                  setIsDropdownOpen(false);
                }}
                className="w-full mt-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white px-4 py-2 rounded-lg text-xs font-medium hover:from-purple-700 hover:to-blue-700 transition-all shadow-md flex items-center justify-center space-x-2"
              >
                <span>✏️</span>
                <span>Edit Profile</span>
              </button>
            </div>

            {/* Security & Access Section */}
            <div className="p-3 border-b border-gray-200">
              <h4 className="text-xs font-semibold text-gray-700 mb-2 flex items-center space-x-2">
                <span>🔒</span>
                <span>Security & Access</span>
              </h4>
              <button
                onClick={() => {
                  setShowChangePasswordModal(true);
                  setIsDropdownOpen(false);
                }}
                className="w-full text-left px-3 py-2 text-xs text-gray-700 hover:bg-gray-50 rounded-lg transition flex items-center space-x-2"
              >
                <span>🔑</span>
                <span>Change Password</span>
              </button>
              <button
                onClick={onLogout}
                className="w-full text-left px-3 py-2 text-xs text-red-600 hover:bg-red-50 rounded-lg transition flex items-center space-x-2"
              >
                <span>🚪</span>
                <span>Logout</span>
              </button>
            </div>

            {/* Support & About Section */}
            <div className="p-3">
              <h4 className="text-xs font-semibold text-gray-700 mb-2 flex items-center space-x-2">
                <span>📞</span>
                <span>Support & About</span>
              </h4>
              <button
                onClick={() => {
                  setShowHelpModal(true);
                  setIsDropdownOpen(false);
                }}
                className="w-full text-left px-3 py-2 text-xs text-gray-700 hover:bg-gray-50 rounded-lg transition flex items-center space-x-2"
              >
                <span>📚</span>
                <span>Help & Documentation</span>
              </button>
              <button
                onClick={() => {
                  setShowPrivacyModal(true);
                  setIsDropdownOpen(false);
                }}
                className="w-full text-left px-3 py-2 text-xs text-gray-700 hover:bg-gray-50 rounded-lg transition flex items-center space-x-2"
              >
                <span>🧭</span>
                <span>Privacy Policy & Terms</span>
              </button>
              <button
                onClick={() => {
                  setShowAboutModal(true);
                  setIsDropdownOpen(false);
                }}
                className="w-full text-left px-3 py-2 text-xs text-gray-700 hover:bg-gray-50 rounded-lg transition flex items-center space-x-2"
              >
                <span>🏷️</span>
                <span>About TANAW</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Edit Profile Modal */}
      {showEditProfileModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-[60] p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
                  <span>✏️</span>
                  <span>Edit Profile</span>
                </h2>
                <button
                  onClick={() => setShowEditProfileModal(false)}
                  className="text-gray-400 hover:text-gray-600 transition"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <form onSubmit={handleEditProfile} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={profileForm.fullName}
                    onChange={(e) => setProfileForm({ ...profileForm, fullName: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Enter your full name"
                    required
                  />
                  {!user?.fullName && (
                    <p className="text-xs text-blue-600 mt-1">
                      💡 Add your full name to personalize your profile
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Business Name
                  </label>
                  <input
                    type="text"
                    value={profileForm.businessName}
                    onChange={(e) => setProfileForm({ ...profileForm, businessName: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={profileForm.email}
                    onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    required
                  />
                </div>

                <div className="flex space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowEditProfileModal(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isUpdatingProfile}
                    className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isUpdatingProfile ? "Saving..." : "Save Changes"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Change Password Modal */}
      {showChangePasswordModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-[60] p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
                  <span>🔑</span>
                  <span>Change Password</span>
                </h2>
                <button
                  onClick={() => setShowChangePasswordModal(false)}
                  className="text-gray-400 hover:text-gray-600 transition"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <form onSubmit={handleChangePassword} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Current Password
                  </label>
                  <input
                    type="password"
                    value={passwordForm.currentPassword}
                    onChange={(e) => setPasswordForm({ ...passwordForm, currentPassword: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    New Password
                  </label>
                  <input
                    type="password"
                    value={passwordForm.newPassword}
                    onChange={(e) => setPasswordForm({ ...passwordForm, newPassword: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    required
                    minLength={6}
                  />
                  <p className="text-xs text-gray-500 mt-1">Must be at least 6 characters long</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    value={passwordForm.confirmPassword}
                    onChange={(e) => setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    required
                  />
                </div>

                <div className="flex space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowChangePasswordModal(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isChangingPassword}
                    className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isChangingPassword ? "Changing..." : "Change Password"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Help & Documentation Modal */}
      {showHelpModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-[60] p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
                  <span>📚</span>
                  <span>Help & Documentation</span>
                </h2>
                <button
                  onClick={() => setShowHelpModal(false)}
                  className="text-gray-400 hover:text-gray-600 transition"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-6">
                {/* Getting Started */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center space-x-2">
                    <span>🚀</span>
                    <span>Getting Started</span>
                  </h3>
                  <p className="text-sm text-gray-600 mb-2">
                    Welcome to TANAW! This platform helps you analyze your business data and generate insightful analytics.
                  </p>
                  <ul className="list-disc list-inside text-sm text-gray-600 space-y-1 ml-4">
                    <li>Upload your CSV or Excel files</li>
                    <li>Wait for automatic analysis to complete</li>
                    <li>View generated charts and insights</li>
                    <li>Download analytics reports</li>
                  </ul>
                </div>

                {/* File Upload Guide */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center space-x-2">
                    <span>📤</span>
                    <span>Uploading Files</span>
                  </h3>
                  <ul className="list-disc list-inside text-sm text-gray-600 space-y-1 ml-4">
                    <li>Supported formats: CSV (.csv), Excel (.xlsx, .xls)</li>
                    <li>Maximum file size: 10MB</li>
                    <li>Ensure your data has proper headers</li>
                    <li>Remove any special characters in column names</li>
                  </ul>
                </div>

                {/* Analytics Features */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center space-x-2">
                    <span>📊</span>
                    <span>Analytics Features</span>
                  </h3>
                  <ul className="list-disc list-inside text-sm text-gray-600 space-y-1 ml-4">
                    <li>Automatic chart generation based on your data</li>
                    <li>AI-powered insights and recommendations</li>
                    <li>Interactive visualizations</li>
                    <li>Export analytics in multiple formats (JSON, PNG, PDF)</li>
                  </ul>
                </div>

                {/* Contact Support */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-blue-900 mb-2 flex items-center space-x-2">
                    <span>💬</span>
                    <span>Need More Help?</span>
                  </h3>
                  <p className="text-sm text-blue-800 mb-2">
                    Contact our support team for assistance:
                  </p>
                  <p className="text-sm text-blue-900 font-medium">
                    📧 support@tanaw.com<br />
                    📱 +63 123 456 7890
                  </p>
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <button
                  onClick={() => setShowHelpModal(false)}
                  className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition font-medium"
                >
                  Got it!
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Privacy Policy & Terms Modal */}
      {showPrivacyModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-[60] p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
                  <span>🧭</span>
                  <span>Privacy Policy & Terms of Service</span>
                </h2>
                <button
                  onClick={() => setShowPrivacyModal(false)}
                  className="text-gray-400 hover:text-gray-600 transition"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-6">
                {/* Privacy Policy */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Privacy Policy</h3>
                  
                  <div className="space-y-4 text-sm text-gray-600">
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-1">Data Collection</h4>
                      <p>
                        We collect only the information necessary to provide our services, including:
                        business name, email address, and uploaded data files for analysis.
                      </p>
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-800 mb-1">Data Usage</h4>
                      <p>
                        Your data is used solely for generating analytics and insights. We do not
                        share your business data with third parties without your explicit consent.
                      </p>
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-800 mb-1">Data Security</h4>
                      <p>
                        We employ industry-standard security measures to protect your data,
                        including encryption, secure servers, and regular security audits.
                      </p>
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-800 mb-1">Data Retention</h4>
                      <p>
                        Your uploaded files and analytics are stored securely and can be deleted
                        at any time from your dashboard. Deleted data is permanently removed
                        from our systems within 30 days.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Terms of Service */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Terms of Service</h3>
                  
                  <div className="space-y-4 text-sm text-gray-600">
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-1">Acceptable Use</h4>
                      <p>
                        You agree to use TANAW only for lawful purposes and in accordance with
                        these terms. You must not use the service to upload illegal, harmful,
                        or inappropriate content.
                      </p>
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-800 mb-1">Account Responsibility</h4>
                      <p>
                        You are responsible for maintaining the confidentiality of your account
                        credentials and for all activities that occur under your account.
                      </p>
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-800 mb-1">Service Availability</h4>
                      <p>
                        While we strive for 99.9% uptime, we do not guarantee uninterrupted
                        access to the service. Maintenance windows will be communicated in advance.
                      </p>
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-800 mb-1">Intellectual Property</h4>
                      <p>
                        You retain all rights to your uploaded data. TANAW retains rights to
                        the platform software and generated analytics frameworks.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <p className="text-xs text-gray-500">
                    Last updated: October 22, 2025<br />
                    By using TANAW, you agree to these terms and policies.
                  </p>
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <button
                  onClick={() => setShowPrivacyModal(false)}
                  className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition font-medium"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* About TANAW Modal */}
      {showAboutModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-[60] p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
                  <span>🏷️</span>
                  <span>About TANAW</span>
                </h2>
                <button
                  onClick={() => setShowAboutModal(false)}
                  className="text-gray-400 hover:text-gray-600 transition"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-6">
                {/* Logo and Tagline */}
                <div className="text-center pb-4 border-b border-gray-200">
                  <div className="w-20 h-20 bg-gradient-to-br from-purple-600 to-blue-600 rounded-2xl flex items-center justify-center text-white text-3xl font-bold mx-auto mb-3 shadow-lg">
                    T
                  </div>
                  <h3 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-2">
                    TANAW
                  </h3>
                  <p className="text-sm text-gray-600 italic">
                    "See Beyond the Numbers"
                  </p>
                </div>

                {/* Mission */}
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">Our Mission</h4>
                  <p className="text-sm text-gray-600">
                    TANAW empowers small and medium businesses to make data-driven decisions
                    through intuitive analytics and AI-powered insights. We believe that
                    powerful business intelligence should be accessible to everyone, regardless
                    of technical expertise.
                  </p>
                </div>

                {/* Features */}
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-3">Key Features</h4>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-purple-50 p-3 rounded-lg">
                      <div className="text-2xl mb-1">📊</div>
                      <div className="text-xs font-semibold text-gray-800">Smart Analytics</div>
                    </div>
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <div className="text-2xl mb-1">🤖</div>
                      <div className="text-xs font-semibold text-gray-800">AI-Powered</div>
                    </div>
                    <div className="bg-green-50 p-3 rounded-lg">
                      <div className="text-2xl mb-1">⚡</div>
                      <div className="text-xs font-semibold text-gray-800">Fast Processing</div>
                    </div>
                    <div className="bg-orange-50 p-3 rounded-lg">
                      <div className="text-2xl mb-1">🔒</div>
                      <div className="text-xs font-semibold text-gray-800">Secure & Private</div>
                    </div>
                  </div>
                </div>

                {/* Development Team */}
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">Development Team</h4>
                  <div className="bg-gradient-to-br from-purple-50 to-blue-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-700 mb-2">
                      TANAW is developed by a dedicated team of student developers
                      from Batangas State University as part of their capstone project.
                    </p>
                    <p className="text-xs text-gray-600">
                      <strong>Contributors:</strong> Development Team, Faculty Advisors,
                      Industry Partners
                    </p>
                  </div>
                </div>

                {/* Version Info */}
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500 text-xs mb-1">Version</p>
                      <p className="font-semibold text-gray-800">1.0.0</p>
                    </div>
                    <div>
                      <p className="text-gray-500 text-xs mb-1">Last Updated</p>
                      <p className="font-semibold text-gray-800">October 22, 2025</p>
                    </div>
                    <div>
                      <p className="text-gray-500 text-xs mb-1">Platform</p>
                      <p className="font-semibold text-gray-800">Web Application</p>
                    </div>
                    <div>
                      <p className="text-gray-500 text-xs mb-1">Status</p>
                      <p className="font-semibold text-green-600">✓ Active</p>
                    </div>
                  </div>
                </div>

                {/* Contact */}
                <div className="text-center pt-4 border-t border-gray-200">
                  <p className="text-sm text-gray-600 mb-2">
                    Questions or feedback? Reach out to us!
                  </p>
                  <div className="flex justify-center space-x-4 text-sm">
                    <a href="mailto:support@tanaw.com" className="text-purple-600 hover:text-purple-700">
                      📧 Email
                    </a>
                    <span className="text-gray-300">|</span>
                    <a href="#" className="text-purple-600 hover:text-purple-700">
                      🌐 Website
                    </a>
                  </div>
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <button
                  onClick={() => setShowAboutModal(false)}
                  className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition font-medium"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default UserProfileDropdown;

