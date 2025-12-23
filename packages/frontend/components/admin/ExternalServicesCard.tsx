import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Icons } from "@/components/icons";
import { cn } from "@/lib/utils";

const statusColorMap = {
  healthy: "text-green-500",
  degraded: "text-yellow-500",
  down: "text-red-500",
};

const statusIconMap = {
  healthy: <Icons.checkCircle className="h-4 w-4" />,
  degraded: <Icons.alertTriangle className="h-4 w-4" />,
  down: <Icons.xCircle className="h-4 w-4" />,
};

function ServiceStatus({ name, status }) {
  const color = statusColorMap[status] || "text-gray-500";
  const icon = statusIconMap[status] || <Icons.helpCircle className="h-4 w-4" />;

  return (
    <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
      <span className="font-semibold">{name}</span>
      <div className={cn("flex items-center gap-2 font-semibold", color)}>
        {icon}
        <span>{status.charAt(0).toUpperCase() + status.slice(1)}</span>
      </div>
    </div>
  );
}

export function ExternalServicesCard({ metrics }) {
  if (!metrics) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>External Service Status</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <ServiceStatus name="Daily.co (Voice)" status={metrics.daily_co} />
        <ServiceStatus name="LiveKit (Video)" status={metrics.livekit} />
        <ServiceStatus name="Beyond Presence (Avatar)" status={metrics.beyond_presence} />
      </CardContent>
    </Card>
  );
}