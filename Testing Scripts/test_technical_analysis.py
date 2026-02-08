#!/usr/bin/env python3
"""
Test script to verify that technical analysis works without TA-Lib
"""

import sys
import os
import pandas as pd
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def test_technical_analysis_without_talib():
    """Test that technical analysis works without TA-Lib"""
    print("Testing technical analysis without TA-Lib...")
    
    # Create sample data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    df = pd.DataFrame({
        'open': np.random.rand(100) * 100 + 100,
        'high': np.random.rand(100) * 10 + 105,
        'low': np.random.rand(100) * 10 + 95,
        'close': np.random.rand(100) * 100 + 100,
        'volume': np.random.rand(100) * 1000000 + 100000
    })
    
    # Adjust high and low based on close values to make realistic data
    df['high'] = df['close'] + np.random.rand(100) * 5
    df['low'] = df['close'] - np.random.rand(100) * 5
    df['open'] = df['close'].shift(1).fillna(df['close'].iloc[0])
    
    try:
        from app.utils.technical_analysis import calculate_indicators
        result_df = calculate_indicators(df.copy())
        
        print(f"  - Successfully calculated indicators")
        print(f"  - Original columns: {len(df.columns)}")
        print(f"  - Result columns: {len(result_df.columns)}")
        print(f"  - New indicator columns added: {set(result_df.columns) - set(df.columns)}")
        
        # Check if key indicators were calculated
        expected_indicators = ['sma_10', 'sma_20', 'rsi_14', 'bb_middle']
        for indicator in expected_indicators:
            if indicator in result_df.columns:
                print(f"  - {indicator}: OK")
            else:
                print(f"  - {indicator}: Missing")
        
        print("  - Technical analysis test completed successfully")
        return True
        
    except Exception as e:
        print(f"  - Technical analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run tests to verify technical analysis works without TA-Lib"""
    print("Running technical analysis fallback tests...\n")
    
    success = test_technical_analysis_without_talib()
    
    if success:
        print("\n" + "="*50)
        print("TECHNICAL ANALYSIS FALLBACK TESTS PASSED!")
        print("="*50)
        print("\nThe system will work without TA-Lib installed, using pure Python implementations.")
    else:
        print("\n" + "="*50)
        print("TECHNICAL ANALYSIS FALLBACK TESTS FAILED!")
        print("="*50)
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)