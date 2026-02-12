import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { socket, fetchUsers, fetchUser, fetchPortfolioSummary, fetchHoldings, fetchWatchlist, fetchTrades, fetchProjections, fetchMarketMovers, fetchExchangeStatus, updateUser, fetchMarketResearch, fetchSectorHeatmap, fetchMarketNews, fetchOptionsSnapshot, fetchOrderBookDepth, fetchMacroIndicators, fetchStrategies, fetchCurrencyMovers, fetchMetalsMovers, fetchCommodityMovers } from '../services/api';
import { useUser } from './UserContext';

const AppDataContext = createContext();

export const useAppData = () => useContext(AppDataContext);

export const AppDataProvider = ({ children }) => {
    const location = useLocation();
    const { user, selectedUser, setUser: setContextUser, setSelectedUser, isAdmin } = useUser();
    const [summary, setSummary] = useState(null);
    const [holdings, setHoldings] = useState([]);
    const [watchlist, setWatchlist] = useState([]);
    const [trades, setTrades] = useState([]);
    const [projections, setProjections] = useState([]);
    const [strategies, setStrategies] = useState([]);
    const [marketMovers, setMarketMovers] = useState({
        gainers: [],
        losers: [],
        currencies: [],
        metals: [],
        commodities: []
    });
    const [marketResearch, setMarketResearch] = useState(null);
    const [sectorHeatmap, setSectorHeatmap] = useState([]);
    const [marketNews, setMarketNews] = useState([]);
    const [optionsSnapshot, setOptionsSnapshot] = useState([]);
    const [orderBook, setOrderBook] = useState({ bids: [], asks: [] });
    const [macroIndicators, setMacroIndicators] = useState(null);
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
    const [hasLoaded, setHasLoaded] = useState(false);

    const viewId = selectedUser?.id || user?.id;

    const refreshAllData = useCallback(async () => {
        if (!viewId) return;
        if (!hasLoaded) {
            setLoading(true);
        }
        try {
            const [sumData, holdingsData, watchlistData, tradesData, projData, strategiesData, moversData, statusData, userData, researchData, heatmapData, newsData, optionsData, depthData, macroData, currencyData, metalsData, commodityData] = await Promise.all([
                fetchPortfolioSummary(viewId),
                fetchHoldings(viewId),
                fetchWatchlist(viewId),
                fetchTrades(viewId),
                fetchProjections(),
                fetchStrategies(viewId),
                fetchMarketMovers(),
                fetchExchangeStatus(),
                fetchUser(viewId),
                fetchMarketResearch(),
                fetchSectorHeatmap(),
                fetchMarketNews(),
                fetchOptionsSnapshot(),
                fetchOrderBookDepth(),
                fetchMacroIndicators(),
                fetchCurrencyMovers(),
                fetchMetalsMovers(),
                fetchCommodityMovers()
            ]);

            const safeSummary = sumData && typeof sumData === 'object'
                ? sumData
                : {
                    cash_balance: 0,
                    invested_amount: 0,
                    win_rate: 0,
                    positions_count: 0,
                    total_trades: 0
                };
            setSummary(safeSummary);
            if (!hasLoaded || (Array.isArray(holdingsData) && holdingsData.length > 0)) {
                setHoldings(Array.isArray(holdingsData) ? holdingsData : []);
            }
            if (!hasLoaded || (Array.isArray(watchlistData) && watchlistData.length > 0)) {
                setWatchlist(Array.isArray(watchlistData) ? watchlistData : []);
            }
            if (!hasLoaded || (Array.isArray(tradesData) && tradesData.length > 0)) {
                setTrades(Array.isArray(tradesData) ? tradesData : []);
            }
            if (!hasLoaded || (Array.isArray(projData) && projData.length > 0)) {
                setProjections(Array.isArray(projData) ? projData : []);
            }
            if (!hasLoaded) {
                setStrategies(Array.isArray(strategiesData) ? strategiesData : []);
            }

            // Update User Context with fresh data from backend
            if (userData && typeof userData === 'object') {
                if (viewId === user?.id) {
                    setContextUser({
                        ...userData,
                        name: userData?.full_name || userData?.name || userData?.email
                    });
                } else if (viewId === selectedUser?.id) {
                    setSelectedUser({
                        ...userData,
                        name: userData?.full_name || userData?.name || userData?.email
                    });
                }
            }

            // Prepare the marketMovers object with all data
            const updatedMarketMovers = {
                gainers: [],
                losers: [],
                currencies: [],
                metals: [],
                commodities: []
            };

            if (moversData) {
                if (Array.isArray(moversData)) {
                    // If it's an array, treat it as gainers
                    updatedMarketMovers.gainers = moversData;
                } else if (moversData.gainers !== undefined || moversData.losers !== undefined) {
                    // If it has gainers/losers properties, use as-is but ensure structure
                    updatedMarketMovers.gainers = Array.isArray(moversData.gainers) ? moversData.gainers : [];
                    updatedMarketMovers.losers = Array.isArray(moversData.losers) ? moversData.losers : [];
                }
            }

            // Add currency data if available
            if (currencyData && Array.isArray(currencyData.currencies)) {
                updatedMarketMovers.currencies = currencyData.currencies;
            }

            // Add metals data if available
            if (metalsData && Array.isArray(metalsData.metals)) {
                updatedMarketMovers.metals = metalsData.metals;
            }

            // Add commodities data if available
            if (commodityData && Array.isArray(commodityData.commodities)) {
                updatedMarketMovers.commodities = commodityData.commodities;
            }

            setMarketMovers(updatedMarketMovers);

            setExchangeStatus(statusData || { status: 'ONLINE', latency: '24ms', exchange: 'NSE/BSE' });
            setMarketResearch(researchData);
            if (!hasLoaded || (Array.isArray(heatmapData) && heatmapData.length > 0)) {
                setSectorHeatmap(Array.isArray(heatmapData) ? heatmapData : []);
            }
            if (!hasLoaded || (Array.isArray(newsData) && newsData.length > 0)) {
                setMarketNews(Array.isArray(newsData) ? newsData : []);
            }
            if (!hasLoaded || (Array.isArray(optionsData) && optionsData.length > 0)) {
                setOptionsSnapshot(Array.isArray(optionsData) ? optionsData : []);
            }
            if (!hasLoaded || depthData) {
                setOrderBook(depthData || { bids: [], asks: [] });
            }
            if (!hasLoaded || macroData) {
                setMacroIndicators(macroData);
            }

            if (isAdmin || user?.is_superuser) {
                const users = await fetchUsers();
                setAllUsers((users || []).map(u => ({
                    ...u,
                    name: u.full_name || u.name || u.email
                })));
            }
        } catch (error) {
            console.error("Failed to refresh app data:", error);
        } finally {
            if (!hasLoaded) {
                setLoading(false);
                setHasLoaded(true);
            }
        }
    }, [viewId, user, selectedUser, isAdmin, setContextUser, setSelectedUser, hasLoaded]);

    useEffect(() => {
        if (viewId) {
            refreshAllData();
        }
    }, [viewId, refreshAllData]);

    useEffect(() => {
        if (!viewId) return;
        // Auto-refresh every 60 seconds for most pages, but allow disabling for specific pages
        // Added more pages to exclude from auto-refresh to prevent unwanted page refreshes
        const currentPath = location.pathname;
        const shouldRefresh = !['/reports', '/reports/investment', '/investment', '/portfolio', '/users', '/support', '/help', '/subscription', '/kyc'].includes(currentPath);

        if (shouldRefresh) {
            const interval = setInterval(() => {
                refreshAllData();
            }, 60000); // Increased to 60 seconds to reduce frequency further
            return () => clearInterval(interval);
        }
    }, [viewId, refreshAllData, location.pathname]);

    useEffect(() => {
        if (!socket) return;

        const onConnect = () => {
            console.log("AppDataContext connected to socket");
            socket.emit('join_stream', { role: user?.role || 'TRADER', userId: user?.id });
        };

        const onMarketUpdate = (data) => {};

        const onStewardPrediction = (data) => {
            if (data && typeof data === 'object') {
                setStewardPrediction(data);
            }
        };

        const onAdminMetrics = (data) => {
            setAdminTelemetry(data);
        };

        const onMarketMovers = (data) => {
            if (data && typeof data === 'object') {
                // Ensure consistent structure with gainers and losers arrays
                const gainers = Array.isArray(data.gainers) ? data.gainers : [];
                const losers = Array.isArray(data.losers) ? data.losers : [];
                setMarketMovers({ gainers, losers });
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
            marketResearch,
            sectorHeatmap,
            marketNews,
            optionsSnapshot,
            orderBook,
            macroIndicators,
            strategies,
            loading,
            refreshAllData,
            toggleTradingMode
        }}>
            {children}
        </AppDataContext.Provider>
    );
};
