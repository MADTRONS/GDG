'use client';

import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';

function VoiceSessionContent() {
  const searchParams = useSearchParams();
  
  const roomUrl = searchParams.get('room_url');
  const userToken = searchParams.get('user_token');
  const sessionId = searchParams.get('session_id');
  const category = searchParams.get('category');

  if (!roomUrl || !userToken || !sessionId) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-destructive">Invalid session parameters</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Voice Session: {category}</h1>
      <p className="mb-2">Room URL: {roomUrl}</p>
      <p className="mb-2">Session ID: {sessionId}</p>
      <p className="text-muted-foreground">Story 3.4 will implement RTVIClient connection here</p>
    </div>
  );
}

export default function VoiceSessionPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen">Loading session...</div>}>
      <VoiceSessionContent />
    </Suspense>
  );
}
