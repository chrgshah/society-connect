import axios from 'axios';

const defaultApiBaseUrl = `${window.location.protocol}//${window.location.hostname}:8000/api/v1`;

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || defaultApiBaseUrl,
  timeout: 10000,
  withCredentials: true,
  withXSRFToken: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
});

let refreshRequest: Promise<void> | null = null;

const refreshSession = async () => {
  if (!refreshRequest) {
    refreshRequest = apiClient
      .post('/auth/refresh/', {})
      .then(() => undefined)
      .finally(() => {
        refreshRequest = null;
      });
  }
  return refreshRequest;
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const isAuthRequest =
      originalRequest?.url?.includes('/auth/login/') ||
      originalRequest?.url?.includes('/auth/refresh/');

    if (error.response?.status === 401 && !originalRequest?._retry && !isAuthRequest) {
      originalRequest._retry = true;
      try {
        await refreshSession();
        return apiClient(originalRequest);
      } catch {
        window.dispatchEvent(new Event('auth:expired'));
      }
    }
    return Promise.reject(error);
  },
);

export default apiClient;
