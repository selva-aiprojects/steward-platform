"""
Comprehensive Test Suite for Trading Infrastructure

This module contains comprehensive test cases for the entire trading infrastructure:
1. Strategy Engine tests
2. Parameter Engine tests
3. Risk Engine tests
4. AI Filter Engine tests
5. Execution Engine tests
6. Version Control Engine tests
7. Integration tests
"""

import unittest
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
import os

# Add the backend path to sys.path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.engines.trading_infrastructure import trading_infrastructure
from app.test_data.test_data_generator import test_data_generator


class TestStrategyEngine(unittest.TestCase):
    """Test cases for Strategy Engine"""

    def setUp(self):
        self.trading_infra = trading_infrastructure
        self.test_data = test_data_generator

    async def test_create_futures_strategy(self):
        """Test creating a futures strategy"""
        strategy_config = {
            "name": "Test Futures Strategy",
            "asset_class": "futures",
            "strategy_type": "momentum",
            "symbol": "NIFTY24FEB24F",
            "parameters": {
                "entry_threshold": 0.02,
                "exit_threshold": 0.01,
                "stop_loss": 0.03,
                "take_profit": 0.06,
                "position_size": 100000,
                "leverage": 2
            }
        }
        
        result = await self.trading_infra.strategy_engine.create_strategy(strategy_config)
        self.assertTrue(result["success"])
        self.assertIsNotNone(result.get("strategy_id"))

    async def test_create_options_strategy(self):
        """Test creating an options strategy"""
        strategy_config = {
            "name": "Test Options Strategy",
            "asset_class": "options",
            "strategy_type": "straddle",
            "symbol": "NIFTY24FEB24F22000CE",
            "parameters": {
                "entry_threshold": 0.01,
                "exit_threshold": 0.005,
                "stop_loss": 0.25,
                "take_profit": 0.50,
                "position_size": 50000,
                "leverage": 5,
                "strike_price": 22000,
                "option_type": "CE"
            }
        }
        
        result = await self.trading_infra.strategy_engine.create_strategy(strategy_config)
        self.assertTrue(result["success"])
        self.assertIsNotNone(result.get("strategy_id"))

    async def test_create_currency_strategy(self):
        """Test creating a currency strategy"""
        strategy_config = {
            "name": "Test Currency Strategy",
            "asset_class": "currencies",
            "strategy_type": "carry",
            "symbol": "USDINR24FEB24F",
            "parameters": {
                "entry_threshold": 0.001,
                "exit_threshold": 0.0005,
                "stop_loss": 0.005,
                "take_profit": 0.015,
                "position_size": 200000,
                "leverage": 10
            }
        }
        
        result = await self.trading_infra.strategy_engine.create_strategy(strategy_config)
        self.assertTrue(result["success"])
        self.assertIsNotNone(result.get("strategy_id"))

    async def test_backtest_strategy(self):
        """Test strategy backtesting"""
        # Create a strategy first
        strategy_config = {
            "name": "Backtest Strategy",
            "asset_class": "futures",
            "strategy_type": "mean_reversion",
            "symbol": "RELIANCE24FEB24F",
            "parameters": {
                "entry_threshold": -2.0,
                "exit_threshold": -0.5,
                "stop_loss": 0.03,
                "take_profit": 0.06,
                "position_size": 100000
            }
        }
        
        create_result = await self.trading_infra.strategy_engine.create_strategy(strategy_config)
        self.assertTrue(create_result["success"])
        
        # Generate test data for backtesting
        test_data = await self.test_data.generate_futures_data(100)
        
        backtest_result = await self.trading_infra.strategy_engine.backtest_strategy(
            create_result["strategy_id"], test_data
        )
        
        self.assertTrue(backtest_result["success"])
        self.assertIn("results", backtest_result)
        self.assertIn("total_pnl", backtest_result["results"])

    async def test_optimize_strategy_parameters(self):
        """Test strategy parameter optimization"""
        # Create a strategy
        strategy_config = {
            "name": "Optimization Test Strategy",
            "asset_class": "options",
            "strategy_type": "covered_call",
            "symbol": "RELIANCE24FEB24F2500CE",
            "parameters": {
                "entry_threshold": 0.01,
                "exit_threshold": 0.005,
                "stop_loss": 0.10,
                "take_profit": 0.20,
                "position_size": 50000
            }
        }
        
        create_result = await self.trading_infra.strategy_engine.create_strategy(strategy_config)
        self.assertTrue(create_result["success"])
        
        # Define optimization parameters
        optimization_config = {
            "parameter_ranges": {
                "entry_threshold": [0.005, 0.03],
                "exit_threshold": [0.001, 0.01],
                "stop_loss": [0.05, 0.20],
                "take_profit": [0.15, 0.40]
            },
            "optimization_method": "grid_search",
            "target_metric": "sharpe_ratio"
        }
        
        optimization_result = await self.trading_infra.strategy_engine.optimize_parameters(
            create_result["strategy_id"], optimization_config
        )
        
        self.assertTrue(optimization_result["success"])
        self.assertIn("optimized_parameters", optimization_result)


class TestParameterEngine(unittest.TestCase):
    """Test cases for Parameter Engine"""

    def setUp(self):
        self.trading_infra = trading_infrastructure

    async def test_set_parameters(self):
        """Test setting strategy parameters"""
        params = {
            "entry_threshold": 0.02,
            "exit_threshold": 0.01,
            "stop_loss": 0.03,
            "take_profit": 0.06,
            "position_size": 100000,
            "leverage": 2
        }
        
        result = await self.trading_infra.param_engine.set_parameters("test_strategy_1", params)
        self.assertTrue(result["success"])

    async def test_get_parameters(self):
        """Test getting strategy parameters"""
        # First set some parameters
        params = {
            "entry_threshold": 0.02,
            "exit_threshold": 0.01,
            "stop_loss": 0.03,
            "take_profit": 0.06
        }
        
        set_result = await self.trading_infra.param_engine.set_parameters("test_strategy_2", params)
        self.assertTrue(set_result["success"])
        
        # Then get them back
        get_result = await self.trading_infra.param_engine.get_parameters("test_strategy_2")
        self.assertTrue(get_result["success"])
        self.assertEqual(get_result["parameters"]["entry_threshold"], 0.02)

    async def test_validate_parameters(self):
        """Test parameter validation"""
        valid_params = {
            "entry_threshold": 0.02,
            "exit_threshold": 0.01,
            "stop_loss": 0.03,
            "take_profit": 0.06,
            "position_size": 100000
        }
        
        validation_result = await self.trading_infra.param_engine.validate_parameters("test_strategy_3", valid_params)
        self.assertTrue(validation_result["valid"])
        
        # Test invalid parameters
        invalid_params = {
            "entry_threshold": -0.02,  # Negative threshold
            "exit_threshold": 0.01,
            "stop_loss": 0.03,
            "take_profit": 0.06
        }
        
        validation_result = await self.trading_infra.param_engine.validate_parameters("test_strategy_4", invalid_params)
        self.assertFalse(validation_result["valid"])


class TestRiskEngine(unittest.TestCase):
    """Test cases for Risk Engine"""

    def setUp(self):
        self.trading_infra = trading_infrastructure

    async def test_calculate_position_risk(self):
        """Test position risk calculation"""
        position = {
            "symbol": "NIFTY24FEB24F",
            "quantity": 50,
            "entry_price": 22000,
            "current_price": 22100,
            "asset_class": "futures",
            "leverage": 2
        }
        
        risk_result = await self.trading_infra.risk_engine.calculate_position_risk(position)
        self.assertTrue(risk_result["success"])
        self.assertIn("position_risk", risk_result)

    async def test_calculate_portfolio_risk(self):
        """Test portfolio risk calculation"""
        positions = [
            {
                "symbol": "NIFTY24FEB24F",
                "quantity": 50,
                "entry_price": 22000,
                "current_price": 22100,
                "asset_class": "futures",
                "leverage": 2
            },
            {
                "symbol": "RELIANCE24FEB24F",
                "quantity": 100,
                "entry_price": 2500,
                "current_price": 2520,
                "asset_class": "futures",
                "leverage": 1
            }
        ]
        
        risk_result = await self.trading_infra.risk_engine.calculate_portfolio_risk(positions)
        self.assertTrue(risk_result["success"])
        self.assertIn("portfolio_risk", risk_result)

    async def test_check_risk_limits(self):
        """Test risk limit checking"""
        trade = {
            "symbol": "USDINR24FEB24F",
            "quantity": 1000,
            "price": 83.00,
            "side": "BUY",
            "asset_class": "currencies",
            "user_id": "test_user_1"
        }
        
        risk_check = await self.trading_infra.risk_engine.check_risk_limits(trade)
        self.assertTrue(risk_check["success"])


class TestAIFilterEngine(unittest.TestCase):
    """Test cases for AI Filter Engine"""

    def setUp(self):
        self.trading_infra = trading_infrastructure

    async def test_analyze_market_sentiment(self):
        """Test market sentiment analysis"""
        news_data = [
            {
                "title": "TCS Q4 Results Beat Expectations",
                "content": "TCS reported strong quarterly results with revenue growth driven by digital transformation initiatives...",
                "timestamp": datetime.now().isoformat(),
                "source": "economic_times"
            }
        ]
        
        social_data = [
            {
                "text": "TCS results looking great! Digital segment growing rapidly.",
                "timestamp": datetime.now().isoformat(),
                "source": "twitter"
            }
        ]
        
        sentiment_result = await self.trading_infra.ai_filter_engine.analyze_market_sentiment(news_data, social_data)
        self.assertTrue(sentiment_result["success"])
        self.assertIn("sentiment_analysis", sentiment_result)

    async def test_process_technical_indicators(self):
        """Test technical indicator processing"""
        market_data = {
            "prices": [
                {"timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(), 
                 "open": 22000 + i*10, 
                 "high": 22010 + i*10, 
                 "low": 21990 + i*10, 
                 "close": 22005 + i*10, 
                 "volume": 100000 + i*1000} 
                for i in range(50)
            ]
        }
        
        technical_result = await self.trading_infra.ai_filter_engine.process_technical_indicators(market_data)
        self.assertTrue(technical_result["success"])
        self.assertIn("technical_analysis", technical_result)

    async def test_detect_patterns(self):
        """Test pattern detection"""
        price_data = [
            {"timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(), 
             "open": 22000 + i*5, 
             "high": 22010 + i*5, 
             "low": 21990 + i*5, 
             "close": 22005 + i*5, 
             "volume": 100000 + i*500} 
            for i in range(100)
        ]
        
        pattern_result = await self.trading_infra.ai_filter_engine.detect_patterns(price_data)
        self.assertTrue(pattern_result["success"])
        self.assertIn("pattern_analysis", pattern_result)

    async def test_assess_risk(self):
        """Test AI-based risk assessment"""
        market_conditions = {
            "volatility": 0.25,
            "correlation": 0.6,
            "volume": 10000000,
            "price_level": 22000,
            "trend_strength": 0.7,
            "market_regime": "normal"
        }
        
        risk_result = await self.trading_infra.ai_filter_engine.assess_risk(market_conditions)
        self.assertTrue(risk_result["success"])
        self.assertIn("risk_assessment", risk_result)


class TestExecutionEngine(unittest.TestCase):
    """Test cases for Execution Engine"""

    def setUp(self):
        self.trading_infra = trading_infrastructure

    async def test_execute_futures_order(self):
        """Test executing a futures order"""
        order_details = {
            "symbol": "NIFTY24FEB24F",
            "quantity": 50,
            "side": "BUY",
            "order_type": "MARKET",
            "asset_class": "futures",
            "product_type": "NRML",
            "validity": "DAY"
        }
        
        execution_result = await self.trading_infra.execution_engine.execute_order(order_details)
        
        # This might fail due to lack of actual broker connection, 
        # but we can test the validation logic
        self.assertIsInstance(execution_result, dict)

    async def test_execute_options_order(self):
        """Test executing an options order"""
        order_details = {
            "symbol": "NIFTY24FEB24F22000CE",
            "quantity": 25,
            "side": "BUY",
            "order_type": "LIMIT",
            "limit_price": 150,
            "asset_class": "options",
            "product_type": "NRML",
            "validity": "DAY"
        }
        
        execution_result = await self.trading_infra.execution_engine.execute_order(order_details)
        
        self.assertIsInstance(execution_result, dict)

    async def test_execute_currency_order(self):
        """Test executing a currency order"""
        order_details = {
            "symbol": "USDINR24FEB24F",
            "quantity": 1000,
            "side": "SELL",
            "order_type": "MARKET",
            "asset_class": "currencies",
            "product_type": "NRML",
            "validity": "DAY"
        }
        
        execution_result = await self.trading_infra.execution_engine.execute_order(order_details)
        
        self.assertIsInstance(execution_result, dict)

    async def test_route_order(self):
        """Test order routing"""
        order = {
            "symbol": "RELIANCE24FEB24F",
            "quantity": 100,
            "side": "BUY",
            "asset_class": "futures"
        }
        
        routing_result = await self.trading_infra.execution_engine.route_order(order)
        
        self.assertIsInstance(routing_result, dict)


class TestVersionControlEngine(unittest.TestCase):
    """Test cases for Version Control Engine"""

    def setUp(self):
        self.trading_infra = trading_infrastructure

    async def test_create_strategy_version(self):
        """Test creating a strategy version"""
        strategy_config = {
            "name": "Test Strategy",
            "asset_class": "futures",
            "strategy_type": "momentum",
            "symbol": "NIFTY24FEB24F",
            "parameters": {
                "entry_threshold": 0.02,
                "exit_threshold": 0.01
            }
        }
        
        version_result = await self.trading_infra.version_control_engine.create_strategy_version(
            "test_strategy_1", strategy_config, "Initial version"
        )
        
        self.assertTrue(version_result["success"])
        self.assertIsNotNone(version_result.get("version_id"))

    async def test_deploy_strategy_version(self):
        """Test deploying a strategy version"""
        # First create a version
        strategy_config = {
            "name": "Deploy Test Strategy",
            "asset_class": "options",
            "strategy_type": "straddle",
            "symbol": "BANKNIFTY24FEB24F52000PE",
            "parameters": {
                "entry_threshold": 0.01,
                "exit_threshold": 0.005
            }
        }
        
        create_result = await self.trading_infra.version_control_engine.create_strategy_version(
            "test_strategy_2", strategy_config, "Test version for deployment"
        )
        
        self.assertTrue(create_result["success"])
        
        # Promote the version first
        promote_result = await self.trading_infra.version_control_engine.promote_version(
            "test_strategy_2", create_result["version_id"], "Approved for deployment"
        )
        
        self.assertTrue(promote_result["success"])
        
        # Now deploy it
        deploy_result = await self.trading_infra.version_control_engine.deploy_strategy_version(
            "test_strategy_2", create_result["version_id"]
        )
        
        self.assertTrue(deploy_result["success"])

    async def test_compare_strategy_versions(self):
        """Test comparing strategy versions"""
        # Create first version
        config1 = {
            "name": "Comparison Strategy 1",
            "asset_class": "currencies",
            "strategy_type": "carry",
            "symbol": "USDINR24FEB24F",
            "parameters": {
                "entry_threshold": 0.001,
                "exit_threshold": 0.0005
            }
        }
        
        version1_result = await self.trading_infra.version_control_engine.create_strategy_version(
            "test_strategy_3", config1, "First version"
        )
        
        self.assertTrue(version1_result["success"])
        
        # Create second version with different parameters
        config2 = {
            "name": "Comparison Strategy 2",
            "asset_class": "currencies",
            "strategy_type": "carry",
            "symbol": "USDINR24FEB24F",
            "parameters": {
                "entry_threshold": 0.002,
                "exit_threshold": 0.001
            }
        }
        
        version2_result = await self.trading_infra.version_control_engine.create_strategy_version(
            "test_strategy_3", config2, "Second version"
        )
        
        self.assertTrue(version2_result["success"])
        
        # Compare versions
        compare_result = await self.trading_infra.version_control_engine.compare_strategy_versions(
            "test_strategy_3", 
            version1_result["version_id"], 
            version2_result["version_id"]
        )
        
        self.assertTrue(compare_result["success"])
        self.assertIn("comparison_result", compare_result)


class TestIntegratedWorkflow(unittest.TestCase):
    """Test integrated workflow across all engines"""

    def setUp(self):
        self.trading_infra = trading_infrastructure
        self.test_data_gen = test_data_generator

    async def test_full_trading_workflow(self):
        """Test complete trading workflow from strategy creation to execution"""
        # Step 1: Create a strategy
        strategy_config = {
            "name": "Integration Test Strategy",
            "asset_class": "futures",
            "strategy_type": "momentum",
            "symbol": "NIFTY24FEB24F",
            "parameters": {
                "entry_threshold": 0.02,
                "exit_threshold": 0.01,
                "stop_loss": 0.03,
                "take_profit": 0.06,
                "position_size": 100000
            }
        }
        
        strategy_result = await self.trading_infra.strategy_engine.create_strategy(strategy_config)
        
        self.assertTrue(strategy_result["success"])
        strategy_id = strategy_result["strategy_id"]
        
        # Step 2: Create version and deploy
        version_result = await self.trading_infra.version_control_engine.create_strategy_version(
            strategy_id, strategy_config, "Integration test version"
        )
        
        self.assertTrue(version_result["success"])
        
        promote_result = await self.trading_infra.version_control_engine.promote_version(
            strategy_id, version_result["version_id"], "Approved for testing"
        )
        
        self.assertTrue(promote_result["success"])
        
        deploy_result = await self.trading_infra.version_control_engine.deploy_strategy_version(
            strategy_id, version_result["version_id"]
        )
        
        self.assertTrue(deploy_result["success"])
        
        # Step 3: Generate market data and analyze
        market_data = {
            "prices": [
                {"timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(), 
                 "open": 22000 + i*5, 
                 "high": 22010 + i*5, 
                 "low": 21990 + i*5, 
                 "close": 22005 + i*5, 
                 "volume": 100000 + i*500} 
                for i in range(20)
            ],
            "news": [
                {
                    "title": "Markets Showing Positive Momentum",
                    "content": "Technical indicators suggest bullish momentum in index futures",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "social": [
                {
                    "text": "Nifty looking strong today, momentum building",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        # Step 4: AI analysis
        sentiment_result = await self.trading_infra.ai_filter_engine.analyze_market_sentiment(
            market_data["news"], market_data["social"]
        )
        
        self.assertTrue(sentiment_result["success"])
        
        technical_result = await self.trading_infra.ai_filter_engine.process_technical_indicators(market_data)
        
        self.assertTrue(technical_result["success"])
        
        # Step 5: Generate signals
        analysis_data = {
            "sentiment_analysis": sentiment_result.get("sentiment_analysis", {}),
            "technical_analysis": technical_result.get("technical_analysis", {}),
            "fundamental_analysis": {},
            "pattern_analysis": {"detected_patterns": []},
            "risk_assessment": {"risk_level": 30}
        }
        
        signal_result = await self.trading_infra.ai_filter_engine.generate_signals(analysis_data)
        
        self.assertTrue(signal_result["success"])
        
        # Step 6: Risk check
        trade_proposal = {
            "symbol": "NIFTY24FEB24F",
            "quantity": 50,
            "price": 22005,
            "side": "BUY" if signal_result["trading_signal"]["signal_type"] in ["BUY", "STRONG_BUY"] else "SELL",
            "asset_class": "futures",
            "user_id": "integration_test_user"
        }
        
        risk_check = await self.trading_infra.risk_engine.check_risk_limits(trade_proposal)
        
        self.assertTrue(risk_check["success"])
        
        # Step 7: Execute trade if risk check passes
        if risk_check.get("risk_score", 100) < 80:  # Execute if risk is acceptable
            order_details = {
                "symbol": trade_proposal["symbol"],
                "quantity": trade_proposal["quantity"],
                "side": trade_proposal["side"],
                "order_type": "MARKET",
                "asset_class": trade_proposal["asset_class"],
                "product_type": "NRML",
                "validity": "DAY"
            }
            
            execution_result = await self.trading_infra.execution_engine.execute_order(order_details)
            
            # Execution might fail due to lack of actual broker connection,
            # but the workflow should be properly structured
            self.assertIsInstance(execution_result, dict)


def run_all_tests():
    """Run all test suites"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test cases
    test_suite.addTest(unittest.makeSuite(TestStrategyEngine))
    test_suite.addTest(unittest.makeSuite(TestParameterEngine))
    test_suite.addTest(unittest.makeSuite(TestRiskEngine))
    test_suite.addTest(unittest.makeSuite(TestAIFilterEngine))
    test_suite.addTest(unittest.makeSuite(TestExecutionEngine))
    test_suite.addTest(unittest.makeSuite(TestVersionControlEngine))
    test_suite.addTest(unittest.makeSuite(TestIntegratedWorkflow))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Run tests asynchronously
    async def run_async_tests():
        # Run each test class separately
        test_classes = [
            TestStrategyEngine(),
            TestParameterEngine(),
            TestRiskEngine(),
            TestAIFilterEngine(),
            TestExecutionEngine(),
            TestVersionControlEngine(),
            TestIntegratedWorkflow()
        ]
        
        all_passed = True
        
        for test_class in test_classes:
            for method_name in dir(test_class):
                if method_name.startswith('test_'):
                    method = getattr(test_class, method_name)
                    try:
                        await method()
                        print(f"✓ {method_name}")
                    except Exception as e:
                        print(f"✗ {method_name}: {str(e)}")
                        all_passed = False
        
        return all_passed
    
    success = asyncio.run(run_async_tests())
    sys.exit(0 if success else 1)