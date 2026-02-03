from fastapi import APIRouter
# Fixed: Added users and updated portfolio prefix
from app.api.v1.endpoints import trades, portfolios, users, strategies, projections, logs, audit, tickets, ai, market, watchlist, approvals, auth

api_router = APIRouter()
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])
api_router.include_router(portfolios.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(projections.router, prefix="/projections", tags=["projections"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
