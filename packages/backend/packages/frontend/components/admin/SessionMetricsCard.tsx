import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

export function SessionMetricsCard({ metrics }) {
  if (!metrics) return null;

  const categoryData = Object.entries(metrics.sessions_by_category).map(([name, value]) => ({ name, value }));
  const qualityData = Object.entries(metrics.connection_quality_distribution).map(([name, value]) => ({ name, value }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Session Metrics (30 days)</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-6">
          <h3 className="text-lg font-semibold">Total Sessions: {metrics.total_sessions}</h3>
        </div>
        <div className="h-64">
          <h4 className="text-center font-semibold mb-2">Sessions by Category</h4>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={categoryData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={60} fill="#8884d8" label>
                {categoryData.map((entry, index) => (
                  <Cell key={cell-} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="h-64 mt-8">
          <h4 className="text-center font-semibold mb-2">Connection Quality</h4>
           <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={qualityData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={60} fill="#82ca9d" label>
                 {qualityData.map((entry, index) => (
                  <Cell key={cell-} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}