'use client';

import { useState, useEffect } from 'react';
import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { CounselorCard } from './CounselorCard';
import { CounselorCardSkeleton } from './CounselorCardSkeleton';
import { getCategories, type CounselorCategory } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';

export function CounselorCardGrid() {
  const [categories, setCategories] = useState<CounselorCategory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loadingVoice, setLoadingVoice] = useState<string | null>(null);
  const [loadingVideo, setLoadingVideo] = useState<string | null>(null);
  const { toast } = useToast();

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

  const handleVoiceCall = async (category: CounselorCategory) => {
    console.log('Voice call requested for category:', category.name);
    console.log('Category ID:', category.id);
    
    // Set loading state
    setLoadingVoice(category.id);
    
    // Show toast notification
    toast({
      title: "Coming Soon",
      description: "Voice calling will be available in the next update. Stay tuned!",
      duration: 4000,
    });
    
    // Clear loading state after delay
    setTimeout(() => {
      setLoadingVoice(null);
    }, 4000);
  };

  const handleVideoCall = async (category: CounselorCategory) => {
    console.log('Video call requested for category:', category.name);
    console.log('Category ID:', category.id);
    
    // Set loading state
    setLoadingVideo(category.id);
    
    // Show toast notification
    toast({
      title: "Coming Soon",
      description: "Video calling will be available in the next update. Stay tuned!",
      duration: 4000,
    });
    
    // Clear loading state after delay
    setTimeout(() => {
      setLoadingVideo(null);
    }, 4000);
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
          onVoiceCall={handleVoiceCall}
          onVideoCall={handleVideoCall}
          isVoiceLoading={loadingVoice === category.id}
          isVideoLoading={loadingVideo === category.id}
        />
      ))}
    </div>
  );
}
