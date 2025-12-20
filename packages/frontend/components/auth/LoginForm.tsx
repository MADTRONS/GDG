'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { loginSchema, type LoginFormData } from '@/lib/schemas';
import { loginUser } from '@/lib/api';

export function LoginForm() {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    mode: 'onBlur',
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      await loginUser(data);
      router.push('/dashboard');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md space-y-8 rounded-lg bg-white p-8 shadow-lg">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Welcome Back</h1>
        <p className="mt-2 text-sm text-gray-600">
          Sign in to access counseling services
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-6">
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="username">Username</Label>
            <Input
              id="username"
              type="text"
              autoFocus
              aria-label="Username"
              aria-describedby={errors.username ? 'username-error' : undefined}
              placeholder="\domain\username"
              disabled={isLoading}
              {...register('username')}
            />
            {errors.username && (
              <p
                id="username-error"
                className="text-sm text-red-600"
                role="alert"
              >
                {errors.username.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              aria-label="Password"
              aria-describedby={errors.password ? 'password-error' : undefined}
              placeholder="Enter your password"
              disabled={isLoading}
              {...register('password')}
            />
            {errors.password && (
              <p
                id="password-error"
                className="text-sm text-red-600"
                role="alert"
              >
                {errors.password.message}
              </p>
            )}
          </div>
        </div>

        {error && (
          <div
            className="rounded-md bg-red-50 border border-red-200 p-3"
            role="alert"
          >
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <Button
          type="submit"
          className="w-full"
          disabled={isLoading}
          aria-label={isLoading ? 'Logging in...' : 'Login'}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" role="status" />
              Logging in...
            </>
          ) : (
            'Login'
          )}
        </Button>
      </form>
    </div>
  );
}
