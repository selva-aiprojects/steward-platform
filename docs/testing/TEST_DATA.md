# StockSteward AI - Test Data for Investment Reports

## Test User Accounts

### Trader User
- **Email**: trader@stocksteward.ai
- **Password**: trader123
- **Role**: TRADER
- **Permissions**: Trading, Portfolio Management, Basic Reporting
- **Test Data**: 
  - Portfolio Value: ₹150,000
  - Cash Balance: ₹50,000
  - Holdings: 5 stocks
  - Trading History: 25 trades

### Business Owner
- **Email**: owner@stocksteward.ai
- **Password**: owner123
- **Role**: BUSINESS_OWNER
- **Permissions**: All Trader + Team Management, Revenue Reports
- **Test Data**:
  - Managed Assets: ₹2,500,000
  - Team Size: 12 traders
  - Revenue Metrics: Available

### Super Admin
- **Email**: admin@stocksteward.ai
- **Password**: admin123
- **Role**: SUPERADMIN
- **Permissions**: All system access, user management, global controls
- **Test Data**:
  - System Overview: Complete access
  - User Management: All users visible
  - Audit Logs: Full access

### Auditor
- **Email**: auditor@stocksteward.ai
- **Password**: audit123
- **Role**: AUDITOR
- **Permissions**: Compliance, Audit, Risk Reports
- **Test Data**:
  - Audit Trail: Full access
  - Compliance Reports: Available
  - Risk Metrics: Visible

## Performance Data

### Algorithmic Trading Performance
- **Total Return**: 12.5%
- **Win Rate**: 87%
- **Sharpe Ratio**: 1.85
- **Max Drawdown**: -3.2%
- **Volatility**: 8.4%
- **Trades Executed**: 127
- **Avg Profit Per Trade**: ₹245.67
- **Time Period**: Last 30 days

### Manual Trading Performance
- **Total Return**: 6.8%
- **Win Rate**: 62%
- **Sharpe Ratio**: 0.92
- **Max Drawdown**: -7.8%
- **Volatility**: 14.2%
- **Trades Executed**: 45
- **Avg Profit Per Trade**: ₹134.22
- **Time Period**: Last 30 days

### Performance Differences
- **Return Advantage**: +5.7%
- **Win Rate Advantage**: +25%
- **Sharpe Ratio Advantage**: +0.93
- **Risk Reduction**: -4.6% max drawdown improvement

## Transaction Data

### Sample Transactions
| ID | Date | Symbol | Action | Quantity | Price | Strategy | P&L | Status |
|----|------|--------|--------|----------|-------|----------|-----|--------|
| 1 | 2024-06-15 | RELIANCE | BUY | 10 | 2850.50 | ALGO | 125.50 | COMPLETED |
| 2 | 2024-06-14 | HDFCBANK | SELL | 5 | 1520.75 | MANUAL | -45.25 | COMPLETED |
| 3 | 2024-06-13 | INFY | BUY | 8 | 1450.25 | ALGO | 89.75 | COMPLETED |
| 4 | 2024-06-12 | TCS | SELL | 3 | 3450.00 | ALGO | 156.50 | COMPLETED |
| 5 | 2024-06-11 | SBIN | BUY | 15 | 680.25 | MANUAL | -23.75 | COMPLETED |

### Transaction Summary
- **Total Transactions**: 150
- **Algo Transactions**: 95
- **Manual Transactions**: 55
- **Winning Trades**: 98
- **Losing Trades**: 52
- **Overall Win Rate**: 65.3%

## Portfolio Data

### Sample Portfolio Composition
| Symbol | Quantity | Avg Price | Current Price | Market Value | P&L | P&L % |
|--------|----------|-----------|---------------|--------------|-----|-------|
| RELIANCE | 25 | 2750.00 | 2850.50 | 71,262.50 | 2,512.50 | +3.6% |
| HDFCBANK | 15 | 1500.00 | 1520.75 | 22,811.25 | 311.25 | +1.4% |
| INFY | 20 | 1400.00 | 1450.25 | 29,005.00 | 1,005.00 | +3.6% |
| TCS | 10 | 3400.00 | 3450.00 | 34,500.00 | 500.00 | +1.5% |
| SBIN | 30 | 650.00 | 680.25 | 20,407.50 | 907.50 | +4.6% |

### Portfolio Summary
- **Total Value**: ₹177,986.25
- **Cash Balance**: ₹22,013.75
- **Invested Amount**: ₹155,972.50
- **Overall P&L**: +7.2%

## Strategy Data

### Active Strategies
| Name | Symbol | Status | P&L | Drawdown | Execution Mode |
|------|--------|--------|-----|----------|----------------|
| SMA Crossover | NIFTY | RUNNING | +4.2% | -1.2% | PAPER_TRADING |
| RSI Mean Reversion | BANKNIFTY | RUNNING | +2.8% | -0.8% | PAPER_TRADING |
| MACD Strategy | RECENT | PAUSED | +1.5% | -2.1% | PAPER_TRADING |
| Ensemble Strategy | MULTI | RUNNING | +6.7% | -1.5% | PAPER_TRADING |

### Strategy Performance Summary
- **Total Active Strategies**: 3
- **Total P&L**: +13.7%
- **Avg Win Rate**: 78%
- **Avg Sharpe Ratio**: 1.45

## Market Data

### Current Market Conditions
- **NIFTY Level**: 22,500
- **SENSEX Level**: 75,000
- **Volatility Index**: 18.5
- **Market Sentiment**: BULLISH
- **Trading Volume**: HIGH

### Market Movers
| Symbol | Change | Direction |
|--------|--------|-----------|
| RELIANCE | +1.2% | UP |
| HDFCBANK | +0.8% | UP |
| TCS | -0.5% | DOWN |
| INFY | +0.6% | UP |
| ICICIBANK | -0.3% | DOWN |

## Mock API Response Examples

### Performance Report API Response
```json
{
  "algoPerformance": {
    "totalReturn": 12.5,
    "winRate": 87,
    "sharpeRatio": 1.85,
    "maxDrawdown": -3.2,
    "volatility": 8.4,
    "tradesExecuted": 127,
    "avgProfitPerTrade": 245.67
  },
  "manualPerformance": {
    "totalReturn": 6.8,
    "winRate": 62,
    "sharpeRatio": 0.92,
    "maxDrawdown": -7.8,
    "volatility": 14.2,
    "tradesExecuted": 45,
    "avgProfitPerTrade": 134.22
  },
  "combinedPerformance": [
    { "date": "Jan", "algo": 100000, "manual": 100000 },
    { "date": "Feb", "algo": 102500, "manual": 101200 },
    { "date": "Mar", "algo": 105800, "manual": 102800 }
  ],
  "transactionHistory": [
    { "id": 1, "date": "2024-06-15", "symbol": "RELIANCE", "action": "BUY", "strategy": "ALGO", "pnl": 125.50 }
  ]
}
```

### Transaction History API Response
```json
{
  "transactions": [
    {
      "id": 1,
      "date": "2024-06-15T10:30:00Z",
      "symbol": "RELIANCE",
      "action": "BUY",
      "quantity": 10,
      "price": 2850.50,
      "strategy": "ALGO",
      "pnl": 125.50,
      "status": "COMPLETED"
    }
  ]
}
```

## Test Scenarios

### Scenario 1: New User with No Trading History
- **Profile**: New trader account
- **Expected**: Empty transaction history
- **Performance**: Default values shown

### Scenario 2: Active Trader with Mixed Results
- **Profile**: Active trader with 50+ trades
- **Expected**: Balanced performance metrics
- **Performance**: Realistic win/loss ratios

### Scenario 3: High-Performing Algorithmic User
- **Profile**: User with active algo strategies
- **Expected**: Strong algo performance
- **Performance**: Positive return differences

### Scenario 4: Conservative Manual Trader
- **Profile**: User who prefers manual trading
- **Expected**: Manual trading focus
- **Performance**: Lower but steady returns

## Validation Criteria

### Performance Metrics Validation
- [ ] Total Return calculations accurate
- [ ] Win Rate calculations correct
- [ ] Sharpe Ratio formulas valid
- [ ] Drawdown calculations precise

### Data Integrity Validation
- [ ] No null/undefined values
- [ ] Currency formatting correct
- [ ] Percentage values properly calculated
- [ ] Date formats consistent

### Security Validation
- [ ] User data isolated
- [ ] Role-based access enforced
- [ ] No unauthorized data access
- [ ] Authentication required

### Performance Validation
- [ ] Page loads under 3 seconds
- [ ] Charts render smoothly
- [ ] API calls respond quickly
- [ ] No memory leaks

This test data provides comprehensive coverage for validating the investment reports and performance analysis features across all user types and scenarios.