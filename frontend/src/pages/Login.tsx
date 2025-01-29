import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from "@/components/ui/button"
// Removed unused import
import { apiClient } from '@/lib/api-client';

export function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Check for auth callback
    const searchParams = new URLSearchParams(location.search);
    const token = searchParams.get('token');
    const error = searchParams.get('error');
    const errorMessage = searchParams.get('message');
    
    if (error) {
      const message = errorMessage ? decodeURIComponent(errorMessage) : 'Authentication failed';
      setError(message);
      // Remove error from URL
      window.history.replaceState({}, '', window.location.pathname);
      setIsLoading(false);
      return;
    }
    
    if (token) {
      setIsLoading(true);
      try {
        // Handle auth callback through api client
        apiClient.handleAuthCallback(token)
          .catch((error) => {
            console.error('Error handling authentication:', error);
            setError('Failed to complete authentication. Please try again.');
            setIsLoading(false);
          });
      } catch (error) {
        console.error('Error processing authentication:', error);
        setError('Failed to process authentication. Please try again.');
        setIsLoading(false);
      }
    }
  }, [location]);

  const handleGoogleLogin = async () => {
    try {
      setError(null);
      setIsLoading(true);
      
      // Store the current URL to redirect back after login
      const returnTo = location.pathname === '/login' ? '/studio' : location.pathname;
      sessionStorage.setItem('returnTo', returnTo);
      
      // Generate state for CSRF protection
      const state = Math.random().toString(36).substring(7);
      sessionStorage.setItem('oauth_state', state);
      
      // This will handle the redirect internally
      await apiClient.loginWithGoogle();
    } catch (error: any) {
      console.error('Failed to initiate Google login:', error);
      setError(error.message || 'Failed to initiate login. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-lg">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in or Register for Spreadify A
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Start streaming to multiple platforms
          </p>
        </div>
        {error && (
          <div className="mt-2 p-4 bg-red-50 border border-red-200 rounded-lg shadow-sm">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-semibold text-red-800">Unable to Sign In</h3>
                <p className="mt-1 text-sm text-red-600">{error}</p>
                <div className="mt-2 text-sm text-red-600">
                  <p>Please try:</p>
                  <ul className="list-disc ml-4 mt-1 space-y-1">
                    <li>Ensuring you have a verified email address</li>
                    <li>Clearing your browser cache and cookies</li>
                    <li>Using a different browser</li>
                  </ul>
                  <p className="mt-2">
                    If the problem persists, please{' '}
                    <a href="mailto:support@spreadify.app" className="text-red-700 hover:text-red-800 underline">
                      contact support
                    </a>
                    .
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
        <div className="mt-8 space-y-6">
          <Button
            className="w-full flex justify-center py-2 px-4 bg-white hover:bg-gray-50 text-gray-900 border border-gray-300 shadow-sm"
            onClick={handleGoogleLogin}
            disabled={isLoading}
          >
            {isLoading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-700 mr-2"></div>
                <span className="text-gray-700">Signing in...</span>
              </div>
            ) : (
              <div className="flex items-center justify-center">
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                <span className="text-gray-700 font-medium">Sign in with Google</span>
              </div>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
