const BASE_URL = 'http://localhost:8000/api/v1';

export const fetchPortfolioHistory = async (userId: number = 1) => {
    try {
        const response = await fetch(`${BASE_URL}/portfolio/history?user_id=${userId}`);
        if (!response.ok) throw new Error('Failed to fetch history');
        return await response.ok ? await response.json() : [];
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const fetchDailyPnL = async (userId: number = 1) => {
    try {
        const response = await fetch(`${BASE_URL}/trades/daily-pnl?user_id=${userId}`);
        if (!response.ok) throw new Error('Failed to fetch daily pnl');
        return await response.ok ? await response.json() : [];
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const fetchPortfolioSummary = async (userId: number = 1) => {
    try {
        const response = await fetch(`${BASE_URL}/portfolio/?user_id=${userId}`);
        if (!response.ok) throw new Error('Failed to fetch summary');
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
};
