from fastapi import APIRouter
# Fixed: Added users and updated portfolio prefix
from app.api.v1.endpoints import trades, portfolios, users

api_router = APIRouter()
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(portfolios.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
