/**
 * Crisis Alert Banner Component
 * 
 * Displays a prominent alert with emergency resources when crisis keywords
 * are detected in the conversation.
 */

'use client';

import { useState } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { AlertTriangle, X, Phone, ExternalLink } from 'lucide-react';

interface CrisisAlertProps {
  onDismiss: () => void;
}

export function CrisisAlert({ onDismiss }: CrisisAlertProps) {
  const [showConfirmDismiss, setShowConfirmDismiss] = useState(false);

  const handleCall988 = () => {
    // Track analytics event
    console.log('[Crisis Alert] User clicked Call 988');
    
    // Mobile: initiate phone call
    // Desktop: open 988 website
    if (typeof window !== 'undefined') {
      if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
        window.location.href = 'tel:988';
      } else {
        window.open('https://988lifeline.org/', '_blank', 'noopener,noreferrer');
      }
    }
  };

  const handleChatOnline = () => {
    console.log('[Crisis Alert] User clicked Chat Online');
    if (typeof window !== 'undefined') {
      window.open('https://988lifeline.org/chat/', '_blank', 'noopener,noreferrer');
    }
  };

  const handleDismiss = () => {
    if (!showConfirmDismiss) {
      setShowConfirmDismiss(true);
      return;
    }
    
    console.log('[Crisis Alert] Alert dismissed by user');
    onDismiss();
  };

  return (
    <Alert 
      className="fixed top-0 left-0 right-0 z-50 rounded-none border-0 bg-red-600 text-white shadow-lg"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div className="container mx-auto flex items-start gap-4 py-4 px-4">
        <AlertTriangle 
          className="h-6 w-6 flex-shrink-0 mt-0.5" 
          aria-hidden="true" 
        />
        
        <div className="flex-1 space-y-2">
          <AlertTitle className="text-lg font-bold text-white">
            Crisis Support Available
          </AlertTitle>
          <AlertDescription className="text-white/90">
            If you're experiencing thoughts of suicide or self-harm, help is available 24/7.
            You are not alone, and there are people who care and want to help.
          </AlertDescription>
          
          <div className="flex flex-wrap gap-2 mt-3">
            <Button
              onClick={handleCall988}
              size="sm"
              variant="secondary"
              className="bg-white text-red-600 hover:bg-white/90 font-bold"
              aria-label="Call 988 Suicide and Crisis Lifeline"
            >
              <Phone className="mr-2 h-4 w-4" aria-hidden="true" />
              Call 988 (Suicide & Crisis Lifeline)
            </Button>
            
            <Button
              onClick={handleChatOnline}
              size="sm"
              variant="outline"
              className="border-white text-white hover:bg-white/10"
              aria-label="Chat online with crisis counselor"
            >
              <ExternalLink className="mr-2 h-4 w-4" aria-hidden="true" />
              Chat Online
            </Button>
          </div>
          
          <p className="text-sm text-white/80 mt-2">
            Campus Counseling Center: Available during business hours • Emergency: 911
          </p>
        </div>
        
        <Button
          onClick={handleDismiss}
          size="icon"
          variant="ghost"
          className="text-white hover:bg-white/10 flex-shrink-0"
          aria-label="Dismiss alert"
        >
          <X className="h-5 w-5" />
        </Button>
      </div>
      
      {showConfirmDismiss && (
        <div className="container mx-auto mt-2 pb-4 px-4 text-sm border-t border-white/20 pt-3">
          <p className="text-white/90">
            Are you sure you want to dismiss this? The resources will still be available if you need them.
          </p>
          <Button
            onClick={handleDismiss}
            size="sm"
            variant="ghost"
            className="mt-2 text-white hover:bg-white/10 underline"
          >
            Yes, dismiss alert
          </Button>
        </div>
      )}
    </Alert>
  );
}
