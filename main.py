"""
APEX TRADER - Main Bot
Coordinates scanner and trader for automated trading
Engineer: Mane 🔥💙
For: Ikel
"""

import time
import signal
import sys
from datetime import datetime
from scanner import CoinScanner
from trader import Trader
from database import Database
import config

class ApexTrader:
    def __init__(self):
        """Initialize APEX TRADER bot"""
        self.scanner = CoinScanner()
        self.trader = Trader()
        self.db = Database()
        self.running = False
        self.stats = {
            'trades_today': 0,
            'consecutive_losses': 0,
            'daily_pnl': 0.0,
            'start_balance': 0.0
        }
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
    
    def shutdown(self, signum, frame):
        """Graceful shutdown"""
        print("\n\n🛑 Shutting down APEX TRADER...")
        self.running = False
        
        # Close any open positions
        if self.trader.has_open_position():
            print("⚠️ Closing open position...")
            self.trader.exit_trade("SHUTDOWN")
        
        print("✅ Shutdown complete")
        sys.exit(0)
    
    def check_daily_limits(self) -> bool:
        """Check if daily trading limits are reached"""
        daily_stats = self.db.get_daily_stats()
        
        # Check max trades per day
        if daily_stats['total_trades'] >= config.MAX_TRADES_PER_DAY:
            print(f"⚠️ Max trades per day reached ({config.MAX_TRADES_PER_DAY})")
            return False
        
        # Check max daily loss
        if daily_stats['total_profit_percent'] <= -config.MAX_DAILY_LOSS_PERCENT:
            print(f"⚠️ Max daily loss reached ({config.MAX_DAILY_LOSS_PERCENT}%)")
            return False
        
        # Check consecutive losses
        if self.stats['consecutive_losses'] >= config.MAX_CONSECUTIVE_LOSSES:
            print(f"⚠️ Max consecutive losses reached ({config.MAX_CONSECUTIVE_LOSSES})")
            print(f"⏸️ Pausing for {config.PAUSE_AFTER_LOSSES}s...")
            time.sleep(config.PAUSE_AFTER_LOSSES)
            self.stats['consecutive_losses'] = 0
        
        return True
    
    def update_stats(self):
        """Update trading statistics"""
        daily_stats = self.db.get_daily_stats()
        self.stats['trades_today'] = daily_stats['total_trades']
        self.stats['daily_pnl'] = daily_stats['total_profit_percent']
        
        # Check last trade result for consecutive losses
        recent_trades = self.db.get_recent_trades(limit=1)
        if recent_trades:
            last_trade = recent_trades[0]
            if last_trade['status'] == 'CLOSED':
                if last_trade['profit_percent'] < 0:
                    self.stats['consecutive_losses'] += 1
                else:
                    self.stats['consecutive_losses'] = 0
    
    def print_status(self):
        """Print current bot status"""
        daily_stats = self.db.get_daily_stats()
        all_time_stats = self.db.get_all_time_stats()
        balance = self.trader.get_account_balance('USDT')
        
        print("\n" + "="*60)
        print("🔥 APEX TRADER STATUS 🔥")
        print("="*60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mode: {'DRY RUN' if config.DRY_RUN else 'LIVE TRADING'}")
        print(f"Balance: ${balance:.2f}")
        print(f"\n📊 TODAY:")
        print(f"   Trades: {daily_stats['total_trades']}/{config.MAX_TRADES_PER_DAY}")
        print(f"   Win Rate: {daily_stats['win_rate']:.1f}%")
        print(f"   P&L: {daily_stats['total_profit_percent']:+.2f}% (${daily_stats['total_profit_usd']:+.2f})")
        print(f"   Best: {daily_stats['best_trade']:+.2f}%")
        print(f"   Worst: {daily_stats['worst_trade']:+.2f}%")
        print(f"\n📈 ALL TIME:")
        print(f"   Total Trades: {all_time_stats['total_trades']}")
        print(f"   Win Rate: {all_time_stats['win_rate']:.1f}%")
        print(f"   Total P&L: ${all_time_stats['total_profit_usd']:+.2f}")
        print(f"   Avg Profit: {all_time_stats['avg_profit_percent']:+.2f}%")
        print("="*60)
    
    def run(self):
        """Main bot loop"""
        print("\n" + "="*60)
        print("🔥 APEX TRADER STARTING 🔥")
        print("="*60)
        
        # Validate configuration
        try:
            config.validate_config()
            config.display_config()
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            return
        
        # Get starting balance
        self.stats['start_balance'] = self.trader.get_account_balance('USDT')
        print(f"\n💰 Starting Balance: ${self.stats['start_balance']:.2f}")
        
        self.running = True
        scan_counter = 0
        
        print(f"\n🚀 Bot is now running! Press Ctrl+C to stop.\n")
        
        while self.running:
            try:
                # If we have an open position, monitor it
                if self.trader.has_open_position():
                    self.trader.monitor_position()
                    time.sleep(1)  # Check every second
                    continue
                
                # Check if we can trade
                if not self.check_daily_limits():
                    print("⏸️ Daily limits reached. Waiting until tomorrow...")
                    time.sleep(3600)  # Wait 1 hour
                    continue
                
                # Scan for opportunities
                scan_counter += 1
                print(f"\n🔍 Scan #{scan_counter} - {datetime.now().strftime('%H:%M:%S')}")
                
                opportunity = self.scanner.get_best_opportunity()
                
                if opportunity:
                    print(f"\n✨ OPPORTUNITY FOUND!")
                    print(f"   Symbol: {opportunity['symbol']}")
                    print(f"   Score: {opportunity['final_score']:.2f}/10")
                    print(f"   Price: ${opportunity['current_price']:.4f}")
                    
                    # Enter trade
                    success = self.trader.enter_trade(opportunity)
                    
                    if success:
                        self.update_stats()
                    else:
                        print("❌ Failed to enter trade")
                else:
                    print("⚠️ No opportunities found (scores below threshold)")
                
                # Print status every 10 scans
                if scan_counter % 10 == 0:
                    self.print_status()
                
                # Wait before next scan
                print(f"\n⏳ Waiting {config.SCAN_INTERVAL}s until next scan...")
                time.sleep(config.SCAN_INTERVAL)
            
            except KeyboardInterrupt:
                self.shutdown(None, None)
            
            except Exception as e:
                print(f"\n❌ Error in main loop: {e}")
                print("⏳ Waiting 60s before retry...")
                time.sleep(60)
        
        print("\n✅ APEX TRADER stopped")

def main():
    """Entry point"""
    bot = ApexTrader()
    bot.run()

if __name__ == "__main__":
    main()

