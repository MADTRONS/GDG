'use client';

import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { DashboardFooter } from '@/components/dashboard/DashboardFooter';

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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {/* Counselor cards will be added in Story 2.3 */}
          </div>
        </main>
        
        <DashboardFooter />
      </div>
    </ProtectedRoute>
  );
}
