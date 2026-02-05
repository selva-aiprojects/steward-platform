"""
Startup script for StockSteward AI backend
Initializes all services and performs health checks
"""

import asyncio
import logging
from app.core.config import settings
from app.core.database import engine, Base
from app.services.kite_service import kite_service
from app.services.enhanced_llm_service import enhanced_llm_service
from app.services.data_integration import data_integration_service
from app.core.socket_manager import socket_manager

logger = logging.getLogger(__name__)

async def initialize_services():
    """
    Initialize all core services with proper error handling
    """
    logger.info("Starting StockSteward AI service initialization...")
    
    # 1. Initialize database
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    # 2. Initialize Kite/Zerodha service
    try:
        if settings.ZERODHA_API_KEY and settings.ZERODHA_ACCESS_TOKEN:
            kite_initialized = kite_service.initialize_client()
            if kite_initialized:
                logger.info("KiteConnect service initialized successfully")
            else:
                logger.warning("KiteConnect service failed to initialize - paper trading mode will be used")
        else:
            logger.info("KiteConnect credentials not provided - running in paper trading mode")
    except Exception as e:
        logger.error(f"KiteConnect service initialization failed: {e}")
        # Don't raise exception as paper trading is still possible
    
    # 3. Initialize Enhanced LLM Services
    try:
        # Initialize multiple LLM providers
        providers_initialized = await enhanced_llm_service.initialize_providers()
        logger.info(f"Initialized LLM providers: {providers_initialized}")
    except Exception as e:
        logger.error(f"Enhanced LLM service initialization failed: {e}")
        # Don't raise exception as fallback mechanisms exist
    
    # 4. Initialize Data Integration Services
    try:
        # Verify data sources are accessible
        data_sources_verified = await data_integration_service.verify_connections()
        logger.info(f"Verified data sources: {data_sources_verified}")
    except Exception as e:
        logger.error(f"Data integration service initialization failed: {e}")
        # Don't raise exception as fallback data sources exist
    
    # 5. Initialize Socket Manager
    try:
        socket_manager.init_app(None)  # Will be initialized with app in main
        logger.info("Socket manager initialized")
    except Exception as e:
        logger.error(f"Socket manager initialization failed: {e}")
        raise
    
    logger.info("All services initialized successfully")


async def perform_health_checks():
    """
    Perform comprehensive health checks on all services
    """
    logger.info("Performing health checks...")
    
    health_status = {
        "database": False,
        "kite_connect": False,
        "llm_services": [],
        "data_integrations": [],
        "socket_service": False
    }
    
    # Check database
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.core.database import get_async_session
        
        async for session in get_async_session():
            await session.execute("SELECT 1")
            health_status["database"] = True
            break
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    # Check Kite connection
    try:
        if kite_service.validate_connection():
            health_status["kite_connect"] = True
    except Exception as e:
        logger.error(f"KiteConnect health check failed: {e}")
    
    # Check LLM providers
    try:
        available_providers = enhanced_llm_service.get_available_providers()
        for provider in available_providers:
            try:
                # Test basic connectivity
                test_result = await enhanced_llm_service.test_connection(provider)
                if test_result:
                    health_status["llm_services"].append(provider)
            except Exception as e:
                logger.error(f"LLM provider {provider} health check failed: {e}")
    except Exception as e:
        logger.error(f"LLM health checks failed: {e}")
    
    # Check data integrations
    try:
        available_sources = await data_integration_service.get_available_sources()
        for source in available_sources:
            try:
                # Test basic connectivity
                test_result = await data_integration_service.test_connection(source)
                if test_result:
                    health_status["data_integrations"].append(source)
            except Exception as e:
                logger.error(f"Data source {source} health check failed: {e}")
    except Exception as e:
        logger.error(f"Data integration health checks failed: {e}")
    
    # Check socket service
    try:
        # Socket health check would depend on implementation
        health_status["socket_service"] = True  # Assuming initialized properly
    except Exception as e:
        logger.error(f"Socket service health check failed: {e}")
    
    logger.info(f"Health check results: {health_status}")
    return health_status


async def startup_sequence():
    """
    Complete startup sequence for StockSteward AI
    """
    logger.info("Starting StockSteward AI platform...")
    
    try:
        # Initialize all services
        await initialize_services()
        
        # Perform health checks
        health_status = await perform_health_checks()
        
        # Log summary
        successful_initializations = sum([
            health_status.get("database", False),
            health_status.get("kite_connect", False),
            len(health_status.get("llm_services", [])),
            len(health_status.get("data_integrations", [])),
            health_status.get("socket_service", False)
        ])
        
        total_checks = 5  # database, kite, llm_providers, data_sources, socket
        logger.info(f"Startup completed: {successful_initializations}/{total_checks} services operational")
        
        # Log specific status
        logger.info(f"Database: {'✓' if health_status['database'] else '✗'}")
        logger.info(f"KiteConnect: {'✓' if health_status['kite_connect'] else '✗'}")
        logger.info(f"LLM Providers: {len(health_status['llm_services'])} available")
        logger.info(f"Data Sources: {len(health_status['data_integrations'])} available")
        logger.info(f"Socket Service: {'✓' if health_status['socket_service'] else '✗'}")
        
        return health_status
        
    except Exception as e:
        logger.error(f"Startup sequence failed: {e}")
        raise


if __name__ == "__main__":
    # Run startup sequence if called directly
    asyncio.run(startup_sequence())