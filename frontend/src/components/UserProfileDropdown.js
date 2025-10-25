// UserProfileDropdown.js
import React, { useState, useEffect, useRef } from "react";
import ReactDOM from "react-dom";
import { Link } from "react-router-dom";
import api from "../api";
import toast from "react-hot-toast";

const UserProfileDropdown = ({ user, onUserUpdate, onLogout }) => {
  // Dropdown state
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);


  // Modal states
  const [showEditProfileModal, setShowEditProfileModal] = useState(false);
  const [showChangePasswordModal, setShowChangePasswordModal] = useState(false);

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
              <Link
                to="/docs"
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => setIsDropdownOpen(false)}
                className="w-full text-left px-3 py-2 text-xs text-gray-700 hover:bg-gray-50 rounded-lg transition flex items-center space-x-2"
              >
                <span>📚</span>
                <span>Help & Documentation</span>
              </Link>
              <Link
                to="/support"
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => setIsDropdownOpen(false)}
                className="w-full text-left px-3 py-2 text-xs text-gray-700 hover:bg-gray-50 rounded-lg transition flex items-center space-x-2"
              >
                <span>💬</span>
                <span>Support Center</span>
              </Link>
              <Link
                to="/privacy"
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => setIsDropdownOpen(false)}
                className="w-full text-left px-3 py-2 text-xs text-gray-700 hover:bg-gray-50 rounded-lg transition flex items-center space-x-2"
              >
                <span>🧭</span>
                <span>Privacy Policy</span>
              </Link>
              <Link
                to="/terms"
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => setIsDropdownOpen(false)}
                className="w-full text-left px-3 py-2 text-xs text-gray-700 hover:bg-gray-50 rounded-lg transition flex items-center space-x-2"
              >
                <span>📜</span>
                <span>Terms of Service</span>
              </Link>
              <Link
                to="/about"
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => setIsDropdownOpen(false)}
                className="w-full text-left px-3 py-2 text-xs text-gray-700 hover:bg-gray-50 rounded-lg transition flex items-center space-x-2"
              >
                <span>🏷️</span>
                <span>About TANAW</span>
              </Link>
            </div>
          </div>
        )}
      </div>

      {/* Edit Profile Modal - Using React Portal */}
      {showEditProfileModal && ReactDOM.createPortal(
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-2xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-center mb-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </div>
              </div>
              
              <h2 className="text-xl font-bold text-gray-900 mb-3 text-center">
                Edit Profile
              </h2>

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

                <div className="flex flex-col sm:flex-row gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowEditProfileModal(false)}
                    className="flex-1 bg-gray-600 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-gray-700 transition"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isUpdatingProfile}
                    className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isUpdatingProfile ? "Saving..." : "Save Changes"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>,
        document.body
      )}

      {/* Change Password Modal - Using React Portal */}
      {showChangePasswordModal && ReactDOM.createPortal(
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-2xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-center mb-4">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                  </svg>
                </div>
              </div>
              
              <h2 className="text-xl font-bold text-gray-900 mb-3 text-center">
                Change Password
              </h2>

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

                <div className="flex flex-col sm:flex-row gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowChangePasswordModal(false)}
                    className="flex-1 bg-gray-600 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-gray-700 transition"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isChangingPassword}
                    className="flex-1 bg-purple-600 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isChangingPassword ? "Changing..." : "Change Password"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>,
        document.body
      )}

    </>
  );
};

export default UserProfileDropdown;

