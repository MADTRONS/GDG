'use client';

import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Mic, Video, Loader2 } from 'lucide-react';
import { getIcon } from '@/lib/icons';
import { CounselorCategory } from '@/lib/api';

interface CounselorCardProps {
  category: CounselorCategory;
  onVoiceCall: (category: CounselorCategory) => void;
  onVideoCall: (category: CounselorCategory) => void;
  isVoiceLoading?: boolean;
  isVideoLoading?: boolean;
}

export function CounselorCard({ 
  category, 
  onVoiceCall, 
  onVideoCall,
  isVoiceLoading = false,
  isVideoLoading = false
}: CounselorCardProps) {
  const Icon = getIcon(category.icon_name);
  
  return (
    <Card className="group hover:shadow-lg hover:border-blue-300 transition-all duration-200 h-full flex flex-col">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="p-3 bg-blue-50 rounded-lg group-hover:bg-blue-100 transition-colors">
            <Icon className="h-6 w-6 text-blue-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900">
            {category.name}
          </h3>
        </div>
      </CardHeader>
      
      <CardContent className="flex-1">
        <p className="text-gray-600 text-sm leading-relaxed">
          {category.description}
        </p>
      </CardContent>
      
      <CardFooter className="flex gap-2 pt-4">
        <Button
          onClick={() => onVoiceCall(category)}
          disabled={isVoiceLoading}
          className="flex-1 gap-2 bg-blue-600 hover:bg-blue-700"
          aria-label={`Start voice call with ${category.name} counselor`}
        >
          {isVoiceLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Mic className="h-4 w-4" />
          )}
          Voice Call
        </Button>
        <Button
          onClick={() => onVideoCall(category)}
          disabled={isVideoLoading}
          variant="outline"
          className="flex-1 gap-2 border-blue-600 text-blue-600 hover:bg-blue-50"
          aria-label={`Start video call with ${category.name} counselor`}
        >
          {isVideoLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Video className="h-4 w-4" />
          )}
          Video Call
        </Button>
      </CardFooter>
    </Card>
  );
}
