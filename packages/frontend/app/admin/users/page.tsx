"use client";

import { useState } from "react";
import useSWR from "swr";
import { Plus, Edit, Trash2, Key } from "lucide-react";

interface AdminUser {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
}

const fetcher = async (url: string) => {
  const response = await fetch(url, { credentials: "include" });
  if (!response.ok) {
    throw new Error("Failed to fetch admin users");
  }
  return response.json();
};

export default function AdminUsersPage() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedAdmin, setSelectedAdmin] = useState<AdminUser | null>(null);
  const [tempPassword, setTempPassword] = useState<string | null>(null);

  const { data: admins, error, isLoading, mutate } = useSWR<AdminUser[]>(
    `${process.env.NEXT_PUBLIC_API_URL}/api/admin/users`,
    fetcher
  );

  const getRoleBadgeClass = (role: string) => {
    switch (role) {
      case "SUPER_ADMIN":
        return "bg-red-100 text-red-800";
      case "CONTENT_MANAGER":
        return "bg-blue-100 text-blue-800";
      case "SYSTEM_MONITOR":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const handleCreateAdmin = async (email: string, role: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/users`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, role }),
      });

      if (!response.ok) {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
        return;
      }

      const data = await response.json();
      setTempPassword(data.temporary_password);
      mutate();
    } catch (err) {
      alert("Failed to create admin user");
    }
  };

  const handleUpdateAdmin = async (adminId: string, updates: { role?: string; is_active?: boolean }) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/users/${adminId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
        return;
      }

      mutate();
      setShowEditModal(false);
    } catch (err) {
      alert("Failed to update admin user");
    }
  };

  const handleDeactivate = async (adminId: string) => {
    if (!confirm("Are you sure you want to deactivate this admin user?")) {
      return;
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/users/${adminId}`, {
        method: "DELETE",
        credentials: "include",
      });

      if (!response.ok) {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
        return;
      }

      mutate();
    } catch (err) {
      alert("Failed to deactivate admin user");
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="mx-auto max-w-7xl">
          <div className="rounded-lg bg-red-50 p-4">
            <p className="text-red-800">Error loading admin users: {error.message}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">Admin Users</h1>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          >
            <Plus className="h-4 w-4" />
            Create Admin
          </button>
        </div>

        {/* Admin Users Table */}
        <div className="rounded-lg bg-white shadow">
          {isLoading ? (
            <div className="p-8 text-center">
              <p className="text-gray-500">Loading admin users...</p>
            </div>
          ) : admins && admins.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Last Login
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {admins.map((admin) => (
                    <tr key={admin.id}>
                      <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-gray-900">
                        {admin.email}
                      </td>
                      <td className="whitespace-nowrap px-6 py-4 text-sm">
                        <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${getRoleBadgeClass(admin.role)}`}>
                          {admin.role}
                        </span>
                      </td>
                      <td className="whitespace-nowrap px-6 py-4 text-sm">
                        <span
                          className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                            admin.is_active
                              ? "bg-green-100 text-green-800"
                              : "bg-gray-100 text-gray-800"
                          }`}
                        >
                          {admin.is_active ? "Active" : "Inactive"}
                        </span>
                      </td>
                      <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                        {admin.last_login_at ? new Date(admin.last_login_at).toLocaleString() : "Never"}
                      </td>
                      <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                        <div className="flex gap-2">
                          <button
                            onClick={() => {
                              setSelectedAdmin(admin);
                              setShowEditModal(true);
                            }}
                            className="text-blue-600 hover:text-blue-800"
                            title="Edit"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDeactivate(admin.id)}
                            className="text-red-600 hover:text-red-800"
                            title="Deactivate"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center">
              <p className="text-gray-500">No admin users found</p>
            </div>
          )}
        </div>

        {/* Create Admin Modal */}
        {showCreateModal && (
          <CreateAdminModal
            onClose={() => {
              setShowCreateModal(false);
              setTempPassword(null);
            }}
            onSubmit={handleCreateAdmin}
            tempPassword={tempPassword}
          />
        )}

        {/* Edit Admin Modal */}
        {showEditModal && selectedAdmin && (
          <EditAdminModal
            admin={selectedAdmin}
            onClose={() => {
              setShowEditModal(false);
              setSelectedAdmin(null);
            }}
            onSubmit={(updates) => handleUpdateAdmin(selectedAdmin.id, updates)}
          />
        )}
      </div>
    </div>
  );
}

// Create Admin Modal Component
function CreateAdminModal({
  onClose,
  onSubmit,
  tempPassword,
}: {
  onClose: () => void;
  onSubmit: (email: string, role: string) => void;
  tempPassword: string | null;
}) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("CONTENT_MANAGER");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(email, role);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="w-full max-w-md rounded-lg bg-white p-6">
        <h2 className="mb-4 text-xl font-bold text-gray-900">Create Admin User</h2>
        
        {tempPassword ? (
          <div className="mb-4 rounded-lg bg-green-50 p-4">
            <p className="mb-2 text-sm font-medium text-green-800">Admin created successfully!</p>
            <p className="mb-2 text-sm text-green-700">Temporary password:</p>
            <div className="rounded bg-white p-2">
              <code className="text-sm font-mono text-gray-900">{tempPassword}</code>
            </div>
            <p className="mt-2 text-xs text-green-600">
              Please save this password securely. It will not be shown again.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="mb-1 block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full rounded-lg border px-3 py-2 focus:border-blue-500 focus:outline-none"
                placeholder="admin@example.com"
              />
            </div>
            <div className="mb-4">
              <label className="mb-1 block text-sm font-medium text-gray-700">Role</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full rounded-lg border px-3 py-2 focus:border-blue-500 focus:outline-none"
              >
                <option value="SUPER_ADMIN">Super Admin</option>
                <option value="CONTENT_MANAGER">Content Manager</option>
                <option value="SYSTEM_MONITOR">System Monitor</option>
              </select>
            </div>
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
              >
                {tempPassword ? "Close" : "Cancel"}
              </button>
              {!tempPassword && (
                <button
                  type="submit"
                  className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
                >
                  Create
                </button>
              )}
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

// Edit Admin Modal Component
function EditAdminModal({
  admin,
  onClose,
  onSubmit,
}: {
  admin: AdminUser;
  onClose: () => void;
  onSubmit: (updates: { role?: string; is_active?: boolean }) => void;
}) {
  const [role, setRole] = useState(admin.role);
  const [isActive, setIsActive] = useState(admin.is_active);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const updates: { role?: string; is_active?: boolean } = {};
    
    if (role !== admin.role) {
      updates.role = role;
    }
    if (isActive !== admin.is_active) {
      updates.is_active = isActive;
    }
    
    onSubmit(updates);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="w-full max-w-md rounded-lg bg-white p-6">
        <h2 className="mb-4 text-xl font-bold text-gray-900">Edit Admin User</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="mb-1 block text-sm font-medium text-gray-700">Email</label>
            <input
              type="text"
              value={admin.email}
              disabled
              className="w-full rounded-lg border bg-gray-100 px-3 py-2 text-gray-500"
            />
          </div>
          <div className="mb-4">
            <label className="mb-1 block text-sm font-medium text-gray-700">Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full rounded-lg border px-3 py-2 focus:border-blue-500 focus:outline-none"
            >
              <option value="SUPER_ADMIN">Super Admin</option>
              <option value="CONTENT_MANAGER">Content Manager</option>
              <option value="SYSTEM_MONITOR">System Monitor</option>
            </select>
          </div>
          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={isActive}
                onChange={(e) => setIsActive(e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm font-medium text-gray-700">Active</span>
            </label>
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}