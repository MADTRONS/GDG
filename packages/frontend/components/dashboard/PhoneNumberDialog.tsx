'use client';

import { useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Phone } from 'lucide-react';

interface PhoneNumberDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  counselorName: string;
  onSubmit: (phoneNumber: string) => Promise<void>;
}

export function PhoneNumberDialog({
  open,
  onOpenChange,
  counselorName,
  onSubmit,
}: PhoneNumberDialogProps) {
  
  useEffect(() => {
    // Listen for messages from the iframe (form submission)
    const handleMessage = (event: MessageEvent) => {
      // Only accept messages from the form origin
      if (event.origin !== 'http://localhost:5678') {
        return;
      }
      
      // Handle form submission success
      if (event.data.type === 'form-submitted' && event.data.phoneNumber) {
        onSubmit(event.data.phoneNumber);
        onOpenChange(false);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [onSubmit, onOpenChange]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Phone className="h-5 w-5 text-blue-600" />
            Voice Call Setup
          </DialogTitle>
          <DialogDescription>
            Enter your phone number to receive a call from your {counselorName} counselor.
            You'll be connected immediately.
          </DialogDescription>
        </DialogHeader>

        <div className="w-full h-[500px] overflow-hidden rounded-lg border">
          <iframe
            src="http://localhost:5678/form/0751fa66-da39-4b7a-8d29-c0b9e8d4f722"
            className="w-full h-full border-0"
            title="Phone Number Form"
            allow="microphone"
            sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}
