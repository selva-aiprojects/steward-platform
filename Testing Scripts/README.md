# Testing Scripts

This directory contains all testing, validation, and utility scripts for the StockSteward AI platform.

## Directory Structure

### Python Scripts
- **Basic Tests**: `basic_test.py` - Fundamental functionality tests
- **Comprehensive Tests**: `comprehensive_test.py` - Full system integration tests
- **Smoke Tests**: `smoke_test.py` - Quick functionality verification
- **API Tests**: `test_api_fixes.py`, `test_auth_fix.py`, `test_auth_system.py` - API-specific tests
- **Integration Tests**: `test_integration.js` - Cross-module integration tests
- **Optimization Tests**: `test_optimization_api.py` - Performance and optimization tests
- **Technical Analysis Tests**: `test_technical_analysis.py` - Algorithm and analysis tests
- **Utility Scripts**: `fix_demo_users.py`, `debug_schema.py` - Utility and debugging scripts

### JavaScript Scripts
- **Automated Tests**: `AUTOMATED_TESTS.js` - Automated test suite
- **Validation Scripts**: `create_validation_test.js`, `validate_workflow.js` - Validation utilities
- **Investment Tests**: `INVESTMENT_WORKFLOW_VALIDATION.js`, `test_investment_reports.js` - Investment-specific tests

### Verification Scripts
- **API Verification**: `verify_kite.py`, `verify_live_feed.py`, `verify_sockets.py` - External service verification

### Log Files
- **Debug Logs**: Various `.txt` and `.log` files containing test results and debug information

## Script Categories

### 1. Functional Tests
- `basic_test.py` - Core functionality verification
- `comprehensive_test.py` - End-to-end system tests
- `smoke_test.py` - Quick health checks

### 2. API and Integration Tests
- `test_api_fixes.py` - API endpoint testing
- `test_auth_system.py` - Authentication system tests
- `test_integration.js` - Cross-module integration tests

### 3. Utility and Setup Scripts
- `fix_demo_users.py` - Demo user setup and maintenance
- `debug_schema.py` - Schema validation and debugging
- `get_kite_token.py` - External service token management

### 4. Validation and Verification
- `validate_workflow.js` - Workflow validation
- `INVESTMENT_WORKFLOW_VALIDATION.js` - Investment workflow validation
- `verify_*.py` - External service verification scripts

## Usage

Most scripts can be run individually:
```bash
python basic_test.py
python smoke_test.py
node test_integration.js
```

Some scripts may require specific environment variables or dependencies to be set up.

## Maintenance

- Regular cleanup of log files may be necessary
- Test scripts should be updated when functionality changes
- Verification scripts should be run periodically to ensure external service connectivity