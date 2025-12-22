'use client';

import { useEffect, useState, useRef, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Room, RoomEvent, Track } from 'livekit-client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { PhoneOff, Loader2, Video as VideoIcon } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import type { ConnectionState } from '@/types/video';

function VideoSessionContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { toast } = useToast();

  // Extract room credentials from URL
  const roomUrl = searchParams.get('room_url');
  const accessToken = searchParams.get('access_token');
  const sessionId = searchParams.get('session_id');
  const category = searchParams.get('category') || 'Counselor';

  // State
  const [connectionState, setConnectionState] = useState<ConnectionState>('idle');
  const [showEndDialog, setShowEndDialog] = useState(false);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [avatarVideoTrack, setAvatarVideoTrack] = useState<MediaStreamTrack | null>(null);

  // Refs
  const roomRef = useRef<Room | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const hasConnected = useRef(false);
  const avatarJoinTimeout = useRef<NodeJS.Timeout | null>(null);

  // Validate params
  useEffect(() => {
    if (!roomUrl || !accessToken || !sessionId) {
      toast({
        title: "Invalid Session",
        description: "Missing required session parameters. Returning to dashboard.",
        variant: "destructive"
      });
      router.push('/dashboard');
    }
  }, [roomUrl, accessToken, sessionId, router, toast]);

  // Initialize LiveKit Room and connect
  useEffect(() => {
    if (!roomUrl || !accessToken || hasConnected.current) return;

    const initializeRoom = async () => {
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
            description: "Please allow microphone access to join the video session.",
            variant: "destructive"
          });
          return;
        }

        // Initialize LiveKit Room
        const room = new Room({
          adaptiveStream: true,
          dynacast: true,
          videoCaptureDefaults: {
            resolution: { width: 1280, height: 720 },
          },
        });

        // Set up event listeners
        room.on(RoomEvent.Connected, () => {
          console.log('Connected to room');
          setConnectionState('waiting_avatar');
          
          // Start timeout for avatar joining
          avatarJoinTimeout.current = setTimeout(() => {
            if (connectionState === 'waiting_avatar') {
              setConnectionState('error');
              toast({
                title: "Avatar Connection Timeout",
                description: "The counselor avatar didn't join. Please try again.",
                variant: "destructive"
              });
            }
          }, 30000); // 30 second timeout
        });

        room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
          console.log('Track subscribed:', track.kind, 'from', participant.identity);
          
          // Check if this is the avatar's video track
          if (participant.identity.includes('avatar') && track.kind === Track.Kind.Video) {
            console.log('Avatar video track received');
            
            // Clear avatar join timeout
            if (avatarJoinTimeout.current) {
              clearTimeout(avatarJoinTimeout.current);
            }
            
            setConnectionState('connected');
            setAvatarVideoTrack(track.mediaStreamTrack);
            
            toast({
              title: "Connected",
              description: `You're now connected to ${category}. The avatar can see and hear you.`
            });
          }
          
          // Audio tracks play automatically
          if (track.kind === Track.Kind.Audio) {
            track.attach();  // Attach to default audio output
          }
        });

        room.on(RoomEvent.Disconnected, () => {
          console.log('Disconnected from room');
          setConnectionState('disconnected');
        });

        room.on(RoomEvent.ConnectionQualityChanged, (quality, participant) => {
          console.log('Connection quality:', quality, 'for', participant.identity);
          // Could update UI with quality indicator
        });

        // Connect to room
        await room.connect(roomUrl, accessToken);
        roomRef.current = room;
        hasConnected.current = true;

      } catch (error) {
        console.error('Failed to initialize LiveKit room:', error);
        setConnectionState('error');
        toast({
          title: "Connection Failed",
          description: error instanceof Error ? error.message : "Unable to connect to video session.",
          variant: "destructive"
        });
      }
    };

    initializeRoom();

    // Cleanup on unmount
    return () => {
      if (avatarJoinTimeout.current) {
        clearTimeout(avatarJoinTimeout.current);
      }
      if (roomRef.current) {
        roomRef.current.disconnect();
        roomRef.current = null;
      }
    };
  }, [roomUrl, accessToken, category, toast]);

  // Attach avatar video track to video element
  useEffect(() => {
    if (avatarVideoTrack && videoRef.current) {
      const stream = new MediaStream([avatarVideoTrack]);
      videoRef.current.srcObject = stream;
      videoRef.current.play().catch(err => {
        console.error('Failed to play video:', err);
      });
    }
  }, [avatarVideoTrack]);

  // End session handler
  const handleEndSession = async () => {
    if (roomRef.current) {
      await roomRef.current.disconnect();
    }
    
    toast({
      title: "Session Ended",
      description: "Your video counseling session has ended. Take care!"
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
            <span>Connecting to room...</span>
          </div>
        );
      case 'waiting_avatar':
        return (
          <div className="flex items-center gap-2 text-yellow-600">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Waiting for {category} avatar to join...</span>
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
              Video calling requires microphone access. Please enable microphone permissions in your browser settings and reload the page.
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
    <div className="container mx-auto flex flex-col min-h-screen p-4 bg-black">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-gray-900 rounded-t-lg">
        <div>
          <h1 className="text-xl font-bold text-white">Video Session: {category}</h1>
          <p className="text-sm text-gray-400">Session ID: {sessionId}</p>
        </div>
        {renderConnectionStatus()}
      </div>

      {/* Main video area */}
      <div className="flex-1 flex items-center justify-center bg-gray-900 p-4">
        {avatarVideoTrack ? (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="max-w-full max-h-full object-contain rounded-lg shadow-2xl"
            style={{ aspectRatio: '16/9' }}
          />
        ) : (
          <div className="flex flex-col items-center gap-4 text-white">
            <Loader2 className="h-16 w-16 animate-spin text-blue-500" />
            <p className="text-lg">
              {connectionState === 'connecting' 
                ? 'Connecting to video session...'
                : connectionState === 'waiting_avatar'
                ? 'Waiting for avatar to appear...'
                : 'Initializing...'}
            </p>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="p-4 bg-gray-900 rounded-b-lg">
        <div className="flex items-center justify-center gap-4">
          <Button
            onClick={() => setShowEndDialog(true)}
            variant="destructive"
            size="lg"
          >
            <PhoneOff className="mr-2 h-5 w-5" />
            End Session
          </Button>
        </div>
        
        <div className="text-xs text-gray-400 text-center mt-4">
          <p>If you're in crisis, call 988 (Suicide & Crisis Lifeline) immediately.</p>
        </div>
      </div>

      {/* End session confirmation dialog */}
      <AlertDialog open={showEndDialog} onOpenChange={setShowEndDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>End Video Session?</AlertDialogTitle>
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

export default function VideoSessionPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen bg-black">
        <Loader2 className="h-8 w-8 animate-spin text-white" />
      </div>
    }>
      <VideoSessionContent />
    </Suspense>
  );
}
