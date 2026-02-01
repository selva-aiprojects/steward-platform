// Dynamic API URL for production support
// Fallback to localhost for development
const BASE_URL = process.env.REACT_APP_API_URL || '';

console.log("API Connection:", BASE_URL); // Debug log for deployment verification

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

export const fetchUser = async (userId = 1) => {
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

export const fetchTrades = async () => {
    try {
        const response = await fetch(`${BASE_URL}/trades/`);
        if (!response.ok) throw new Error('Failed to fetch trades');
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const fetchPortfolioHistory = async (userId = 1) => {
    try {
        const response = await fetch(`${BASE_URL}/portfolio/history?user_id=${userId}`);
        if (!response.ok) throw new Error('Failed to fetch history');
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const fetchDailyPnL = async (userId = 1) => {
    try {
        const response = await fetch(`${BASE_URL}/trades/daily-pnl?user_id=${userId}`);
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

export const fetchPortfolioSummary = async (userId = 1) => {
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
