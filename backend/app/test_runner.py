#!/usr/bin/env python3
"""
Test Runner for Trading Infrastructure

This module provides a comprehensive test runner for all trading engines:
1. Strategy Engine
2. Parameter Engine
3. Risk Engine
4. AI Filter Engine
5. Execution Engine
6. Version Control Engine
"""

import unittest
import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the backend path to sys.path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import test modules
from app.test_cases.automated_tests import (
    TestStrategyEngine, TestParameterEngine, TestRiskEngine, 
    TestAIFilterEngine, TestExecutionEngine, TestVersionControlEngine
)
from app.test_cases.trading_infra_tests import TestIntegratedWorkflow


class TestRunner:
    """Main test runner for trading infrastructure"""

    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None

    def run_unit_tests(self) -> bool:
        """Run unit tests using unittest framework"""
        logger.info("Starting unit tests...")
        
        # Create test suite
        test_suite = unittest.TestSuite()
        
        # Add test cases from both test modules
        test_classes = [
            TestStrategyEngine,
            TestParameterEngine,
            TestRiskEngine,
            TestAIFilterEngine,
            TestExecutionEngine,
            TestVersionControlEngine,
            TestIntegratedWorkflow
        ]
        
        for test_class in test_classes:
            test_suite.addTest(unittest.makeSuite(test_class))
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(test_suite)
        
        logger.info(f"Unit tests completed. Passed: {result.testsRun - len(result.failures) - len(result.errors)}, Failed: {len(result.failures) + len(result.errors)}")
        
        return result.wasSuccessful()

    async def run_integration_tests(self) -> bool:
        """Run integration tests"""
        logger.info("Starting integration tests...")
        
        # Import and run integration tests
        from app.test_cases.trading_infra_tests import TestIntegratedWorkflow
        
        integration_test = TestIntegratedWorkflow()
        all_passed = True
        
        # Run each integration test method
        for method_name in dir(integration_test):
            if method_name.startswith('test_'):
                method = getattr(integration_test, method_name)
                try:
                    if asyncio.iscoroutinefunction(method):
                        await method()
                    else:
                        method()
                    logger.info(f"✓ {method_name}")
                except Exception as e:
                    logger.error(f"✗ {method_name}: {str(e)}")
                    all_passed = False
        
        logger.info(f"Integration tests completed. All passed: {all_passed}")
        return all_passed

    async def run_performance_tests(self) -> bool:
        """Run performance tests"""
        logger.info("Starting performance tests...")
        
        # Import performance test module if it exists
        try:
            from app.test_cases.performance_tests import run_performance_tests
            result = await run_performance_tests()
            logger.info("Performance tests completed")
            return result
        except ImportError:
            logger.warning("Performance tests module not found, skipping...")
            return True

    async def run_end_to_end_tests(self) -> bool:
        """Run end-to-end tests"""
        logger.info("Starting end-to-end tests...")
        
        # Test complete workflow
        try:
            # Import the trading infrastructure
            from app.engines.trading_infrastructure import trading_infrastructure
            
            # Test complete trading cycle
            market_data = {
                "prices": [
                    {"timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(), 
                     "open": 22000 + i*5, 
                     "high": 22010 + i*5, 
                     "low": 21990 + i*5, 
                     "close": 22005 + i*5, 
                     "volume": 100000 + i*500} 
                    for i in range(10)
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
            
            # Initialize a trading session
            session_result = await trading_infrastructure.initialize_trading_session(
                "test_user_e2e", "futures", 1000000
            )
            
            if session_result["success"]:
                session_id = session_result["session_id"]
                
                # Run a trading cycle
                cycle_result = await trading_infrastructure.execute_trading_cycle(session_id, market_data)
                
                # Terminate session
                await trading_infrastructure.terminate_trading_session(session_id)
                
                logger.info("End-to-end test completed successfully")
                return cycle_result["success"]
            else:
                logger.error(f"Failed to initialize trading session: {session_result['error']}")
                return False
                
        except Exception as e:
            logger.error(f"Error in end-to-end test: {str(e)}")
            return False

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all types of tests"""
        self.start_time = datetime.now()
        logger.info(f"Starting comprehensive test suite at {self.start_time}")
        
        results = {
            "unit_tests": False,
            "integration_tests": False,
            "performance_tests": False,
            "end_to_end_tests": False,
            "overall_success": False
        }
        
        try:
            # Run unit tests
            results["unit_tests"] = self.run_unit_tests()
            
            # Run integration tests
            results["integration_tests"] = await self.run_integration_tests()
            
            # Run performance tests
            results["performance_tests"] = await self.run_performance_tests()
            
            # Run end-to-end tests
            results["end_to_end_tests"] = await self.run_end_to_end_tests()
            
            # Overall success is True only if all test types pass
            results["overall_success"] = all([
                results["unit_tests"],
                results["integration_tests"], 
                results["performance_tests"],
                results["end_to_end_tests"]
            ])
            
            self.end_time = datetime.now()
            duration = self.end_time - self.start_time
            
            logger.info(f"All tests completed in {duration.total_seconds():.2f} seconds")
            logger.info(f"Results: Unit={results['unit_tests']}, Integration={results['integration_tests']}, Performance={results['performance_tests']}, E2E={results['end_to_end_tests']}")
            
        except Exception as e:
            logger.error(f"Error running tests: {str(e)}")
            results["overall_success"] = False
        
        return results

    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate test report"""
        report = f"""
        ========= TRADING INFRASTRUCTURE TEST REPORT =========
        
        Test Execution Summary:
        - Start Time: {self.start_time}
        - End Time: {self.end_time}
        - Duration: {(self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0:.2f} seconds
        
        Test Results:
        - Unit Tests: {'PASS' if results['unit_tests'] else 'FAIL'}
        - Integration Tests: {'PASS' if results['integration_tests'] else 'FAIL'}
        - Performance Tests: {'PASS' if results['performance_tests'] else 'FAIL'}
        - End-to-End Tests: {'PASS' if results['end_to_end_tests'] else 'FAIL'}
        
        Overall Status: {'PASS' if results['overall_success'] else 'FAIL'}
        
        =====================================================
        """
        
        return report


async def main():
    """Main function to run all tests"""
    logger.info("Starting Trading Infrastructure Test Suite")
    
    test_runner = TestRunner()
    results = await test_runner.run_all_tests()
    
    # Generate and print report
    report = test_runner.generate_test_report(results)
    print(report)
    
    # Write report to file
    with open("test_results_report.txt", "w") as f:
        f.write(report)
    
    logger.info("Test suite completed")
    
    # Exit with appropriate code
    sys.exit(0 if results["overall_success"] else 1)


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())