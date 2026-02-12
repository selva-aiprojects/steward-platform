import React, { useState } from 'react';
import { Card } from '../components/ui/card';
import { Zap, TrendingUp, TrendingDown, DollarSign, Shield, Target, BarChart3, Clock } from 'lucide-react';

const AlgoStrategySelector = ({ onSelectStrategy, selectedStrategy }) => {
  const [activeTab, setActiveTab] = useState('all');

  // Predefined algorithmic strategies
  const strategies = [
    {
      id: 'momentum',
      name: 'Momentum Trader',
      type: 'momentum',
      category: 'equities',
      description: 'Capitalizes on the continuance of existing trends in the market',
      icon: <TrendingUp className="w-5 h-5" />,
      riskLevel: 'Medium',
      avgReturns: '+12.4%',
      avgWinRate: '68%',
      avgHoldingTime: '2-5 days',
      minCapital: '₹50,000',
      features: ['Trend following', 'Volume analysis', 'Breakout detection'],
      color: 'from-blue-500 to-cyan-500',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/20'
    },
    {
      id: 'mean-reversion',
      name: 'Mean Reversion',
      type: 'mean_reversion',
      category: 'equities',
      description: 'Exploits the tendency of prices to revert to their historical mean',
      icon: <TrendingDown className="w-5 h-5" />,
      riskLevel: 'Low',
      avgReturns: '+8.7%',
      avgWinRate: '72%',
      avgHoldingTime: '1-3 days',
      minCapital: '₹25,000',
      features: ['Statistical arbitrage', 'Bollinger bands', 'RSI signals'],
      color: 'from-green-500 to-emerald-500',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/20'
    },
    {
      id: 'breakout',
      name: 'Breakout Hunter',
      type: 'breakout',
      category: 'equities',
      description: 'Identifies stocks breaking out of key resistance/support levels',
      icon: <Zap className="w-5 h-5" />,
      riskLevel: 'High',
      avgReturns: '+18.2%',
      avgWinRate: '58%',
      avgHoldingTime: '1-2 days',
      minCapital: '₹75,000',
      features: ['Price pattern recognition', 'Volume confirmation', 'Stop loss'],
      color: 'from-purple-500 to-violet-500',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/20'
    },
    {
      id: 'swing-trade',
      name: 'Swing Trader',
      type: 'swing_trade',
      category: 'equities',
      description: 'Captures short to medium-term gains over several days to weeks',
      icon: <BarChart3 className="w-5 h-5" />,
      riskLevel: 'Medium',
      avgReturns: '+10.3%',
      avgWinRate: '65%',
      avgHoldingTime: '3-10 days',
      minCapital: '₹40,000',
      features: ['Technical indicators', 'Support/resistance', 'Risk management'],
      color: 'from-orange-500 to-amber-500',
      bgColor: 'bg-orange-500/10',
      borderColor: 'border-orange-500/20'
    },
    {
      id: 'options-straddle',
      name: 'Options Straddle',
      type: 'options_straddle',
      category: 'options',
      description: 'Neutral strategy profiting from high volatility regardless of direction',
      icon: <Target className="w-5 h-5" />,
      riskLevel: 'Medium-High',
      avgReturns: '+15.6%',
      avgWinRate: '62%',
      avgHoldingTime: '1-5 days',
      minCapital: '₹1,00,000',
      features: ['Volatility analysis', 'Delta neutral', 'Theta decay'],
      color: 'from-pink-500 to-rose-500',
      bgColor: 'bg-pink-500/10',
      borderColor: 'border-pink-500/20'
    },
    {
      id: 'pairs-trading',
      name: 'Pairs Trading',
      type: 'pairs_trading',
      category: 'equities',
      description: 'Exploits correlation between two related securities',
      icon: <DollarSign className="w-5 h-5" />,
      riskLevel: 'Low-Medium',
      avgReturns: '+9.1%',
      avgWinRate: '70%',
      avgHoldingTime: '1-2 weeks',
      minCapital: '₹60,000',
      features: ['Correlation analysis', 'Cointegration', 'Market neutral'],
      color: 'from-teal-500 to-cyan-500',
      bgColor: 'bg-teal-500/10',
      borderColor: 'border-teal-500/20'
    },
    {
      id: 'carry-trade',
      name: 'Carry Trade',
      type: 'carry_trade',
      category: 'currencies',
      description: 'Profits from interest rate differentials between currencies',
      icon: <Clock className="w-5 h-5" />,
      riskLevel: 'Medium',
      avgReturns: '+7.8%',
      avgWinRate: '75%',
      avgHoldingTime: '2-4 weeks',
      minCapital: '₹30,000',
      features: ['Interest rate analysis', 'Forward points', 'Risk hedging'],
      color: 'from-indigo-500 to-blue-500',
      bgColor: 'bg-indigo-500/10',
      borderColor: 'border-indigo-500/20'
    },
    {
      id: 'volatility',
      name: 'Volatility Capture',
      type: 'volatility',
      category: 'options',
      description: 'Capitalizes on periods of high market volatility',
      icon: <Shield className="w-5 h-5" />,
      riskLevel: 'High',
      avgReturns: '+22.1%',
      avgWinRate: '55%',
      avgHoldingTime: '1-3 days',
      minCapital: '₹1,50,000',
      features: ['VIX analysis', 'Implied volatility', 'Gamma scalping'],
      color: 'from-red-500 to-orange-500',
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/20'
    }
  ];

  const filteredStrategies = activeTab === 'all' 
    ? strategies 
    : strategies.filter(strategy => strategy.category === activeTab);

  const handleSelect = (strategy) => {
    onSelectStrategy(strategy);
  };

  const getRiskColor = (riskLevel) => {
    switch(riskLevel.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-red-600 bg-red-100';
      case 'low-medium': return 'text-amber-600 bg-amber-100';
      case 'medium-high': return 'text-orange-600 bg-orange-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6">
      {/* Category Tabs */}
      <div className="flex flex-wrap gap-2">
        {[
          { id: 'all', label: 'All Strategies' },
          { id: 'equities', label: 'Equities' },
          { id: 'options', label: 'Options' },
          { id: 'currencies', label: 'Currencies' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-primary text-white shadow-md'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Strategy Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredStrategies.map((strategy) => (
          <Card
            key={strategy.id}
            className={`p-5 cursor-pointer transition-all duration-300 border-2 ${
              selectedStrategy?.id === strategy.id
                ? 'ring-2 ring-primary ring-offset-2 border-primary'
                : strategy.borderColor
            } hover:shadow-lg hover:border-primary/40 ${
              selectedStrategy?.id === strategy.id ? strategy.bgColor : 'hover:bg-slate-50'
            }`}
            onClick={() => handleSelect(strategy)}
          >
            <div className="flex items-start justify-between mb-3">
              <div className={`p-2 rounded-lg bg-gradient-to-r ${strategy.color} text-white`}>
                {strategy.icon}
              </div>
              <div className={`px-2 py-1 rounded-full text-xs font-bold ${getRiskColor(strategy.riskLevel)}`}>
                {strategy.riskLevel}
              </div>
            </div>

            <h3 className="font-black text-slate-900 text-lg mb-2">{strategy.name}</h3>
            <p className="text-slate-600 text-sm mb-4 line-clamp-2">{strategy.description}</p>

            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Avg Returns:</span>
                <span className="font-black text-green-600">{strategy.avgReturns}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Win Rate:</span>
                <span className="font-black">{strategy.avgWinRate}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Holding Time:</span>
                <span className="font-black">{strategy.avgHoldingTime}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Min Capital:</span>
                <span className="font-black">{strategy.minCapital}</span>
              </div>
            </div>

            <div className="flex flex-wrap gap-1 mb-4">
              {strategy.features.slice(0, 2).map((feature, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 bg-slate-100 text-slate-600 text-xs rounded-md font-medium"
                >
                  {feature}
                </span>
              ))}
              {strategy.features.length > 2 && (
                <span className="px-2 py-1 bg-slate-100 text-slate-600 text-xs rounded-md font-medium">
                  +{strategy.features.length - 2} more
                </span>
              )}
            </div>

            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-500 uppercase tracking-widest font-bold">
                {strategy.category}
              </span>
              <div className={`w-4 h-4 rounded-full ${
                selectedStrategy?.id === strategy.id ? 'bg-primary' : 'bg-slate-300'
              }`} />
            </div>
          </Card>
        ))}
      </div>

      {/* Selected Strategy Details */}
      {selectedStrategy && (
        <Card className="p-6 border-primary/30 bg-gradient-to-r from-primary/5 to-slate-50">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-xl font-black text-slate-900 mb-2">
                Selected: {selectedStrategy.name}
              </h3>
              <p className="text-slate-600">{selectedStrategy.description}</p>
            </div>
            <button
              onClick={() => onSelectStrategy(null)}
              className="text-slate-400 hover:text-slate-600 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="text-center p-3 bg-white rounded-lg border">
              <div className="text-2xl font-black text-slate-900">{selectedStrategy.avgReturns}</div>
              <div className="text-xs text-slate-500 uppercase tracking-widest">Avg Returns</div>
            </div>
            <div className="text-center p-3 bg-white rounded-lg border">
              <div className="text-2xl font-black text-slate-900">{selectedStrategy.avgWinRate}</div>
              <div className="text-xs text-slate-500 uppercase tracking-widest">Win Rate</div>
            </div>
            <div className="text-center p-3 bg-white rounded-lg border">
              <div className="text-2xl font-black text-slate-900">{selectedStrategy.avgHoldingTime}</div>
              <div className="text-xs text-slate-500 uppercase tracking-widest">Holding Time</div>
            </div>
            <div className="text-center p-3 bg-white rounded-lg border">
              <div className="text-2xl font-black text-slate-900">{selectedStrategy.minCapital}</div>
              <div className="text-xs text-slate-500 uppercase tracking-widest">Min Capital</div>
            </div>
          </div>

          <div className="mb-4">
            <h4 className="font-black text-slate-900 mb-2">Strategy Features:</h4>
            <div className="flex flex-wrap gap-2">
              {selectedStrategy.features.map((feature, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-primary/10 text-primary text-sm rounded-full font-medium"
                >
                  {feature}
                </span>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-slate-200">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${
                selectedStrategy.riskLevel.toLowerCase().includes('low') ? 'bg-green-500' :
                selectedStrategy.riskLevel.toLowerCase().includes('medium') ? 'bg-yellow-500' :
                'bg-red-500'
              }`} />
              <span className="text-sm font-medium">Risk Level: {selectedStrategy.riskLevel}</span>
            </div>
            <button
              onClick={() => onSelectStrategy(selectedStrategy)}
              className="px-6 py-2 bg-primary text-white rounded-lg font-bold hover:opacity-90 transition-opacity"
            >
              Deploy Strategy
            </button>
          </div>
        </Card>
      )}
    </div>
  );
};

export default AlgoStrategySelector;