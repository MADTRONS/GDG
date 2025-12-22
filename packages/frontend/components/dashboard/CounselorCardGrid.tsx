'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { CounselorCard } from './CounselorCard';
import { CounselorCardSkeleton } from './CounselorCardSkeleton';
import { getCategories, type CounselorCategory } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';
import { useAuth } from '@/components/auth/AuthProvider';

export function CounselorCardGrid() {
  const [categories, setCategories] = useState<CounselorCategory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loadingVoice, setLoadingVoice] = useState<string | null>(null);
  const [loadingVideo, setLoadingVideo] = useState<string | null>(null);
  const { toast } = useToast();
  const { user } = useAuth();
  const router = useRouter();

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
    // Guard: prevent duplicate requests
    if (loadingVoice === category.id) return;

    // Guard: check authentication
    if (!user) {
      toast({
        title: "Authentication Required",
        description: "Please log in to start a voice session.",
        variant: "destructive"
      });
      router.push('/');
      return;
    }

    setLoadingVoice(category.id);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'}/voice/create-room`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            counselor_category: category.id
          })
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create voice session');
      }

      const data = await response.json();
      
      // Navigate to voice session page with room credentials
      router.push(
        `/voice-session?` +
        `room_url=${encodeURIComponent(data.room_url)}&` +
        `user_token=${encodeURIComponent(data.user_token)}&` +
        `session_id=${encodeURIComponent(data.session_id)}&` +
        `category=${encodeURIComponent(category.name)}`
      );

    } catch (error) {
      console.error('Voice call initiation error:', error);
      
      toast({
        title: "Connection Failed",
        description: error instanceof Error ? error.message : "Unable to start voice session. Please try again.",
        variant: "destructive",
        action: (
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => handleVoiceCall(category)}
          >
            Retry
          </Button>
        )
      });
    } finally {
      setLoadingVoice(null);
    }
  };

  const handleVideoCall = async (category: CounselorCategory) => {
    // Guard: prevent duplicate requests
    if (loadingVideo === category.id) return;

    // Guard: check authentication
    if (!user) {
      toast({
        title: "Authentication Required",
        description: "Please log in to start a video session.",
        variant: "destructive"
      });
      router.push('/');
      return;
    }

    setLoadingVideo(category.id);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'}/video/create-room`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            counselor_category: category.id
          })
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create video session');
      }

      const data = await response.json();
      
      // Navigate to video session page with room credentials
      router.push(
        `/video-session?` +
        `room_url=${encodeURIComponent(data.room_url)}&` +
        `access_token=${encodeURIComponent(data.access_token)}&` +
        `session_id=${encodeURIComponent(data.session_id)}&` +
        `category=${encodeURIComponent(category.name)}`
      );

    } catch (error) {
      console.error('Video call initiation error:', error);
      
      toast({
        title: "Connection Failed",
        description: error instanceof Error ? error.message : "Unable to start video session. Please try again.",
        variant: "destructive",
        action: (
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => handleVideoCall(category)}
          >
            Retry
          </Button>
        )
      });
    } finally {
      setLoadingVideo(null);
    }
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
