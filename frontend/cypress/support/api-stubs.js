// API stubs for testing to prevent actual API calls
// This file will be imported in support/e2e.js

// Stub the API service functions to return mock data
Cypress.on('window:before:load', (win) => {
  // Create a stubbed version of the API functions
  const stubbedApi = {
    fetchUsers: () => Promise.resolve([]),
    fetchUser: (userId) => Promise.resolve({
      id: userId,
      name: 'Mock User',
      email: 'mock@example.com',
      role: 'TRADER',
      trading_mode: 'AUTO'
    }),
    fetchAllPortfolios: () => Promise.resolve([]),
    fetchStrategies: () => Promise.resolve([]),
    fetchProjections: () => Promise.resolve([]),
    fetchTrades: (userId) => Promise.resolve([]),
    fetchPortfolioHistory: (userId) => Promise.resolve([]),
    fetchPortfolioSummary: (userId) => Promise.resolve({
      cash_balance: 100000,
      invested_amount: 50000,
      win_rate: 0.65,
      positions_count: 5,
      total_trades: 42
    }),
    fetchDailyPnL: (userId) => Promise.resolve([]),
    createAuditLog: (logData) => Promise.resolve({ success: true }),
    fetchHoldings: (userId) => Promise.resolve([]),
    fetchWatchlist: (userId) => Promise.resolve([]),
    fetchExchangeStatus: () => Promise.resolve({ status: 'ONLINE', latency: '24ms', exchange: 'NSE' }),
    executeTrade: (userId, tradeData) => Promise.resolve({ status: 'SUCCESS' }),
    depositFunds: (userId, amount) => Promise.resolve({ success: true }),
    launchStrategy: (userId, strategyData) => Promise.resolve({ id: 'mock-strategy-1', ...strategyData }),
    loginUser: (email, password) => Promise.resolve({ id: 'mock-user-1', email, role: 'TRADER' }),
    fetchMarketMovers: () => Promise.resolve([]),
    fetchMarketResearch: () => Promise.resolve({}),
    fetchSectorHeatmap: () => Promise.resolve([]),
    fetchMarketNews: () => Promise.resolve([]),
    fetchOptionsSnapshot: () => Promise.resolve([]),
    fetchOrderBookDepth: () => Promise.resolve({ bids: [], asks: [] }),
    fetchMacroIndicators: () => Promise.resolve({}),
    submitKycApplication: (payload) => Promise.resolve({ id: 'mock-kyc-1', status: 'PENDING' }),
    fetchKycApplications: () => Promise.resolve([]),
    reviewKycApplication: (kycId, status, notes) => Promise.resolve({ id: kycId, status }),
    approveKycApplication: (kycId) => Promise.resolve({ id: kycId, status: 'APPROVED' }),
    rejectKycApplication: (kycId, notes) => Promise.resolve({ id: kycId, status: 'REJECTED' }),
    updateUser: (userId, data) => Promise.resolve({ id: userId, ...data })
  };

  // Override the API functions in the window object
  win.stubbedApi = stubbedApi;
});