import axios from 'axios';
import { env } from './env';

export const apiClient = axios.create({
  baseURL: env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const api = {
  auth: {
    googleLogin: (code: string) =>
      apiClient.post('/auth/google/callback', { code }),
  },
  stripe: {
    createCheckoutSession: (priceId: string) =>
      apiClient.post('/stripe/create-checkout-session', { priceId }),
    verifySession: (sessionId: string) =>
      apiClient.post('/stripe/verify-session', { sessionId }),
  },
  streams: {
    list: () => apiClient.get('/streams'),
    create: (data: any) => apiClient.post('/streams', data),
    get: (id: string) => apiClient.get(`/streams/${id}`),
    update: (id: string, data: any) => apiClient.put(`/streams/${id}`, data),
    delete: (id: string) => apiClient.delete(`/streams/${id}`),
  },
};
