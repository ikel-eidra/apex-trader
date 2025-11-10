"""
APEX TRADER - Configuration
Engineer: Mane 🔥💙
For: Ikel
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# BINANCE API CREDENTIALS
# ============================================================================
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
BINANCE_TESTNET = os.getenv("BINANCE_TESTNET", "true").lower() == "true"

# ============================================================================
# TRADING PARAMETERS
# ============================================================================
TAKE_PROFIT_PERCENT = float(os.getenv("TAKE_PROFIT_PERCENT", "0.5"))  # 0.5%
STOP_LOSS_PERCENT = float(os.getenv("STOP_LOSS_PERCENT", "0.3"))      # 0.3%
MAX_TRADE_DURATION = int(os.getenv("MAX_TRADE_DURATION", "1800"))     # 30 minutes
CAPITAL_PER_TRADE = float(os.getenv("CAPITAL_PER_TRADE", "0.95"))     # 95% of balance

# ============================================================================
# RISK MANAGEMENT
# ============================================================================
MAX_DAILY_LOSS_PERCENT = float(os.getenv("MAX_DAILY_LOSS_PERCENT", "2.0"))     # 2%
MAX_CONSECUTIVE_LOSSES = int(os.getenv("MAX_CONSECUTIVE_LOSSES", "3"))         # 3 losses
MAX_TRADES_PER_DAY = int(os.getenv("MAX_TRADES_PER_DAY", "20"))               # 20 trades
PAUSE_AFTER_LOSSES = int(os.getenv("PAUSE_AFTER_LOSSES", "3600"))            # 1 hour

# ============================================================================
# SCANNING PARAMETERS
# ============================================================================
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "60"))                # Scan every 60 seconds
MIN_SCORE_TO_TRADE = float(os.getenv("MIN_SCORE_TO_TRADE", "7.0"))   # Minimum score: 7/10
TOP_N_COINS = int(os.getenv("TOP_N_COINS", "100"))                    # Top 100 coins

# ============================================================================
# COIN SELECTION WEIGHTS
# ============================================================================
VOLATILITY_WEIGHT = float(os.getenv("VOLATILITY_WEIGHT", "0.30"))    # 30%
VOLUME_WEIGHT = float(os.getenv("VOLUME_WEIGHT", "0.25"))            # 25%
MOMENTUM_WEIGHT = float(os.getenv("MOMENTUM_WEIGHT", "0.25"))        # 25%
TECHNICAL_WEIGHT = float(os.getenv("TECHNICAL_WEIGHT", "0.15"))      # 15%
RISK_WEIGHT = float(os.getenv("RISK_WEIGHT", "0.05"))                # 5%

# ============================================================================
# TECHNICAL INDICATORS
# ============================================================================
RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
RSI_OVERSOLD = float(os.getenv("RSI_OVERSOLD", "30"))
RSI_OVERBOUGHT = float(os.getenv("RSI_OVERBOUGHT", "70"))

MACD_FAST = int(os.getenv("MACD_FAST", "12"))
MACD_SLOW = int(os.getenv("MACD_SLOW", "26"))
MACD_SIGNAL = int(os.getenv("MACD_SIGNAL", "9"))

BB_PERIOD = int(os.getenv("BB_PERIOD", "20"))
BB_STD = float(os.getenv("BB_STD", "2"))

# ============================================================================
# DATABASE
# ============================================================================
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/trades.db")

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/apex_trader.log")

# ============================================================================
# WEB API
# ============================================================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "10000"))

# ============================================================================
# DRY RUN MODE
# ============================================================================
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

# ============================================================================
# VALIDATION
# ============================================================================
def validate_config():
    """Validate configuration parameters"""
    errors = []
    
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        if not DRY_RUN:
            errors.append("Binance API credentials are required for live trading")
    
    if TAKE_PROFIT_PERCENT <= 0:
        errors.append("TAKE_PROFIT_PERCENT must be positive")
    
    if STOP_LOSS_PERCENT <= 0:
        errors.append("STOP_LOSS_PERCENT must be positive")
    
    if STOP_LOSS_PERCENT >= TAKE_PROFIT_PERCENT:
        errors.append("STOP_LOSS_PERCENT should be less than TAKE_PROFIT_PERCENT")
    
    if CAPITAL_PER_TRADE <= 0 or CAPITAL_PER_TRADE > 1:
        errors.append("CAPITAL_PER_TRADE must be between 0 and 1")
    
    weights_sum = (VOLATILITY_WEIGHT + VOLUME_WEIGHT + MOMENTUM_WEIGHT + 
                   TECHNICAL_WEIGHT + RISK_WEIGHT)
    if abs(weights_sum - 1.0) > 0.01:
        errors.append(f"Selection weights must sum to 1.0 (currently {weights_sum})")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"- {e}" for e in errors))
    
    return True

# ============================================================================
# DISPLAY CONFIGURATION
# ============================================================================
def display_config():
    """Display current configuration"""
    print("=" * 60)
    print("🔥 APEX TRADER CONFIGURATION 🔥")
    print("=" * 60)
    print(f"Mode: {'DRY RUN (TESTNET)' if DRY_RUN else 'LIVE TRADING'}")
    print(f"Take Profit: {TAKE_PROFIT_PERCENT}%")
    print(f"Stop Loss: {STOP_LOSS_PERCENT}%")
    print(f"Max Trade Duration: {MAX_TRADE_DURATION}s ({MAX_TRADE_DURATION//60}min)")
    print(f"Capital Per Trade: {CAPITAL_PER_TRADE*100}%")
    print(f"Max Daily Loss: {MAX_DAILY_LOSS_PERCENT}%")
    print(f"Max Trades/Day: {MAX_TRADES_PER_DAY}")
    print(f"Scan Interval: {SCAN_INTERVAL}s")
    print(f"Min Score to Trade: {MIN_SCORE_TO_TRADE}/10")
    print(f"Top N Coins: {TOP_N_COINS}")
    print("=" * 60)
    print("Selection Weights:")
    print(f"  Volatility: {VOLATILITY_WEIGHT*100}%")
    print(f"  Volume: {VOLUME_WEIGHT*100}%")
    print(f"  Momentum: {MOMENTUM_WEIGHT*100}%")
    print(f"  Technical: {TECHNICAL_WEIGHT*100}%")
    print(f"  Risk: {RISK_WEIGHT*100}%")
    print("=" * 60)

if __name__ == "__main__":
    validate_config()
    display_config()

