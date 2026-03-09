import { apiFetch, BASE_URL, API_PREFIX, getAuthHeaders } from './httpClient';

export const fetchUsers = async () => {
  try {
    const headers = getAuthHeaders();
    if (!Object.keys(headers).length) return [];
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/users/`, { headers });
    if (!response.ok) throw new Error('Failed to fetch users');
    return await response.json();
  } catch (error) {
    console.error(error);
    return [];
  }
};

export const fetchUser = async (userId) => {
  try {
    const headers = getAuthHeaders();
    if (!Object.keys(headers).length) return null;
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/users/${userId}`, { headers });
    if (!response.ok) throw new Error('Failed to fetch user');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

export const updateUser = async (userId, data) => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/users/${userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update user');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

export const createUser = async (data) => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/users/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create user');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

export const createAuditLog = async (logData) => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/audit/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(logData),
    });
    if (!response.ok) throw new Error('Failed to create audit log');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

export const fetchMetricsSummary = async () => {
  try {
    const headers = getAuthHeaders();
    if (!Object.keys(headers).length) return null;
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/logs/metrics/summary`, { headers });
    if (!response.ok) throw new Error('Failed to fetch metrics summary');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

export const fetchSupersetEmbedUrl = async () => {
  try {
    const headers = getAuthHeaders();
    if (!Object.keys(headers).length) return null;
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/admin/observability/embed-url`, { headers });
    if (!response.ok) throw new Error('Failed to fetch superset embed url');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

