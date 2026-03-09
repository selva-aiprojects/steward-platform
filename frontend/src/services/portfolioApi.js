import { apiFetch, BASE_URL, API_PREFIX } from './httpClient';

export const fetchAllPortfolios = async () => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/portfolio/`);
    if (!response.ok) throw new Error('Failed to fetch portfolios');
    return await response.json();
  } catch (error) {
    console.error(error);
    return [];
  }
};

export const fetchPortfolioHistory = async (userId) => {
  try {
    const url = userId ? `${BASE_URL}${API_PREFIX}/portfolio/history?user_id=${userId}` : `${BASE_URL}${API_PREFIX}/portfolio/history`;
    const response = await apiFetch(url);
    if (!response.ok) throw new Error('Failed to fetch history');
    return await response.json();
  } catch (error) {
    console.error(error);
    return [];
  }
};

export const fetchPortfolioSummary = async (userId) => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/portfolio/?user_id=${userId}`);
    if (!response.ok) throw new Error('Failed to fetch summary');
    const data = await response.json();
    return Array.isArray(data) ? data[0] : data;
  } catch (error) {
    console.error(error);
    return null;
  }
};

export const fetchHoldings = async (userId) => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/portfolio/holdings?user_id=${userId}`);
    if (!response.ok) throw new Error('Failed to fetch holdings');
    return await response.json();
  } catch (error) {
    console.error(error);
    return [];
  }
};

export const depositFunds = async (userId, amount) => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/portfolio/deposit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, amount }),
    });
    if (!response.ok) throw new Error('Deposit failed');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

export const withdrawFunds = async (userId, amount) => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/portfolio/withdraw`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, amount }),
    });
    if (!response.ok) throw new Error('Withdraw failed');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

