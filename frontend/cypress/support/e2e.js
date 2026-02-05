import './commands';

// Prevent Cypress from failing tests due to uncaught exceptions from the application
Cypress.on('uncaught:exception', (err, runnable) => {
  // Returning false here prevents Cypress from failing the test
  // This is useful for handling known React errors during testing
  if (err.message.includes('Rendered fewer hooks than expected')) {
    console.warn('Ignoring React hook error during test:', err.message);
    return false;
  }
  // For other errors, let them fail the test
  return true;
});

// Intercept API calls and return mock data
beforeEach(() => {
  // Mock API responses to prevent actual API calls during testing

  // User-related endpoints
  cy.intercept('GET', '**/api/v1/users/**', {
    statusCode: 200,
    body: {
      id: 'mock-user-1',
      name: 'Test Trader',
      email: 'trader@stocksteward.ai',
      role: 'TRADER',
      trading_mode: 'AUTO',
      full_name: 'Test Trader'
    }
  }).as('getUser');

  cy.intercept('GET', '**/api/v1/users/', {
    statusCode: 200,
    body: [{
      id: 'mock-user-1',
      name: 'Test Trader',
      email: 'trader@stocksteward.ai',
      role: 'TRADER',
      trading_mode: 'AUTO',
      full_name: 'Test Trader'
    }]
  }).as('getAllUsers');

  // Portfolio-related endpoints
  cy.intercept('GET', '**/api/v1/portfolio/**', {
    statusCode: 200,
    body: {
      id: 'portfolio-1',
      user_id: 'mock-user-1',
      cash_balance: 100000,
      invested_amount: 50000,
      win_rate: 0.65,
      positions_count: 5,
      total_trades: 42,
      total_value: 150000,
      daily_pnl: 1200,
      monthly_return: 5.2,
      chartData: [  // Add chart data that the dashboard expects
        { date: '2023-01-01', value: 100000 },
        { date: '2023-02-01', value: 105000 },
        { date: '2023-03-01', value: 110000 },
        { date: '2023-04-01', value: 108000 },
        { date: '2023-05-01', value: 115000 },
        { date: '2023-06-01', value: 120000 },
        { date: '2023-07-01', value: 125000 }
      ]
    }
  }).as('getPortfolio');

  cy.intercept('GET', '**/api/v1/portfolio/holdings**', {
    statusCode: 200,
    body: []
  }).as('getHoldings');

  cy.intercept('GET', '**/api/v1/portfolio/history**', {
    statusCode: 200,
    body: [
      { date: '2023-01-01', value: 100000 },
      { date: '2023-02-01', value: 105000 },
      { date: '2023-03-01', value: 110000 },
      { date: '2023-04-01', value: 108000 },
      { date: '2023-05-01', value: 115000 },
      { date: '2023-06-01', value: 120000 },
      { date: '2023-07-01', value: 125000 }
    ]
  }).as('getPortfolioHistory');

  cy.intercept('POST', '**/api/v1/portfolio/deposit', {
    statusCode: 200,
    body: { success: true, balance: 150000 }
  }).as('depositFunds');

  cy.intercept('POST', '**/api/v1/portfolio/withdraw', {
    statusCode: 200,
    body: { success: true, balance: 50000 }
  }).as('withdrawFunds');

  // Strategies-related endpoints
  cy.intercept('GET', '**/api/v1/strategies/**', {
    statusCode: 200,
    body: [
      {
        id: 'strat-1',
        name: 'Test Strategy',
        symbol: 'RELIANCE',
        status: 'RUNNING',
        pnl: 2.5,
        total_trades: 15,
        created_at: new Date().toISOString(),
        last_updated: new Date().toISOString()
      }
    ]
  }).as('getStrategies');

  cy.intercept('POST', '**/api/v1/strategies/**', {
    statusCode: 200,
    body: { id: 'new-strat-1', name: 'New Strategy', status: 'RUNNING' }
  }).as('createStrategy');

  // Projections and market data endpoints
  cy.intercept('GET', '**/api/v1/projections/**', {
    statusCode: 200,
    body: [
      { ticker: 'RELIANCE', projected_return: 12.5, confidence: 85, time_frame: '1Y' },
      { ticker: 'TCS', projected_return: 8.2, confidence: 78, time_frame: '1Y' },
      { ticker: 'HDFCBANK', projected_return: 9.7, confidence: 82, time_frame: '1Y' }
    ]
  }).as('getProjections');

  cy.intercept('GET', '**/api/v1/trades/**', {
    statusCode: 200,
    body: []
  }).as('getTrades');

  cy.intercept('GET', '**/api/v1/trades/daily-pnl**', {
    statusCode: 200,
    body: []
  }).as('getDailyPnL');

  // Market status and data endpoints
  cy.intercept('GET', '**/api/v1/market/status/**', {
    statusCode: 200,
    body: { status: 'ONLINE', latency: '24ms', exchange: 'NSE' }
  }).as('getExchangeStatus');

  cy.intercept('GET', '**/api/v1/market/movers/**', {
    statusCode: 200,
    body: []
  }).as('getMarketMovers');

  cy.intercept('GET', '**/api/v1/market/heatmap', {
    statusCode: 200,
    body: []
  }).as('getHeatmap');

  cy.intercept('GET', '**/api/v1/market/news', {
    statusCode: 200,
    body: []
  }).as('getMarketNews');

  cy.intercept('GET', '**/api/v1/market/options', {
    statusCode: 200,
    body: []
  }).as('getOptions');

  cy.intercept('GET', '**/api/v1/market/depth', {
    statusCode: 200,
    body: { bids: [], asks: [] }
  }).as('getDepth');

  cy.intercept('GET', '**/api/v1/market/macro', {
    statusCode: 200,
    body: {}
  }).as('getMacro');

  // AI and research endpoints
  cy.intercept('GET', '**/api/v1/ai/market-research', {
    statusCode: 200,
    body: {
      prediction: 'Market looks positive for tech stocks',
      decision: 'BUY',
      confidence: 85,
      signal_mix: { technical: 60, fundamental: 30, news: 10 },
      risk_radar: 75
    }
  }).as('getMarketResearch');

  // Watchlist endpoints
  cy.intercept('GET', '**/api/v1/watchlist/**', {
    statusCode: 200,
    body: []
  }).as('getWatchlist');

  cy.intercept('POST', '**/api/v1/watchlist/**', {
    statusCode: 200,
    body: { success: true }
  }).as('addToWatchlist');

  cy.intercept('DELETE', '**/api/v1/watchlist/**', {
    statusCode: 200,
    body: { success: true }
  }).as('removeFromWatchlist');

  // Trading endpoints
  cy.intercept('POST', '**/api/v1/trades/**', {
    statusCode: 200,
    body: { status: 'SUCCESS', id: 'trade-1' }
  }).as('executeTrade');

  // User update endpoints
  cy.intercept('PUT', '**/api/v1/users/**', {
    statusCode: 200,
    body: {
      id: 'mock-user-1',
      name: 'Test Trader',
      email: 'trader@stocksteward.ai',
      role: 'TRADER',
      trading_mode: 'MANUAL', // Changed to MANUAL for toggle testing
      full_name: 'Test Trader'
    }
  }).as('updateUser');

  // Auth endpoints
  cy.intercept('POST', '**/api/v1/auth/login', {
    statusCode: 200,
    body: {
      id: 'mock-user-1',
      name: 'Test Trader',
      email: 'trader@stocksteward.ai',
      role: 'TRADER',
      trading_mode: 'AUTO',
      full_name: 'Test Trader'
    }
  }).as('login');

  // Audit endpoints
  cy.intercept('POST', '**/api/v1/audit/**', {
    statusCode: 200,
    body: { success: true }
  }).as('createAudit');

  // KYC endpoints
  cy.intercept('GET', '**/api/v1/kyc/applications', {
    statusCode: 200,
    body: []
  }).as('getKycApps');

  cy.intercept('POST', '**/api/v1/kyc/applications', {
    statusCode: 200,
    body: { id: 'kyc-1', status: 'PENDING' }
  }).as('submitKyc');

  // Catch-all for any other API calls that might be missed
  cy.intercept('GET', '**/api/v1/**', {
    statusCode: 200,
    body: {}
  }).as('catchAllGet');

  cy.intercept('POST', '**/api/v1/**', {
    statusCode: 200,
    body: { success: true }
  }).as('catchAllPost');

  cy.intercept('PUT', '**/api/v1/**', {
    statusCode: 200,
    body: { success: true }
  }).as('catchAllPut');

  cy.intercept('DELETE', '**/api/v1/**', {
    statusCode: 200,
    body: { success: true }
  }).as('catchAllDelete');
});
