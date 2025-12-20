'use client';

import { useState, useEffect } from 'react';
import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { CounselorCard } from './CounselorCard';
import { CounselorCardSkeleton } from './CounselorCardSkeleton';
import { getCategories, type CounselorCategory } from '@/lib/api';

export function CounselorCardGrid() {
  const [categories, setCategories] = useState<CounselorCategory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCategories = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const categories = await getCategories();
      setCategories(categories);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load counselor categories');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  const handleVoiceCall = (category: CounselorCategory) => {
    console.log('Voice call initiated for:', category.name);
    // TODO: Navigate to voice call session (Story 3.3)
  };

  const handleVideoCall = (category: CounselorCategory) => {
    console.log('Video call initiated for:', category.name);
    // TODO: Navigate to video call session (Story 4.3)
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {Array.from({ length: 6 }).map((_, index) => (
          <CounselorCardSkeleton key={index} />
        ))}
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-red-50 rounded-lg border border-red-200">
        <AlertCircle className="h-12 w-12 text-red-600 mb-4" />
        <h3 className="text-lg font-semibold text-red-900 mb-2">Error Loading Categories</h3>
        <p className="text-red-700 mb-4 text-center">{error}</p>
        <Button
          onClick={fetchCategories}
          variant="outline"
          className="border-red-300 text-red-700 hover:bg-red-100"
        >
          Try Again
        </Button>
      </div>
    );
  }

  // Success state
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {categories.map((category) => (
        <CounselorCard
          key={category.id}
          category={category}
          onVoiceCall={() => handleVoiceCall(category)}
          onVideoCall={() => handleVideoCall(category)}
        />
      ))}
    </div>
  );
}
