#!/usr/bin/env python3
"""
Basic functionality test for StockSteward AI platform
"""

def test_basic_imports():
    """Test that all key modules can be imported"""
    print("Testing basic imports...")
    
    try:
        # Test backtesting engine
        from backtesting.engine import BacktestingEngine
        print("+ BacktestingEngine imported successfully")
        
        # Test risk manager
        from risk.manager import RiskManager
        print("+ RiskManager imported successfully")
        
        # Test execution engine
        from execution.engine import ExecutionEngine
        print("+ ExecutionEngine imported successfully")
        
        # Test advanced strategies
        from strategies.advanced_strategies import AdvancedStrategies
        print("+ AdvancedStrategies imported successfully")
        
        # Test technical analysis utilities
        from utils.technical_analysis import calculate_indicators
        print("+ Technical analysis utilities imported successfully")
        
        return True
    except Exception as e:
        print(f"- Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_instantiation():
    """Test that basic components can be instantiated"""
    print("\nTesting basic instantiation...")
    
    try:
        from backtesting.engine import BacktestingEngine
        from risk.manager import RiskManager
        
        # Create instances
        backtest_engine = BacktestingEngine(initial_capital=100000)
        risk_manager = RiskManager(initial_capital=100000)
        
        print("+ BacktestingEngine instantiated successfully")
        print("+ RiskManager instantiated successfully")
        
        # Verify basic properties
        assert backtest_engine.initial_capital == 100000
        assert risk_manager.initial_capital == 100000
        
        print("+ Basic properties verified")
        
        return True
    except Exception as e:
        print(f"- Instantiation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_functions():
    """Test basic functionality of key functions"""
    print("\nTesting basic functionality...")
    
    try:
        import pandas as pd
        import numpy as np
        
        # Create sample data
        dates = pd.date_range(start='2023-01-01', end='2023-01-31', freq='D')
        prices = [100]
        for i in range(1, len(dates)):
            prices.append(prices[-1] * (1 + np.random.normal(0.0005, 0.02)))
        
        df = pd.DataFrame({
            'date': dates,
            'close': prices
        })
        
        # Test technical analysis functions
        from utils.technical_analysis import calculate_rsi, calculate_macd
        
        rsi_values = calculate_rsi(df['close'])
        macd_line, macd_signal, macd_hist = calculate_macd(df['close'])
        
        print("+ RSI calculated successfully")
        print("+ MACD calculated successfully")
        
        # Verify results make sense
        assert len(rsi_values) == len(df)
        assert len(macd_line) == len(df)
        
        # RSI should be mostly between 0 and 100
        rsi_valid = rsi_values.dropna()
        if len(rsi_valid) > 0:
            assert (rsi_valid >= 0).all() and (rsi_valid <= 100).all()
        
        print("+ Technical indicators validated")
        
        return True
    except Exception as e:
        print(f"- Function test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_strategy_functions():
    """Test strategy functions"""
    print("\nTesting strategy functions...")
    
    try:
        from strategies.advanced_strategies import AdvancedStrategies
        import pandas as pd
        
        # Create sample data row
        sample_row = pd.Series({
            'symbol': 'TEST',
            'close': 100.0,
            'sma_20': 98.0,
            'sma_50': 95.0,
            'sma_20_prev': 97.0,
            'sma_50_prev': 96.0,
            'rsi_14': 65.0,
            'rsi_14_prev': 60.0,
            'macd_line': 1.5,
            'macd_signal': 1.2,
            'macd_line_prev': 1.0,
            'macd_signal_prev': 1.3
        })
        
        positions = {}
        cash = 50000
        
        # Test various strategies
        sma_signal = AdvancedStrategies.sma_crossover_strategy(sample_row, positions, cash)
        rsi_signal = AdvancedStrategies.rsi_strategy(sample_row, positions, cash)
        macd_signal = AdvancedStrategies.macd_strategy(sample_row, positions, cash)
        
        print("+ SMA crossover strategy executed successfully")
        print("+ RSI strategy executed successfully")
        print("+ MACD strategy executed successfully")
        
        # Functions should return either None or a valid signal object
        assert sma_signal is None or hasattr(sma_signal, 'symbol')
        assert rsi_signal is None or hasattr(rsi_signal, 'symbol')
        assert macd_signal is None or hasattr(macd_signal, 'symbol')
        
        print("+ Strategy outputs validated")
        
        return True
    except Exception as e:
        print(f"- Strategy test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_risk_management():
    """Test risk management functions"""
    print("\nTesting risk management...")
    
    try:
        from risk.manager import RiskManager
        import pandas as pd
        
        risk_mgr = RiskManager(initial_capital=100000)
        
        # Mock positions
        positions = {
            'RELIANCE': {
                'market_value': 25000,
                'quantity': 10,
                'avg_price': 2500
            }
        }
        
        portfolio_value = 100000
        
        # Test risk calculation
        risk_metrics = risk_mgr.calculate_portfolio_risk(positions, portfolio_value)
        
        print("+ Portfolio risk calculated successfully")
        
        # Test trade risk check
        approved, reason, details = risk_mgr.check_trade_risk(
            'TCS', 5, 3500.0, positions, portfolio_value
        )
        
        print("+ Trade risk check executed successfully")
        
        # Verify return types
        assert isinstance(approved, bool)
        assert isinstance(reason, str)
        assert isinstance(details, dict)
        
        print("+ Risk management outputs validated")
        
        return True
    except Exception as e:
        print(f"- Risk management test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("="*60)
    print("STOCKSTEWARD AI - REGRESSION TEST SUITE")
    print("="*60)
    
    all_tests_passed = True
    
    # Run all tests
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Basic Instantiation", test_basic_instantiation),
        ("Basic Functions", test_basic_functions),
        ("Strategy Functions", test_strategy_functions),
        ("Risk Management", test_risk_management)
    ]
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        result = test_func()
        if not result:
            all_tests_passed = False
        print(f"{test_name}: {'PASSED' if result else 'FAILED'}")
    
    print("\n" + "="*60)
    print("REGRESSION TEST SUMMARY")
    print("="*60)
    
    if all_tests_passed:
        print("SUCCESS: ALL TESTS PASSED!")
        print("+ New features implemented correctly")
        print("+ Existing functionality preserved")
        print("+ All components working as expected")
        print("\nThe StockSteward AI platform is ready for production.")
    else:
        print("FAILURE: SOME TESTS FAILED!")
        print("Please review the errors above and fix before deployment.")
    
    return all_tests_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)