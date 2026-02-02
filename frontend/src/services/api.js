import io from 'socket.io-client';

// Dynamic API URL for production support
// Fallback to localhost for development
const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

console.log("API Connection:", BASE_URL); // Debug log for deployment verification

export const socket = io(BASE_URL, {
    transports: ['websocket'],
    autoConnect: true,
    reconnectionAttempts: 5
});

export const fetchUsers = async () => {
    try {
        const response = await fetch(`${BASE_URL}/users/`);
        if (!response.ok) throw new Error('Failed to fetch users');
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const fetchUser = async (userId) => {
    try {
        const response = await fetch(`${BASE_URL}/users/${userId}`);
        if (!response.ok) throw new Error('Failed to fetch user');
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const updateUser = async (userId, data) => {
    try {
        const response = await fetch(`${BASE_URL}/users/${userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Failed to update user');
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const fetchAllPortfolios = async () => {
    try {
        const response = await fetch(`${BASE_URL}/portfolio/`);
        if (!response.ok) throw new Error('Failed to fetch portfolios');
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const fetchStrategies = async () => {
    try {
        const response = await fetch(`${BASE_URL}/strategies/`);
        if (!response.ok) throw new Error('Failed to fetch strategies');
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const fetchProjections = async () => {
    try {
        const response = await fetch(`${BASE_URL}/projections/`);
        if (!response.ok) throw new Error('Failed to fetch projections');
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const fetchTrades = async (userId) => {
    try {
        const url = userId ? `${BASE_URL}/trades/?user_id=${userId}` : `${BASE_URL}/trades/`;
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
        const url = userId ? `${BASE_URL}/portfolio/history?user_id=${userId}` : `${BASE_URL}/portfolio/history`;
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
        const url = userId ? `${BASE_URL}/trades/daily-pnl?user_id=${userId}` : `${BASE_URL}/trades/daily-pnl`;
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
        const response = await fetch(`${BASE_URL}/audit/`, {
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
        const response = await fetch(`${BASE_URL}/portfolio/?user_id=${userId}`);
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
        const response = await fetch(`${BASE_URL}/portfolio/holdings?user_id=${userId}`);
        if (!response.ok) throw new Error('Failed to fetch holdings');
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const fetchWatchlist = async () => {
    try {
        const response = await fetch(`${BASE_URL}/watchlist/`);
        if (!response.ok) throw new Error('Failed to fetch watchlist');
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const depositFunds = async (userId, amount) => {
    try {
        const response = await fetch(`${BASE_URL}/portfolio/deposit`, {
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
        const response = await fetch(`${BASE_URL}/strategies/`, {
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
        const response = await fetch(`${BASE_URL}/market/status/`);
        if (!response.ok) throw new Error();
        return await response.json();
    } catch (error) {
        return { status: 'ONLINE', latency: '24ms', exchange: 'NASDAQ/NYSE-AMEX' };
    }
};

export const executeTrade = async (userId, tradeData) => {
    try {
        const response = await fetch(`${BASE_URL}/trades/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                ...tradeData,
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

export const fetchMarketMovers = async () => {
    try {
        const response = await fetch(`${BASE_URL}/market/movers/`);
        if (!response.ok) throw new Error();
        return await response.json();
    } catch (error) {
        return [];
    }
};
