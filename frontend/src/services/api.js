import { apiFetch, BASE_URL, API_PREFIX, getAuthHeaders, socket } from './httpClient';

export { socket };
export { loginUser } from './authApi';
export { fetchTrades, fetchDailyPnL, executeTrade } from './tradesApi';
export {
  fetchAllPortfolios,
  fetchPortfolioHistory,
  fetchPortfolioSummary,
  fetchHoldings,
  depositFunds,
  withdrawFunds,
} from './portfolioApi';
export {
  fetchUsers,
  fetchUser,
  updateUser,
  createUser,
  createAuditLog,
  fetchMetricsSummary,
  fetchSupersetEmbedUrl,
} from './adminApi';
export {
  fetchExchangeStatus,
  fetchMarketMovers,
  fetchCurrencyMovers,
  fetchMetalsMovers,
  fetchCommodityMovers,
  fetchSectorHeatmap,
  fetchMarketNews,
  fetchOptionsSnapshot,
  fetchOrderBookDepth,
  fetchMacroIndicators,
  fetchMarketResearch,
} from './marketApi';

export const checkApiHealth = async () => {
  try {
    const response = await apiFetch(`${BASE_URL}/health`);
    const data = await response.json();
    console.log('API Health Status:', data);
    return data;
  } catch (error) {
    console.error('API Health Check FAILED:', error);
    return { status: 'unreachable', error: error.message };
  }
};

export const fetchStrategies = async (userId = null) => {
  try {
    let url = `${BASE_URL}${API_PREFIX}/strategies/`;
    if (userId) {
      url += `?user_id=${userId}`;
    }
    const response = await apiFetch(url);
    if (!response.ok) throw new Error('Failed to fetch strategies');
    return await response.json();
  } catch (error) {
    console.error(error);
    return [];
  }
};

export const fetchProjections = async () => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/projections/`);
    if (!response.ok) throw new Error('Failed to fetch projections');
    return await response.json();
  } catch (error) {
    console.error(error);
    return [];
  }
};

export const fetchWatchlist = async (userId) => {
  try {
    const url = userId ? `${BASE_URL}${API_PREFIX}/watchlist/?user_id=${userId}` : `${BASE_URL}${API_PREFIX}/watchlist/`;
    const response = await apiFetch(url);
    if (!response.ok) throw new Error('Failed to fetch watchlist');
    return await response.json();
  } catch (error) {
    console.error(error);
    return [];
  }
};

export const launchStrategy = async (userId, strategyData) => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/strategies/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, ...strategyData }),
    });
    if (!response.ok) throw new Error('Strategy launch failed');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

export const addToWatchlist = async (userId, symbol) => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/watchlist/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, symbol, current_price: 0, change: '0.0%' }),
    });
    if (!response.ok) throw new Error('Failed to add to watchlist');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

export const removeFromWatchlist = async (userId, symbol) => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/watchlist/${symbol}?user_id=${userId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to remove from watchlist');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

export const submitKycApplication = async (payload) => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/kyc/applications`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error('Failed to submit KYC');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

export const fetchKycApplications = async () => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/kyc/applications`, {
      headers: { ...getAuthHeaders() },
    });
    if (!response.ok) throw new Error('Failed to fetch KYC applications');
    return await response.json();
  } catch (error) {
    console.error(error);
    return [];
  }
};

export const reviewKycApplication = async (kycId, status, review_notes) => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/kyc/applications/${kycId}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ status, review_notes }),
    });
    if (!response.ok) throw new Error('Failed to review KYC application');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

export const approveKycApplication = async (kycId) => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/kyc/applications/${kycId}/approve`, {
      method: 'POST',
      headers: { ...getAuthHeaders() },
    });
    if (!response.ok) throw new Error('Failed to approve KYC application');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

export const rejectKycApplication = async (kycId, review_notes) => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/kyc/applications/${kycId}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ status: 'REJECTED', review_notes }),
    });
    if (!response.ok) throw new Error('Failed to reject KYC application');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

