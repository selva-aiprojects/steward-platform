import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { socket, fetchUsers, fetchUser, fetchPortfolioSummary, fetchHoldings, fetchWatchlist, fetchTrades, fetchProjections, fetchMarketMovers, fetchExchangeStatus, updateUser } from '../services/api';
import { useUser } from './UserContext';

const AppDataContext = createContext();

export const useAppData = () => useContext(AppDataContext);

export const AppDataProvider = ({ children }) => {
    const { user, selectedUser, setUser: setContextUser, setSelectedUser } = useUser();
    const [summary, setSummary] = useState(null);
    const [holdings, setHoldings] = useState([]);
    const [watchlist, setWatchlist] = useState([]);
    const [trades, setTrades] = useState([]);
    const [projections, setProjections] = useState([]);
    const [marketMovers, setMarketMovers] = useState([]);
    const [exchangeStatus, setExchangeStatus] = useState({ status: 'ONLINE', latency: '24ms', exchange: 'NSE/BSE' });
    const [stewardPrediction, setStewardPrediction] = useState({
        prediction: "Initializing market intelligence...",
        decision: "NEUTRAL",
        confidence: 0,
        signal_mix: { technical: 0, fundamental: 0, news: 0 },
        risk_radar: 0
    });
    const [allUsers, setAllUsers] = useState([]);
    const [adminTelemetry, setAdminTelemetry] = useState(null);
    const [loading, setLoading] = useState(false);

    const viewId = selectedUser?.id || user?.id;

    const refreshAllData = useCallback(async () => {
        if (!viewId) return;
        setLoading(true);
        try {
            const [sumData, holdingsData, watchlistData, tradesData, projData, moversData, statusData, userData] = await Promise.all([
                fetchPortfolioSummary(viewId),
                fetchHoldings(viewId),
                fetchWatchlist(), // Watchlist usually global or user specific? api.js doesn't take userId
                fetchTrades(viewId),
                fetchProjections(),
                fetchMarketMovers(),
                fetchExchangeStatus(),
                fetchUser(viewId)
            ]);

            setSummary(sumData);
            setHoldings(Array.isArray(holdingsData) ? holdingsData : []);
            setWatchlist(Array.isArray(watchlistData) ? watchlistData : []);
            setTrades(Array.isArray(tradesData) ? tradesData : []);
            setProjections(Array.isArray(projData) ? projData : []);

            // Update User Context with fresh data from backend
            if (viewId === user?.id) {
                setContextUser(userData);
            } else if (viewId === selectedUser?.id) {
                setSelectedUser(userData);
            }

            if (moversData) {
                if (Array.isArray(moversData)) {
                    setMarketMovers(moversData);
                } else if (moversData.gainers) {
                    setMarketMovers([...moversData.gainers, ...moversData.losers]);
                }
            }

            setExchangeStatus(statusData);

            if (user?.role === 'ADMIN' || user?.is_superuser) {
                const users = await fetchUsers();
                setAllUsers(users);
            }
        } catch (error) {
            console.error("Failed to refresh app data:", error);
        } finally {
            setLoading(false);
        }
    }, [viewId]);

    useEffect(() => {
        if (viewId) {
            refreshAllData();
        }
    }, [viewId, refreshAllData]);

    useEffect(() => {
        if (!socket) return;

        const onConnect = () => {
            console.log("AppDataContext connected to socket");
            socket.emit('join_stream', { role: user?.role || 'USER', userId: user?.id });
        };

        const onMarketUpdate = (data) => {
            setMarketMovers(prev => {
                const exists = prev.find(m => m.symbol === data.symbol);
                if (exists) {
                    return prev.map(m => m.symbol === data.symbol ? { ...m, ...data } : m);
                } else {
                    return [data, ...prev].slice(0, 10);
                }
            });
        };

        const onStewardPrediction = (data) => {
            if (data && typeof data === 'object') {
                setStewardPrediction(data);
            }
        };

        const onAdminMetrics = (data) => {
            setAdminTelemetry(data);
        };

        const onMarketMovers = (data) => {
            if (data.gainers) {
                setMarketMovers([...data.gainers, ...data.losers]);
            }
        };

        socket.on('connect', onConnect);
        socket.on('market_update', onMarketUpdate);
        socket.on('steward_prediction', onStewardPrediction);
        socket.on('admin_metrics', onAdminMetrics);
        socket.on('market_movers', onMarketMovers);

        if (socket.connected) onConnect();

        return () => {
            socket.off('connect', onConnect);
            socket.off('market_update', onMarketUpdate);
            socket.off('steward_prediction', onStewardPrediction);
            socket.off('admin_metrics', onAdminMetrics);
            socket.off('market_movers', onMarketMovers);
        };
    }, [user]);

    const toggleTradingMode = async () => {
        if (!user) return;
        const newMode = user.trading_mode === 'AUTO' ? 'MANUAL' : 'AUTO';
        try {
            const updated = await updateUser(user.id, { trading_mode: newMode });
            if (updated) {
                setContextUser(updated); // This updates UserContext which might trigger refresh
            }
            return updated;
        } catch (error) {
            console.error("Failed to toggle trading mode:", error);
        }
    };

    return (
        <AppDataContext.Provider value={{
            summary,
            holdings,
            watchlist,
            trades,
            projections,
            marketMovers,
            exchangeStatus,
            stewardPrediction,
            allUsers,
            adminTelemetry,
            loading,
            refreshAllData,
            toggleTradingMode
        }}>
            {children}
        </AppDataContext.Provider>
    );
};
