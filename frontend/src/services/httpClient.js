import io from 'socket.io-client';

const RAW_API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const HAS_VERSIONED_PATH = RAW_API_URL.includes('/api/v1');

export const BASE_URL = RAW_API_URL.replace(/[\/?]+$/, '');
export const API_PREFIX = HAS_VERSIONED_PATH ? '' : '/api/v1';
export const SOCKET_URL = HAS_VERSIONED_PATH ? BASE_URL.replace(/\/api\/v1$/, '') : BASE_URL;
export const REQUEST_TIMEOUT_MS = Number(process.env.REACT_APP_API_TIMEOUT_MS || 12000);
const REQUEST_RETRY_COUNT = Number(process.env.REACT_APP_API_RETRY_COUNT || 1);

console.log('API Connection:', BASE_URL);

export const getAuthHeaders = () => {
  try {
    const raw = localStorage.getItem('stocksteward_user');
    if (!raw) return {};
    const user = JSON.parse(raw);
    const headers = {};
    if (user?.id) {
      headers['X-User-Id'] = String(user.id);
      headers['X-User-Role'] = user.role || 'TRADER';
    }
    if (user?.access_token) {
      headers.Authorization = `Bearer ${user.access_token}`;
    }
    if (!Object.keys(headers).length) return {};
    return headers;
  } catch (error) {
    return {};
  }
};

export const getCurrentUserId = () => {
  try {
    const raw = localStorage.getItem('stocksteward_user');
    if (!raw) return null;
    const user = JSON.parse(raw);
    return user?.id || null;
  } catch (error) {
    return null;
  }
};

export const socket = io(SOCKET_URL, {
  transports: ['websocket', 'polling'],
  autoConnect: true,
  reconnectionAttempts: 5,
});

socket.on('connect', () => console.log('Socket connected:', socket.id));
socket.on('connect_error', (err) => console.error('Socket connection error:', err));

export const apiFetch = async (url, options = {}, timeoutMs = REQUEST_TIMEOUT_MS) => {
  let lastError = null;
  const method = String(options.method || 'GET').toUpperCase();
  const canRetry = method === 'GET' || method === 'HEAD';

  for (let attempt = 0; attempt <= REQUEST_RETRY_COUNT; attempt += 1) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    const authHeaders = getAuthHeaders();
    const mergedOptions = {
      ...options,
      headers: {
        ...authHeaders,
        ...options.headers,
      },
      signal: controller.signal,
    };

    try {
      const response = await fetch(url, mergedOptions);
      if (!canRetry || attempt === REQUEST_RETRY_COUNT || response.status < 500) {
        return response;
      }
      lastError = new Error(`Retryable server status: ${response.status}`);
    } catch (error) {
      lastError = error;
      if (!canRetry || attempt === REQUEST_RETRY_COUNT) {
        throw error;
      }
    } finally {
      clearTimeout(timeoutId);
    }
  }
  throw lastError || new Error('Request failed');
};
