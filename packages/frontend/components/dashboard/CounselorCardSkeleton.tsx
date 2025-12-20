import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';

export function CounselorCardSkeleton() {
  return (
    <Card className="h-full flex flex-col" data-testid="skeleton-card">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="h-12 w-12 bg-gray-200 rounded-lg animate-pulse" />
          <div className="h-6 w-32 bg-gray-200 rounded animate-pulse" />
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 space-y-2">
        <div className="h-4 bg-gray-200 rounded animate-pulse" />
        <div className="h-4 bg-gray-200 rounded animate-pulse w-5/6" />
        <div className="h-4 bg-gray-200 rounded animate-pulse w-4/6" />
      </CardContent>
      
      <CardFooter className="flex gap-2 pt-4">
        <div className="flex-1 h-10 bg-gray-200 rounded animate-pulse" />
        <div className="flex-1 h-10 bg-gray-200 rounded animate-pulse" />
      </CardFooter>
    </Card>
  );
}
