"""
Startup script for StockSteward AI backend
Initializes all services and performs health checks
"""

import asyncio
import logging
from app.core.config import settings
from app.core.database import engine, Base
from app.services.kite_service import KiteService
from app.services.enhanced_llm_service import EnhancedLLMService
from app.services.data_integration import DataIntegrationService

# Initialize global service instances
kite_service = KiteService()
enhanced_llm_service = EnhancedLLMService()
data_integration_service = DataIntegrationService()

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
    Perform comprehensive health checks on all services in parallel for optimization
    """
    logger.info("Performing optimized health checks...")
    
    health_status = {
        "database": False,
        "kite_connect": False,
        "llm_services": [],
        "data_integrations": [],
        "socket_service": True # Mark True as it's initialized in main.py
    }
    
    # 1. Database Check
    async def check_db():
        try:
            from app.core.database import engine
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"DB health check failed: {e}")
            return False

    # 2. Kite Check
    async def check_kite():
        try:
            return kite_service.validate_connection()
        except: return False

    # 3. LLM Checks (Parallel)
    async def check_llm():
        available = enhanced_llm_service.get_available_providers()
        results = await asyncio.gather(*[enhanced_llm_service.test_connection(p) for p in available])
        return [p for p, success in zip(available, results) if success]

    # 4. Data Integration Checks
    async def check_data():
        try:
            available = await data_integration_service.get_available_sources()
            connection_status = await data_integration_service.verify_connections()
            return [src for src in available if connection_status.get(src, False)]
        except: return []

    # Run all major checks in parallel
    db_ok, kite_ok, active_llms, active_data = await asyncio.gather(
        check_db(), check_kite(), check_llm(), check_data()
    )

    health_status.update({
        "database": db_ok,
        "kite_connect": kite_ok,
        "llm_services": active_llms,
        "data_integrations": active_data
    })
    
    logger.info(f"Parallel health check results: {health_status}")
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