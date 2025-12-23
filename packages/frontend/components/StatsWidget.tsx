'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import { Clock, TrendingUp, Award, Calendar } from 'lucide-react';

interface SessionStats {
  total_sessions: number;
  total_hours: number;
  top_category: string | null;
  top_category_icon: string | null;
  last_session_date: string | null;
}

export function StatsWidget() {
  const [stats, setStats] = useState<SessionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
      const response = await fetch(`${API_BASE_URL}/v1/sessions/stats`, {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to fetch stats');
      }

      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Error fetching stats:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const formatLastSessionDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Your Session Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !stats) {
    // Don't show error for new users with no sessions
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Your Session Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            You haven&apos;t started any sessions yet. Connect with a counselor to begin your journey.
          </p>
          <Button variant="outline" disabled>
            View All Sessions
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (stats.total_sessions === 0) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Your Session Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            You haven&apos;t started any sessions yet. Connect with a counselor to begin your journey.
          </p>
          <Button variant="outline" disabled>
            View All Sessions
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Your Session Summary</CardTitle>
        <Button
          variant="outline"
          size="sm"
          onClick={() => router.push('/session-history')}
        >
          View All Sessions
        </Button>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Total Sessions */}
          <div className="flex items-start space-x-3 p-4 rounded-lg border bg-card">
            <div className="p-2 rounded-md bg-primary/10">
              <TrendingUp className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.total_sessions}</p>
              <p className="text-sm text-muted-foreground">Total Sessions</p>
            </div>
          </div>

          {/* Total Hours */}
          <div className="flex items-start space-x-3 p-4 rounded-lg border bg-card">
            <div className="p-2 rounded-md bg-primary/10">
              <Clock className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.total_hours}</p>
              <p className="text-sm text-muted-foreground">Total Hours</p>
            </div>
          </div>

          {/* Top Category */}
          <div className="flex items-start space-x-3 p-4 rounded-lg border bg-card">
            <div className="p-2 rounded-md bg-primary/10">
              {stats.top_category_icon ? (
                <span className="text-xl">{stats.top_category_icon}</span>
              ) : (
                <Award className="h-5 w-5 text-primary" />
              )}
            </div>
            <div>
              <p className="text-sm font-semibold truncate" title={stats.top_category || 'N/A'}>
                {stats.top_category || 'N/A'}
              </p>
              <p className="text-sm text-muted-foreground">Top Category</p>
            </div>
          </div>

          {/* Last Session */}
          <div className="flex items-start space-x-3 p-4 rounded-lg border bg-card">
            <div className="p-2 rounded-md bg-primary/10">
              <Calendar className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-sm font-semibold">
                {formatLastSessionDate(stats.last_session_date)}
              </p>
              <p className="text-sm text-muted-foreground">Last Session</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}