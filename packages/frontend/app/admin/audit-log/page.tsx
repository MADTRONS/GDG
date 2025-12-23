"use client";

import { useEffect, useState } from "react";
import useSWR from "swr";
import { Download } from "lucide-react";

interface AuditLogEntry {
  id: string;
  admin_email: string;
  action: string;
  resource_type: string;
  details: Record<string, any>;
  ip_address: string;
  timestamp: string;
}

interface AuditLogResponse {
  logs: AuditLogEntry[];
  total_count: number;
  page: number;
  limit: number;
  total_pages: number;
}

const fetcher = async (url: string) => {
  const response = await fetch(url, { credentials: "include" });
  if (!response.ok) {
    throw new Error("Failed to fetch audit log");
  }
  return response.json();
};

export default function AuditLogPage() {
  const [page, setPage] = useState(1);
  const [limit] = useState(50);
  const [adminUserId, setAdminUserId] = useState("");
  const [action, setAction] = useState("");
  const [resourceType, setResourceType] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [activeFilters, setActiveFilters] = useState<string>("");

  // Build query string
  const buildQueryString = () => {
    const params = new URLSearchParams({ page: page.toString(), limit: limit.toString() });
    if (activeFilters) {
      return `?${activeFilters}`;
    }
    return `?${params.toString()}`;
  };

  const { data, error, isLoading } = useSWR<AuditLogResponse>(
    `${process.env.NEXT_PUBLIC_API_URL}/api/admin/audit-log${buildQueryString()}`,
    fetcher,
    { refreshInterval: 30000 }
  );

  const applyFilters = () => {
    const params = new URLSearchParams({ page: "1", limit: limit.toString() });
    if (adminUserId) params.append("admin_user_id", adminUserId);
    if (action) params.append("action", action);
    if (resourceType) params.append("resource_type", resourceType);
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    setActiveFilters(params.toString());
    setPage(1);
  };

  const resetFilters = () => {
    setAdminUserId("");
    setAction("");
    setResourceType("");
    setStartDate("");
    setEndDate("");
    setActiveFilters("");
    setPage(1);
  };

  const exportToCSV = () => {
    if (!data?.logs || data.logs.length === 0) return;

    const headers = ["Timestamp", "Admin Email", "Action", "Resource Type", "Details", "IP Address"];
    const csvRows = [
      headers.join(","),
      ...data.logs.map((log) =>
        [
          new Date(log.timestamp).toLocaleString(),
          log.admin_email,
          log.action,
          log.resource_type,
          JSON.stringify(log.details).replace(/,/g, ";"),
          log.ip_address,
        ].join(",")
      ),
    ];

    const blob = new Blob([csvRows.join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `audit-log-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getActionBadgeClass = (action: string) => {
    switch (action) {
      case "CREATE":
        return "bg-green-100 text-green-800";
      case "UPDATE":
        return "bg-blue-100 text-blue-800";
      case "DELETE":
        return "bg-red-100 text-red-800";
      case "LOGIN":
        return "bg-purple-100 text-purple-800";
      case "LOGOUT":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const isSensitiveAction = (action: string, resourceType: string) => {
    return (
      action === "CREATE" && resourceType === "counselor_category" ||
      action === "DELETE" && resourceType === "counselor_category" ||
      action === "CREATE" && resourceType === "admin_user"
    );
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="mx-auto max-w-7xl">
          <div className="rounded-lg bg-red-50 p-4">
            <p className="text-red-800">Error loading audit log: {error.message}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">Audit Log</h1>
          <button
            onClick={exportToCSV}
            disabled={!data?.logs || data.logs.length === 0}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:bg-gray-400"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </button>
        </div>

        {/* Filters */}
        <div className="mb-6 rounded-lg bg-white p-6 shadow">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Filters</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Admin User ID</label>
              <input
                type="text"
                value={adminUserId}
                onChange={(e) => setAdminUserId(e.target.value)}
                placeholder="UUID"
                className="w-full rounded-lg border px-3 py-2 focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Action</label>
              <select
                value={action}
                onChange={(e) => setAction(e.target.value)}
                className="w-full rounded-lg border px-3 py-2 focus:border-blue-500 focus:outline-none"
              >
                <option value="">All Actions</option>
                <option value="CREATE">CREATE</option>
                <option value="UPDATE">UPDATE</option>
                <option value="DELETE">DELETE</option>
                <option value="LOGIN">LOGIN</option>
                <option value="LOGOUT">LOGOUT</option>
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Resource Type</label>
              <input
                type="text"
                value={resourceType}
                onChange={(e) => setResourceType(e.target.value)}
                placeholder="e.g., counselor_category"
                className="w-full rounded-lg border px-3 py-2 focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full rounded-lg border px-3 py-2 focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">End Date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full rounded-lg border px-3 py-2 focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>
          <div className="mt-4 flex gap-2">
            <button
              onClick={applyFilters}
              className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              Apply Filters
            </button>
            <button
              onClick={resetFilters}
              className="rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
            >
              Reset
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="rounded-lg bg-white shadow">
          {isLoading ? (
            <div className="p-8 text-center">
              <p className="text-gray-500">Loading audit log...</p>
            </div>
          ) : data?.logs && data.logs.length > 0 ? (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                        Timestamp
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                        Admin Email
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                        Action
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                        Resource Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                        Details
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                        IP Address
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 bg-white">
                    {data.logs.map((log) => (
                      <tr
                        key={log.id}
                        className={isSensitiveAction(log.action, log.resource_type) ? "bg-yellow-50" : ""}
                      >
                        <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
                          {new Date(log.timestamp).toLocaleString()}
                        </td>
                        <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
                          {log.admin_email}
                        </td>
                        <td className="whitespace-nowrap px-6 py-4 text-sm">
                          <span
                            className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${getActionBadgeClass(log.action)}`}
                          >
                            {log.action}
                          </span>
                        </td>
                        <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
                          {log.resource_type}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">
                          <pre className="max-w-xs overflow-auto text-xs">
                            {JSON.stringify(log.details, null, 2)}
                          </pre>
                        </td>
                        <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                          {log.ip_address}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="flex items-center justify-between border-t border-gray-200 bg-white px-6 py-4">
                <div className="flex flex-1 justify-between sm:hidden">
                  <button
                    onClick={() => setPage(Math.max(1, page - 1))}
                    disabled={page === 1}
                    className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:bg-gray-100"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(Math.min(data.total_pages, page + 1))}
                    disabled={page === data.total_pages}
                    className="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:bg-gray-100"
                  >
                    Next
                  </button>
                </div>
                <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      Showing <span className="font-medium">{(page - 1) * limit + 1}</span> to{" "}
                      <span className="font-medium">
                        {Math.min(page * limit, data.total_count)}
                      </span>{" "}
                      of <span className="font-medium">{data.total_count}</span> results
                    </p>
                  </div>
                  <div>
                    <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm">
                      <button
                        onClick={() => setPage(Math.max(1, page - 1))}
                        disabled={page === 1}
                        className="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:bg-gray-100"
                      >
                        Previous
                      </button>
                      <span className="relative inline-flex items-center px-4 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300">
                        {page} / {data.total_pages}
                      </span>
                      <button
                        onClick={() => setPage(Math.min(data.total_pages, page + 1))}
                        disabled={page === data.total_pages}
                        className="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:bg-gray-100"
                      >
                        Next
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="p-8 text-center">
              <p className="text-gray-500">No audit logs found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}