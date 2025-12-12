'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { authenticateMagicLink } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (status !== 'loading') {
      return;
    }

    const token = searchParams.get('token') || searchParams.get('stytch_token');
    const tokenType = searchParams.get('stytch_token_type');
    
    if (!token) {
      setStatus('error');
      setError('No authentication token provided in URL');
      return;
    }

    const handleAuth = async () => {
      try {
        const response = await authenticateMagicLink(token);
        login(response.user, response.session_token);
        setStatus('success');
        
        setTimeout(() => {
          router.push('/');
        }, 2000);
      } catch (err) {
        setStatus('error');
        const errorMessage = err instanceof Error ? err.message : 'Authentication failed';
        setError(errorMessage);
      }
    };

    const timeoutId = setTimeout(() => {
      handleAuth();
    }, 100);

    return () => clearTimeout(timeoutId);
  }, [searchParams, login, router, status]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-lg shadow-xl p-8 text-center">
          {status === 'loading' && (
            <div className="space-y-4">
              <div className="flex justify-center">
                <svg
                  className="animate-spin h-12 w-12 text-indigo-600"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Authenticating...</h2>
              <p className="text-sm text-gray-600">Please wait while we sign you in</p>
            </div>
          )}

          {status === 'success' && (
            <div className="space-y-4">
              <div className="flex justify-center">
                <svg
                  className="h-12 w-12 text-green-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Success!</h2>
              <p className="text-sm text-gray-600">You've been signed in successfully</p>
              <p className="text-xs text-gray-500">Redirecting to home page...</p>
            </div>
          )}

          {status === 'error' && (
            <div className="space-y-4">
              <div className="flex justify-center">
                <svg
                  className="h-12 w-12 text-red-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Authentication Failed</h2>
              <p className="text-sm text-red-600">{error}</p>
              <div className="pt-4">
                <Link
                  href="/login"
                  className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  Try again
                </Link>
              </div>
              <div className="pt-2">
                <Link
                  href="/"
                  className="text-sm text-indigo-600 hover:text-indigo-500"
                >
                  ← Back to home
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

