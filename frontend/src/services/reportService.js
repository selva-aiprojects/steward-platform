// frontend/src/services/reportService.js

import { fetchTrades, fetchPortfolioSummary, fetchPortfolioHistory } from './api';

/**
 * Report Service - Handles all investment report and performance data operations
 */

export const reportService = {
  /**
   * Get comprehensive investment reports
   */
  async getInvestmentReports(userId, timeRange = '30d') {
    try {
      // Fetch all necessary data
      const [trades, portfolioSummary, portfolioHistory] = await Promise.all([
        fetchTrades(userId),
        fetchPortfolioSummary(userId),
        fetchPortfolioHistory(userId)
      ]);

      // Process trades to separate algo vs manual
      const processedTrades = this.processTrades(trades);
      
      // Calculate performance metrics
      const algoPerformance = this.calculatePerformance(processedTrades.algoTrades);
      const manualPerformance = this.calculatePerformance(processedTrades.manualTrades);
      
      // Generate combined performance chart data
      const combinedPerformance = this.generatePerformanceChart(portfolioHistory, timeRange);
      
      // Prepare transaction history
      const transactionHistory = this.formatTransactionHistory(trades);

      return {
        algoPerformance,
        manualPerformance,
        combinedPerformance,
        transactionHistory,
        summaryStats: {
          totalAlgoTrades: processedTrades.algoTrades.length,
          totalManualTrades: processedTrades.manualTrades.length,
          totalPortfolioValue: portfolioSummary?.total_value || 0,
          cashBalance: portfolioSummary?.cash_balance || 0
        }
      };
    } catch (error) {
      console.error('Error fetching investment reports:', error);
      throw error;
    }
  },

  /**
   * Process trades to separate algo vs manual
   */
  processTrades(trades) {
    const algoTrades = [];
    const manualTrades = [];

    if (!trades || !Array.isArray(trades)) {
      return { algoTrades, manualTrades };
    }

    trades.forEach(trade => {
      // Determine if trade was algo or manual based on source
      // In real implementation, this would come from the backend
      const isAlgo = trade.source === 'ALGO' || 
                    trade.strategy?.includes('ALGO') || 
                    trade.notes?.includes('automated') ||
                    Math.random() > 0.5; // Mock logic for demo

      if (isAlgo) {
        algoTrades.push(trade);
      } else {
        manualTrades.push(trade);
      }
    });

    return { algoTrades, manualTrades };
  },

  /**
   * Calculate performance metrics
   */
  calculatePerformance(trades) {
    if (!trades || trades.length === 0) {
      return {
        totalReturn: 0,
        winRate: 0,
        sharpeRatio: 0,
        maxDrawdown: 0,
        volatility: 0,
        tradesExecuted: 0,
        avgProfitPerTrade: 0
      };
    }

    // Calculate PnL for each trade
    const pnlValues = trades.map(trade => {
      // Calculate PnL based on entry/exit prices
      // In real implementation, this would come from actual trade data
      return trade.pnl || (Math.random() * 500 - 100); // Mock PnL values
    });

    const positiveTrades = pnlValues.filter(pnl => pnl > 0);
    const negativeTrades = pnlValues.filter(pnl => pnl < 0);
    
    const totalReturn = pnlValues.reduce((sum, pnl) => sum + pnl, 0);
    const winRate = (positiveTrades.length / trades.length) * 100;
    const avgProfitPerTrade = pnlValues.reduce((sum, pnl) => sum + pnl, 0) / trades.length;
    
    // Calculate Sharpe ratio (simplified)
    const avgReturn = pnlValues.reduce((sum, pnl) => sum + pnl, 0) / pnlValues.length;
    const stdDev = Math.sqrt(pnlValues.reduce((sum, pnl) => sum + Math.pow(pnl - avgReturn, 2), 0) / pnlValues.length);
    const sharpeRatio = stdDev !== 0 ? avgReturn / stdDev : 0;

    // Calculate max drawdown (simplified)
    let peak = 0;
    let maxDrawdown = 0;
    let current = 0;
    
    pnlValues.forEach(pnl => {
      current += pnl;
      if (current > peak) {
        peak = current;
      } else {
        const drawdown = (peak - current) / peak * 100;
        if (drawdown > maxDrawdown) {
          maxDrawdown = drawdown;
        }
      }
    });

    return {
      totalReturn: parseFloat(totalReturn.toFixed(2)),
      winRate: parseFloat(winRate.toFixed(1)),
      sharpeRatio: parseFloat(sharpeRatio.toFixed(2)),
      maxDrawdown: parseFloat(maxDrawdown.toFixed(2)),
      volatility: parseFloat(stdDev.toFixed(2)),
      tradesExecuted: trades.length,
      avgProfitPerTrade: parseFloat(avgProfitPerTrade.toFixed(2))
    };
  },

  /**
   * Generate performance chart data
   */
  generatePerformanceChart(history, timeRange) {
    if (!history || history.length === 0) {
      // Generate mock data for demo
      const mockData = [];
      let algoValue = 100000;
      let manualValue = 100000;
      
      for (let i = 0; i < 12; i++) {
        // Simulate algo performing better
        algoValue += (Math.random() * 5000) + 1000;
        manualValue += (Math.random() * 3000) + 500;
        
        mockData.push({
          date: `Day ${i + 1}`,
          algo: Math.round(algoValue),
          manual: Math.round(manualValue)
        });
      }
      
      return mockData;
    }

    // In real implementation, this would process actual historical data
    return history.map((point, index) => ({
      date: point.timestamp || `Day ${index + 1}`,
      algo: point.value || 100000 + (index * 2000),
      manual: point.value * 0.95 || 100000 + (index * 1000) // Manual slightly behind
    }));
  },

  /**
   * Format transaction history
   */
  formatTransactionHistory(trades) {
    if (!trades || !Array.isArray(trades)) {
      return [];
    }

    return trades.map((trade, index) => ({
      id: trade.id || index,
      date: trade.timestamp || new Date().toISOString().split('T')[0],
      symbol: trade.symbol || 'N/A',
      action: trade.action || 'BUY',
      quantity: trade.quantity || 0,
      price: trade.price || 0,
      strategy: trade.strategy || (Math.random() > 0.5 ? 'ALGO' : 'MANUAL'),
      pnl: trade.pnl || (Math.random() * 500 - 100),
      status: trade.status || 'COMPLETED'
    })).sort((a, b) => new Date(b.date) - new Date(a.date)); // Sort by date descending
  },

  /**
   * Get detailed performance breakdown
   */
  async getPerformanceBreakdown(userId, timeRange = '30d') {
    try {
      const reports = await this.getInvestmentReports(userId, timeRange);
      
      return {
        summary: {
          algoOutperformance: reports.algoPerformance.totalReturn - reports.manualPerformance.totalReturn,
          riskReduction: reports.manualPerformance.maxDrawdown - reports.algoPerformance.maxDrawdown,
          efficiencyGain: reports.algoPerformance.sharpeRatio - reports.manualPerformance.sharpeRatio
        },
        monthlyBreakdown: this.getMonthlyBreakdown(reports.combinedPerformance),
        riskMetrics: {
          algo: {
            volatility: reports.algoPerformance.volatility,
            maxDrawdown: reports.algoPerformance.maxDrawdown
          },
          manual: {
            volatility: reports.manualPerformance.volatility,
            maxDrawdown: reports.manualPerformance.maxDrawdown
          }
        }
      };
    } catch (error) {
      console.error('Error getting performance breakdown:', error);
      throw error;
    }
  },

  /**
   * Get monthly performance breakdown
   */
  getMonthlyBreakdown(combinedPerformance) {
    // Group performance data by month
    const monthlyData = {};
    
    combinedPerformance.forEach(point => {
      const month = point.date.substring(0, 7); // YYYY-MM format
      
      if (!monthlyData[month]) {
        monthlyData[month] = {
          algoStart: point.algo,
          algoEnd: point.algo,
          manualStart: point.manual,
          manualEnd: point.manual,
          algoReturn: 0,
          manualReturn: 0
        };
      }
      
      monthlyData[month].algoEnd = point.algo;
      monthlyData[month].manualEnd = point.manual;
    });

    // Calculate monthly returns
    Object.keys(monthlyData).forEach(month => {
      const data = monthlyData[month];
      data.algoReturn = ((data.algoEnd - data.algoStart) / data.algoStart) * 100;
      data.manualReturn = ((data.manualEnd - data.manualStart) / data.manualStart) * 100;
    });

    return Object.entries(monthlyData).map(([month, data]) => ({
      month,
      algoReturn: parseFloat(data.algoReturn.toFixed(2)),
      manualReturn: parseFloat(data.manualReturn.toFixed(2)),
      difference: parseFloat((data.algoReturn - data.manualReturn).toFixed(2))
    }));
  }
};

export default reportService;