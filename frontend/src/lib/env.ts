export const env = {
  VITE_API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  VITE_STRIPE_PUBLIC_KEY: import.meta.env.VITE_STRIPE_PUBLIC_KEY || '',
  VITE_GOOGLE_CLIENT_ID: import.meta.env.VITE_GOOGLE_CLIENT_ID || '',
  VITE_WS_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
  VITE_PUBLIC_URL: import.meta.env.VITE_PUBLIC_URL || 'http://localhost:5173',
} as const;

export type Env = typeof env;
