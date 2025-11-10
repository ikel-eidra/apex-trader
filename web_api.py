"""
APEX TRADER - Web API
FastAPI server for monitoring dashboard
Engineer: Mane 🔥💙
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from database import Database
import config

app = FastAPI(title="APEX TRADER API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "APEX TRADER",
        "version": "1.0.0",
        "engineer": "Mane 🔥💙",
        "for": "Ikel"
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "mode": "DRY_RUN" if config.DRY_RUN else "LIVE",
        "config": {
            "take_profit": f"{config.TAKE_PROFIT_PERCENT}%",
            "stop_loss": f"{config.STOP_LOSS_PERCENT}%",
            "max_trades_per_day": config.MAX_TRADES_PER_DAY
        }
    }

@app.get("/status")
async def status():
    """Get current bot status"""
    daily_stats = db.get_daily_stats()
    all_time_stats = db.get_all_time_stats()
    open_trade = db.get_open_trade()
    
    return {
        "mode": "DRY_RUN" if config.DRY_RUN else "LIVE",
        "has_open_position": open_trade is not None,
        "open_position": open_trade,
        "daily": daily_stats,
        "all_time": all_time_stats
    }

@app.get("/trades/recent")
async def recent_trades(limit: int = 20):
    """Get recent trades"""
    trades = db.get_recent_trades(limit=limit)
    return {"trades": trades}

@app.get("/trades/daily")
async def daily_trades():
    """Get today's trades"""
    stats = db.get_daily_stats()
    return stats

@app.get("/trades/all-time")
async def all_time_trades():
    """Get all-time statistics"""
    stats = db.get_all_time_stats()
    return stats

@app.get("/config")
async def get_config():
    """Get bot configuration"""
    return {
        "trading": {
            "take_profit_percent": config.TAKE_PROFIT_PERCENT,
            "stop_loss_percent": config.STOP_LOSS_PERCENT,
            "max_trade_duration": config.MAX_TRADE_DURATION,
            "capital_per_trade": config.CAPITAL_PER_TRADE
        },
        "risk": {
            "max_daily_loss_percent": config.MAX_DAILY_LOSS_PERCENT,
            "max_consecutive_losses": config.MAX_CONSECUTIVE_LOSSES,
            "max_trades_per_day": config.MAX_TRADES_PER_DAY
        },
        "scanning": {
            "scan_interval": config.SCAN_INTERVAL,
            "min_score_to_trade": config.MIN_SCORE_TO_TRADE,
            "top_n_coins": config.TOP_N_COINS
        },
        "weights": {
            "volatility": config.VOLATILITY_WEIGHT,
            "volume": config.VOLUME_WEIGHT,
            "momentum": config.MOMENTUM_WEIGHT,
            "technical": config.TECHNICAL_WEIGHT,
            "risk": config.RISK_WEIGHT
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", config.API_PORT))
    print(f"🚀 Starting APEX TRADER API on port {port}...")
    uvicorn.run(app, host=config.API_HOST, port=port)

