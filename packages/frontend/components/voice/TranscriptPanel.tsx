import { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowDown } from 'lucide-react';
import { TranscriptMessage } from './TranscriptMessage';
import { TranscriptEntry } from '@/types/transcript';

interface TranscriptPanelProps {
  entries: TranscriptEntry[];
}

export function TranscriptPanel({ entries }: TranscriptPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [showScrollButton, setShowScrollButton] = useState(false);

  // Auto-scroll to bottom when new entries added
  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [entries, autoScroll]);

  // Detect user scroll
  const handleScroll = () => {
    if (!scrollRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;

    setAutoScroll(isAtBottom);
    setShowScrollButton(!isAtBottom);
  };

  // Scroll to bottom manually
  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
      setAutoScroll(true);
      setShowScrollButton(false);
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">Conversation Transcript</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 relative p-0">
        <div
          ref={scrollRef}
          onScroll={handleScroll}
          className="h-full overflow-y-auto px-4 pb-4 space-y-3"
          aria-live="polite"
          aria-label="Conversation transcript"
          data-testid="transcript-container"
        >
          {entries.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <p>Transcript will appear here as you speak...</p>
            </div>
          ) : (
            entries.map(entry => (
              <TranscriptMessage key={entry.id} entry={entry} />
            ))
          )}
        </div>

        {/* Scroll to bottom button */}
        {showScrollButton && (
          <Button
            onClick={scrollToBottom}
            size="icon"
            variant="secondary"
            className="absolute bottom-4 right-4 rounded-full shadow-lg"
            aria-label="Scroll to latest message"
            data-testid="scroll-to-bottom-button"
          >
            <ArrowDown className="h-4 w-4" />
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
