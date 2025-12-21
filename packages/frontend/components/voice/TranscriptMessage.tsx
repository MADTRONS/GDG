import { format } from 'date-fns';
import { TranscriptEntry } from '@/types/transcript';
import { cn } from '@/lib/utils';

interface TranscriptMessageProps {
  entry: TranscriptEntry;
}

export function TranscriptMessage({ entry }: TranscriptMessageProps) {
  const isUser = entry.speaker === 'user';

  return (
    <div
      className={cn(
        'flex flex-col gap-1 p-3 rounded-lg',
        isUser ? 'bg-primary/10 ml-8' : 'bg-muted mr-8'
      )}
      data-testid={`transcript-message-${entry.speaker}`}
    >
      <div className="flex items-center gap-2 text-sm font-medium">
        <span className={cn(isUser ? 'text-primary' : 'text-foreground')}>
          {isUser ? 'You' : 'Counselor'}
        </span>
        <span className="text-xs text-muted-foreground">
          {format(entry.timestamp, 'h:mm a')}
        </span>
      </div>
      <p className="text-base leading-relaxed">
        {entry.text}
      </p>
    </div>
  );
}
