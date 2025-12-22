'use client';

import { useEffect, useState, useRef, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Room, RoomEvent, Track, ConnectionQuality } from 'livekit-client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { ScrollArea } from '@/components/ui/scroll-area';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { 
  PhoneOff, 
  Loader2, 
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Volume1,
  Wifi,
  WifiOff,
  MessageSquare
} from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { cn } from '@/lib/utils';
import type { ConnectionState } from '@/types/video';

type ConnectionQualityLevel = 'excellent' | 'good' | 'fair' | 'poor';

interface TranscriptMessage {
  speaker: 'user' | 'counselor';
  text: string;
  timestamp: Date;
}

interface VideoQualityMetrics {
  bitrateReadings: number[];
  fpsReadings: number[];
  packetLossEvents: number;
  connectionQualityReadings: ConnectionQualityLevel[];
}

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
  const [connectionQuality, setConnectionQuality] = useState<ConnectionQualityLevel>('good');
  const [showEndDialog, setShowEndDialog] = useState(false);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState<number>(80);
  const [transcript, setTranscript] = useState<TranscriptMessage[]>([]);
  const [autoScroll, setAutoScroll] = useState(true);
  const [showTranscript, setShowTranscript] = useState(true);
  const [avatarVideoTrack, setAvatarVideoTrack] = useState<MediaStreamTrack | null>(null);
  const [avatarAudioTrack, setAvatarAudioTrack] = useState<any>(null);
  const [sessionStartTime] = useState<Date>(new Date());
  const [qualityMetrics, setQualityMetrics] = useState<VideoQualityMetrics>({
    bitrateReadings: [],
    fpsReadings: [],
    packetLossEvents: 0,
    connectionQualityReadings: []
  });

  // Refs
  const roomRef = useRef<Room | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const transcriptRef = useRef<HTMLDivElement>(null);
  const hasConnected = useRef(false);
  const avatarJoinTimeout = useRef<NodeJS.Timeout | null>(null);
  const localAudioTrackRef = useRef<any>(null);
  const qualityMonitorInterval = useRef<NodeJS.Timeout | null>(null);
  const sessionSaved = useRef(false);

  // Load volume from localStorage
  useEffect(() => {
    const savedVolume = localStorage.getItem('avatar_volume');
    if (savedVolume) {
      setVolume(parseInt(savedVolume));
    }
  }, []);

  // Save volume to localStorage
  useEffect(() => {
    localStorage.setItem('avatar_volume', volume.toString());
  }, [volume]);

  // Apply volume to avatar audio track
  useEffect(() => {
    if (avatarAudioTrack) {
      avatarAudioTrack.setVolume(volume / 100);
    }
  }, [volume, avatarAudioTrack]);

  // Auto-scroll transcript
  useEffect(() => {
    if (autoScroll && transcriptRef.current) {
      transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight;
    }
  }, [transcript, autoScroll]);

  // Handle transcript scroll
  const handleTranscriptScroll = () => {
    if (transcriptRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = transcriptRef.current;
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 10;
      setAutoScroll(isAtBottom);
    }
  };

  // Calculate connection quality average
  const calculateConnectionQualityAverage = (readings: ConnectionQualityLevel[]): string => {
    if (readings.length === 0) return 'unknown';
    
    const qualityScores: Record<ConnectionQualityLevel, number> = {
      'excellent': 4,
      'good': 3,
      'fair': 2,
      'poor': 1
    };
    
    const totalScore = readings.reduce((sum, quality) => {
      return sum + qualityScores[quality];
    }, 0);
    
    const avgScore = totalScore / readings.length;
    
    if (avgScore >= 3.5) return 'excellent';
    if (avgScore >= 2.5) return 'good';
    if (avgScore >= 1.5) return 'fair';
    return 'poor';
  };

  // Save session function with retry logic
  const saveSession = async (retryCount = 0): Promise<boolean> => {
    if (sessionSaved.current) {
      console.log('Session already saved');
      return true;
    }

    const sessionEndTime = new Date();
    const durationSeconds = Math.floor(
      (sessionEndTime.getTime() - sessionStartTime.getTime()) / 1000
    );

    // Calculate average quality metrics
    const avgBitrate = qualityMetrics.bitrateReadings.length > 0
      ? qualityMetrics.bitrateReadings.reduce((a, b) => a + b, 0) / qualityMetrics.bitrateReadings.length
      : 0;
      
    const avgFps = qualityMetrics.fpsReadings.length > 0
      ? qualityMetrics.fpsReadings.reduce((a, b) => a + b, 0) / qualityMetrics.fpsReadings.length
      : 0;
      
    const totalReadings = qualityMetrics.bitrateReadings.length;
    const packetLossPercentage = totalReadings > 0
      ? (qualityMetrics.packetLossEvents / totalReadings) * 100
      : 0;

    // Construct session payload
    const sessionPayload = {
      session_id: sessionId,
      counselor_category: category,
      mode: 'video',
      start_time: sessionStartTime.toISOString(),
      end_time: sessionEndTime.toISOString(),
      duration_seconds: durationSeconds,
      transcript: transcript.map(msg => ({
        speaker: msg.speaker,
        text: msg.text,
        timestamp: msg.timestamp.toISOString()
      })),
      quality_metrics: {
        average_bitrate: parseFloat(avgBitrate.toFixed(2)),
        average_fps: parseFloat(avgFps.toFixed(2)),
        packet_loss_percentage: parseFloat(packetLossPercentage.toFixed(2)),
        connection_quality_average: calculateConnectionQualityAverage(qualityMetrics.connectionQualityReadings),
        total_readings: totalReadings
      }
    };

    try {
      const response = await fetch('/api/v1/sessions/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(sessionPayload)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to save session: ${response.statusText} - ${errorText}`);
      }

      sessionSaved.current = true;
      
      const durationMinutes = Math.floor(durationSeconds / 60);
      const durationSecondsRemainder = durationSeconds % 60;
      
      toast({
        title: "Session Saved",
        description: `Your video session (${durationMinutes}m ${durationSecondsRemainder}s) has been saved to your history.`,
      });
      
      console.log('Session saved successfully');
      return true;

    } catch (error) {
      console.error('Error saving session:', error);

      // Retry logic with exponential backoff
      if (retryCount < 3) {
        const backoffDelay = Math.pow(2, retryCount) * 1000; // 1s, 2s, 4s
        console.log(`Retrying save in ${backoffDelay}ms (attempt ${retryCount + 1}/3)`);
        
        await new Promise(resolve => setTimeout(resolve, backoffDelay));
        return saveSession(retryCount + 1);
      }

      // All retries failed
      toast({
        title: "Failed to Save Session",
        description: "Your session data couldn't be saved. Please contact support if this persists.",
        variant: "destructive"
      });
      
      return false;
    }
  };

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
          
          // Store local audio track for mute/unmute
          room.localParticipant.audioTracks.forEach(publication => {
            localAudioTrackRef.current = publication.audioTrack;
          });
          
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

        // Connection quality change handler
        room.on(RoomEvent.ConnectionQualityChanged, (quality: ConnectionQuality) => {
          console.log('Connection quality:', quality);
          let qualityLevel: ConnectionQualityLevel;
          switch (quality) {
            case ConnectionQuality.Excellent:
              qualityLevel = 'excellent';
              break;
            case ConnectionQuality.Good:
              qualityLevel = 'good';
              break;
            case ConnectionQuality.Poor:
              qualityLevel = 'poor';
              // Show notification for poor quality
              toast({
                title: "Poor Connection Quality",
                description: "Your connection is unstable. Consider switching to voice-only mode if video continues to lag.",
                variant: "destructive"
              });
              break;
            default:
              qualityLevel = 'fair';
          }
          setConnectionQuality(qualityLevel);
          
          // Track quality reading for session metrics
          setQualityMetrics(prev => ({
            ...prev,
            connectionQualityReadings: [...prev.connectionQualityReadings, qualityLevel]
          }));
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
          
          // Audio tracks - store reference and set volume
          if (participant.identity.includes('avatar') && track.kind === Track.Kind.Audio) {
            setAvatarAudioTrack(track);
            track.setVolume(volume / 100);
            track.attach(); // Attach to default audio output
          }
        });

        room.on(RoomEvent.Disconnected, async () => {
          console.log('Disconnected from room');
          setConnectionState('disconnected');
          
          // Auto-save session on disconnect
          await saveSession();
        });

        // Data received handler (for transcript)
        room.on(RoomEvent.DataReceived, (payload: Uint8Array) => {
          try {
            const data = JSON.parse(new TextDecoder().decode(payload));
            if (data.type === 'transcript') {
              setTranscript(prev => [...prev, {
                speaker: data.speaker,
                text: data.text,
                timestamp: new Date()
              }]);
            }
          } catch (error) {
            console.error('Failed to parse data:', error);
          }
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

  // Quality monitoring - track video metrics every 10 seconds
  useEffect(() => {
    if (!roomRef.current || connectionState !== 'connected') return;

    const monitorQuality = async () => {
      try {
        const room = roomRef.current;
        if (!room) return;

        // Get stats from local participant
        const stats = await room.localParticipant.getStats();
        
        stats.forEach((report) => {
          // Track bitrate from outbound-rtp stats
          if (report.type === 'outbound-rtp' && report.kind === 'video') {
            const bytesSent = report.bytesSent || 0;
            const timestamp = report.timestamp || Date.now();
            
            // Calculate bitrate in kbps
            if (report.bytesSent !== undefined) {
              const bitrate = (bytesSent * 8) / 1000; // Convert to kbps
              setQualityMetrics(prev => ({
                ...prev,
                bitrateReadings: [...prev.bitrateReadings, bitrate]
              }));
            }
            
            // Track frame rate
            if (report.framesPerSecond !== undefined) {
              setQualityMetrics(prev => ({
                ...prev,
                fpsReadings: [...prev.fpsReadings, report.framesPerSecond]
              }));
            }
            
            // Track packet loss events
            const packetsLost = report.packetsLost || 0;
            if (packetsLost > 0) {
              setQualityMetrics(prev => ({
                ...prev,
                packetLossEvents: prev.packetLossEvents + 1
              }));
            }
          }
        });
      } catch (error) {
        console.error('Failed to collect quality metrics:', error);
      }
    };

    // Start monitoring interval
    qualityMonitorInterval.current = setInterval(monitorQuality, 10000); // Every 10 seconds
    
    // Initial reading
    monitorQuality();

    // Cleanup on unmount
    return () => {
      if (qualityMonitorInterval.current) {
        clearInterval(qualityMonitorInterval.current);
        qualityMonitorInterval.current = null;
      }
    };
  }, [connectionState]);

  // Auto-save session on page unload
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (!sessionSaved.current && roomRef.current) {
        saveSession();
        // Show browser warning
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  // End session handler
  const handleEndSession = async () => {
    // Save session before disconnecting
    await saveSession();
    
    if (roomRef.current) {
      await roomRef.current.disconnect();
    }
    
    toast({
      title: "Session Ended",
      description: "Your video counseling session has ended. Take care!"
    });
    
    router.push('/dashboard');
  };

  // Mute/unmute toggle
  const toggleMute = () => {
    if (localAudioTrackRef.current) {
      if (isMuted) {
        localAudioTrackRef.current.unmute();
      } else {
        localAudioTrackRef.current.mute();
      }
      setIsMuted(!isMuted);
      
      toast({
        description: isMuted ? "Microphone unmuted" : "Microphone muted",
        duration: 2000
      });
    }
  };

  // Keyboard shortcut for mute (Space bar)
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.code === 'Space' && e.target === document.body) {
        e.preventDefault();
        toggleMute();
      }
    };
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isMuted]);

  // Connection quality icon component
  const ConnectionQualityIcon = () => {
    const icons: Record<ConnectionQualityLevel, { Icon: any; color: string; label: string }> = {
      excellent: { Icon: Wifi, color: 'text-green-600', label: 'Excellent' },
      good: { Icon: Wifi, color: 'text-green-500', label: 'Good' },
      fair: { Icon: Wifi, color: 'text-yellow-500', label: 'Fair' },
      poor: { Icon: WifiOff, color: 'text-red-600', label: 'Poor' },
    };
    const { Icon, color, label } = icons[connectionQuality];
    return (
      <div className={cn("flex items-center gap-1", color)} title={`Connection: ${label}`}>
        <Icon className="h-4 w-4" />
        <span className="text-xs hidden sm:inline">{label}</span>
      </div>
    );
  };

  // Volume icon component
  const VolumeIcon = () => {
    if (volume === 0) return <VolumeX className="h-4 w-4" />;
    if (volume < 33) return <Volume1 className="h-4 w-4" />;
    return <Volume2 className="h-4 w-4" />;
  };

  // Retry connection
  const retryConnection = () => {
    hasConnected.current = false;
    setConnectionState('idle');
    window.location.reload();
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
    <div className="flex flex-col h-screen bg-black">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-gray-900 border-b border-gray-800">
        <div>
          <h1 className="text-lg font-bold text-white">Video Session: {category}</h1>
          <p className="text-xs text-gray-400">Session ID: {sessionId}</p>
        </div>
        <div className="flex items-center gap-4">
          <ConnectionQualityIcon />
          <div className={cn(
            "flex items-center gap-1",
            connectionState === 'connected' ? 'text-green-600' : 'text-yellow-500'
          )}>
            <div className="h-2 w-2 rounded-full bg-current animate-pulse" />
            <span className="text-xs hidden sm:inline">
              {connectionState === 'connected' ? 'Connected' : 'Connecting...'}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content - Split Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Video Section (70% on desktop) */}
        <div className={cn(
          "flex items-center justify-center bg-gray-900 p-4 transition-all",
          showTranscript ? "w-full md:w-[70%]" : "w-full"
        )}>
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

        {/* Transcript Panel (30% on desktop, hidden by default on mobile) */}
        {showTranscript && (
          <div className="hidden md:flex md:w-[30%] bg-gray-800 border-l border-gray-700 flex-col">
            <div className="p-3 border-b border-gray-700">
              <h2 className="text-sm font-semibold text-white flex items-center gap-2">
                <MessageSquare className="h-4 w-4" />
                Live Transcript
              </h2>
            </div>
            <div 
              ref={transcriptRef}
              className="flex-1 overflow-y-auto p-4"
              onScroll={handleTranscriptScroll}
            >
              <div className="space-y-3">
                {transcript.length === 0 ? (
                  <p className="text-gray-400 text-sm italic">Transcript will appear here as you talk...</p>
                ) : (
                  transcript.map((msg, idx) => (
                    <div key={idx} className="text-sm">
                      <div className={cn(
                        "font-semibold mb-1",
                        msg.speaker === 'user' ? 'text-blue-400' : 'text-green-400'
                      )}>
                        {msg.speaker === 'user' ? 'You:' : 'Counselor:'}
                      </div>
                      <div className="text-gray-200">{msg.text}</div>
                    </div>
                  ))
                )}
              </div>
            </div>
            {!autoScroll && (
              <div className="p-2 border-t border-gray-700">
                <Button 
                  size="sm" 
                  variant="outline" 
                  onClick={() => setAutoScroll(true)}
                  className="w-full text-xs"
                >
                  Scroll to Latest
                </Button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Control Bar */}
      <div className="p-4 bg-gray-900 border-t border-gray-800">
        <div className="flex items-center justify-between max-w-4xl mx-auto gap-2 sm:gap-4">
          {/* Mute Button */}
          <Button
            onClick={toggleMute}
            variant={isMuted ? "destructive" : "outline"}
            size="lg"
            aria-label={isMuted ? "Unmute" : "Mute"}
            className="shrink-0"
          >
            {isMuted ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
            <span className="ml-2 hidden sm:inline">{isMuted ? "Unmute" : "Mute"}</span>
          </Button>

          {/* Volume Control */}
          <div className="hidden sm:flex items-center gap-3 flex-1 max-w-md">
            <VolumeIcon />
            <Slider
              value={[volume]}
              onValueChange={(values) => setVolume(values[0])}
              max={100}
              step={1}
              className="flex-1"
              aria-label="Volume"
            />
            <span className="text-xs text-gray-400 w-8 text-right">{volume}%</span>
          </div>

          {/* Mobile Transcript Toggle */}
          <Button
            onClick={() => setShowTranscript(!showTranscript)}
            variant="outline"
            size="lg"
            className="md:hidden shrink-0"
            aria-label="Toggle transcript"
          >
            <MessageSquare className="h-5 w-5" />
          </Button>

          {/* End Session Button */}
          <Button
            onClick={() => setShowEndDialog(true)}
            variant="destructive"
            size="lg"
            className="shrink-0"
          >
            <PhoneOff className="mr-2 h-5 w-5" />
            <span className="hidden sm:inline">End Session</span>
          </Button>
        </div>

        <div className="text-xs text-gray-400 text-center mt-3">
          <p>Press Space to {isMuted ? 'unmute' : 'mute'}. If you're in crisis, call 988 immediately.</p>
        </div>
      </div>

      {/* End Session Dialog */}
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
