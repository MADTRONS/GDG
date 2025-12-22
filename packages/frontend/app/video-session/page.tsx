'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { Suspense, useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { AlertCircle, ArrowLeft } from 'lucide-react';

function VideoSessionContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  
  const roomUrl = searchParams.get('room_url');
  const accessToken = searchParams.get('access_token');
  const sessionId = searchParams.get('session_id');
  const category = searchParams.get('category');

  useEffect(() => {
    // Validate required parameters
    if (!roomUrl || !accessToken || !sessionId) {
      setError('Invalid session parameters. Please start a new video session.');
    }
  }, [roomUrl, accessToken, sessionId]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-red-900 mb-2">
                Session Error
              </h3>
              <p className="text-red-700 mb-4">
                {error}
              </p>
              <Button
                onClick={() => router.push('/dashboard')}
                variant="outline"
                className="gap-2 border-red-300 text-red-700 hover:bg-red-100"
              >
                <ArrowLeft className="h-4 w-4" />
                Return to Dashboard
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="container mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">
              Video Session: {category || 'Counselor'}
            </h1>
            <p className="text-sm text-gray-500">Session ID: {sessionId}</p>
          </div>
          <Button
            onClick={() => router.push('/dashboard')}
            variant="ghost"
            size="sm"
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Button>
        </div>
      </header>

      {/* Main content area - Story 4.4 will implement LiveKit client here */}
      <main className="flex-1 container mx-auto p-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Video Connection Ready
            </h2>
            <p className="text-gray-600 mb-4">
              Room URL: <span className="font-mono text-sm">{roomUrl}</span>
            </p>
            <p className="text-gray-500 text-sm">
              Story 4.4 will implement the LiveKit client connection and video rendering here.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function VideoSessionPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Loading video session...</p>
        </div>
      </div>
    }>
      <VideoSessionContent />
    </Suspense>
  );
}
