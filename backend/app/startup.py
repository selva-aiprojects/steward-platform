"""
Lean startup for StockSteward AI backend.
Initializes only critical services by default.
"""

import asyncio
import logging
import os
from app.core.database import Base

logger = logging.getLogger(__name__)


async def initialize_services() -> None:
    """Initialize critical runtime dependencies."""
    logger.info("Starting core service initialization...")
    try:
        from app.core.database import engine as sync_engine
        Base.metadata.create_all(bind=sync_engine)
        logger.info("Database initialized successfully")
    except Exception as error:
        logger.error(f"Database initialization failed: {error}")
        raise


async def initialize_optional_services() -> dict:
    """
    Optional legacy service initialization.
    Controlled by RUN_LEGACY_SERVICE_INIT=1.
    """
    status = {"kite": False, "llm_providers": [], "data_integrations": []}
    if os.getenv("RUN_LEGACY_SERVICE_INIT", "0").strip() != "1":
        logger.info("Skipping legacy service initialization")
        return status

    logger.info("Running legacy service initialization")

    try:
        from app.services.kite_service import kite_service
        status["kite"] = kite_service.get_client() is not None
    except Exception as error:
        logger.warning(f"Kite init skipped: {error}")

    try:
        from app.services.enhanced_llm_service import EnhancedLLMService
        llm_service = EnhancedLLMService()
        status["llm_providers"] = llm_service.get_available_providers()
    except Exception as error:
        logger.warning(f"LLM init skipped: {error}")

    try:
        from app.services.data_integration import DataIntegrationService
        data_service = DataIntegrationService()
        status["data_integrations"] = [
            key for key, ok in (await data_service.verify_connections()).items() if ok
        ]
    except Exception as error:
        logger.warning(f"Data integration init skipped: {error}")

    return status


async def startup_sequence() -> dict:
    """Execute startup sequence for the backend."""
    logger.info("Starting StockSteward AI platform...")
    await initialize_services()
    optional_status = await initialize_optional_services()
    summary = {"database": True, "socket_service": True, **optional_status}
    logger.info(
        "Startup ready: database=%s kite=%s llm=%d data=%d",
        summary["database"],
        summary["kite"],
        len(summary["llm_providers"]),
        len(summary["data_integrations"]),
    )
    return summary


if __name__ == "__main__":
    asyncio.run(startup_sequence())
