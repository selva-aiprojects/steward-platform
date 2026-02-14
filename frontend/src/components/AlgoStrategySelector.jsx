import React, { useState } from 'react';
import { Card } from '../components/ui/card';
import {
  Zap,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Shield,
  Target,
  BarChart3,
  Clock,
  Sparkles,
  Activity,
  Layers
} from 'lucide-react';

const AlgoStrategySelector = ({ onSelectStrategy, selectedStrategy }) => {
  const [activeTab, setActiveTab] = useState('all');

  // Predefined algorithmic strategies with enhanced realistic metadata
  const strategies = [
    {
      id: 'momentum',
      name: 'Alpha Momentum',
      type: 'momentum',
      category: 'equities',
      description: 'Quant-driven trend following identifying relative strength anomalies in Nifty 50 constituents.',
      icon: <TrendingUp className="w-5 h-5" />,
      riskLevel: 'Medium',
      avgReturns: '22.4% p.a.',
      avgWinRate: '64%',
      avgHoldingTime: '2-5 days',
      minCapital: '₹1.0L',
      features: ['VWAP Alignment', 'ADX Strength', 'Order Flow Filter'],
      color: 'from-blue-600 to-indigo-600',
      bgColor: 'bg-blue-600/10',
      borderColor: 'border-blue-600/20'
    },
    {
      id: 'mean-reversion',
      name: 'Statistical Arbitrage',
      type: 'mean_reversion',
      category: 'equities',
      description: 'Exploits price divergence from historical Z-score means using pair correlation models.',
      icon: <Layers className="w-5 h-5" />,
      riskLevel: 'Low',
      avgReturns: '14.7% p.a.',
      avgWinRate: '72%',
      avgHoldingTime: '1-3 days',
      minCapital: '₹2.5L',
      features: ['Cointegration', 'Mean Convergence', 'Market Neutral'],
      color: 'from-emerald-600 to-teal-600',
      bgColor: 'bg-emerald-600/10',
      borderColor: 'border-emerald-600/20'
    },
    {
      id: 'breakout',
      name: 'Volatility Hunter',
      type: 'breakout',
      category: 'equities',
      description: 'Aggressive capture of multi-session consolidation breakouts with high volume confirmation.',
      icon: <Zap className="w-5 h-5" />,
      riskLevel: 'High',
      avgReturns: '32.2% p.a.',
      avgWinRate: '52%',
      avgHoldingTime: '1 day',
      minCapital: '₹75k',
      features: ['Range Expansion', 'Pocket Pivot', 'Tight Stop-Loss'],
      color: 'from-orange-600 to-red-600',
      bgColor: 'bg-orange-600/10',
      borderColor: 'border-orange-600/20'
    },
    {
      id: 'options-income',
      name: 'Theta Harvester',
      type: 'options',
      category: 'options',
      description: 'Delta-neutral option selling with dynamic gamma hedging for consistent decay capture.',
      icon: <Clock className="w-5 h-5" />,
      riskLevel: 'Medium-High',
      avgReturns: '28.6% p.a.',
      avgWinRate: '78%',
      avgHoldingTime: 'Weekly',
      minCapital: '₹5.0L',
      features: ['Straddle Optimization', 'VIX Sensitivity', 'Dynamic Rolling'],
      color: 'from-purple-600 to-indigo-600',
      bgColor: 'bg-purple-600/10',
      borderColor: 'border-purple-600/20'
    },
    {
      id: 'carry-trade',
      name: 'Currency Carry',
      type: 'carry',
      category: 'currencies',
      description: 'Interest rate differential capture across USD/INR and major pairs with macro hedging.',
      icon: <Globe className="w-5 h-5" />,
      riskLevel: 'Medium',
      avgReturns: '9.8% p.a.',
      avgWinRate: '82%',
      avgHoldingTime: 'Monthly',
      minCapital: '₹50k',
      features: ['Swap Rate Arb', 'Macro Alignment', 'Low Volatile Yield'],
      color: 'from-sky-600 to-cyan-600',
      bgColor: 'bg-sky-600/10',
      borderColor: 'border-sky-600/20'
    },
    {
      id: 'indices-scalp',
      name: 'Flash Index Scalper',
      type: 'scalping',
      category: 'indices',
      description: 'Ultra high-frequency execution targeting tick-level momentum on BankNifty / Nifty.',
      icon: <Activity className="w-5 h-5" />,
      riskLevel: 'High',
      avgReturns: '45.1% p.a.',
      avgWinRate: '58%',
      avgHoldingTime: 'Minutes',
      minCapital: '₹1.5L',
      features: ['L2 Order Flow', 'Flash Execution', 'Hedge Guard'],
      color: 'from-rose-600 to-pink-600',
      bgColor: 'bg-rose-600/10',
      borderColor: 'border-rose-600/20'
    }
  ];

  const filteredStrategies = activeTab === 'all'
    ? strategies
    : strategies.filter(strategy => strategy.category === activeTab);

  return (
    <div className="space-y-8">
      {/* Premium Glass Tabs */}
      <div className="flex items-center p-1.5 bg-white/5 border border-white/10 rounded-2xl w-fit">
        {[
          { id: 'all', label: 'All Models' },
          { id: 'equities', label: 'Equities' },
          { id: 'options', label: 'Options' },
          { id: 'indices', label: 'Indices' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 ${activeTab === tab.id
                ? 'bg-primary text-white shadow-lg shadow-primary/20 scale-105'
                : 'text-slate-500 hover:text-slate-300'
              }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredStrategies.map((strategy) => (
          <div
            key={strategy.id}
            onClick={() => onSelectStrategy(strategy)}
            className={`group relative overflow-hidden p-6 rounded-3xl border transition-all duration-500 cursor-pointer ${selectedStrategy?.id === strategy.id
                ? `${strategy.borderColor} bg-white/5 ring-1 ring-primary/30 shadow-[0_0_30px_rgba(59,130,246,0.1)]`
                : 'border-slate-800 bg-slate-900/40 hover:border-slate-700 hover:bg-slate-900'
              }`}
          >
            {/* Hover Shine Effect */}
            <div className="absolute top-0 -left-[100%] group-hover:left-[100%] w-full h-full bg-gradient-to-r from-transparent via-white/5 to-transparent skew-x-[-25deg] transition-all duration-1000" />

            <div className="flex justify-between items-start mb-6">
              <div className={`p-3 rounded-2xl bg-gradient-to-br ${strategy.color} text-white shadow-lg`}>
                {strategy.icon}
              </div>
              <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[8px] font-black uppercase tracking-tighter ${strategy.riskLevel.includes('High') ? 'bg-red-500/10 text-red-500' :
                  strategy.riskLevel.includes('Low') ? 'bg-green-500/10 text-green-500' : 'bg-amber-500/10 text-amber-500'
                }`}>
                <Shield size={10} />
                {strategy.riskLevel}
              </div>
            </div>

            <h3 className="text-xl font-black text-white mb-2 leading-tight">
              {strategy.name}
            </h3>
            <p className="text-slate-400 text-xs leading-relaxed mb-6 line-clamp-2">
              {strategy.description}
            </p>

            <div className="grid grid-cols-2 gap-y-4 gap-x-6 mb-6">
              <div>
                <div className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">Target Yield</div>
                <div className="text-sm font-black text-white">{strategy.avgReturns}</div>
              </div>
              <div>
                <div className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">Success Rate</div>
                <div className="text-sm font-black text-slate-200">{strategy.avgWinRate}</div>
              </div>
            </div>

            <div className="flex flex-wrap gap-1.5 mb-8">
              {strategy.features.map((f, i) => (
                <span key={i} className="px-2 py-0.5 rounded-md bg-white/5 text-[8px] font-bold text-slate-500 uppercase tracking-widest">
                  {f}
                </span>
              ))}
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-slate-800/50">
              <div>
                <div className="text-[8px] font-black text-slate-500 uppercase tracking-widest">Min Capital</div>
                <div className="text-xs font-black text-white">{strategy.minCapital}</div>
              </div>
              <button
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all ${selectedStrategy?.id === strategy.id
                    ? 'bg-primary text-white'
                    : 'bg-slate-800 text-slate-400 group-hover:bg-slate-700 group-hover:text-white'
                  }`}
              >
                {selectedStrategy?.id === strategy.id ? 'Optimizing...' : 'Deploy'}
                <ChevronRight size={12} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Internal icon for consistency
const ChevronRight = ({ size, ...props }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <polyline points="9 18 15 12 9 6"></polyline>
  </svg>
);

const Globe = ({ size, ...props }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <circle cx="12" cy="12" r="10"></circle>
    <line x1="2" y1="12" x2="22" y2="12"></line>
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
  </svg>
);

export default AlgoStrategySelector;