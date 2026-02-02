from fastapi import APIRouter
# Fixed: Added users and updated portfolio prefix
from app.api.v1.endpoints import trades, portfolios, users, strategies, projections, logs, audit, tickets

api_router = APIRouter()
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(portfolios.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(projections.router, prefix="/projections", tags=["projections"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
