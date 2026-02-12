# StockSteward AI - Technical Design Document

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Security & Authentication](#security--authentication)
4. [Data Management](#data-management)
5. [AI & Machine Learning Services](#ai--machine-learning-services)
6. [Market Data Integration](#market-data-integration)
7. [Frontend Architecture](#frontend-architecture)
8. [Deployment & Infrastructure](#deployment--infrastructure)
9. [Secrets Management](#secrets-management)

## Overview
StockSteward AI is a comprehensive wealth management platform that combines algorithmic trading, AI-powered market analysis, and real-time market data to provide institutional-grade investment solutions. The platform supports multiple user roles with role-based access control and offers both paper and live trading capabilities.

## Architecture
The application follows a microservices architecture with a clear separation between frontend and backend services:

- **Frontend**: React-based SPA with role-based routing and real-time data visualization
- **Backend**: FastAPI-based REST API with WebSocket support for real-time market data
- **Database**: PostgreSQL for production, SQLite for local development
- **Authentication**: JWT-based authentication with role-based access control
- **AI Services**: Integration with multiple LLM providers (Groq, OpenAI, Anthropic)

## Security & Authentication
- JWT-based authentication with configurable expiration
- Role-based access control (SUPERADMIN, BUSINESS_OWNER, TRADER, AUDITOR)
- Secure password hashing using bcrypt
- CORS configuration for cross-origin requests
- Input validation using Pydantic models

## Data Management
- SQLAlchemy ORM for database operations
- Alembic for database migrations
- Comprehensive data models for users, portfolios, trades, strategies, and holdings
- Support for multiple exchanges (NSE, BSE, MCX)
- Historical data tracking and reporting

## AI & Machine Learning Services
- Integration with multiple LLM providers (Groq, OpenAI, Anthropic)
- Market analysis and prediction capabilities
- Algorithmic strategy recommendations
- Real-time sentiment analysis
- Automated trading decision support

## Market Data Integration
- Real-time market data from yfinance
- Support for multiple exchanges (NSE, BSE, MCX)
- Currency and commodity tracking
- Market movers and sector analysis
- Live ticker with exchange-specific data

## Frontend Architecture
- React with Context API for state management
- Responsive design with Tailwind CSS
- Real-time data visualization with WebSocket integration
- Role-based UI components and routing
- Interactive dashboards and trading interfaces

## Deployment & Infrastructure
- Docker-based containerization
- Environment-specific configurations
- Health checks and monitoring
- Scalable architecture for multiple users
- CI/CD pipeline support

## Secrets Management

### Overview
The StockSteward AI platform implements a robust secrets management system to securely store and manage sensitive API keys and credentials. This system ensures that sensitive information is never stored in plain text or committed to version control systems.

### Components

#### 1. Secrets Manager
- **Location**: `backend/app/utils/secrets_manager.py`
- **Technology**: Uses Fernet encryption (AES 128) with PBKDF2 key derivation
- **Purpose**: Encrypt and decrypt sensitive data locally

#### 2. Encryption Methodology
- **Algorithm**: Fernet (symmetric encryption using AES 128 in CBC mode)
- **Key Derivation**: PBKDF2 with SHA256 and 100,000 iterations
- **Salt**: Fixed salt for local development (in production, use random salt)
- **Encoding**: Base64 URL-safe encoding

#### 3. Storage Mechanism
- **File**: `secrets.enc` (encrypted binary file)
- **Format**: JSON object stored in encrypted form
- **Protection**: Added to `.gitignore` to prevent commits

#### 4. Supported Secrets
Currently supports encryption of:
- `GROQ_API_KEY` - Groq API key for LLM services
- `OPENAI_API_KEY` - OpenAI API key for LLM services
- `ANTHROPIC_API_KEY` - Anthropic API key for LLM services
- `HUGGINGFACE_API_KEY` - Hugging Face API key for ML services

### Implementation Details

#### Configuration Integration
- Modified `backend/app/core/config.py` to load secrets from encrypted storage
- Falls back to environment variables if encrypted secrets are not available
- Transparent integration with existing application code

#### Migration Process
- `backend/migrate_secrets.py` - Script to migrate existing API keys from .env to encrypted storage
- Preserves existing functionality while enhancing security
- Automatic verification of migration success

#### Update Utility
- `backend/update_secrets.py` - Interactive command-line tool to update encrypted secrets
- Secure input handling using `getpass` to hide sensitive values
- Menu-driven interface for easy management

### Security Features
- **Encryption at Rest**: All API keys stored in encrypted format
- **Memory Protection**: Keys loaded only when needed
- **Version Control Safety**: Encrypted file automatically ignored by git
- **Fallback Support**: Maintains environment variable support as backup
- **Key Isolation**: Encryption key derived from master password

### Usage Workflow
1. **Initial Setup**: Run migration script to move existing keys to encrypted storage
2. **Runtime**: Application automatically loads encrypted secrets
3. **Updates**: Use update utility to modify encrypted secrets
4. **Deployment**: Environment variables used for production (Render)

### Security Best Practices
- Master password should be strong and unique
- `secrets.enc` file must never be committed to version control
- Regular rotation of API keys recommended
- Access to the system should be restricted to authorized personnel
- Monitor access logs for unusual activities

### Integration Points
- **LLM Service**: Loads API keys from encrypted storage for Groq, OpenAI, Anthropic
- **Configuration**: Transparent integration with existing settings system
- **Authentication**: Secure handling of sensitive credentials
- **Market Data**: Secure access to premium data sources

This secrets management system provides enterprise-level security for sensitive API keys while maintaining ease of use for development and deployment.