'use client';

import { useEffect, useState, useRef, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { RTVIClient } from '@pipecat-ai/client-js';
import DailyIframe from '@daily-co/daily-js';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { PhoneOff, Loader2, Mic, MicOff } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import type { ConnectionState } from '@/types/voice';

function VoiceSessionContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { toast } = useToast();

  // Extract room credentials from URL
  const roomUrl = searchParams.get('room_url');
  const userToken = searchParams.get('user_token');
  const sessionId = searchParams.get('session_id');
  const category = searchParams.get('category') || 'Counselor';

  // State
  const [connectionState, setConnectionState] = useState<ConnectionState>('idle');
  const [isMuted, setIsMuted] = useState(false);
  const [showEndDialog, setShowEndDialog] = useState(false);
  const [permissionDenied, setPermissionDenied] = useState(false);

  // Refs
  const dailyCallRef = useRef<any>(null);
  const hasConnected = useRef(false);

  // Validate params
  useEffect(() => {
    if (!roomUrl || !userToken || !sessionId) {
      toast({
        title: "Invalid Session",
        description: "Missing required session parameters. Returning to dashboard.",
        variant: "destructive"
      });
      router.push('/dashboard');
    }
  }, [roomUrl, userToken, sessionId, router, toast]);

  // Initialize Daily call and connect
  useEffect(() => {
    if (!roomUrl || !userToken || hasConnected.current) return;

    const initializeClient = async () => {
      try {
        setConnectionState('connecting');

        // Request microphone permission
        try {
          await navigator.mediaDevices.getUserMedia({ audio: true });
        } catch (permError) {
          console.error('Microphone permission denied:', permError);
          setPermissionDenied(true);
          setConnectionState('error');
          toast({
            title: "Microphone Required",
            description: "Please allow microphone access to join the voice session.",
            variant: "destructive"
          });
          return;
        }

        // Create Daily call instance
        const dailyCall = DailyIframe.createCallObject({
          audioSource: true,
          videoSource: false,
        });

        // Event listeners
        dailyCall.on('joined-meeting', () => {
          console.log('Joined Daily meeting');
          setConnectionState('connected');
          toast({
            title: "Connected",
            description: `You're now connected to ${category}. Start speaking!`
          });
        });

        dailyCall.on('left-meeting', () => {
          console.log('Left Daily meeting');
          setConnectionState('disconnected');
        });

        dailyCall.on('error', (error: any) => {
          console.error('Daily call error:', error);
          setConnectionState('error');
          toast({
            title: "Connection Error",
            description: "Lost connection to the session. Please try reconnecting.",
            variant: "destructive"
          });
        });

        // Join the room
        await dailyCall.join({
          url: roomUrl,
          token: userToken,
        });

        dailyCallRef.current = dailyCall;
        hasConnected.current = true;

      } catch (error) {
        console.error('Failed to initialize Daily call:', error);
        setConnectionState('error');
        toast({
          title: "Connection Failed",
          description: error instanceof Error ? error.message : "Unable to connect to voice session.",
          variant: "destructive"
        });
      }
    };

    initializeClient();

    // Cleanup on unmount
    return () => {
      if (dailyCallRef.current) {
        dailyCallRef.current.leave();
        dailyCallRef.current.destroy();
        dailyCallRef.current = null;
      }
    };
  }, [roomUrl, userToken, category, toast]);

  // Mute/Unmute microphone
  const toggleMute = async () => {
    if (!dailyCallRef.current) return;

    try {
      const newMutedState = !isMuted;
      await dailyCallRef.current.setLocalAudio(!newMutedState);
      setIsMuted(newMutedState);
    } catch (error) {
      console.error('Failed to toggle mute:', error);
    }
  };

  // End session handler
  const handleEndSession = async () => {
    if (dailyCallRef.current) {
      await dailyCallRef.current.leave();
      dailyCallRef.current.destroy();
    }
    
    toast({
      title: "Session Ended",
      description: "Your counseling session has ended. Take care!"
    });
    
    router.push('/dashboard');
  };

  // Retry connection
  const retryConnection = () => {
    hasConnected.current = false;
    setConnectionState('idle');
    window.location.reload();
  };

  // Render connection status
  const renderConnectionStatus = () => {
    switch (connectionState) {
      case 'connecting':
        return (
          <div className="flex items-center gap-2 text-blue-600">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Connecting to {category}...</span>
          </div>
        );
      case 'connected':
        return (
          <div className="flex items-center gap-2 text-green-600">
            <div className="h-3 w-3 rounded-full bg-green-600 animate-pulse" />
            <span>Connected</span>
          </div>
        );
      case 'disconnected':
        return (
          <div className="flex items-center gap-2 text-red-600">
            <div className="h-3 w-3 rounded-full bg-red-600" />
            <span>Disconnected</span>
          </div>
        );
      case 'error':
        return (
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2 text-red-600">
              <div className="h-3 w-3 rounded-full bg-red-600" />
              <span>Connection Error</span>
            </div>
            <Button onClick={retryConnection} variant="outline" size="sm">
              Retry Connection
            </Button>
          </div>
        );
      default:
        return null;
    }
  };

  // Handle permission denied state
  if (permissionDenied) {
    return (
      <div className="container mx-auto flex items-center justify-center min-h-screen p-4">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>Microphone Access Required</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              Voice calling requires microphone access. Please enable microphone permissions in your browser settings and reload the page.
            </p>
            <div className="flex gap-2">
              <Button onClick={() => window.location.reload()} className="flex-1">
                Try Again
              </Button>
              <Button onClick={() => router.push('/dashboard')} variant="outline" className="flex-1">
                Go Back
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto flex flex-col items-center justify-center min-h-screen p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Voice Session: {category}</CardTitle>
            {renderConnectionStatus()}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Audio visualization placeholder (Story 3.5 will add transcript) */}
          <div className="flex items-center justify-center p-12 bg-muted rounded-lg">
            <div className="text-center space-y-4">
              <div className="text-6xl">
                {isMuted ? <MicOff className="mx-auto" /> : <Mic className="mx-auto animate-pulse" />}
              </div>
              <p className="text-muted-foreground">
                {connectionState === 'connected' 
                  ? isMuted 
                    ? 'Microphone muted. Click to unmute.'
                    : 'Listening... Speak freely.'
                  : 'Connecting...'}
              </p>
            </div>
          </div>

          {/* Session controls */}
          <div className="flex gap-3 justify-center">
            <Button
              onClick={toggleMute}
              variant={isMuted ? 'destructive' : 'secondary'}
              disabled={connectionState !== 'connected'}
              className="flex-1 max-w-xs"
            >
              {isMuted ? <MicOff className="mr-2 h-4 w-4" /> : <Mic className="mr-2 h-4 w-4" />}
              {isMuted ? 'Unmute' : 'Mute'}
            </Button>
            
            <Button
              onClick={() => setShowEndDialog(true)}
              variant="destructive"
              className="flex-1 max-w-xs"
            >
              <PhoneOff className="mr-2 h-4 w-4" />
              End Session
            </Button>
          </div>

          {/* Session info */}
          <div className="text-xs text-muted-foreground text-center space-y-1">
            <p>Session ID: {sessionId}</p>
            <p>If you&apos;re in crisis, call 988 (Suicide & Crisis Lifeline) immediately.</p>
          </div>
        </CardContent>
      </Card>

      {/* End session confirmation dialog */}
      <AlertDialog open={showEndDialog} onOpenChange={setShowEndDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>End Voice Session?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to end this counseling session? You can always start a new session from the dashboard.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Stay in Session</AlertDialogCancel>
            <AlertDialogAction onClick={handleEndSession}>
              End Session
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

export default function VoiceSessionPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    }>
      <VoiceSessionContent />
    </Suspense>
  );
}
