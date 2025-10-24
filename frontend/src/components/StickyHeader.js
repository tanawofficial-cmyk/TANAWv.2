// StickyHeader.js
import React, { useState, useEffect } from "react";
import TANAWLogo from "../assets/TANAW-LOGO.png";
import UserProfileDropdown from "./UserProfileDropdown";

const StickyHeader = ({ user, onUserUpdate, onLogout, onSearch, onDateFilter }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [showSearchInput, setShowSearchInput] = useState(false);
  const [dateFilter, setDateFilter] = useState("");
  const [showDateFilter, setShowDateFilter] = useState(false);

  // Handle real-time search filtering
  const handleSearchChange = (value) => {
    setSearchTerm(value);
    if (onSearch) {
      onSearch(value);
    }
  };

  // Handle search form submission
  const handleSearch = (e) => {
    e.preventDefault();
    // Search is already handled by real-time filtering
  };

  // Handle date filter change
  const handleDateFilterChange = (value) => {
    setDateFilter(value);
    if (onDateFilter) {
      onDateFilter(value);
    }
  };

  // Close search input and date filter when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showSearchInput && !event.target.closest('.search-container')) {
        setShowSearchInput(false);
        setSearchTerm("");
        handleSearchChange(""); // Clear the search filter
      }
      if (showDateFilter && !event.target.closest('.date-filter-container')) {
        setShowDateFilter(false);
      }
    };

    if (showSearchInput || showDateFilter) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showSearchInput, showDateFilter]);

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-lg border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14 sm:h-16">
          
          {/* Logo Section - Responsive */}
          <div className="flex items-center space-x-2 sm:space-x-3 group cursor-pointer">
            <div className="relative">
              {/* Gradient background with blur effect */}
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full blur-sm opacity-70 group-hover:opacity-90 transition-opacity"></div>
              <div className="relative w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 transform group-hover:scale-105 overflow-hidden">
                {/* Original TANAW Logo - Round */}
                <img 
                  src={TANAWLogo} 
                  alt="TANAW Logo" 
                  className="w-7 h-7 sm:w-8 sm:h-8 md:w-10 md:h-10 object-contain rounded-full"
                />
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-base sm:text-lg md:text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                TANAW
              </span>
              <span className="text-[10px] sm:text-xs text-gray-500 -mt-1 hidden sm:block">Analytics Platform</span>
            </div>
          </div>

          {/* Search and Filter Section - Responsive */}
          <div className="flex-1 max-w-2xl mx-2 sm:mx-4 md:mx-8">
            <div className="flex items-center space-x-2 sm:space-x-4">
              {/* Search Container */}
              <div className="relative search-container flex-1">
              {!showSearchInput ? (
                <button
                  onClick={() => setShowSearchInput(true)}
                  className="w-full flex items-center justify-center sm:justify-start space-x-2 sm:space-x-3 px-2 sm:px-4 py-1.5 sm:py-2 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-lg transition-colors text-gray-500"
                >
                  <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <span className="text-xs sm:text-sm hidden sm:inline">Search datasets...</span>
                </button>
              ) : (
                <form onSubmit={handleSearch} className="relative">
                  <div className="flex items-center space-x-2">
                    <div className="relative flex-1">
                      <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                      <input
                        type="text"
                        placeholder="Search datasets..."
                        value={searchTerm}
                        onChange={(e) => handleSearchChange(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                        autoFocus
                      />
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        setSearchTerm("");
                        handleSearchChange(""); // Clear the search filter
                        setShowSearchInput(false);
                      }}
                      className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  {searchTerm && (
                    <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-2">
                      <div className="text-xs text-gray-500">
                        Press Enter to search for "{searchTerm}"
                      </div>
                    </div>
                  )}
                </form>
              )}
              </div>

              {/* Date Filter - Responsive */}
              <div className="relative date-filter-container">
                <button
                  onClick={() => setShowDateFilter(!showDateFilter)}
                  className="flex items-center justify-center sm:justify-start space-x-1 sm:space-x-2 px-2 sm:px-4 py-1.5 sm:py-2 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-lg transition-colors text-gray-500"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span className="text-xs sm:text-sm hidden sm:inline">Filter by date</span>
                  {dateFilter && (
                    <span className="text-[10px] sm:text-xs bg-blue-100 text-blue-600 px-1.5 sm:px-2 py-0.5 sm:py-1 rounded-full">
                      {new Date(dateFilter).toLocaleDateString()}
                    </span>
                  )}
                </button>

                {showDateFilter && (
                  <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                    <div className="p-4">
                      <div className="flex items-center space-x-2 mb-3">
                        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <span className="text-sm font-medium text-gray-700">Filter by Upload Date</span>
                      </div>
                      
                      <div className="space-y-3">
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">From Date</label>
                          <input
                            type="date"
                            value={dateFilter}
                            onChange={(e) => handleDateFilterChange(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                          />
                        </div>
                        
                        <div className="flex justify-between items-center">
                          <button
                            onClick={() => {
                              setDateFilter("");
                              handleDateFilterChange("");
                              setShowDateFilter(false);
                            }}
                            className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
                          >
                            Clear Filter
                          </button>
                          <button
                            onClick={() => setShowDateFilter(false)}
                            className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors"
                          >
                            Apply
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* User Profile Section - Responsive */}
          <div className="flex items-center space-x-2 sm:space-x-4">
            {/* User Profile Dropdown */}
            <UserProfileDropdown 
              user={user} 
              onUserUpdate={onUserUpdate}
              onLogout={onLogout}
            />
          </div>
        </div>
      </div>
    </header>
  );
};

export default StickyHeader;
