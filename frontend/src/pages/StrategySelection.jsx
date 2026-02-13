import React, { useState } from 'react';
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
  CheckCircle 
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { launchStrategy } from '../services/api';

const StrategySelectionPage = () => {
  const { user } = useUser();
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [deploymentStep, setDeploymentStep] = useState(0); // 0: selection, 1: configuration, 2: confirmation
  const [strategyParams, setStrategyParams] = useState({
    capitalAllocation: '',
    riskTolerance: 'medium',
    investmentHorizon: 'short',
    stopLoss: '5',
    takeProfit: '10'
  });

  const handleSelectStrategy = (strategy) => {
    setSelectedStrategy(strategy);
    setDeploymentStep(1); // Move to configuration step
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
        symbol: 'NIFTY', // Default symbol, could be configurable
        status: 'RUNNING',
        pnl: '0',
        drawdown: 0.0,
        execution_mode: 'PAPER_TRADING' // Default to paper trading
      };

      const result = await launchStrategy(user.id, strategyData);
      
      if (result) {
        setDeploymentStep(2); // Move to confirmation
        console.log('Strategy deployed successfully:', result);
      }
    } catch (error) {
      console.error('Error deploying strategy:', error);
      alert('Failed to deploy strategy: ' + error.message);
    }
  };

  const resetSelection = () => {
    setSelectedStrategy(null);
    setDeploymentStep(0);
    setStrategyParams({
      capitalAllocation: '',
      riskTolerance: 'medium',
      investmentHorizon: 'short',
      stopLoss: '5',
      takeProfit: '10'
    });
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center justify-center p-3 bg-primary/10 rounded-full">
          <Zap className="w-8 h-8 text-primary" />
        </div>
        <h1 className="text-3xl font-bold text-slate-900 font-heading">
          Algorithmic Strategy Selection
        </h1>
        <p className="text-slate-600 max-w-2xl mx-auto">
          Choose from our curated collection of proven algorithmic trading strategies. 
          Each strategy is designed for different market conditions and risk profiles.
        </p>
      </div>

      {/* Progress Steps */}
      <div className="flex justify-center">
        <div className="flex items-center space-x-4">
          {[
            { step: 0, label: 'Select Strategy', icon: Target },
            { step: 1, label: 'Configure', icon: Shield },
            { step: 2, label: 'Deploy', icon: TrendingUp }
          ].map((item, index) => (
            <div key={item.step} className="flex items-center">
              <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                deploymentStep >= item.step 
                  ? 'bg-primary border-primary text-white' 
                  : 'border-slate-200 text-slate-400'
              }`}>
                {deploymentStep > item.step ? (
                  <CheckCircle className="w-5 h-5" />
                ) : (
                  <item.icon className="w-5 h-5" />
                )}
              </div>
              {index < 2 && (
                <div className={`w-16 h-0.5 ${
                  deploymentStep > item.step ? 'bg-primary' : 'bg-slate-200'
                }`} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Strategy Selection Step */}
      {deploymentStep === 0 && (
        <div className="space-y-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Choose Your Strategy</h2>
            <p className="text-slate-600">Browse our collection of algorithmic trading strategies</p>
          </div>
          
          <AlgoStrategySelector 
            onSelectStrategy={handleSelectStrategy}
            selectedStrategy={selectedStrategy}
          />
        </div>
      )}

      {/* Configuration Step */}
      {deploymentStep === 1 && selectedStrategy && (
        <div className="space-y-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Configure {selectedStrategy.name}</h2>
            <p className="text-slate-600">Customize your strategy parameters</p>
          </div>

          <Card className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Strategy Info */}
              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-lg bg-gradient-to-r ${selectedStrategy.color} text-white`}>
                    {selectedStrategy.icon}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-slate-900">{selectedStrategy.name}</h3>
                    <p className="text-slate-600 mt-1">{selectedStrategy.description}</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-slate-50 rounded-lg">
                      <div className="text-sm text-slate-500">Risk Level</div>
                      <div className="font-bold text-slate-900">{selectedStrategy.riskLevel}</div>
                    </div>
                    <div className="p-4 bg-slate-50 rounded-lg">
                      <div className="text-sm text-slate-500">Avg Returns</div>
                      <div className="font-bold text-green-600">{selectedStrategy.avgReturns}</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-bold text-slate-900 mb-2">Features</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedStrategy.features.map((feature, idx) => (
                        <span key={idx} className="px-3 py-1 bg-primary/10 text-primary text-sm rounded-full">
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Configuration Form */}
              <div className="space-y-6">
                <h3 className="text-lg font-bold text-slate-900">Strategy Parameters</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-bold text-slate-700 mb-2">Capital Allocation</label>
                    <input
                      type="number"
                      value={strategyParams.capitalAllocation}
                      onChange={(e) => handleParamChange('capitalAllocation', e.target.value)}
                      placeholder="Enter amount to allocate"
                      className="w-full p-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-bold text-slate-700 mb-2">Risk Tolerance</label>
                    <select
                      value={strategyParams.riskTolerance}
                      onChange={(e) => handleParamChange('riskTolerance', e.target.value)}
                      className="w-full p-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                    >
                      <option value="low">Low Risk</option>
                      <option value="medium">Medium Risk</option>
                      <option value="high">High Risk</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-bold text-slate-700 mb-2">Investment Horizon</label>
                    <select
                      value={strategyParams.investmentHorizon}
                      onChange={(e) => handleParamChange('investmentHorizon', e.target.value)}
                      className="w-full p-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                    >
                      <option value="short">Short Term (1-3 months)</option>
                      <option value="medium">Medium Term (3-12 months)</option>
                      <option value="long">Long Term (1+ years)</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-slate-700 mb-2">Stop Loss (%)</label>
                      <input
                        type="number"
                        value={strategyParams.stopLoss}
                        onChange={(e) => handleParamChange('stopLoss', e.target.value)}
                        className="w-full p-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-slate-700 mb-2">Take Profit (%)</label>
                      <input
                        type="number"
                        value={strategyParams.takeProfit}
                        onChange={(e) => handleParamChange('takeProfit', e.target.value)}
                        className="w-full p-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex gap-4 pt-4">
                  <button
                    onClick={() => setDeploymentStep(0)}
                    className="flex-1 py-3 px-6 border border-slate-200 text-slate-700 rounded-lg font-bold hover:bg-slate-50 transition-colors"
                  >
                    Back
                  </button>
                  <button
                    onClick={handleDeploy}
                    className="flex-1 py-3 px-6 bg-primary text-white rounded-lg font-bold hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
                  >
                    Deploy Strategy <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Confirmation Step */}
      {deploymentStep === 2 && (
        <div className="text-center space-y-6">
          <div className="inline-flex items-center justify-center p-4 bg-green-100 rounded-full">
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900">Strategy Deployed Successfully!</h2>
          <p className="text-slate-600 max-w-md mx-auto">
            Your {selectedStrategy?.name} strategy has been successfully deployed and is now actively managing your investments.
          </p>
          
          <div className="max-w-md mx-auto p-6 bg-slate-50 rounded-xl">
            <div className="space-y-3 text-left">
              <div className="flex justify-between">
                <span className="text-slate-600">Strategy:</span>
                <span className="font-bold">{selectedStrategy?.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Status:</span>
                <span className="font-bold text-green-600">Active</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Risk Level:</span>
                <span className="font-bold">{selectedStrategy?.riskLevel}</span>
              </div>
            </div>
          </div>

          <div className="flex gap-4 justify-center">
            <button
              onClick={resetSelection}
              className="px-6 py-3 bg-primary text-white rounded-lg font-bold hover:opacity-90 transition-opacity"
            >
              Select Another Strategy
            </button>
            <Link
              to="/"
              className="px-6 py-3 border border-slate-200 text-slate-700 rounded-lg font-bold hover:bg-slate-50 transition-colors"
            >
              Go to Dashboard
            </Link>
            <Link
              to="/portfolio"
              className="px-6 py-3 border border-slate-200 text-slate-700 rounded-lg font-bold hover:bg-slate-50 transition-colors"
            >
              Go to Portfolio
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default StrategySelectionPage;
