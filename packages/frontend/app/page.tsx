'use client';

import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { LoginForm } from "@/components/auth/LoginForm";
import { useToast } from "@/components/ui/use-toast";

export default function Home() {
  const searchParams = useSearchParams();
  const { toast } = useToast();
  
  useEffect(() => {
    // Check if user was just logged out
    if (searchParams.get('logout') === 'true') {
      toast({
        title: "Logged Out",
        description: "You have been logged out.",
        duration: 3000,
      });
      
      // Clear the URL parameter
      window.history.replaceState({}, '', '/');
    }
  }, [searchParams, toast]);
  
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 bg-gradient-to-b from-slate-50 to-slate-100">
      <LoginForm />
    </main>
  );
}
