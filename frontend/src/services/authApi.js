import { apiFetch, BASE_URL, API_PREFIX } from './httpClient';

export const loginUser = async (email, password) => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/auth/login`.replace(/\?+$/, ''), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) throw new Error('Invalid credentials');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

