import React, { useState, useEffect } from 'react';
import AlgoStrategySelector from '../components/AlgoStrategySelector';
import { Card } from '../components/ui/card';
import {
  Shield,
  TrendingUp,
  Target,
  BarChart3,
  DollarSign,
  Zap,
  ArrowRight,
  CheckCircle,
  Cpu,
  Globe,
  Lock,
  ArrowLeft,
  ChevronRight,
  Info
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { launchStrategy } from '../services/api';

const StrategySelectionPage = () => {
  const { user } = useUser();
  const navigate = useNavigate();
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [deploymentStep, setDeploymentStep] = useState(0); // 0: selection, 1: configuration, 2: confirmation
  const [strategyParams, setStrategyParams] = useState({
    capitalAllocation: '50000',
    riskTolerance: 'medium',
    investmentHorizon: 'medium',
    stopLoss: '5',
    takeProfit: '15'
  });

  const handleSelectStrategy = (strategy) => {
    setSelectedStrategy(strategy);
    setDeploymentStep(1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleParamChange = (param, value) => {
    setStrategyParams(prev => ({
      ...prev,
      [param]: value
    }));
  };

  const handleDeploy = async () => {
    if (!user || !selectedStrategy) return;

    try {
      const strategyData = {
        user_id: user.id,
        name: selectedStrategy.name,
        symbol: selectedStrategy.category === 'indices' ? 'NIFTY' : 'RELIANCE',
        status: 'RUNNING',
        pnl: '0',
        drawdown: 0.0,
        execution_mode: 'PAPER_TRADING',
        metadata: {
          ...strategyParams,
          strategyId: selectedStrategy.id
        }
      };

      const result = await launchStrategy(user.id, strategyData);

      if (result) {
        setDeploymentStep(2);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    } catch (error) {
      console.error('Error deploying strategy:', error);
    }
  };

  const resetSelection = () => {
    setSelectedStrategy(null);
    setDeploymentStep(0);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 pb-20">
      {/* Premium Header */}
      <div className="relative overflow-hidden bg-slate-900 border-b border-slate-800 py-16 mb-12">
        <div className="absolute top-0 left-0 w-full h-full opacity-10">
          <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_50%,#3b82f6,transparent_50%)]" />
        </div>

        <div className="max-w-6xl mx-auto px-6 relative z-10">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="space-y-4 text-center md:text-left">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/20 border border-primary/30 text-primary text-[10px] font-black uppercase tracking-[0.2em]">
                <Cpu size={12} />
                Autonomous Engine v4.2
              </div>
              <h1 className="text-4xl md:text-5xl font-black text-white tracking-tighter leading-tight font-heading">
                ALGORITHMIC <span className="text-primary italic">MANDATES</span>
              </h1>
              <p className="text-slate-400 max-w-xl text-lg font-medium leading-relaxed">
                Deploy high-fidelity quantitative models across global markets.
                Secured by Steward AI risk-mitigation protocols.
              </p>
            </div>

            <div className="hidden lg:grid grid-cols-2 gap-4">
              <div className="p-4 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-sm">
                <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Total Deployed</div>
                <div className="text-2xl font-black text-white">₹ 4.2 Cr</div>
              </div>
              <div className="p-4 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-sm">
                <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Win Probability</div>
                <div className="text-2xl font-black text-green-400">72.4%</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6">
        {/* Progress Bar Alternative */}
        <div className="flex items-center gap-4 mb-12 overflow-x-auto pb-4 scrollbar-hide">
          {[
            { id: 0, label: 'Selection', icon: Target },
            { id: 1, label: 'Optimization', icon: Shield },
            { id: 2, label: 'Deployment', icon: Zap }
          ].map((step) => (
            <div key={step.id} className="flex items-center gap-4 group">
              <div className={`flex items-center gap-3 px-6 py-3 rounded-2xl border transition-all duration-300 ${deploymentStep === step.id
                ? 'bg-primary border-primary text-white shadow-[0_0_20px_rgba(59,130,246,0.3)]'
                : deploymentStep > step.id ? 'bg-green-500/10 border-green-500/30 text-green-400' : 'bg-slate-900 border-slate-800 text-slate-500'
                }`}>
                <step.icon size={18} className={deploymentStep === step.id ? 'animate-pulse' : ''} />
                <span className="text-xs font-black uppercase tracking-widest whitespace-nowrap">{step.label}</span>
              </div>
              {step.id < 2 && <ChevronRight size={16} className="text-slate-700" />}
            </div>
          ))}
        </div>

        {/* Dynamic Steps */}
        {deploymentStep === 0 && (
          <div className="space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-end justify-between border-b border-slate-800 pb-4">
              <div>
                <h2 className="text-2xl font-black text-white uppercase tracking-tight">Select Mandate</h2>
                <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">Choose a quantitative strategy to activate</p>
              </div>
            </div>

            <AlgoStrategySelector
              onSelectStrategy={handleSelectStrategy}
              selectedStrategy={selectedStrategy}
            />

            {/* Comparison Table */}
            <div className="pt-12">
              <h3 className="text-lg font-black text-white mb-6 uppercase tracking-widest">Mandate Comparison Matrix</h3>
              <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/50">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="bg-slate-900 text-slate-500 text-[10px] font-black uppercase tracking-widest">
                      <th className="px-6 py-4">Strategy</th>
                      <th className="px-6 py-4">Risk Profile</th>
                      <th className="px-6 py-4">Sharpe Ratio</th>
                      <th className="px-6 py-4">Max Drawdown</th>
                      <th className="px-6 py-4">Avg Hold</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {[
                      { name: 'Momentum Trader', risk: 'Medium', sharpe: '1.85', drawdown: '3.2%', hold: '2-5 Days' },
                      { name: 'Mean Reversion', risk: 'Low', sharpe: '1.42', drawdown: '1.8%', hold: '1-3 Days' },
                      { name: 'Breakout Hunter', risk: 'High', sharpe: '2.10', drawdown: '7.5%', hold: '1-2 Days' },
                    ].map((row, i) => (
                      <tr key={i} className="hover:bg-white/5 transition-colors">
                        <td className="px-6 py-4 font-black text-white">{row.name}</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-0.5 rounded-full text-[9px] font-black uppercase ${row.risk === 'Low' ? 'bg-green-500/20 text-green-400' : row.risk === 'High' ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'
                            }`}>
                            {row.risk}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-slate-300">{row.sharpe}</td>
                        <td className="px-6 py-4 text-slate-300">{row.drawdown}</td>
                        <td className="px-6 py-4 text-slate-300">{row.hold}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {deploymentStep === 1 && selectedStrategy && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 animate-in fade-in slide-in-from-right-4 duration-500">
            {/* Left: Summary */}
            <div className="lg:col-span-1 space-y-6">
              <button
                onClick={() => setDeploymentStep(0)}
                className="flex items-center gap-2 text-slate-500 hover:text-white transition-colors text-xs font-black uppercase tracking-widest mb-4"
              >
                <ArrowLeft size={14} />
                Change Selection
              </button>

              <Card className="p-8 bg-slate-900 border-slate-800 text-white relative overflow-hidden">
                <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${selectedStrategy.color} opacity-10 rounded-full -mr-16 -mt-16 blur-2xl`} />
                <div className={`p-3 w-fit rounded-2xl bg-gradient-to-r ${selectedStrategy.color} text-white mb-6`}>
                  {selectedStrategy.icon}
                </div>
                <h3 className="text-2xl font-black mb-2">{selectedStrategy.name}</h3>
                <p className="text-slate-400 text-sm leading-relaxed mb-8">{selectedStrategy.description}</p>

                <div className="grid grid-cols-2 gap-4 border-t border-slate-800 pt-8">
                  <div>
                    <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Expected Return</div>
                    <div className="text-xl font-black text-green-400">{selectedStrategy.avgReturns}</div>
                  </div>
                  <div>
                    <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Risk Rating</div>
                    <div className="text-xl font-black text-white">{selectedStrategy.riskLevel}</div>
                  </div>
                </div>
              </Card>

              <div className="p-6 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-start gap-4">
                <Info size={20} className="flex-shrink-0 mt-1" />
                <p className="text-xs font-medium leading-relaxed">
                  Historical performance does not guarantee future results. Steward AI employs circuit breakers at 3% intra-day drawdown levels to safeguard capital.
                </p>
              </div>
            </div>

            {/* Right: config */}
            <div className="lg:col-span-2 space-y-8">
              <div className="border-b border-slate-800 pb-4">
                <h2 className="text-2xl font-black text-white uppercase tracking-tight">Optimization Parameters</h2>
                <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">Fine-tune the execution engine</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-4">
                  <label className="block text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Capital Allocation (INR)</label>
                  <div className="relative">
                    <DollarSign size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                      type="number"
                      value={strategyParams.capitalAllocation}
                      onChange={(e) => handleParamChange('capitalAllocation', e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-2xl px-12 py-4 text-white font-black focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <label className="block text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Risk Tolerance</label>
                  <div className="grid grid-cols-3 gap-2">
                    {['low', 'medium', 'high'].map((lvl) => (
                      <button
                        key={lvl}
                        onClick={() => handleParamChange('riskTolerance', lvl)}
                        className={`py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${strategyParams.riskTolerance === lvl
                          ? 'bg-primary text-white border-primary shadow-lg shadow-primary/20'
                          : 'bg-slate-900 border border-slate-800 text-slate-500 hover:text-slate-300'
                          }`}
                      >
                        {lvl}
                      </button>
                    ))}
                  </div>
                  <div className="mt-2 text-[8px] font-bold text-slate-500 uppercase tracking-widest leading-relaxed">
                    {strategyParams.riskTolerance === 'low' && 'Defensive: Focuses on capital preservation with ~1-2% stop-loss strictness.'}
                    {strategyParams.riskTolerance === 'medium' && 'Balanced: Optimal risk-reward ratio with standard circuit breakers.'}
                    {strategyParams.riskTolerance === 'high' && 'Aggressive: Targets maximum alpha with wider volatility allowance.'}
                  </div>
                </div>

                <div className="space-y-4">
                  <label className="block text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Exit Protocol: Stop Loss</label>
                  <div className="flex items-center gap-4 bg-slate-900 border border-slate-800 p-4 rounded-2xl">
                    <input
                      type="range" min="1" max="15"
                      value={strategyParams.stopLoss}
                      onChange={(e) => handleParamChange('stopLoss', e.target.value)}
                      className="flex-1 accent-primary"
                    />
                    <span className="text-xl font-black text-white w-12 text-right">{strategyParams.stopLoss}%</span>
                  </div>
                </div>

                <div className="space-y-4">
                  <label className="block text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Exit Protocol: Take Profit</label>
                  <div className="flex items-center gap-4 bg-slate-900 border border-slate-800 p-4 rounded-2xl">
                    <input
                      type="range" min="5" max="50"
                      value={strategyParams.takeProfit}
                      onChange={(e) => handleParamChange('takeProfit', e.target.value)}
                      className="flex-1 accent-green-500"
                    />
                    <span className="text-xl font-black text-white w-12 text-right">{strategyParams.takeProfit}%</span>
                  </div>
                </div>
              </div>

              <div className="pt-8 flex justify-end">
                <button
                  onClick={handleDeploy}
                  disabled={!strategyParams.capitalAllocation}
                  className="px-12 py-5 bg-primary hover:bg-primary/90 text-white rounded-2xl font-black text-xs uppercase tracking-[0.3em] transition-all flex items-center gap-3 shadow-2xl shadow-primary/40 active:scale-95 disabled:opacity-50"
                >
                  Confirm & Deploy
                  <Zap size={16} fill="currentColor" className="animate-pulse" />
                </button>
              </div>
            </div>
          </div>
        )}

        {deploymentStep === 2 && (
          <div className="max-w-2xl mx-auto py-12 animate-in fade-in zoom-in-95 duration-700">
            <Card className="p-12 bg-slate-900 border-slate-800 text-center relative overflow-hidden">
              <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-64 bg-green-500/10 rounded-full blur-3xl -mt-32" />

              <div className="inline-flex items-center justify-center h-24 w-24 rounded-full bg-green-500/10 border border-green-500/20 text-green-400 mb-8 relative z-10">
                <CheckCircle size={48} />
              </div>

              <h2 className="text-3xl font-black text-white uppercase tracking-tight mb-4">Mandate Successfully Activated</h2>
              <p className="text-slate-400 font-medium mb-12">
                All systems nominal. The {selectedStrategy?.name} engine is now live and executing according to your parameters.
              </p>

              <div className="grid grid-cols-2 gap-4 mb-12">
                <div className="p-6 rounded-2xl bg-white/5 border border-white/10 text-left">
                  <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Portfolio Impact</div>
                  <div className="text-lg font-black text-white">Active Allocation</div>
                </div>
                <div className="p-6 rounded-2xl bg-white/5 border border-white/10 text-left">
                  <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Engine Status</div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-lg font-black text-green-400">EXECUTING</span>
                  </div>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => navigate('/')}
                  className="flex-1 px-8 py-4 bg-primary text-white rounded-2xl font-black text-xs uppercase tracking-widest hover:opacity-90 shadow-lg shadow-primary/20 transition-all active:scale-95"
                >
                  Return to Dashboard
                </button>
                <Link to="/portfolio" className="flex-1 px-8 py-4 bg-slate-800 text-white rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-slate-700 transition-all">
                  Manage Holdings
                </Link>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default StrategySelectionPage;
