'use client';

import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { DashboardFooter } from '@/components/dashboard/DashboardFooter';
import { CounselorCardGrid } from '@/components/dashboard/CounselorCardGrid';

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <a 
        href="#main-content" 
        className="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 focus:z-50 focus:p-4 focus:bg-blue-600 focus:text-white focus:outline-none"
      >
        Skip to main content
      </a>
      
      <div className="min-h-screen flex flex-col">
        <DashboardHeader />
        
        <main 
          id="main-content"
          className="flex-1 container mx-auto px-4 py-8" 
          role="main"
          aria-label="Counselor categories"
        >
          <CounselorCardGrid />
        </main>
        
        <DashboardFooter />
      </div>
    </ProtectedRoute>
  );
}
