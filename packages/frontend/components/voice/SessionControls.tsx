import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Card } from '@/components/ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Mic, MicOff, PhoneOff, Volume2 } from 'lucide-react';
import { ConnectionState } from '@/types/voice';

interface SessionControlsProps {
  isMuted: boolean;
  onToggleMute: () => void;
  volume: number;
  onVolumeChange: (volume: number) => void;
  onEndSession: () => void;
  connectionState: ConnectionState;
  connectionQuality: 'excellent' | 'fair' | 'poor' | null;
}

export function SessionControls({
  isMuted,
  onToggleMute,
  volume,
  onVolumeChange,
  onEndSession,
  connectionState,
  connectionQuality
}: SessionControlsProps) {
  const isConnected = connectionState === 'connected';

  const qualityConfig = {
    excellent: { color: 'text-green-600', label: 'Excellent', bgColor: 'bg-green-600' },
    fair: { color: 'text-yellow-600', label: 'Fair', bgColor: 'bg-yellow-600' },
    poor: { color: 'text-red-600', label: 'Poor', bgColor: 'bg-red-600' }
  };

  const currentQuality = connectionQuality ? qualityConfig[connectionQuality] : null;

  return (
    <Card className='p-4'>
      <div className='space-y-4'>
        {/* Connection Quality Indicator */}
        {currentQuality && (
          <div className="flex items-center justify-between pb-3 border-b">
            <span className="text-sm font-medium">Connection Quality:</span>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="flex items-center gap-2">
                    <div className={`h-3 w-3 rounded-full ${currentQuality.bgColor}`} />
                    <span className={`text-sm ${currentQuality.color}`}>
                      {currentQuality.label}
                    </span>
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Network connection quality affects call clarity</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        )}

        {/* Main Controls */}
        <div className='flex gap-3'>
          {/* Mute Button */}
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  onClick={onToggleMute}
                  disabled={!isConnected}
                  variant={isMuted ? 'destructive' : 'secondary'}
                  className='flex-1'
                  aria-label={isMuted ? 'Unmute microphone' : 'Mute microphone'}
                  aria-pressed={isMuted}
                >
                  {isMuted ? (
                    <MicOff className='mr-2 h-4 w-4' />
                  ) : (
                    <Mic className='mr-2 h-4 w-4' />
                  )}
                  {isMuted ? 'Unmute' : 'Mute'}
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{isMuted ? 'Turn microphone on' : 'Turn microphone off'}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          {/* End Session Button */}
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  onClick={onEndSession}
                  variant='destructive'
                  className='flex-1'
                  aria-label='End session'
                >
                  <PhoneOff className='mr-2 h-4 w-4' />
                  End Session
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Disconnect and return to dashboard</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>

        {/* Volume Control */}
        <div className='space-y-2'>
          <div className='flex items-center justify-between'>
            <label htmlFor='volume-slider' className='text-sm font-medium flex items-center gap-2'>
              <Volume2 className='h-4 w-4' />
              Volume
            </label>
            <span className='text-sm text-muted-foreground' aria-live='polite'>
              {volume}%
            </span>
          </div>
          <Slider
            id='volume-slider'
            value={[volume]}
            onValueChange={([value]) => onVolumeChange(value)}
            min={0}
            max={100}
            step={5}
            disabled={!isConnected}
            aria-label='Adjust counselor volume'
            className='w-full'
          />
        </div>
      </div>
    </Card>
  );
}
