// frontend/src/pages/InvestmentDashboard.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { useAppData } from '../context/AppDataContext';
import { ConfidenceInvestmentCard } from '../components/ConfidenceInvestmentCard';
import { investmentService } from '../services/investmentService';
import { Card } from "../components/ui/card";
import { 
  DollarSign, 
  TrendingUp, 
  Activity, 
  Shield, 
  Zap, 
  Target,
  Brain,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';

export function InvestmentDashboard() {
  const { user, selectedUser } = useUser();
  const {
    summary,
    holdings: activeHoldings,
    loading,
    refreshAllData
  } = useAppData();

  const [investmentReadiness, setInvestmentReadiness] = useState({
    hasCash: false,
    hasHoldings: false,
    hasActiveStrategies: false,
    isReadyForInvestment: false,
    cashBalance: 0
  });

  const [strategyStatus, setStrategyStatus] = useState('IDLE');
  const [isLoading, setIsLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const navigate = useNavigate();

  // Load investment readiness status
  useEffect(() => {
    const loadInvestmentReadiness = async () => {
      const userId = selectedUser?.id || user?.id;
      if (!userId) return;

      try {
        const readiness = await investmentService.getInvestmentReadiness(userId);
        setInvestmentReadiness(readiness);
        
        // Set strategy status based on active strategies
        if (readiness.hasActiveStrategies) {
          setStrategyStatus('RUNNING');
        } else {
          setStrategyStatus('IDLE');
        }
      } catch (error) {
        console.error('Error loading investment readiness:', error);
      }
    };

    loadInvestmentReadiness();
  }, [user, selectedUser, summary]);

  // Handle strategy launch
  const handleLaunchStrategy = async () => {
    const userId = selectedUser?.id || user?.id;
    if (!userId) {
      alert('No user selected');
      return;
    }

    setIsLoading(true);
    
    try {
      await investmentService.launchStrategy(userId, {
        name: "Auto Steward Primary",
        symbol: "",
        status: "RUNNING",
        execution_mode: "PAPER_TRADING"
      });

      setStrategyStatus('RUNNING');
      setInvestmentReadiness(prev => ({
        ...prev,
        isReadyForInvestment: false,
        hasActiveStrategies: true
      }));
      
      setShowSuccess(true);
      setTimeout(() => {
        setShowSuccess(false);
        refreshAllData(); // Refresh all data to show new holdings
      }, 3000);
    } catch (error) {
      console.error('Error launching strategy:', error);
      alert('Failed to launch strategy: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="pb-8 space-y-8">
      {/* Success Message */}
      {showSuccess && (
        <div className="fixed top-4 right-4 z-50 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2 animate-fade-in">
          <CheckCircle size={20} />
          <span>Strategy launched successfully! Your investment is now active.</span>
        </div>
      )}

      {/* Header */}
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-slate-900 font-heading">
            Investment Dashboard
          </h1>
          <p className="text-slate-500 mt-1 uppercase text-[10px] font-bold tracking-widest leading-none">
            Intelligent Portfolio Management
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Total Value</p>
            <h2 className="text-2xl font-black text-slate-900 leading-none">
              ₹{(summary?.total_value || 0).toLocaleString()}
            </h2>
          </div>
        </div>
      </header>

      {/* Investment Readiness Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6 border-slate-100 shadow-sm bg-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-black text-slate-400 uppercase tracking-widest">Cash Available</p>
              <h3 className="text-2xl font-black text-slate-900 mt-1">
                ₹{(summary?.cash_balance || 0).toLocaleString()}
              </h3>
            </div>
            <div className={`h-12 w-12 rounded-xl flex items-center justify-center ${
              investmentReadiness.hasCash ? 'bg-green-100' : 'bg-slate-100'
            }`}>
              <DollarSign className={investmentReadiness.hasCash ? 'text-green-600' : 'text-slate-400'} size={24} />
            </div>
          </div>
        </Card>

        <Card className="p-6 border-slate-100 shadow-sm bg-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-black text-slate-400 uppercase tracking-widest">Stock Holdings</p>
              <h3 className="text-2xl font-black text-slate-900 mt-1">
                {activeHoldings?.length || 0}
              </h3>
            </div>
            <div className={`h-12 w-12 rounded-xl flex items-center justify-center ${
              investmentReadiness.hasHoldings ? 'bg-blue-100' : 'bg-slate-100'
            }`}>
              <Activity className={investmentReadiness.hasHoldings ? 'text-blue-600' : 'text-slate-400'} size={24} />
            </div>
          </div>
        </Card>

        <Card className="p-6 border-slate-100 shadow-sm bg-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-black text-slate-400 uppercase tracking-widest">Active Strategies</p>
              <h3 className="text-2xl font-black text-slate-900 mt-1">
                {investmentReadiness.hasActiveStrategies ? 'Yes' : 'None'}
              </h3>
            </div>
            <div className={`h-12 w-12 rounded-xl flex items-center justify-center ${
              investmentReadiness.hasActiveStrategies ? 'bg-purple-100' : 'bg-slate-100'
            }`}>
              <Zap className={investmentReadiness.hasActiveStrategies ? 'text-purple-600' : 'text-slate-400'} size={24} />
            </div>
          </div>
        </Card>

        <Card className="p-6 border-slate-100 shadow-sm bg-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-black text-slate-400 uppercase tracking-widest">Investment Ready</p>
              <h3 className="text-2xl font-black mt-1">
                {investmentReadiness.isReadyForInvestment ? (
                  <span className="text-green-600">Ready</span>
                ) : (
                  <span className="text-slate-400">Not Ready</span>
                )}
              </h3>
            </div>
            <div className={`h-12 w-12 rounded-xl flex items-center justify-center ${
              investmentReadiness.isReadyForInvestment ? 'bg-green-100' : 'bg-slate-100'
            }`}>
              {investmentReadiness.isReadyForInvestment ? (
                <CheckCircle className="text-green-600" size={24} />
              ) : (
                <AlertTriangle className="text-slate-400" size={24} />
              )}
            </div>
          </div>
        </Card>
      </div>

      {/* Confidence Investment Card - Only shows when ready for investment */}
      {investmentReadiness.isReadyForInvestment && (
        <ConfidenceInvestmentCard 
          cashBalance={summary?.cash_balance || 0}
          investedAmount={summary?.invested_amount || 0}
          onLaunchStrategy={handleLaunchStrategy}
          isLoading={isLoading}
          strategyStatus={strategyStatus}
          userRole={user?.role || 'TRADER'}
        />
      )}

      {/* Investment Status Card - Shows when not ready */}
      {!investmentReadiness.isReadyForInvestment && (
        <Card className="p-8 border-2 border-slate-200 bg-slate-50 shadow-lg">
          <div className="text-center">
            <div className="h-16 w-16 rounded-2xl bg-slate-200 flex items-center justify-center mx-auto mb-6">
              <Target className="text-slate-500" size={32} />
            </div>
            <h2 className="text-2xl font-black text-slate-900 mb-4">Investment Status</h2>
            
            {investmentReadiness.hasActiveStrategies ? (
              <div className="space-y-4">
                <p className="text-slate-600">
                  Your investment strategy is currently running and managing your portfolio.
                </p>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 inline-block">
                  <p className="font-black text-green-700">Auto-Investment ACTIVE</p>
                  <p className="text-sm text-green-600">Your funds are being actively managed</p>
                </div>
                <div className="mt-6">
                  <button 
                    onClick={() => navigate('/trading')}
                    className="bg-primary text-white px-6 py-3 rounded-xl font-black hover:opacity-90 transition-all"
                  >
                    View Strategy Details
                  </button>
                </div>
              </div>
            ) : investmentReadiness.hasHoldings ? (
              <div className="space-y-4">
                <p className="text-slate-600">
                  Your portfolio already contains investments.
                </p>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 inline-block">
                  <p className="font-black text-blue-700">Portfolio Active</p>
                  <p className="text-sm text-blue-600">You have {activeHoldings.length} stock holdings</p>
                </div>
                <div className="mt-6">
                  <button 
                    onClick={() => navigate('/portfolio')}
                    className="bg-primary text-white px-6 py-3 rounded-xl font-black hover:opacity-90 transition-all"
                  >
                    View Portfolio
                  </button>
                </div>
              </div>
            ) : investmentReadiness.hasCash ? (
              <div className="space-y-4">
                <p className="text-slate-600">
                  You have cash available but no active investments.
                </p>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 inline-block">
                  <p className="font-black text-yellow-700">Ready for Investment</p>
                  <p className="text-sm text-yellow-600">₹{(summary?.cash_balance || 0).toLocaleString()} available</p>
                </div>
                <div className="mt-6">
                  <button 
                    onClick={handleLaunchStrategy}
                    className="bg-primary text-white px-6 py-3 rounded-xl font-black hover:opacity-90 transition-all"
                  >
                    Launch Investment Strategy
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-slate-600">
                  No funds available for investment.
                </p>
                <div className="bg-slate-100 border border-slate-200 rounded-lg p-4 inline-block">
                  <p className="font-black text-slate-700">No Available Funds</p>
                  <p className="text-sm text-slate-600">Deposit funds to get started</p>
                </div>
                <div className="mt-6">
                  <button 
                    onClick={() => navigate('/portfolio')}
                    className="bg-primary text-white px-6 py-3 rounded-xl font-black hover:opacity-90 transition-all"
                  >
                    Deposit Funds
                  </button>
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Investment Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="p-6 border-slate-100 shadow-sm bg-white">
          <h3 className="text-lg font-black text-slate-900 mb-6">Investment Insights</h3>
          <div className="space-y-4">
            <div className="flex items-start gap-4 p-4 bg-slate-50 rounded-lg">
              <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center flex-shrink-0">
                <Brain size={20} className="text-green-600" />
              </div>
              <div>
                <h4 className="font-black text-slate-900">AI-Powered Allocation</h4>
                <p className="text-sm text-slate-600 mt-1">
                  Our steward AI continuously analyzes market conditions to optimize your portfolio allocation.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4 p-4 bg-slate-50 rounded-lg">
              <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                <Shield size={20} className="text-blue-600" />
              </div>
              <div>
                <h4 className="font-black text-slate-900">Risk Management</h4>
                <p className="text-sm text-slate-600 mt-1">
                  Automatic position sizing and stop-loss controls protect your investment capital.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4 p-4 bg-slate-50 rounded-lg">
              <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0">
                <TrendingUp size={20} className="text-purple-600" />
              </div>
              <div>
                <h4 className="font-black text-slate-900">Performance Tracking</h4>
                <p className="text-sm text-slate-600 mt-1">
                  Real-time performance metrics and detailed analytics for your investment strategy.
                </p>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6 border-slate-100 shadow-sm bg-white">
          <h3 className="text-lg font-black text-slate-900 mb-6">Next Steps</h3>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-white font-black text-sm">
                1
              </div>
              <div>
                <h4 className="font-black text-slate-900">Launch Strategy</h4>
                <p className="text-sm text-slate-600">
                  Click the button above to start your investment journey
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-black text-sm">
                2
              </div>
              <div>
                <h4 className="font-black text-slate-900">Monitor Performance</h4>
                <p className="text-sm text-slate-600">
                  Track your portfolio growth and strategy performance
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-black text-sm">
                3
              </div>
              <div>
                <h4 className="font-black text-slate-900">Adjust Strategy</h4>
                <p className="text-sm text-slate-600">
                  Fine-tune your investment approach based on performance
                </p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default InvestmentDashboard;