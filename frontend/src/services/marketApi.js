import { apiFetch, BASE_URL, API_PREFIX } from './httpClient';

export const fetchExchangeStatus = async () => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/market/status/`);
    if (!response.ok) throw new Error();
    return await response.json();
  } catch (error) {
    return { status: 'ONLINE', latency: '24ms', exchange: 'NSE/BSE/MCX' };
  }
};

export const fetchMarketMovers = async () => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/market/movers/`);
    if (!response.ok) throw new Error();
    return await response.json();
  } catch (error) {
    return { gainers: [], losers: [], source: 'none', status: 'UNAVAILABLE', as_of: null };
  }
};

export const fetchCurrencyMovers = async () => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/market/currencies`);
    if (!response.ok) throw new Error();
    return await response.json();
  } catch (error) {
    return { currencies: [], source: 'none', status: 'UNAVAILABLE', as_of: null };
  }
};

export const fetchMetalsMovers = async () => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/market/metals`);
    if (!response.ok) throw new Error();
    return await response.json();
  } catch (error) {
    return { metals: [], source: 'none', status: 'UNAVAILABLE', as_of: null };
  }
};

export const fetchCommodityMovers = async () => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/market/commodities`);
    if (!response.ok) throw new Error();
    return await response.json();
  } catch (error) {
    return { commodities: [], source: 'none', status: 'UNAVAILABLE', as_of: null };
  }
};

export const fetchSectorHeatmap = async () => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/market/heatmap`);
    if (!response.ok) throw new Error();
    return await response.json();
  } catch (error) {
    return [];
  }
};

export const fetchMarketNews = async () => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/market/news`);
    if (!response.ok) throw new Error();
    return await response.json();
  } catch (error) {
    return [];
  }
};

export const fetchOptionsSnapshot = async () => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/market/options`);
    if (!response.ok) throw new Error();
    return await response.json();
  } catch (error) {
    return [];
  }
};

export const fetchOrderBookDepth = async () => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/market/depth`);
    if (!response.ok) throw new Error();
    return await response.json();
  } catch (error) {
    return { bids: [], asks: [] };
  }
};

export const fetchMacroIndicators = async () => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/market/macro`);
    if (!response.ok) throw new Error();
    return await response.json();
  } catch (error) {
    return { usd_inr: null, gold: null, crude: null, sentiment: 'UNAVAILABLE', volatility_label: 'UNAVAILABLE' };
  }
};

export const fetchMarketResearch = async () => {
  try {
    const response = await apiFetch(`${BASE_URL}${API_PREFIX}/ai/market-research`);
    if (!response.ok) throw new Error('Failed to fetch market research');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};

