import io from 'socket.io-client';

// Dynamic API URL for production support
// Fallback to hosted backend for production, localhost for local dev
const RAW_API_URL = process.env.REACT_APP_API_URL || 'https://stocksteward-ai-backend.onrender.com';
const HAS_VERSIONED_PATH = RAW_API_URL.includes('/api/v1');
const BASE_URL = RAW_API_URL.replace(/[\/?]+$/, '');
const API_PREFIX = HAS_VERSIONED_PATH ? '' : '/api/v1';
const SOCKET_URL = HAS_VERSIONED_PATH ? BASE_URL.replace(/\/api\/v1$/, '') : BASE_URL;

console.log("API Connection:", BASE_URL); // Debug log for deployment verification

const getAuthHeaders = () => {
    try {
        const raw = localStorage.getItem('stocksteward_user');
        if (!raw) return {};
        const user = JSON.parse(raw);
        if (!user?.id) return {};
        return {
            'X-User-Id': String(user.id),
            'X-User-Role': user.role || 'TRADER'
        };
    } catch (error) {
        return {};
    }
};

const getCurrentUserId = () => {
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
    transports: ['websocket'],
    autoConnect: true,
    reconnectionAttempts: 5
});

socket.on('connect', () => console.log("Socket connected:", socket.id));
socket.on('connect_error', (err) => console.error("Socket connection error:", err));

export const checkApiHealth = async () => {
    try {
        const response = await fetch(`${BASE_URL}/health`);
        const data = await response.json();
        console.log("API Health Status:", data);
        return data;
    } catch (error) {
        console.error("API Health Check FAILED:", error);
        return { status: "unreachable", error: error.message };
    }
};

export const fetchUsers = async () => {
    try {
        const headers = getAuthHeaders();
        if (!Object.keys(headers).length) {
            return [];
        }
        const response = await fetch(`${BASE_URL}${API_PREFIX}/users/`, {
            headers
        });
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
        if (!Object.keys(headers).length) {
            return null;
        }
        const response = await fetch(`${BASE_URL}${API_PREFIX}/users/${userId}`, {
            headers
        });
        if (!response.ok) throw new Error('Failed to fetch user');
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const updateUser = async (userId, data) => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/users/${userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
            body: JSON.stringify(data)
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
        const response = await fetch(`${BASE_URL}${API_PREFIX}/users/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Failed to create user');
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const fetchAllPortfolios = async () => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/portfolio/`);
        if (!response.ok) throw new Error('Failed to fetch portfolios');
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const fetchStrategies = async (userId = null) => {
    try {
        let url = `${BASE_URL}${API_PREFIX}/strategies/`;
        if (userId) {
            url += `?user_id=${userId}`;
        }
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch strategies');
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const fetchProjections = async () => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/projections/`);
        if (!response.ok) throw new Error('Failed to fetch projections');
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const fetchTrades = async (userId) => {
    try {
        const url = userId ? `${BASE_URL}${API_PREFIX}/trades/?user_id=${userId}` : `${BASE_URL}${API_PREFIX}/trades/`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch trades');
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const fetchPortfolioHistory = async (userId) => {
    try {
        const url = userId ? `${BASE_URL}${API_PREFIX}/portfolio/history?user_id=${userId}` : `${BASE_URL}${API_PREFIX}/portfolio/history`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch history');
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const fetchDailyPnL = async (userId) => {
    try {
        const url = userId ? `${BASE_URL}${API_PREFIX}/trades/daily-pnl?user_id=${userId}` : `${BASE_URL}${API_PREFIX}/trades/daily-pnl`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch daily pnl');
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const createAuditLog = async (logData) => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/audit/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(logData)
        });
        if (!response.ok) throw new Error('Failed to create audit log');
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const fetchPortfolioSummary = async (userId) => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/portfolio/?user_id=${userId}`);
        if (!response.ok) throw new Error('Failed to fetch summary');
        const data = await response.json();
        // Return first portfolio if multiple returned
        return Array.isArray(data) ? data[0] : data;
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const fetchHoldings = async (userId) => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/portfolio/holdings?user_id=${userId}`);
        if (!response.ok) throw new Error('Failed to fetch holdings');
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const fetchWatchlist = async (userId) => {
    try {
        const url = userId ? `${BASE_URL}${API_PREFIX}/watchlist/?user_id=${userId}` : `${BASE_URL}${API_PREFIX}/watchlist/`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch watchlist');
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const loginUser = async (email, password) => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/auth/login`.replace(/\?+$/, ''), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        if (!response.ok) throw new Error('Invalid credentials');
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const depositFunds = async (userId, amount) => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/portfolio/deposit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, amount })
        });
        if (!response.ok) throw new Error('Deposit failed');
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const launchStrategy = async (userId, strategyData) => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/strategies/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, ...strategyData })
        });
        if (!response.ok) throw new Error('Strategy launch failed');
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const fetchExchangeStatus = async () => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/market/status/`);
        if (!response.ok) throw new Error();
        return await response.json();
    } catch (error) {
        return { status: 'ONLINE', latency: '24ms', exchange: 'NSE/BSE/MCX' };
    }
};

export const executeTrade = async (userId, tradeData) => {
    try {
        const resolvedUserId = typeof userId === 'object' && userId !== null
            ? (userId.user_id || getCurrentUserId())
            : userId;
        const resolvedTrade = typeof userId === 'object' && userId !== null
            ? userId
            : tradeData;
        if (!resolvedTrade || !resolvedUserId) {
            throw new Error('Missing user id or trade data');
        }
        const response = await fetch(`${BASE_URL}${API_PREFIX}/trades/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: resolvedUserId,
                ...resolvedTrade,
                timestamp: new Date().toISOString()
            })
        });
        if (!response.ok) throw new Error('Trade execution failed');
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const addToWatchlist = async (userId, symbol) => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/watchlist/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, symbol, current_price: 0, change: '0.0%' })
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
        const response = await fetch(`${BASE_URL}${API_PREFIX}/watchlist/${symbol}?user_id=${userId}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to remove from watchlist');
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const fetchMarketMovers = async () => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/market/movers/`);
        if (!response.ok) throw new Error();
        return await response.json();
    } catch (error) {
        return [];
    }
};

export const fetchCurrencyMovers = async () => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/market/currencies`);
        if (!response.ok) throw new Error();
        return await response.json();
    } catch (error) {
        return { currencies: [] };
    }
};

export const fetchMetalsMovers = async () => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/market/metals`);
        if (!response.ok) throw new Error();
        return await response.json();
    } catch (error) {
        return { metals: [] };
    }
};

export const fetchCommodityMovers = async () => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/market/commodities`);
        if (!response.ok) throw new Error();
        return await response.json();
    } catch (error) {
        return { commodities: [] };
    }
};

export const withdrawFunds = async (userId, amount) => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/portfolio/withdraw`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, amount })
        });
        if (!response.ok) throw new Error('Withdraw failed');
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const fetchSectorHeatmap = async () => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/market/heatmap`);
        if (!response.ok) throw new Error();
        return await response.json();
    } catch (error) {
        return [];
    }
};

export const fetchMarketNews = async () => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/market/news`);
        if (!response.ok) throw new Error();
        return await response.json();
    } catch (error) {
        return [];
    }
};

export const fetchOptionsSnapshot = async () => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/market/options`);
        if (!response.ok) throw new Error();
        return await response.json();
    } catch (error) {
        return [];
    }
};

export const fetchOrderBookDepth = async () => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/market/depth`);
        if (!response.ok) throw new Error();
        return await response.json();
    } catch (error) {
        return { bids: [], asks: [] };
    }
};

export const fetchMacroIndicators = async () => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/market/macro`);
        if (!response.ok) throw new Error();
        return await response.json();
    } catch (error) {
        return null;
    }
};

export const fetchMarketResearch = async () => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/ai/market-research`);
        if (!response.ok) throw new Error('Failed to fetch market research');
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const submitKycApplication = async (payload) => {
    try {
        const response = await fetch(`${BASE_URL}${API_PREFIX}/kyc/applications`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
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
        const response = await fetch(`${BASE_URL}${API_PREFIX}/kyc/applications`, {
            headers: { ...getAuthHeaders() }
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
        const response = await fetch(`${BASE_URL}${API_PREFIX}/kyc/applications/${kycId}/review`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
            body: JSON.stringify({ status, review_notes })
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
        const response = await fetch(`${BASE_URL}${API_PREFIX}/kyc/applications/${kycId}/approve`, {
            method: 'POST',
            headers: { ...getAuthHeaders() }
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
        const response = await fetch(`${BASE_URL}${API_PREFIX}/kyc/applications/${kycId}/reject`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
            body: JSON.stringify({ status: 'REJECTED', review_notes })
        });
        if (!response.ok) throw new Error('Failed to reject KYC application');
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
};
