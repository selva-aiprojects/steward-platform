import { apiFetch, BASE_URL, API_PREFIX, getCurrentUserId } from './httpClient';

export const fetchTrades = async (userId) => {
  try {
    const url = userId ? `${BASE_URL}${API_PREFIX}/trades/?user_id=${userId}` : `${BASE_URL}${API_PREFIX}/trades/`;
    const response = await apiFetch(url);
    if (!response.ok) throw new Error('Failed to fetch trades');
    return await response.json();
  } catch (error) {
    console.error(error);
    return [];
  }
};

export const fetchDailyPnL = async (userId) => {
  try {
    const url = userId ? `${BASE_URL}${API_PREFIX}/trades/daily-pnl?user_id=${userId}` : `${BASE_URL}${API_PREFIX}/trades/daily-pnl`;
    const response = await apiFetch(url);
    if (!response.ok) throw new Error('Failed to fetch daily pnl');
    return await response.json();
  } catch (error) {
    console.error(error);
    return [];
  }
};

export const executeTrade = async (userId, tradeData) => {
  try {
    const resolvedUserId = typeof userId === 'object' && userId !== null ? (userId.user_id || getCurrentUserId()) : userId;
    const resolvedTrade = typeof userId === 'object' && userId !== null ? userId : tradeData;

    if (!resolvedTrade || !resolvedUserId) {
      throw new Error('Missing user id or trade data');
    }

    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/trades/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: resolvedUserId,
        ...resolvedTrade,
        timestamp: new Date().toISOString(),
      }),
    });
    if (!response.ok) throw new Error('Trade execution failed');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

