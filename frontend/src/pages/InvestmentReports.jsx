// frontend/src/pages/InvestmentReports.jsx
import React, { useState, useEffect } from 'react';
import { useUser } from '../context/UserContext';
import { useAppData } from '../context/AppDataContext';
import { reportService } from '../services/reportService';
import { PerformanceComparisonChart } from '../components/PerformanceComparisonChart';
import { TransactionStatement } from '../components/TransactionStatement';
import { Card } from "../components/ui/card";
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Zap, 
  Activity, 
  DollarSign,
  Shield,
  Award,
  Users,
  Calendar,
  Clock
} from 'lucide-react';

export function InvestmentReports() {
  const { user, selectedUser } = useUser();
  const { summary, loading, refreshAllData } = useAppData();

  const [reportData, setReportData] = useState({
    algoPerformance: {},
    manualPerformance: {},
    combinedPerformance: [],
    transactionHistory: [],
    summaryStats: {}
  });

  const [timeRange, setTimeRange] = useState('30d');
  const [loadingReports, setLoadingReports] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  // Load report data
  useEffect(() => {
    const loadReportData = async () => {
      const userId = selectedUser?.id || user?.id;
      if (!userId) return;

      setLoadingReports(true);
      try {
        const data = await reportService.getInvestmentReports(userId, timeRange);
        setReportData(data);
      } catch (error) {
        console.error('Error loading report data:', error);
      } finally {
        setLoadingReports(false);
      }
    };

    loadReportData();
  }, [user?.id, selectedUser?.id, timeRange]); // Changed dependency to only watch IDs to prevent infinite loop

  // Mock data for demonstration (will be replaced with real API data)
  const mockAlgoPerformance = {
    totalReturn: 12.5,
    winRate: 87,
    sharpeRatio: 1.85,
    maxDrawdown: -3.2,
    volatility: 8.4,
    tradesExecuted: 127,
    avgProfitPerTrade: 245.67
  };

  const mockManualPerformance = {
    totalReturn: 6.8,
    winRate: 62,
    sharpeRatio: 0.92,
    maxDrawdown: -7.8,
    volatility: 14.2,
    tradesExecuted: 45,
    avgProfitPerTrade: 134.22
  };

  const mockCombinedPerformance = [
    { date: 'Jan 1', algo: 100000, manual: 100000 },
    { date: 'Jan 15', algo: 102500, manual: 101200 },
    { date: 'Feb 1', algo: 105800, manual: 102800 },
    { date: 'Feb 15', algo: 108900, manual: 104100 },
    { date: 'Mar 1', algo: 112300, manual: 105600 },
    { date: 'Mar 15', algo: 115200, manual: 106800 },
    { date: 'Apr 1', algo: 118700, manual: 108200 },
    { date: 'Apr 15', algo: 122400, manual: 109500 },
    { date: 'May 1', algo: 126800, manual: 111200 },
    { date: 'May 15', algo: 131500, manual: 112800 },
    { date: 'Jun 1', algo: 136200, manual: 114500 },
    { date: 'Jun 15', algo: 141800, manual: 116200 }
  ];

  const mockTransactionHistory = [
    { id: 1, date: '2024-06-15', symbol: 'RELIANCE', action: 'BUY', quantity: 10, price: 2850.50, strategy: 'ALGO', pnl: 125.50 },
    { id: 2, date: '2024-06-14', symbol: 'HDFCBANK', action: 'SELL', quantity: 5, price: 1520.75, strategy: 'MANUAL', pnl: -45.25 },
    { id: 3, date: '2024-06-13', symbol: 'INFY', action: 'BUY', quantity: 8, price: 1450.25, strategy: 'ALGO', pnl: 89.75 },
    { id: 4, date: '2024-06-12', symbol: 'TCS', action: 'SELL', quantity: 3, price: 3450.00, strategy: 'ALGO', pnl: 156.50 },
    { id: 5, date: '2024-06-11', symbol: 'SBIN', action: 'BUY', quantity: 15, price: 680.25, strategy: 'MANUAL', pnl: -23.75 }
  ];

  const algoPerformance = reportData.algoPerformance || mockAlgoPerformance;
  const manualPerformance = reportData.manualPerformance || mockManualPerformance;
  const combinedPerformance = reportData.combinedPerformance || mockCombinedPerformance;
  const transactionHistory = reportData.transactionHistory || mockTransactionHistory;

  // Calculate performance differences
  const returnDifference = algoPerformance.totalReturn - manualPerformance.totalReturn;
  const winRateDifference = algoPerformance.winRate - manualPerformance.winRate;
  const sharpeDifference = algoPerformance.sharpeRatio - manualPerformance.sharpeRatio;

  if (loading || loadingReports) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="pb-8 space-y-8">
      {/* Header */}
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-slate-900 font-heading">
            Investment Performance Reports
          </h1>
          <p className="text-slate-500 mt-1 uppercase text-[10px] font-bold tracking-widest leading-none">
            Algorithmic vs Manual Trading Performance Analysis
          </p>
        </div>
        <div className="flex items-center gap-4">
          <select 
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="bg-white border border-slate-200 rounded-xl px-4 py-2 text-sm font-black text-slate-700 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="1y">Last Year</option>
            <option value="all">All Time</option>
          </select>
          <button 
            onClick={refreshAllData}
            className="bg-primary text-white px-4 py-2 rounded-xl font-black hover:opacity-90 transition-all flex items-center gap-2"
          >
            <Clock size={16} />
            Refresh
          </button>
        </div>
      </header>

      {/* Performance Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6 border-slate-100 shadow-sm bg-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-black text-slate-400 uppercase tracking-widest">Total Return</p>
              <h3 className="text-2xl font-black text-slate-900 mt-1">
                {algoPerformance.totalReturn?.toFixed(2)}%
              </h3>
              <p className="text-xs text-green-600 font-black mt-1">vs {manualPerformance.totalReturn?.toFixed(2)}% Manual</p>
            </div>
            <div className="h-12 w-12 rounded-xl bg-green-100 flex items-center justify-center">
              <TrendingUp className="text-green-600" size={24} />
            </div>
          </div>
        </Card>

        <Card className="p-6 border-slate-100 shadow-sm bg-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-black text-slate-400 uppercase tracking-widest">Win Rate</p>
              <h3 className="text-2xl font-black text-slate-900 mt-1">
                {algoPerformance.winRate?.toFixed(1)}%
              </h3>
              <p className="text-xs text-green-600 font-black mt-1">vs {manualPerformance.winRate?.toFixed(1)}% Manual</p>
            </div>
            <div className="h-12 w-12 rounded-xl bg-blue-100 flex items-center justify-center">
              <Target className="text-blue-600" size={24} />
            </div>
          </div>
        </Card>

        <Card className="p-6 border-slate-100 shadow-sm bg-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-black text-slate-400 uppercase tracking-widest">Sharpe Ratio</p>
              <h3 className="text-2xl font-black text-slate-900 mt-1">
                {algoPerformance.sharpeRatio?.toFixed(2)}
              </h3>
              <p className="text-xs text-green-600 font-black mt-1">vs {manualPerformance.sharpeRatio?.toFixed(2)} Manual</p>
            </div>
            <div className="h-12 w-12 rounded-xl bg-purple-100 flex items-center justify-center">
              <Zap className="text-purple-600" size={24} />
            </div>
          </div>
        </Card>

        <Card className="p-6 border-slate-100 shadow-sm bg-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-black text-slate-400 uppercase tracking-widest">Max Drawdown</p>
              <h3 className="text-2xl font-black text-slate-900 mt-1">
                {algoPerformance.maxDrawdown?.toFixed(2)}%
              </h3>
              <p className="text-xs text-red-600 font-black mt-1">vs {manualPerformance.maxDrawdown?.toFixed(2)}% Manual</p>
            </div>
            <div className="h-12 w-12 rounded-xl bg-red-100 flex items-center justify-center">
              <TrendingDown className="text-red-600" size={24} />
            </div>
          </div>
        </Card>
      </div>

      {/* Performance Difference Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6 border-2 border-green-200 bg-green-50">
          <div className="flex items-center gap-3 mb-3">
            <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center">
              <Award className="text-green-600" size={20} />
            </div>
            <h3 className="text-lg font-black text-green-800">Return Advantage</h3>
          </div>
          <p className="text-3xl font-black text-green-700 mb-2">
            +{returnDifference?.toFixed(2)}%
          </p>
          <p className="text-sm text-green-600">
            Higher returns compared to manual trading
          </p>
        </Card>

        <Card className="p-6 border-2 border-blue-200 bg-blue-50">
          <div className="flex items-center gap-3 mb-3">
            <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <Target className="text-blue-600" size={20} />
            </div>
            <h3 className="text-lg font-black text-blue-800">Win Rate Advantage</h3>
          </div>
          <p className="text-3xl font-black text-blue-700 mb-2">
            +{winRateDifference?.toFixed(1)}%
          </p>
          <p className="text-sm text-blue-600">
            Better success rate compared to manual trading
          </p>
        </Card>

        <Card className="p-6 border-2 border-purple-200 bg-purple-50">
          <div className="flex items-center gap-3 mb-3">
            <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center">
              <Zap className="text-purple-600" size={20} />
            </div>
            <h3 className="text-lg font-black text-purple-800">Risk-Adjusted Advantage</h3>
          </div>
          <p className="text-3xl font-black text-purple-700 mb-2">
            +{sharpeDifference?.toFixed(2)}
          </p>
          <p className="text-sm text-purple-600">
            Better risk-adjusted returns compared to manual trading
          </p>
        </Card>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-6 py-3 font-black text-sm uppercase tracking-widest border-b-2 transition-all ${
            activeTab === 'overview'
              ? 'border-primary text-primary'
              : 'border-transparent text-slate-400 hover:text-slate-600'
          }`}
        >
          Performance Overview
        </button>
        <button
          onClick={() => setActiveTab('comparison')}
          className={`px-6 py-3 font-black text-sm uppercase tracking-widest border-b-2 transition-all ${
            activeTab === 'comparison'
              ? 'border-primary text-primary'
              : 'border-transparent text-slate-400 hover:text-slate-600'
          }`}
        >
          Algo vs Manual
        </button>
        <button
          onClick={() => setActiveTab('transactions')}
          className={`px-6 py-3 font-black text-sm uppercase tracking-widest border-b-2 transition-all ${
            activeTab === 'transactions'
              ? 'border-primary text-primary'
              : 'border-transparent text-slate-400 hover:text-slate-600'
          }`}
        >
          Transaction Statement
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          <Card className="p-8 border-slate-100 shadow-sm bg-white">
            <h3 className="text-xl font-black text-slate-900 mb-6">Portfolio Growth Comparison</h3>
            <PerformanceComparisonChart data={combinedPerformance} />
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card className="p-6 border-slate-100 shadow-sm bg-white">
              <h3 className="text-lg font-black text-slate-900 mb-6">Algorithmic Performance</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <span className="font-black text-slate-700">Total Return</span>
                  <span className="font-black text-green-700">+{algoPerformance.totalReturn?.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                  <span className="font-black text-slate-700">Win Rate</span>
                  <span className="font-black text-blue-700">{algoPerformance.winRate?.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                  <span className="font-black text-slate-700">Sharpe Ratio</span>
                  <span className="font-black text-purple-700">{algoPerformance.sharpeRatio?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                  <span className="font-black text-slate-700">Max Drawdown</span>
                  <span className="font-black text-red-700">{algoPerformance.maxDrawdown?.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                  <span className="font-black text-slate-700">Trades Executed</span>
                  <span className="font-black text-slate-700">{algoPerformance.tradesExecuted}</span>
                </div>
              </div>
            </Card>

            <Card className="p-6 border-slate-100 shadow-sm bg-white">
              <h3 className="text-lg font-black text-slate-900 mb-6">Manual Performance</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                  <span className="font-black text-slate-700">Total Return</span>
                  <span className="font-black text-slate-700">{manualPerformance.totalReturn?.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                  <span className="font-black text-slate-700">Win Rate</span>
                  <span className="font-black text-slate-700">{manualPerformance.winRate?.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                  <span className="font-black text-slate-700">Sharpe Ratio</span>
                  <span className="font-black text-slate-700">{manualPerformance.sharpeRatio?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                  <span className="font-black text-slate-700">Max Drawdown</span>
                  <span className="font-black text-slate-700">{manualPerformance.maxDrawdown?.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                  <span className="font-black text-slate-700">Trades Executed</span>
                  <span className="font-black text-slate-700">{manualPerformance.tradesExecuted}</span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      )}

      {activeTab === 'comparison' && (
        <div className="space-y-8">
          <Card className="p-8 border-slate-100 shadow-sm bg-white">
            <h3 className="text-xl font-black text-slate-900 mb-6">Detailed Performance Comparison</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="text-left py-3 px-4 font-black text-slate-400 uppercase tracking-widest text-xs">Metric</th>
                    <th className="text-center py-3 px-4 font-black text-slate-400 uppercase tracking-widest text-xs">Algorithmic</th>
                    <th className="text-center py-3 px-4 font-black text-slate-400 uppercase tracking-widest text-xs">Manual</th>
                    <th className="text-center py-3 px-4 font-black text-slate-400 uppercase tracking-widest text-xs">Advantage</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-slate-100">
                    <td className="py-3 px-4 font-black text-slate-700">Total Return</td>
                    <td className="py-3 px-4 text-center font-black text-green-600">{algoPerformance.totalReturn?.toFixed(2)}%</td>
                    <td className="py-3 px-4 text-center font-black text-slate-600">{manualPerformance.totalReturn?.toFixed(2)}%</td>
                    <td className="py-3 px-4 text-center font-black text-green-600">+{returnDifference?.toFixed(2)}%</td>
                  </tr>
                  <tr className="border-b border-slate-100">
                    <td className="py-3 px-4 font-black text-slate-700">Win Rate</td>
                    <td className="py-3 px-4 text-center font-black text-green-600">{algoPerformance.winRate?.toFixed(1)}%</td>
                    <td className="py-3 px-4 text-center font-black text-slate-600">{manualPerformance.winRate?.toFixed(1)}%</td>
                    <td className="py-3 px-4 text-center font-black text-green-600">+{winRateDifference?.toFixed(1)}%</td>
                  </tr>
                  <tr className="border-b border-slate-100">
                    <td className="py-3 px-4 font-black text-slate-700">Sharpe Ratio</td>
                    <td className="py-3 px-4 text-center font-black text-green-600">{algoPerformance.sharpeRatio?.toFixed(2)}</td>
                    <td className="py-3 px-4 text-center font-black text-slate-600">{manualPerformance.sharpeRatio?.toFixed(2)}</td>
                    <td className="py-3 px-4 text-center font-black text-green-600">+{sharpeDifference?.toFixed(2)}</td>
                  </tr>
                  <tr className="border-b border-slate-100">
                    <td className="py-3 px-4 font-black text-slate-700">Max Drawdown</td>
                    <td className="py-3 px-4 text-center font-black text-green-600">{algoPerformance.maxDrawdown?.toFixed(2)}%</td>
                    <td className="py-3 px-4 text-center font-black text-slate-600">{manualPerformance.maxDrawdown?.toFixed(2)}%</td>
                    <td className="py-3 px-4 text-center font-black text-green-600">Better</td>
                  </tr>
                  <tr className="border-b border-slate-100">
                    <td className="py-3 px-4 font-black text-slate-700">Volatility</td>
                    <td className="py-3 px-4 text-center font-black text-green-600">{algoPerformance.volatility?.toFixed(2)}%</td>
                    <td className="py-3 px-4 text-center font-black text-slate-600">{manualPerformance.volatility?.toFixed(2)}%</td>
                    <td className="py-3 px-4 text-center font-black text-green-600">Lower</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 font-black text-slate-700">Trades Executed</td>
                    <td className="py-3 px-4 text-center font-black text-green-600">{algoPerformance.tradesExecuted}</td>
                    <td className="py-3 px-4 text-center font-black text-slate-600">{manualPerformance.tradesExecuted}</td>
                    <td className="py-3 px-4 text-center font-black text-green-600">More Active</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </Card>

          <Card className="p-6 border-slate-100 shadow-sm bg-white">
            <h3 className="text-lg font-black text-slate-900 mb-6">Key Performance Insights</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-start gap-3 p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                    <TrendingUp className="text-green-600" size={16} />
                  </div>
                  <div>
                    <h4 className="font-black text-green-800">Higher Returns</h4>
                    <p className="text-sm text-green-700 mt-1">
                      Algorithmic trading delivers {returnDifference?.toFixed(2)}% higher returns than manual trading
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                    <Target className="text-blue-600" size={16} />
                  </div>
                  <div>
                    <h4 className="font-black text-blue-800">Better Consistency</h4>
                    <p className="text-sm text-blue-700 mt-1">
                      Algorithmic trading has {winRateDifference?.toFixed(1)}% higher win rate than manual trading
                    </p>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-start gap-3 p-4 bg-purple-50 rounded-lg border border-purple-200">
                  <div className="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
                    <Zap className="text-purple-600" size={16} />
                  </div>
                  <div>
                    <h4 className="font-black text-purple-800">Risk-Adjusted Superiority</h4>
                    <p className="text-sm text-purple-700 mt-1">
                      Algorithmic trading has {sharpeDifference?.toFixed(2)} higher Sharpe ratio than manual trading
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-4 bg-red-50 rounded-lg border border-red-200">
                  <div className="h-8 w-8 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                    <Shield className="text-red-600" size={16} />
                  </div>
                  <div>
                    <h4 className="font-black text-red-800">Lower Risk</h4>
                    <p className="text-sm text-red-700 mt-1">
                      Algorithmic trading has {Math.abs(algoPerformance.maxDrawdown - manualPerformance.maxDrawdown)?.toFixed(2)}% lower maximum drawdown than manual trading
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'transactions' && (
        <div className="space-y-8">
          <Card className="p-8 border-slate-100 shadow-sm bg-white">
            <h3 className="text-xl font-black text-slate-900 mb-6">Transaction Statement</h3>
            <TransactionStatement transactions={transactionHistory} />
          </Card>
        </div>
      )}
    </div>
  );
}

export default InvestmentReports;