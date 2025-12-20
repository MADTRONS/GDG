'use client';

import { useAuth } from '@/components/auth/AuthProvider';
import { Button } from '@/components/ui/button';
import { LogOut } from 'lucide-react';

export function DashboardHeader() {
  const { user, logout } = useAuth();
  
  // Extract just the username part from \domain\username format
  const displayName = user?.username.split('\\').pop() || 'Student';
  
  return (
    <header className="border-b bg-white" role="banner">
      <div className="container mx-auto px-4 py-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          {/* Logo and Welcome */}
          <div className="flex items-center gap-4">
            <div className="text-2xl font-bold text-blue-600">
              College Counseling
            </div>
            <div className="hidden sm:block text-gray-600">
              Welcome, {displayName}!
            </div>
          </div>
          
          {/* Mobile Welcome */}
          <div className="sm:hidden text-gray-600">
            Welcome, {displayName}!
          </div>
          
          {/* Logout Button */}
          <Button
            onClick={logout}
            variant="outline"
            className="gap-2"
            aria-label="Logout"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </Button>
        </div>
      </div>
    </header>
  );
}
