// src/pages/admin/AdminDashboard.js
import React from "react";
import { Routes, Route, NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  BarChart3,
  FileText,
  MessageSquare,
  Settings,
  Search,
} from "lucide-react";

import Overview from "./Overview";
import UsersPage from "./Users";
import Analytics from "./Analytics";
import Files from "./Files";
import Feedback from "./Feedback";
import SettingsPage from "./Settings";

export default function AdminDashboard() {
  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 text-gray-800">
      {/* Sidebar */}
      <aside className="w-64 bg-gradient-to-b from-blue-600 via-blue-700 to-purple-700 text-white flex flex-col shadow-2xl">
        <div className="p-5 text-2xl font-extrabold tracking-wide border-b border-blue-500/30">
          <div className="flex items-center space-x-3 group cursor-pointer">
            <div className="relative">
              <div className="absolute inset-0 bg-white/20 rounded-full blur-sm opacity-70 group-hover:opacity-90 transition-opacity"></div>
              <div className="relative w-10 h-10 bg-white/20 rounded-full flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 transform group-hover:scale-105">
                <span className="text-lg font-bold">T</span>
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
                TANAW
              </span>
              <span className="text-xs text-blue-200 -mt-1">Admin Panel</span>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {[
            { to: "/admin", label: "Overview", icon: <LayoutDashboard size={18} /> },
            { to: "/admin/users", label: "Active Users", icon: <Users size={18} /> },
            { to: "/admin/analytics", label: "Analytics", icon: <BarChart3 size={18} /> },
            { to: "/admin/files", label: "Files", icon: <FileText size={18} /> },
            { to: "/admin/feedback", label: "User Feedback", icon: <MessageSquare size={18} /> },
            { to: "/admin/settings", label: "Settings", icon: <Settings size={18} /> },
          ].map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 transform hover:scale-105 ${
                  isActive
                    ? "bg-white/20 text-white shadow-lg backdrop-blur-sm border border-white/30"
                    : "text-blue-100 hover:bg-white/10 hover:text-white hover:shadow-md"
                }`
              }
            >
              {item.icon}
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        {/* Topbar */}
        <header className="flex items-center justify-between px-6 py-4 bg-white/80 backdrop-blur-lg border-b border-gray-200/50 shadow-sm">
          <div className="text-sm text-gray-600">
            Dashboard &gt;{" "}
            <span className="font-medium text-gray-800 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {/* dynamic breadcrumb (optional later) */}
            </span>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative group">
              <Search size={18} className="text-gray-500 cursor-pointer hover:text-blue-600 transition-colors" />
              <div className="absolute -top-2 -right-2 w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </div>
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full blur-sm opacity-30"></div>
              <img
                src="https://ui-avatars.com/api/?name=Admin&background=4f46e5&color=ffffff"
                alt="Admin Avatar"
                className="relative w-8 h-8 rounded-full ring-2 ring-blue-400/30 shadow-lg"
              />
            </div>
          </div>
        </header>

        {/* Page Routes */}
        <div className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="users" element={<UsersPage />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="files" element={<Files />} />
            <Route path="feedback" element={<Feedback />} />
            <Route path="settings" element={<SettingsPage />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}
