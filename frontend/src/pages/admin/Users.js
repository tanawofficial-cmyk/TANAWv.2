import React, { useEffect, useState } from "react";
import axios from "axios";
import { Loader2, Trash2, UserCheck, UserX } from "lucide-react";

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch all users
  const fetchUsers = async () => {
    try {
      const res = await axios.get("/api/admin/users");
      setUsers(res.data.data || []);
    } catch (error) {
      console.error("Error fetching users:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  // Handle status update (Activate/Suspend)
  const handleStatusChange = async (id, newStatus) => {
    try {
      await axios.patch(`/api/admin/users/${id}/status`, { status: newStatus });
      fetchUsers(); // Refresh list
    } catch (err) {
      console.error("Error updating user status:", err);
    }
  };

  // Handle delete user
  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;
    try {
      await axios.delete(`/api/admin/users/${id}`);
      fetchUsers(); // Refresh list
    } catch (err) {
      console.error("Error deleting user:", err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64 text-gray-500">
        <Loader2 className="animate-spin mr-2" /> Loading users...
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Active Users</h1>
        <p className="text-gray-600 mt-1">
          Manage and monitor registered users in the TANAW platform.
        </p>
      </div>

      <div className="overflow-x-auto bg-white shadow rounded-xl border border-gray-100">
        <table className="w-full border-collapse">
          <thead className="bg-gray-100 text-gray-600 text-sm">
            <tr>
              <th className="py-3 px-4 text-left">Name</th>
              <th className="py-3 px-4 text-left">Email</th>
              <th className="py-3 px-4 text-center">Status</th>
              <th className="py-3 px-4 text-center">Registered</th>
              <th className="py-3 px-4 text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.length > 0 ? (
              users.map((user) => (
                <tr
                  key={user._id}
                  className="border-t border-gray-100 hover:bg-gray-50"
                >
                  <td className="py-3 px-4">{user.name}</td>
                  <td className="py-3 px-4">{user.email}</td>
                  <td className="py-3 px-4 text-center">
                    <span
                      className={`px-3 py-1 text-xs font-semibold rounded-full ${
                        user.status === "active"
                          ? "bg-green-100 text-green-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {user.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    {new Date(user.createdAt).toLocaleDateString()}
                  </td>
                  <td className="py-3 px-4 text-center space-x-2">
                    {user.status === "active" ? (
                      <button
                        onClick={() => handleStatusChange(user._id, "inactive")}
                        className="p-2 bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200"
                        title="Suspend User"
                      >
                        <UserX size={16} />
                      </button>
                    ) : (
                      <button
                        onClick={() => handleStatusChange(user._id, "active")}
                        className="p-2 bg-green-100 text-green-700 rounded hover:bg-green-200"
                        title="Activate User"
                      >
                        <UserCheck size={16} />
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(user._id)}
                      className="p-2 bg-red-100 text-red-700 rounded hover:bg-red-200"
                      title="Delete User"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan="5"
                  className="py-6 text-center text-gray-500 italic"
                >
                  No users found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
