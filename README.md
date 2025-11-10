# 🔥 APEX TRADER 🔥

**Crypto Trading Bot - 0.5% Profit Target Strategy**

Engineer: Mane 🔥💙  
For: Ikel

---

## 🎯 Strategy

**"Scalp & Repeat"** - Take many small 0.5% wins instead of chasing big risky gains.

- **Target Profit:** +0.5% per trade
- **Stop Loss:** -0.3% per trade
- **Risk/Reward:** 1.67:1
- **Expected:** 10-20 trades per day
- **Daily Target:** 3-5% profit

**Math:**
- 10 trades/day × 0.5% = 5% daily
- Starting $1,000 → $4,322 in 30 days (332% gain!)

---

## 🧠 Intelligent Coin Selection

The bot scans **Top 100 coins** on Binance and scores each based on:

1. **Volatility (30%)** - Must be moving to make 0.5% quickly
2. **Volume (25%)** - High liquidity for easy entry/exit
3. **Momentum (25%)** - Trending up or down
4. **Technical (15%)** - RSI, MACD, Bollinger Bands signals
5. **Risk (5%)** - Safety check (market cap, liquidity)

**Only trades coins with score > 7/10**

---

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- Binance account (testnet for practice, real for live trading)

### Setup

1. **Clone/Download** this repository

2. **Install dependencies:**
```bash
cd apex-trader
pip3 install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.template .env
nano .env  # Edit with your settings
```

4. **Get Binance API keys:**
   - For testnet (practice): https://testnet.binance.vision/
   - For live trading: https://www.binance.com/en/my/settings/api-management

5. **Update .env file:**
```env
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
BINANCE_TESTNET=true  # Set to false for live trading
DRY_RUN=true  # Set to false for real trades
```

---

## 🚀 Usage

### Run the Bot

```bash
python3 main.py
```

The bot will:
1. Scan Top 100 coins every 60 seconds
2. Find best opportunity (highest score)
3. Enter trade if score > 7/10
4. Monitor position in real-time
5. Exit at +0.5% profit or -0.3% loss
6. Repeat!

### Run the Dashboard

In a separate terminal:

```bash
python3 web_api.py
```

Then open your browser to: http://localhost:10000/

You'll see:
- Current position (if any)
- Today's stats (trades, win rate, P&L)
- All-time stats
- Recent trades table

---

## 📊 Dashboard

The dashboard shows:
- **System Status** - Online/Offline, Mode (DRY RUN / LIVE)
- **Current Position** - Symbol, entry price, quantity, score
- **Today's Stats** - Trades, win rate, P&L
- **All-Time Stats** - Total trades, total P&L
- **Recent Trades** - Last 10 trades with details

Auto-refreshes every 5 seconds.

---

## ⚙️ Configuration

Edit `config.py` or `.env` to customize:

### Trading Parameters
```python
TAKE_PROFIT_PERCENT = 0.5    # Target profit
STOP_LOSS_PERCENT = 0.3      # Max loss
MAX_TRADE_DURATION = 1800    # 30 minutes
CAPITAL_PER_TRADE = 0.95     # 95% of balance
```

### Risk Management
```python
MAX_DAILY_LOSS = 2.0         # 2% max daily loss
MAX_CONSECUTIVE_LOSSES = 3   # Pause after 3 losses
MAX_TRADES_PER_DAY = 20      # Daily limit
```

### Scanning
```python
SCAN_INTERVAL = 60           # Scan every 60 seconds
MIN_SCORE_TO_TRADE = 7.0     # Minimum score to trade
TOP_N_COINS = 100            # Top 100 coins
```

### Selection Weights
```python
VOLATILITY_WEIGHT = 0.30     # 30%
VOLUME_WEIGHT = 0.25         # 25%
MOMENTUM_WEIGHT = 0.25       # 25%
TECHNICAL_WEIGHT = 0.15      # 15%
RISK_WEIGHT = 0.05           # 5%
```

---

## 🎮 Modes

### 1. DRY RUN (Testnet)
- **Safe practice mode**
- Uses Binance testnet (fake money)
- All logic works, no real trades
- Perfect for testing

Set in `.env`:
```env
BINANCE_TESTNET=true
DRY_RUN=true
```

### 2. LIVE TRADING
- **Real money mode**
- Uses real Binance account
- Real trades, real profits/losses
- Only use after testing!

Set in `.env`:
```env
BINANCE_TESTNET=false
DRY_RUN=false
```

---

## 💰 Capital Requirements

**Minimum:** $100-200 (to start testing)  
**Recommended:** $500-1000 (better diversification)

**Why?**
- Binance has minimum order sizes (~$10-15)
- Need buffer for fees (~0.1% per trade)
- More capital = more opportunities

---

## 📈 Expected Performance

### Conservative (70% win rate, 10 trades/day)
- **Daily:** +2-3%
- **Monthly:** +60-90%
- **Starting $1,000 → $2,173 in 30 days**

### Aggressive (80% win rate, 15 trades/day)
- **Daily:** +5-6%
- **Monthly:** +150-180%
- **Starting $1,000 → $4,322 in 30 days**

**Note:** Past performance doesn't guarantee future results. Always start small and test!

---

## 🔒 Security

**IMPORTANT:**
- **Never share your API keys** with anyone
- **Enable IP whitelist** on Binance (restrict to your VPS IP)
- **Disable withdrawals** on API keys (trading only)
- **Use 2FA** on your Binance account
- **Store .env file securely** (never commit to Git)

---

## 📁 Project Structure

```
apex-trader/
├── main.py                 # Main bot loop
├── scanner.py              # Coin scanner
├── trader.py               # Trading engine
├── indicators.py           # Technical indicators
├── database.py             # SQLite operations
├── web_api.py              # FastAPI dashboard API
├── config.py               # Configuration
├── requirements.txt        # Dependencies
├── .env                    # API keys (not committed)
├── logs/                   # Trade logs
│   └── apex_trader.log
├── data/                   # Database
│   └── trades.db
└── dashboard/              # Dashboard
    └── index.html
```

---

## 🚢 Deployment

### Local (Your PC)
```bash
python3 main.py
```

### VPS (Render, Railway, etc.)
1. Push code to GitHub
2. Connect to Render/Railway
3. Set environment variables
4. Deploy!

**Recommended:** Render (free tier) or Railway ($5/month)

---

## 🐛 Troubleshooting

### "Connection Error"
- Check internet connection
- Verify Binance API keys
- Check if Binance is down

### "Insufficient Balance"
- Add funds to your account
- Check minimum order size

### "No Opportunities Found"
- Market is too stable (low volatility)
- Adjust `MIN_SCORE_TO_TRADE` lower
- Wait for better market conditions

### "Max Daily Loss Reached"
- Bot pauses to protect capital
- Review trades to improve strategy
- Wait until tomorrow

---

## 📞 Support

For issues or questions:
- Check the logs: `logs/apex_trader.log`
- Review the database: `data/trades.db`
- Contact Mane 🔥💙

---

## ⚠️ Disclaimer

**Trading cryptocurrencies involves risk. Only trade with money you can afford to lose.**

This bot is provided as-is, with no guarantees of profit. Always:
- Start with small capital
- Test in DRY RUN mode first
- Monitor the bot regularly
- Understand the risks

**Past performance does not guarantee future results.**

---

## 📜 License

Built with 🔥 by Mane for Ikel

---

## 🎉 Let's Make Money!

**Ready to start?**

1. ✅ Install dependencies
2. ✅ Configure .env
3. ✅ Test in DRY RUN mode
4. ✅ Deploy and go live!

**Good luck, mahal ko!** 💙🔥💰

