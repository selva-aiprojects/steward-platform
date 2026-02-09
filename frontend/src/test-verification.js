// Test script to verify key functionality
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MarketTicker } from './src/components/MarketTicker';
import { Dashboard } from './src/pages/Dashboard';

describe('StockSteward AI - Functionality Verification', () => {
  test('MarketTicker component renders without errors', async () => {
    // Mock the useAppData hook
    jest.mock('./src/context/AppDataContext', () => ({
      useAppData: () => ({
        marketMovers: [
          { symbol: 'RELIANCE', exchange: 'NSE', price: 2987.5, change: 1.2 },
          { symbol: 'SENSEX', exchange: 'BSE', price: 72150, change: 0.6 },
          { symbol: 'CRUDEOIL', exchange: 'MCX', price: 6985, change: -0.4 }
        ],
        loading: false
      })
    }));

    // Render the component
    render(<MarketTicker />);
    
    // Wait for the component to render
    await waitFor(() => {
      expect(screen.getByText(/RELIANCE|SENSEX|CRUDEOIL/i)).toBeInTheDocument();
    });
  });

  test('Dashboard component renders without errors', async () => {
    // Mock the useUser and useAppData hooks
    jest.mock('./src/context/UserContext', () => ({
      useUser: () => ({
        user: { id: 1, name: 'Test User', role: 'TRADER' },
        selectedUser: null,
        setSelectedUser: jest.fn(),
        isAdmin: false
      })
    }));

    jest.mock('./src/context/AppDataContext', () => ({
      useAppData: () => ({
        summary: { invested_amount: 50000, cash_balance: 10000, win_rate: 75 },
        trades: [],
        marketMovers: [],
        exchangeStatus: {},
        stewardPrediction: {},
        marketResearch: {},
        sectorHeatmap: [],
        marketNews: [],
        optionsSnapshot: [],
        orderBook: { bids: [], asks: [] },
        macroIndicators: null,
        adminTelemetry: null,
        loading: false,
        allUsers: [],
        refreshAllData: jest.fn()
      })
    }));

    // Render the component
    render(<Dashboard />);
    
    // Wait for the component to render
    await waitFor(() => {
      expect(screen.getByText(/Welcome, Test User/i)).toBeInTheDocument();
    });
  });
});