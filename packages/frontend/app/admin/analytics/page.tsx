"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { fetchSessionAnalytics, SessionAnalytics } from "@/lib/api";
import { Icons } from "@/components/icons";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884d8", "#82ca9d"];

type DatePreset = "7days" | "30days" | "90days" | "custom";

export default function AdminAnalyticsPage() {
  const [data, setData] = useState<SessionAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [preset, setPreset] = useState<DatePreset>("30days");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let start = startDate;
      let end = endDate;
      
      if (preset !== "custom") {
        const now = new Date();
        end = now.toISOString().split("T")[0];
        
        const daysAgo = preset === "7days" ? 7 : preset === "30days" ? 30 : 90;
        const startDt = new Date(now);
        startDt.setDate(startDt.getDate() - daysAgo);
        start = startDt.toISOString().split("T")[0];
      }
      
      if (!start || !end) {
        setError("Please select or enter valid dates");
        return;
      }
      
      const analytics = await fetchSessionAnalytics(start, end);
      setData(analytics);
    } catch (err: any) {
      setError(err.message || "Failed to fetch analytics");
    } finally {
      setLoading(false);
    }
  };

  const exportCSV = () => {
    if (!data) return;
    
    const rows = [
      ["Metric", "Value"],
      ["Total Sessions", data.total_sessions.toString()],
      ["Average Duration (minutes)", (data.avg_duration / 60).toFixed(1)],
      [""],
      ["Sessions by Category"],
      ...Object.entries(data.sessions_by_category).map(([cat, count]) => [cat, count.toString()]),
      [""],
      ["Sessions by Mode"],
      ...Object.entries(data.sessions_by_mode).map(([mode, count]) => [mode, count.toString()]),
      [""],
      ["Average Duration by Category (minutes)"],
      ...Object.entries(data.avg_duration_by_category).map(([cat, dur]) => [
        cat,
        (dur / 60).toFixed(1),
      ]),
    ];
    
    const csvContent = rows.map(row => row.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `analytics_${startDate || "report"}_${endDate || "report"}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Prepare chart data
  const categoryChartData = data
    ? Object.entries(data.sessions_by_category).map(([name, value]) => ({ name, value }))
    : [];

  const modeChartData = data
    ? Object.entries(data.sessions_by_mode).map(([name, value]) => ({ name, value }))
    : [];

  const dailyTrendData = data
    ? Object.entries(data.daily_trend)
        .map(([date, count]) => ({ date, count }))
        .sort((a, b) => a.date.localeCompare(b.date))
    : [];

  const peakHoursData = data
    ? Object.entries(data.peak_usage_hours)
        .map(([hour, count]) => ({ hour: `${hour}:00`, count }))
        .sort((a, b) => parseInt(a.hour) - parseInt(b.hour))
    : [];

  const durationTableData = data
    ? Object.entries(data.avg_duration_by_category).map(([category, duration]) => ({
        category,
        duration: (duration / 60).toFixed(1),
      }))
    : [];

  return (
    <div className="container mx-auto p-4 sm:p-6 lg:p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Usage Analytics</h1>
        {data && (
          <Button onClick={exportCSV} variant="outline">
            <Icons.download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
        )}
      </div>

      {/* Date Range Selector */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Date Range</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <Label>Preset</Label>
              <Select
                value={preset}
                onValueChange={(value) => setPreset(value as DatePreset)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7days">Last 7 Days</SelectItem>
                  <SelectItem value="30days">Last 30 Days</SelectItem>
                  <SelectItem value="90days">Last 90 Days</SelectItem>
                  <SelectItem value="custom">Custom Range</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            {preset === "custom" && (
              <>
                <div>
                  <Label>Start Date</Label>
                  <Input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </div>
                <div>
                  <Label>End Date</Label>
                  <Input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>
              </>
            )}
            
            <div className="flex items-end">
              <Button onClick={fetchData} disabled={loading} className="w-full">
                {loading ? (
                  <>
                    <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  "Fetch Analytics"
                )}
              </Button>
            </div>
          </div>
          
          {error && (
            <div className="mt-4 p-3 bg-red-50 text-red-600 rounded-md">
              {error}
            </div>
          )}
        </CardContent>
      </Card>

      {data && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{data.total_sessions}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Avg Duration</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {(data.avg_duration / 60).toFixed(1)} min
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Categories</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {Object.keys(data.sessions_by_category).length}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Bar Chart - Sessions by Category */}
            <Card>
              <CardHeader>
                <CardTitle>Sessions by Category</CardTitle>
              </CardHeader>
              <CardContent className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={categoryChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#0088FE" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Pie Chart - Voice vs Video */}
            <Card>
              <CardHeader>
                <CardTitle>Voice vs Video Distribution</CardTitle>
              </CardHeader>
              <CardContent className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={modeChartData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      label
                    >
                      {modeChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Line Chart - Daily Trend */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Session Trend Over Time</CardTitle>
            </CardHeader>
            <CardContent className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={dailyTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="count" stroke="#8884d8" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Peak Usage Hours Heatmap (Bar Chart) */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Peak Usage Hours</CardTitle>
            </CardHeader>
            <CardContent className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={peakHoursData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Duration Table */}
          <Card>
            <CardHeader>
              <CardTitle>Average Duration by Category</CardTitle>
            </CardHeader>
            <CardContent>
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-4">Category</th>
                    <th className="text-right py-2 px-4">Avg Duration (min)</th>
                  </tr>
                </thead>
                <tbody>
                  {durationTableData
                    .sort((a, b) => parseFloat(b.duration) - parseFloat(a.duration))
                    .map((row) => (
                      <tr key={row.category} className="border-b">
                        <td className="py-2 px-4">{row.category}</td>
                        <td className="text-right py-2 px-4 font-semibold">{row.duration}</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}