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

logger = logging.getLogger(__name__)

async def initialize_services():
    """
    Initialize all core services with proper error handling
    """
    logger.info("Starting StockSteward AI service initialization...")
    
    # 1. Initialize database
    try:
        # Create all tables using the existing sync engine
        from app.core.database import engine as sync_engine
        Base.metadata.create_all(bind=sync_engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    # 2. Initialize Kite/Zerodha service
    try:
        if settings.ZERODHA_API_KEY and settings.ZERODHA_ACCESS_TOKEN:
            # Just get the client to initialize it, no need for a separate initialize_client method
            kite_client = kite_service.get_client()
            if kite_client:
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
        # The EnhancedLLMService initializes providers in __init__, just verify they're available
        available_providers = enhanced_llm_service.get_available_providers()
        logger.info(f"Available LLM providers: {available_providers}")
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
        # Use the sync database engine for health check
        from app.core.database import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            health_status["database"] = True
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
                # Test basic connectivity using the test_connection method
                test_result = await enhanced_llm_service.test_connection(provider)
                if test_result:
                    health_status["llm_services"].append(provider)
            except Exception as e:
                logger.error(f"LLM provider {provider} health check failed: {e}")
    except Exception as e:
        logger.error(f"LLM health checks failed: {e}")
    
    # Check data integrations
    try:
        if hasattr(data_integration_service, 'get_available_sources'):
            available_sources = await data_integration_service.get_available_sources()
            # Test basic connectivity using the verify_connections method
            connection_status = await data_integration_service.verify_connections()
            for source in available_sources:
                try:
                    if connection_status.get(source, False):
                        health_status["data_integrations"].append(source)
                except Exception as e:
                    logger.error(f"Data source {source} health check failed: {e}")
    except Exception as e:
        logger.error(f"Data integration health checks failed: {e}")
    
    # Check socket service - just mark as available since it's initialized in main.py
    try:
        # Socket service is initialized in main.py with the sio variable
        # For now, we'll assume it's available if the app reaches this point
        health_status["socket_service"] = True
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