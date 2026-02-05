# Requirements Files Guide

## Overview
This project has multiple requirements files to handle different deployment scenarios:

- `requirements-production.txt`: Standard requirements without TA-Lib for easy Docker deployment
- `requirements-full.txt`: Full requirements including TA-Lib for advanced technical analysis
- `requirements.txt`: Legacy file (now same as production)

## Deployment Scenarios

### Production/Docker Deployment
Use `requirements-production.txt` which excludes TA-Lib to avoid compilation issues.
The technical analysis module will automatically fall back to pure Python implementations.

### Development/Advanced Analysis
Use `requirements-full.txt` if you have the TA-Lib C library installed on your system.
This provides optimized implementations of technical indicators.

## Technical Analysis Module
The technical analysis module (`app/utils/technical_analysis.py`) automatically detects
whether TA-Lib is available and falls back to pure Python implementations if not.

## Docker Build
The Dockerfile uses the production requirements to ensure successful builds in CI/CD environments.