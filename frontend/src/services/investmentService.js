// frontend/src/services/investmentService.js

import { fetchPortfolioSummary, fetchHoldings, fetchStrategies } from './api';

/**
 * Investment Service - Handles all investment-related API operations
 */

export const investmentService = {
  /**
   * Check if user has cash available for investment
   */
  async hasCashForInvestment(userId) {
    try {
      const portfolio = await fetchPortfolioSummary(userId);
      return portfolio && portfolio.cash_balance > 0;
    } catch (error) {
      console.error('Error checking cash balance:', error);
      return false;
    }
  },

  /**
   * Check if user has any holdings
   */
  async hasHoldings(userId) {
    try {
      const holdings = await fetchHoldings(userId);
      return holdings && holdings.length > 0;
    } catch (error) {
      console.error('Error checking holdings:', error);
      return false;
    }
  },

  /**
   * Check if user has active strategies
   */
  async hasActiveStrategies(userId) {
    try {
      const strategies = await fetchStrategies(userId);
      return strategies && strategies.some(strategy => strategy.status === 'RUNNING');
    } catch (error) {
      console.error('Error checking strategies:', error);
      return false;
    }
  },

  /**
   * Get investment readiness status
   */
  async getInvestmentReadiness(userId) {
    const hasCash = await this.hasCashForInvestment(userId);
    const hasHoldings = await this.hasHoldings(userId);
    const hasActiveStrategies = await this.hasActiveStrategies(userId);

    return {
      hasCash,
      hasHoldings,
      hasActiveStrategies,
      isReadyForInvestment: hasCash && !hasHoldings && !hasActiveStrategies,
      cashBalance: hasCash ? (await fetchPortfolioSummary(userId)).cash_balance : 0
    };
  },

  /**
   * Launch investment strategy
   */
  async launchStrategy(userId, strategyData = {}) {
    try {
      const defaultStrategy = {
        user_id: userId,
        name: "Auto Steward Primary",
        symbol: "",
        status: "RUNNING",
        pnl: "0%",
        drawdown: 0.0,
        execution_mode: "PAPER_TRADING",
        ...strategyData
      };

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/strategies/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        },
        body: JSON.stringify(defaultStrategy)
      });

      if (!response.ok) {
        throw new Error(`Failed to launch strategy: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error launching strategy:', error);
      throw error;
    }
  }
};

// Helper function to get auth headers
function getAuthHeaders() {
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
}

export default investmentService;