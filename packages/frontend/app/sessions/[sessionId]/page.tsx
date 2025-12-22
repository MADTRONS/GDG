'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/components/auth/AuthProvider';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { 
  AlertDialog, 
  AlertDialogAction, 
  AlertDialogCancel, 
  AlertDialogContent, 
  AlertDialogDescription, 
  AlertDialogFooter, 
  AlertDialogHeader, 
  AlertDialogTitle, 
  AlertDialogTrigger 
} from '@/components/ui/alert-dialog';
import { ArrowLeft, Phone, Video, Clock, Calendar, Loader2, Download, Trash2 } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';

interface TranscriptMessage {
  timestamp: string;
  speaker: 'user' | 'counselor';
  text: string;
}

interface SessionDetail {
  session_id: string;
  counselor_category: string;
  counselor_icon?: string;
  mode: 'voice' | 'video';
  started_at: string;
  ended_at: string | null;
  duration_seconds: number;
  transcript: TranscriptMessage[];
  crisis_detected?: boolean;
}

export default function SessionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const { toast } = useToast();

  const sessionId = params?.sessionId as string;
  const [session, setSession] = useState<SessionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [deleting, setDeleting] = useState(false);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login?redirect=/sessions');
    }
  }, [user, authLoading, router]);

  // Fetch session detail
  useEffect(() => {
    if (!user || !sessionId) return;

    const fetchSession = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `/api/v1/sessions/${sessionId}`,
          { credentials: 'include' }
        );

        if (response.status === 403) {
          setError('You do not have permission to view this session.');
          return;
        }

        if (response.status === 404) {
          setError('Session not found.');
          return;
        }

        if (!response.ok) {
          throw new Error('Failed to fetch session');
        }

        const data: SessionDetail = await response.json();
        setSession(data);
      } catch (err) {
        console.error('Error fetching session:', err);
        setError('Unable to load session details. Please try again.');
        toast({
          title: 'Error Loading Session',
          description: 'Unable to load session details. Please try again.',
          variant: 'destructive'
        });
      } finally {
        setLoading(false);
      }
    };

    fetchSession();
  }, [user, sessionId, toast]);

  // Format duration
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  // Download transcript as text file
  const downloadTranscript = () => {
    if (!session) return;

    // Format session metadata header
    const header = `======================================
COUNSELING SESSION TRANSCRIPT
======================================

Counselor Category: ${session.counselor_category}
Session Mode: ${session.mode === 'video' ? 'Video Call' : 'Voice Call'}
Date: ${format(new Date(session.started_at), 'PPPP')}
Time: ${format(new Date(session.started_at), 'p')}
Duration: ${formatDuration(session.duration_seconds)}
Session ID: ${session.session_id}

======================================
TRANSCRIPT
======================================

`;

    // Format transcript messages
    const transcript = session.transcript && session.transcript.length > 0
      ? session.transcript
          .map(msg => {
            const timestamp = format(new Date(msg.timestamp), 'h:mm:ss a');
            const speaker = msg.speaker === 'user' ? 'YOU' : 'COUNSELOR';
            return `[${timestamp}] ${speaker}:\n${msg.text}\n`;
          })
          .join('\n')
      : 'No transcript available for this session.\n';

    // Combine content
    const content = header + transcript;

    // Create blob
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });

    // Generate filename: Session_Category_Date.txt
    const dateStr = format(new Date(session.started_at), 'yyyy-MM-dd');
    const categorySlug = session.counselor_category.replace(/\s+/g, '_');
    const filename = `Session_${categorySlug}_${dateStr}.txt`;

    // Create download link
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';

    // Trigger download
    document.body.appendChild(link);
    link.click();

    // Cleanup
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    // Show success toast
    toast({
      title: 'Transcript Downloaded',
      description: `Saved as ${filename}`
    });
  };

  // Delete session function
  const deleteSession = async () => {
    if (!session) return;

    setDeleting(true);

    try {
      const response = await fetch(
        `/api/v1/sessions/${session.session_id}`,
        {
          method: 'DELETE',
          credentials: 'include'
        }
      );

      if (response.status === 403) {
        throw new Error('You do not have permission to delete this session.');
      }

      if (!response.ok) {
        throw new Error('Failed to delete session');
      }

      // Success
      toast({
        title: 'Session Deleted',
        description: 'Your session has been permanently deleted.'
      });

      // Redirect to session history
      router.push('/sessions');

    } catch (error) {
      console.error('Error deleting session:', error);
      
      setDeleting(false);
      setShowDeleteDialog(false);

      toast({
        title: 'Delete Failed',
        description: error instanceof Error ? error.message : 'Unable to delete session. Please try again.',
        variant: 'destructive',
        action: (
          <Button 
            variant='outline' 
            size='sm' 
            onClick={() => setShowDeleteDialog(true)}
          >
            Retry
          </Button>
        )
      });
    }
  };

  // Loading state
  if (authLoading || loading) {
    return (
      <div className='container mx-auto p-6 max-w-4xl'>
        <div className='flex items-center justify-center py-12'>
          <Loader2 className='h-8 w-8 animate-spin text-blue-600' />
        </div>
      </div>
    );
  }

  // Error state
  if (error || !session) {
    return (
      <div className='container mx-auto p-6 max-w-4xl'>
        <Button
          variant='ghost'
          onClick={() => router.push('/sessions')}
          className='mb-6'
        >
          <ArrowLeft className='mr-2 h-4 w-4' />
          Back to Sessions
        </Button>
        <Card className='text-center py-12'>
          <CardContent>
            <h2 className='text-xl font-semibold mb-2'>{error || 'Session Not Found'}</h2>
            <p className='text-gray-600 mb-6'>
              The session you&apos;re looking for doesn&apos;t exist or you don&apos;t have permission to view it.
            </p>
            <Button onClick={() => router.push('/sessions')}>
              Return to Session History
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className='container mx-auto p-6 max-w-4xl'>
      {/* Back Button */}
      <Button
        variant='ghost'
        onClick={() => router.push('/sessions')}
        className='mb-6'
      >
        <ArrowLeft className='mr-2 h-4 w-4' />
        Back to Sessions
      </Button>

      {/* Session Metadata Card */}
      <Card className='mb-6'>
        <CardHeader>
          <div className='flex items-center justify-between flex-wrap gap-4'>
            <div className='flex items-center gap-3'>
              {session.counselor_icon && (
                <span className='text-4xl' aria-label='Counselor category icon'>
                  {session.counselor_icon}
                </span>
              )}
              <div>
                <CardTitle>{session.counselor_category}</CardTitle>
                <CardDescription>
                  Session on {format(new Date(session.started_at), 'MMMM d, yyyy  h:mm a')}
                </CardDescription>
              </div>
            </div>
            {session.mode === 'video' ? (
              <Video className='h-6 w-6 text-purple-600' aria-label='Video session' />
            ) : (
              <Phone className='h-6 w-6 text-blue-600' aria-label='Voice session' />
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className='flex flex-wrap gap-6 text-sm'>
            <div className='flex items-center gap-2'>
              <Calendar className='h-4 w-4 text-gray-500' />
              <span className='text-gray-700'>
                {format(new Date(session.started_at), 'PPP')}
              </span>
            </div>
            <div className='flex items-center gap-2'>
              <Clock className='h-4 w-4 text-gray-500' />
              <span className='text-gray-700'>
                Duration: {formatDuration(session.duration_seconds)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Transcript */}
      <Card>
        <CardHeader>
          <CardTitle>Conversation Transcript</CardTitle>
          <CardDescription>
            Full recording of your counseling session
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className='space-y-4 max-h-[600px] overflow-y-auto pr-4'>
            {session.transcript && session.transcript.length > 0 ? (
              session.transcript.map((message, index) => (
                <TranscriptMessage
                  key={index}
                  message={message}
                  isUser={message.speaker === 'user'}
                />
              ))
            ) : (
              <p className='text-center text-gray-500 py-8'>
                No transcript available for this session.
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className='mt-6 flex flex-wrap gap-4'>
        <Button
          onClick={downloadTranscript}
          variant='outline'
          size='lg'
          aria-label='Download transcript as text file'
        >
          <Download className='mr-2 h-5 w-5' />
          Download Transcript
        </Button>

        {/* Delete Session Button with Confirmation */}
        <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
          <AlertDialogTrigger asChild>
            <Button
              variant='destructive'
              size='lg'
              disabled={deleting}
              aria-label='Delete this session'
            >
              <Trash2 className='mr-2 h-5 w-5' />
              {deleting ? 'Deleting...' : 'Delete Session'}
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Session?</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to delete this session? This action cannot be undone, and all conversation data will be permanently removed.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel disabled={deleting}>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={deleteSession}
                disabled={deleting}
                className='bg-red-600 hover:bg-red-700'
              >
                {deleting ? 'Deleting...' : 'Delete Session'}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
}

function TranscriptMessage({ message, isUser }: { message: TranscriptMessage; isUser: boolean }) {
  return (
    <div
      className={cn(
        'flex',
        isUser ? 'justify-start' : 'justify-end'
      )}
    >
      <div
        className={cn(
          'max-w-[75%] rounded-lg p-4 shadow-sm',
          isUser
            ? 'bg-blue-100 text-blue-900'
            : 'bg-gray-100 text-gray-900'
        )}
      >
        <div className='flex items-center gap-2 mb-1'>
          <span className='font-semibold text-sm'>
            {isUser ? 'You' : 'Counselor'}
          </span>
          <span className='text-xs text-gray-500'>
            {format(new Date(message.timestamp), 'h:mm a')}
          </span>
        </div>
        <p className='text-sm leading-relaxed whitespace-pre-wrap'>
          {message.text}
        </p>
      </div>
    </div>
  );
}
