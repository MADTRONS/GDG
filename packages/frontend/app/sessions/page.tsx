'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { Phone, Video, Clock, ChevronRight, Calendar, Filter, Loader2 } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import type { Session, SessionsResponse } from '@/types/session';

export default function SessionHistoryPage() {
  return (
    <ProtectedRoute>
      <SessionHistoryContent />
    </ProtectedRoute>
  );
}

function SessionHistoryContent() {
  const router = useRouter();
  const { toast } = useToast();

  // State
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [modeFilter, setModeFilter] = useState<string>('all');
  const limit = 20;

  const categories = [
    { value: 'all', label: 'All Categories', icon: '📋' },
    { value: 'Health', label: 'Health Counselor', icon: '🏥' },
    { value: 'Career', label: 'Career Counselor', icon: '💼' },
    { value: 'Academic', label: 'Academic Counselor', icon: '📚' },
    { value: 'Financial', label: 'Financial Counselor', icon: '💰' },
    { value: 'Social', label: 'Social Counselor', icon: '🤝' },
    { value: 'Personal Development', label: 'Personal Development', icon: '🌱' },
  ];

  const modes = [
    { value: 'all', label: 'All Modes' },
    { value: 'voice', label: 'Voice Only' },
    { value: 'video', label: 'Video Call' },
  ];

  // Fetch sessions
  const fetchSessions = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: limit.toString(),
      });

      if (categoryFilter !== 'all') {
        params.append('category', categoryFilter);
      }
      if (modeFilter !== 'all') {
        params.append('mode', modeFilter);
      }

      const response = await fetch(`/api/v1/sessions?${params.toString()}`, {
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Failed to fetch sessions');
      }

      const data: SessionsResponse = await response.json();
      setSessions(data.sessions);
      setTotalCount(data.total_count);
    } catch (error) {
      console.error('Error fetching sessions:', error);
      toast({
        title: "Error Loading Sessions",
        description: "Unable to load your session history. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [currentPage, categoryFilter, modeFilter]);

  // Clear filters
  const clearFilters = () => {
    setCategoryFilter('all');
    setModeFilter('all');
    setCurrentPage(1);
  };

  // Format duration
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  // Loading state
  if (loading && sessions.length === 0) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" role="status" />
        </div>
      </div>
    );
  }

  // Empty state (no sessions at all)
  if (!loading && sessions.length === 0 && categoryFilter === 'all' && modeFilter === 'all') {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">My Counseling Sessions</h1>
        <Card className="text-center py-12">
          <CardContent className="pt-6">
            <Calendar className="h-16 w-16 mx-auto mb-4 text-gray-400" />
            <h2 className="text-xl font-semibold mb-2">No Sessions Yet</h2>
            <p className="text-gray-600 mb-6">
              You haven't started any counseling sessions yet. Visit your dashboard to get started!
            </p>
            <Button onClick={() => router.push('/dashboard')}>
              Go to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Calculate pagination
  const totalPages = Math.ceil(totalCount / limit);
  const showPagination = totalPages > 1;

  return (
    <div className="container mx-auto p-4 sm:p-6 max-w-5xl">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl sm:text-3xl font-bold mb-2">My Counseling Sessions</h1>
        <p className="text-sm sm:text-base text-gray-600">
          Review your past conversations and track your progress
        </p>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Category Filter */}
            <div>
              <label className="text-sm font-medium mb-2 block">Category</label>
              <div className="flex flex-wrap gap-2">
                {categories.map((cat) => (
                  <Button
                    key={cat.value}
                    variant={categoryFilter === cat.value ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => {
                      setCategoryFilter(cat.value);
                      setCurrentPage(1);
                    }}
                    className="text-xs sm:text-sm"
                  >
                    {cat.icon && <span className="mr-1">{cat.icon}</span>}
                    {cat.label}
                  </Button>
                ))}
              </div>
            </div>

            {/* Mode Filter */}
            <div>
              <label className="text-sm font-medium mb-2 block">Mode</label>
              <div className="flex flex-wrap gap-2">
                {modes.map((mode) => (
                  <Button
                    key={mode.value}
                    variant={modeFilter === mode.value ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => {
                      setModeFilter(mode.value);
                      setCurrentPage(1);
                    }}
                    className="text-xs sm:text-sm"
                  >
                    {mode.label}
                  </Button>
                ))}
              </div>
            </div>

            {/* Clear Filters */}
            {(categoryFilter !== 'all' || modeFilter !== 'all') && (
              <div>
                <Button
                  variant="ghost"
                  onClick={clearFilters}
                  className="w-full sm:w-auto"
                >
                  Clear Filters
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Session List */}
      {sessions.length === 0 ? (
        <Card className="text-center py-8">
          <CardContent className="pt-6">
            <p className="text-gray-600">No sessions found matching your filters.</p>
            <Button variant="link" onClick={clearFilters} className="mt-2">
              Clear filters to see all sessions
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {sessions.map((session) => (
            <Card
              key={session.session_id}
              className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => router.push(`/sessions/${session.session_id}`)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  router.push(`/sessions/${session.session_id}`);
                }
              }}
            >
              <CardContent className="p-4 sm:p-6">
                <div className="flex items-start justify-between gap-4">
                  {/* Left: Icon and Content */}
                  <div className="flex gap-3 sm:gap-4 flex-1 min-w-0">
                    <div className="text-3xl sm:text-4xl flex-shrink-0">
                      {session.counselor_icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <h3 className="font-semibold text-base sm:text-lg">
                          {session.counselor_category}
                        </h3>
                        {session.mode === 'video' ? (
                          <Video className="h-4 w-4 text-purple-600 flex-shrink-0" aria-label="Video call" />
                        ) : (
                          <Phone className="h-4 w-4 text-blue-600 flex-shrink-0" aria-label="Voice call" />
                        )}
                      </div>
                      <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4 text-xs sm:text-sm text-gray-600 mb-2">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-4 w-4 flex-shrink-0" />
                          <span className="truncate">
                            {format(new Date(session.started_at), 'MMM d, yyyy • h:mm a')}
                          </span>
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="h-4 w-4 flex-shrink-0" />
                          {formatDuration(session.duration_seconds)}
                        </span>
                      </div>
                      <p className="text-sm sm:text-base text-gray-700 line-clamp-2">
                        {session.transcript_preview}...
                      </p>
                    </div>
                  </div>

                  {/* Right: Arrow */}
                  <ChevronRight className="h-5 w-5 text-gray-400 flex-shrink-0 mt-1" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Pagination */}
      {showPagination && (
        <div className="mt-6 flex flex-col sm:flex-row justify-center items-center gap-4">
          <Button
            variant="outline"
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            size="sm"
          >
            Previous
          </Button>
          
          <div className="flex items-center gap-2 flex-wrap justify-center">
            {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
              // Show first page, last page, current page, and pages around current
              let pageNum: number;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (currentPage <= 3) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = currentPage - 2 + i;
              }
              
              return (
                <Button
                  key={pageNum}
                  variant={currentPage === pageNum ? 'default' : 'outline'}
                  onClick={() => setCurrentPage(pageNum)}
                  className="w-10 h-10"
                  size="sm"
                >
                  {pageNum}
                </Button>
              );
            })}
          </div>
          
          <Button
            variant="outline"
            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            size="sm"
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
