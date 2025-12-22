'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar as CalendarComponent } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { useToast } from '@/components/ui/use-toast';
import { Phone, Video, Clock, ChevronRight, Calendar, Filter, Loader2, Calendar as CalendarIcon } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import type { DateRange } from 'react-day-picker';
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
  const searchParams = useSearchParams();
  const { toast } = useToast();

  // Initialize filters from URL
  const [categoryFilter, setCategoryFilter] = useState<string>(
    searchParams.get('category') || 'all'
  );
  const [modeFilter, setModeFilter] = useState<string>(
    searchParams.get('mode') || 'all'
  );
  const [dateRange, setDateRange] = useState<DateRange | undefined>(() => {
    const startDate = searchParams.get('start_date');
    const endDate = searchParams.get('end_date');
    if (startDate && endDate) {
      return {
        from: new Date(startDate),
        to: new Date(endDate)
      };
    }
    return undefined;
  });

  // State
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(
    parseInt(searchParams.get('page') || '1', 10)
  );
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

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();
    
    if (categoryFilter !== 'all') {
      params.set('category', categoryFilter);
    }
    if (modeFilter !== 'all') {
      params.set('mode', modeFilter);
    }
    if (dateRange?.from) {
      params.set('start_date', dateRange.from.toISOString());
    }
    if (dateRange?.to) {
      params.set('end_date', dateRange.to.toISOString());
    }
    if (currentPage > 1) {
      params.set('page', currentPage.toString());
    }

    const paramsString = params.toString();
    const newUrl = paramsString ? `/sessions?${paramsString}` : '/sessions';
    
    router.replace(newUrl, { scroll: false });
  }, [categoryFilter, modeFilter, dateRange, currentPage, router]);

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
      if (dateRange?.from) {
        params.append('start_date', dateRange.from.toISOString());
      }
      if (dateRange?.to) {
        params.append('end_date', dateRange.to.toISOString());
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
  }, [currentPage, categoryFilter, modeFilter, dateRange]);

  // Clear filters
  const clearFilters = () => {
    setCategoryFilter('all');
    setModeFilter('all');
    setDateRange(undefined);
    setCurrentPage(1);
    
    toast({
      title: "Filters Cleared",
      description: "Showing all sessions"
    });
  };

  // Check if any filters are active
  const hasActiveFilters = () => {
    return categoryFilter !== 'all' || 
           modeFilter !== 'all' || 
           dateRange !== undefined;
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
        <div className="flex flex-col items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mb-2" role="status" />
          <p className="text-gray-600">
            {hasActiveFilters() ? 'Filtering sessions...' : 'Loading sessions...'}
          </p>
        </div>
      </div>
    );
  }

  // Empty state (no sessions at all)
  if (!loading && sessions.length === 0 && !hasActiveFilters()) {
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
            {hasActiveFilters() && (
              <span className="text-sm font-normal text-blue-600">
                ({totalCount} result{totalCount !== 1 ? 's' : ''})
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            {/* Category Filter */}
            <div className="flex-1 min-w-[200px]">
              <label className="text-sm font-medium mb-2 block" htmlFor="category-filter">
                Category
              </label>
              <Select 
                value={categoryFilter} 
                onValueChange={(value) => {
                  setCategoryFilter(value);
                  setCurrentPage(1);
                }}
              >
                <SelectTrigger id="category-filter" aria-label="Filter by counselor category">
                  <SelectValue placeholder="All Categories" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((cat) => (
                    <SelectItem key={cat.value} value={cat.value}>
                      {cat.icon && <span className="mr-1">{cat.icon}</span>}
                      {cat.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Mode Filter */}
            <div className="flex-1 min-w-[200px]">
              <label className="text-sm font-medium mb-2 block" htmlFor="mode-filter">
                Mode
              </label>
              <Select 
                value={modeFilter} 
                onValueChange={(value) => {
                  setModeFilter(value);
                  setCurrentPage(1);
                }}
              >
                <SelectTrigger id="mode-filter" aria-label="Filter by session mode">
                  <SelectValue placeholder="All Modes" />
                </SelectTrigger>
                <SelectContent>
                  {modes.map((mode) => (
                    <SelectItem key={mode.value} value={mode.value}>
                      {mode.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Date Range Picker */}
            <div className="flex-1 min-w-[240px]">
              <label className="text-sm font-medium mb-2 block">
                Date Range
              </label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal",
                      !dateRange && "text-gray-500"
                    )}
                    aria-label="Select date range"
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {dateRange?.from ? (
                      dateRange.to ? (
                        <>
                          {format(dateRange.from, "MMM dd, yyyy")} -{" "}
                          {format(dateRange.to, "MMM dd, yyyy")}
                        </>
                      ) : (
                        format(dateRange.from, "MMM dd, yyyy")
                      )
                    ) : (
                      <span>Pick a date range</span>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <CalendarComponent
                    initialFocus
                    mode="range"
                    defaultMonth={dateRange?.from}
                    selected={dateRange}
                    onSelect={(range) => {
                      setDateRange(range);
                      setCurrentPage(1);
                    }}
                    numberOfMonths={2}
                  />
                </PopoverContent>
              </Popover>
            </div>

            {/* Clear Filters */}
            <div className="flex items-end">
              <Button
                variant="outline"
                onClick={clearFilters}
                disabled={!hasActiveFilters() || loading}
                aria-label="Clear all filters"
              >
                Clear Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Session List */}
      {sessions.length === 0 ? (
        hasActiveFilters() ? (
          <Card className="text-center py-8">
            <CardContent className="pt-6">
              <p className="text-gray-600 mb-4">No sessions found matching your filters.</p>
              <Button variant="link" onClick={clearFilters}>
                Clear filters to see all sessions
              </Button>
            </CardContent>
          </Card>
        ) : null
      ) : (
        <div className="space-y-4">
          {/* Active Filters Badge */}
          {hasActiveFilters() && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span>Showing {totalCount} filtered result{totalCount !== 1 ? 's' : ''}</span>
            </div>
          )}
          
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
