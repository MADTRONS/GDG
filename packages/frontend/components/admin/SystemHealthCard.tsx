import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricCard } from "./MetricCard";
import { Icons } from "@/components/icons";
import { cn } from "@/lib/utils";

const healthColorMap = {
  healthy: "text-green-500",
  degraded: "text-yellow-500",
  critical: "text-red-500",
};

export function SystemHealthCard({ metrics }) {
  if (!metrics) return null;

  const healthClassName = healthColorMap[metrics.system_health] || "text-gray-500";

  return (
    <Card>
      <CardHeader>
        <CardTitle>System Health</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Overall Health"
          value={metrics.system_health.charAt(0).toUpperCase() + metrics.system_health.slice(1)}
          icon={<Icons.heartPulse className={cn("h-4 w-4 text-muted-foreground", healthClassName)} />}
          valueClassName={healthClassName}
        />
        <MetricCard
          title="Active Sessions"
          value={metrics.active_sessions_count}
          icon={<Icons.users className="h-4 w-4 text-muted-foreground" />}
        />
        <MetricCard
          title="Connection Quality"
          value={metrics.avg_connection_quality}
          icon={<Icons.wifi className="h-4 w-4 text-muted-foreground" />}
        />
        <MetricCard
          title="Error Rate (1h)"
          value={metrics.error_rate_last_hour}
          unit="%"
          icon={<Icons.shieldAlert className="h-4 w-4 text-muted-foreground" />}
        />
        <MetricCard
          title="API Latency (p95)"
          value={metrics.api_response_time_p95}
          unit="ms"
          icon={<Icons.timer className="h-4 w-4 text-muted-foreground" />}
        />
        <MetricCard
          title="DB Pool Active"
          value={metrics.db_pool_active}
          icon={<Icons.database className="h-4 w-4 text-muted-foreground" />}
        />
        <MetricCard
          title="DB Pool Size"
          value={metrics.db_pool_size}
          icon={<Icons.database className="h-4 w-4 text-muted-foreground" />}
        />
      </CardContent>
    </Card>
  );
}