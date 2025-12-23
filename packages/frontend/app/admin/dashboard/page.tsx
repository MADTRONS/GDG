"use client";

import { useEffect, useState } from "react";
import { SystemHealthCard } from "@/components/admin/SystemHealthCard";
import { SessionMetricsCard } from "@/components/admin/SessionMetricsCard";
import { ExternalServicesCard } from "@/components/admin/ExternalServicesCard";
import { useAdminMetrics } from "@/lib/hooks/useAdminMetrics";
import { Icons } from "@/components/icons";

export default function AdminDashboardPage() {
  const { data, isLoading, error } = useAdminMetrics({ refreshInterval: 30000 });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Icons.spinner className="h-12 w-12 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen text-red-500">
        <p>Error loading dashboard: {error.message}</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 sm:p-6 lg:p-8">
      <h1 className="text-3xl font-bold tracking-tight mb-6">System Monitoring Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <SystemHealthCard metrics={data?.current} />
        </div>
        <SessionMetricsCard metrics={data?.sessions} />
        <div className="lg:col-span-3">
          <ExternalServicesCard metrics={data?.external} />
        </div>
      </div>
    </div>
  );
}
