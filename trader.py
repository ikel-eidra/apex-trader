"""
APEX TRADER - Trading Engine
Executes trades with Dynamic Risk Management (ATR-based)
Engineer: Mane 🔥💙
"""

import time
from datetime import datetime, timedelta
from typing import Optional, Dict
from binance.client import Client
from binance.exceptions import BinanceAPIException
import config
from database import Database
from indicators import Indicators

class Trader:
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = True):
        """Initialize Binance client and database"""
        self.api_key = api_key or config.BINANCE_API_KEY
        self.api_secret = api_secret or config.BINANCE_API_SECRET
        self.testnet = testnet or config.BINANCE_TESTNET
        self.dry_run = config.DRY_RUN
        
        if not self.dry_run:
            if self.testnet:
                self.client = Client(self.api_key, self.api_secret, testnet=True)
            else:
                self.client = Client(self.api_key, self.api_secret)
        else:
            self.client = None
            print("🔶 DRY RUN MODE - No real trades will be executed")
        
        self.db = Database()
        self.current_position = None
        self.entry_time = None
        
        # Dynamic Risk State
        self.initial_stop_loss = 0.0
        self.initial_take_profit = 0.0
        self.trailing_stop_active = False
        self.highest_price = 0.0
    
    def get_account_balance(self, asset: str = 'USDT') -> float:
        """Get account balance for an asset"""
        if self.dry_run:
            # Return simulated balance
            return 1000.0
        
        try:
            balance = self.client.get_asset_balance(asset=asset)
            return float(balance['free'])
        except BinanceAPIException as e:
            print(f"❌ Error getting balance: {e}")
            return 0.0
    
    def calculate_quantity(self, symbol: str, price: float, capital: float) -> float:
        """Calculate quantity to buy based on available capital"""
        try:
            # Get symbol info for precision
            if not self.dry_run:
                info = self.client.get_symbol_info(symbol)
                step_size = None
                for f in info['filters']:
                    if f['filterType'] == 'LOT_SIZE':
                        step_size = float(f['stepSize'])
                        break
            else:
                step_size = 0.00001  # Default for dry run
            
            # Calculate quantity
            quantity = capital / price
            
            # Round to step size
            if step_size:
                precision = len(str(step_size).split('.')[-1].rstrip('0'))
                quantity = round(quantity, precision)
            
            return quantity
        
        except Exception as e:
            print(f"❌ Error calculating quantity: {e}")
            return 0.0
    
    def place_market_buy(self, symbol: str, quantity: float) -> Optional[Dict]:
        """Place a market buy order"""
        if self.dry_run:
            # Simulate order
            price = 100.0  # Placeholder
            return {
                'symbol': symbol,
                'orderId': int(time.time()),
                'price': price,
                'executedQty': quantity,
                'status': 'FILLED',
                'transactTime': int(time.time() * 1000)
            }
        
        try:
            order = self.client.order_market_buy(
                symbol=symbol,
                quantity=quantity
            )
            return order
        
        except BinanceAPIException as e:
            print(f"❌ Error placing buy order: {e}")
            return None
    
    def place_market_sell(self, symbol: str, quantity: float) -> Optional[Dict]:
        """Place a market sell order"""
        if self.dry_run:
            # Simulate order
            price = 100.5  # Placeholder (0.5% profit)
            return {
                'symbol': symbol,
                'orderId': int(time.time()),
                'price': price,
                'executedQty': quantity,
                'status': 'FILLED',
                'transactTime': int(time.time() * 1000)
            }
        
        try:
            order = self.client.order_market_sell(
                symbol=symbol,
                quantity=quantity
            )
            return order
        
        except BinanceAPIException as e:
            print(f"❌ Error placing sell order: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price"""
        if self.dry_run:
            return 100.0  # Placeholder
        
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except BinanceAPIException as e:
            print(f"❌ Error getting price: {e}")
            return None
    
    def calculate_atr_targets(self, entry_price: float, price_history: list) -> tuple:
        """Calculate dynamic SL/TP based on ATR"""
        if not price_history or len(price_history) < 20:
            # Fallback to fixed percentages if no history
            tp = entry_price * (1 + config.TAKE_PROFIT_PERCENT / 100)
            sl = entry_price * (1 - config.STOP_LOSS_PERCENT / 100)
            return tp, sl
            
        # Calculate ATR (simplified using highs/lows approximation from closes if needed)
        # For better accuracy, we'd need real high/low data, but we'll use volatility estimation
        volatility = Indicators.calculate_volatility(price_history) / 100 # as decimal
        
        # ATR approximation: Price * Volatility
        atr = entry_price * volatility
        
        # Dynamic Targets
        # Stop Loss: 2x ATR
        # Take Profit: 3x ATR (1.5 Risk/Reward)
        
        sl_price = entry_price - (2 * atr)
        tp_price = entry_price + (3 * atr)
        
        # Safety bounds (don't let SL be too tight or too loose)
        min_sl = entry_price * 0.98 # Max 2% loss
        max_sl = entry_price * 0.997 # Min 0.3% risk
        
        sl_price = max(min_sl, min(sl_price, max_sl))
        
        return tp_price, sl_price

    def enter_trade(self, opportunity: Dict) -> bool:
        """Enter a trade based on opportunity"""
        symbol = opportunity['symbol']
        current_price = opportunity['current_price']
        score = opportunity['final_score']
        scores_breakdown = opportunity['scores']
        price_history = opportunity.get('price_history', [])
        
        print(f"\n🎯 ENTERING TRADE:")
        print(f"   Symbol: {symbol}")
        print(f"   Price: ${current_price:.4f}")
        print(f"   Score: {score:.2f}/10")
        
        # Get available capital
        balance = self.get_account_balance('USDT')
        capital_to_use = balance * config.CAPITAL_PER_TRADE
        
        if capital_to_use < 10:  # Minimum $10
            print(f"❌ Insufficient capital: ${capital_to_use:.2f}")
            return False
        
        # Calculate quantity
        quantity = self.calculate_quantity(symbol, current_price, capital_to_use)
        if quantity == 0:
            print(f"❌ Invalid quantity calculated")
            return False
        
        # Place buy order
        order = self.place_market_buy(symbol, quantity)
        if not order:
            print(f"❌ Failed to place buy order")
            return False
        
        # Get actual fill price
        fill_price = float(order.get('price', current_price))
        fill_quantity = float(order.get('executedQty', quantity))
        
        print(f"✅ BUY ORDER FILLED:")
        print(f"   Quantity: {fill_quantity}")
        print(f"   Price: ${fill_price:.4f}")
        print(f"   Total: ${fill_price * fill_quantity:.2f}")
        
        # Calculate Dynamic Targets
        tp_price, sl_price = self.calculate_atr_targets(fill_price, price_history)
        
        self.initial_take_profit = tp_price
        self.initial_stop_loss = sl_price
        self.highest_price = fill_price
        self.trailing_stop_active = False
        
        tp_pct = ((tp_price - fill_price) / fill_price) * 100
        sl_pct = ((fill_price - sl_price) / fill_price) * 100
        
        print(f"📊 DYNAMIC TARGETS (ATR):")
        print(f"   Take Profit: ${tp_price:.4f} (+{tp_pct:.2f}%)")
        print(f"   Stop Loss: ${sl_price:.4f} (-{sl_pct:.2f}%)")
        
        # Log trade in database
        trade_id = self.db.log_trade_entry(
            symbol=symbol,
            entry_price=fill_price,
            quantity=fill_quantity,
            score=score,
            scores_breakdown=scores_breakdown
        )
        
        # Store current position
        self.current_position = {
            'trade_id': trade_id,
            'symbol': symbol,
            'entry_price': fill_price,
            'quantity': fill_quantity,
            'score': score,
            'tp_price': tp_price,
            'sl_price': sl_price
        }
        self.entry_time = datetime.now()
        
        return True
    
    def monitor_position(self) -> bool:
        """Monitor current position and exit if targets hit"""
        if not self.current_position:
            return False
        
        symbol = self.current_position['symbol']
        entry_price = self.current_position['entry_price']
        quantity = self.current_position['quantity']
        trade_id = self.current_position['trade_id']
        
        # Get current price
        current_price = self.get_current_price(symbol)
        if not current_price:
            return True  # Continue monitoring
        
        # Update highest price for trailing stop
        if current_price > self.highest_price:
            self.highest_price = current_price
        
        # Calculate current P&L
        profit_percent = ((current_price - entry_price) / entry_price) * 100
        profit_usd = (current_price - entry_price) * quantity
        
        # Dynamic Risk Logic
        take_profit_price = self.initial_take_profit
        stop_loss_price = self.initial_stop_loss
        
        # Activate Trailing Stop if profit > 1%
        if profit_percent > 1.0:
            self.trailing_stop_active = True
            # Trail by 0.5% from highest price
            new_stop = self.highest_price * 0.995
            if new_stop > stop_loss_price:
                stop_loss_price = new_stop
                # print(f"🔄 Trailing Stop Updated: ${stop_loss_price:.4f}")
        
        # Check time limit
        time_in_trade = (datetime.now() - self.entry_time).total_seconds()
        max_duration = config.MAX_TRADE_DURATION
        
        # Determine if we should exit
        should_exit = False
        exit_reason = None
        
        if current_price >= take_profit_price:
            should_exit = True
            exit_reason = "TAKE_PROFIT_DYNAMIC"
            print(f"✅ TAKE PROFIT HIT! (+{profit_percent:.2f}%)")
        
        elif current_price <= stop_loss_price:
            should_exit = True
            exit_reason = "STOP_LOSS_DYNAMIC" if not self.trailing_stop_active else "TRAILING_STOP"
            print(f"❌ STOP LOSS HIT! ({profit_percent:.2f}%)")
        
        elif time_in_trade >= max_duration:
            should_exit = True
            exit_reason = "MAX_DURATION"
            print(f"⏰ MAX DURATION REACHED ({max_duration}s)")
        
        # Exit if needed
        if should_exit:
            return self.exit_trade(exit_reason)
        
        # Print status
        print(f"📊 {symbol} | Entry: ${entry_price:.4f} | Curr: ${current_price:.4f} | P&L: {profit_percent:+.2f}% | SL: ${stop_loss_price:.4f}", end='\r')
        
        return True  # Continue monitoring
    
    def exit_trade(self, reason: str) -> bool:
        """Exit current trade"""
        if not self.current_position:
            return False
        
        symbol = self.current_position['symbol']
        quantity = self.current_position['quantity']
        trade_id = self.current_position['trade_id']
        
        print(f"\n🚪 EXITING TRADE: {reason}")
        
        # Place sell order
        order = self.place_market_sell(symbol, quantity)
        if not order:
            print(f"❌ Failed to place sell order")
            return False
        
        # Get actual fill price
        exit_price = float(order.get('price', 0))
        
        print(f"✅ SELL ORDER FILLED:")
        print(f"   Price: ${exit_price:.4f}")
        print(f"   Quantity: {quantity}")
        
        # Log trade exit
        self.db.log_trade_exit(
            trade_id=trade_id,
            exit_price=exit_price,
            exit_reason=reason
        )
        
        # Calculate final P&L
        entry_price = self.current_position['entry_price']
        profit_percent = ((exit_price - entry_price) / entry_price) * 100
        profit_usd = (exit_price - entry_price) * quantity
        
        print(f"💰 FINAL P&L: {profit_percent:+.2f}% (${profit_usd:+.2f})")
        
        # Clear position
        self.current_position = None
        self.entry_time = None
        self.highest_price = 0.0
        self.trailing_stop_active = False
        
        return True
    
    def has_open_position(self) -> bool:
        """Check if there's an open position"""
        return self.current_position is not None
    
    def get_position_info(self) -> Optional[Dict]:
        """Get current position info"""
        if not self.current_position:
            return None
        
        symbol = self.current_position['symbol']
        entry_price = self.current_position['entry_price']
        current_price = self.get_current_price(symbol)
        
        if current_price:
            profit_percent = ((current_price - entry_price) / entry_price) * 100
            profit_usd = (current_price - entry_price) * self.current_position['quantity']
            
            return {
                **self.current_position,
                'current_price': current_price,
                'profit_percent': profit_percent,
                'profit_usd': profit_usd,
                'time_in_trade': (datetime.now() - self.entry_time).total_seconds()
            }
        
        return self.current_position

if __name__ == "__main__":
    # Test trader
    print("🔥 APEX TRADER - Trading Engine Test 🔥\n")
    
    trader = Trader()
    
    print(f"Balance: ${trader.get_account_balance('USDT'):.2f}")
    print(f"Has open position: {trader.has_open_position()}")

