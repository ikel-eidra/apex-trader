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
from resident_ai import ResidentAI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="APEX TRADER API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (Dashboard)
# Check if dist exists
if os.path.exists("dashboard/dist"):
    app.mount("/assets", StaticFiles(directory="dashboard/dist/assets"), name="assets")


# Initialize database
db = Database()

# Initialize Resident AI
brain = ResidentAI()

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    """Chat with the Resident AI"""
    # Gather context for the AI
    context = {
        "status": await status(),
        "recent_trades": db.get_recent_trades(limit=5)
    }
    
    response = brain.chat(request.message, context)
    return {"response": response}


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

# Global bot instance (injected by main.py)
bot_instance = None

@app.post("/control/start")
async def start_bot():
    """Start the trading bot"""
    if not bot_instance:
        return JSONResponse(status_code=503, content={"error": "Bot instance not initialized"})
    
    if bot_instance.running:
        return {"status": "already_running", "message": "Bot is already running"}
    
    # In async mode, we can't easily restart the loop if it exited, 
    # but we can set the flag if the loop is checking it.
    # However, if the loop finished, we'd need to restart the task.
    # For now, we assume the loop is running but paused or we just set the flag.
    # A better approach for a robust system is to have a 'paused' state.
    
    bot_instance.running = True
    return {"status": "started", "message": "Bot started"}

@app.post("/control/stop")
async def stop_bot():
    """Stop the trading bot"""
    if not bot_instance:
        return JSONResponse(status_code=503, content={"error": "Bot instance not initialized"})
    
    if not bot_instance.running:
        return {"status": "already_stopped", "message": "Bot is already stopped"}
    
    bot_instance.running = False
    return {"status": "stopped", "message": "Bot stopped"}

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """Serve React App for any other route"""
    if os.path.exists("dashboard/dist/index.html"):
        return FileResponse("dashboard/dist/index.html")
    return {"error": "Dashboard not built"}

if __name__ == "__main__":
    # This block is for standalone API testing only
    port = int(os.environ.get("PORT", config.API_PORT))
    print(f"🚀 Starting APEX TRADER API on port {port}...")
    uvicorn.run(app, host=config.API_HOST, port=port)

