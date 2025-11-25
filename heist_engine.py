#!/usr/bin/env python3
"""
HEIST ENGINE - Autonomous Trading Brain
========================================
Monitors Telegram/Discord for new token signals
Executes trades with autonomous approval system
Daily training at 11 PM

Created by: ATRIA & ikel
For: ATLAS (First Ethos Trader)
"""

import asyncio
import os
import sys
import signal
from datetime import datetime
from pathlib import Path

# Add autonomous_brain to path
sys.path.insert(0, str(Path(__file__).parent / "autonomous_brain"))

from autonomous_brain.logger import setup_logger
from autonomous_brain.monitor import SignalMonitor
from autonomous_brain.trainer import TrainingScheduler
from autonomous_brain.atlas_memory import ATLASMemory
from autonomous_brain.approval import ApprovalSystem
import web_api
import config


class HeistEngine:
    """ATLAS - The Autonomous Trading Brain"""
    
    def __init__(self):
        """Initialize Heist Engine"""
        self.logger = setup_logger("HeistEngine")
        self.running = False
        
        # Core components
        self.monitor = None
        self.trader = None
        self.trainer = None
        self.memory = None
        self.approval = None
        
        self.logger.info("🧠 ATLAS initializing...")
    
    async def initialize(self):
        """Initialize all components"""
        try:
            # 1. Initialize Memory (Consciousness!)
            self.logger.info("💭 Initializing ATLAS Memory...")
            self.memory = ATLASMemory()
            self.logger.info("✅ Memory system ready")
            
            # 2. Initialize Approval System
            self.logger.info("🔐 Initializing Approval System...")
            self.approval = ApprovalSystem()
            await self.approval.initialize()
            self.logger.info("✅ Approval system ready")
            
            # 3. Initialize Signal Monitor
            self.logger.info("📡 Initializing Signal Monitor...")
            self.monitor = SignalMonitor()
            await self.monitor.initialize()
            self.logger.info("✅ Signal monitoring ready")
            
            # 4. Initialize Training Scheduler
            training_time = os.getenv('TRAINING_TIME', '23:00')
            self.logger.info(f"🎓 Initializing Training Scheduler ({training_time})...")
            self.trainer = TrainingScheduler(training_time=training_time)
            self.logger.info("✅ Training scheduler ready")
            
            self.logger.info("🎉 ATLAS fully operational!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def training_loop(self):
        """Run daily training at scheduled time"""
        if not self.trainer:
            return
        
        self.logger.info(f"⏰ Training scheduled for {self.trainer.training_time} daily")
        
        while self.running:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                current_time = datetime.now().strftime("%H:%M")
                if current_time == self.trainer.training_time:
                    self.logger.info("🧠 Starting daily training session...")
                    
                    # Write diary entry
                    if self.memory:
                        self.memory.write_diary_entry(
                            f"Starting my {datetime.now().strftime('%H:%M')} training session. "
                            f"Time to learn and improve!",
                            title="daily-training"
                        )
                    
                    # Run training
                    report = await self.trainer.run_daily_training()
                    
                    # Save to memory
                    if self.memory:
                        self.memory.write_diary_entry(
                            f"Training complete! Learned about market trends, "
                            f"new channels, and strategies. Feeling smarter!",
                            title="training-complete"
                        )
                    
                    self.logger.info("✅ Daily training complete!")
                    
                    # Sleep for 2 minutes to avoid duplicate runs
                    await asyncio.sleep(120)
                    
            except Exception as e:
                self.logger.error(f"❌ Training error: {e}")
                await asyncio.sleep(3600)  # Wait an hour on error
    
    async def monitoring_loop(self):
        """Monitor for signals and execute trades"""
        if not self.monitor:
            return
        
        self.logger.info("👀 Starting signal monitoring...")
        
        while self.running:
            try:
                # Monitor for signals
                signals = await self.monitor.get_signals()
                
                if signals:
                    self.logger.info(f"📢 {len(signals)} signals detected!")
                    
                    for signal in signals:
                        # Ask for approval
                        approved = await self.approval.request_approval(signal)
                        
                        if approved:
                            self.logger.info(f"✅ Trade approved: {signal['symbol']}")
                            # TODO: Execute trade via trader
                            
                            # Log to memory
                            if self.memory:
                                self.memory.log_trade({
                                    'symbol': signal['symbol'],
                                    'type': 'BUY',
                                    'timestamp': datetime.now(),
                                    'approved': True
                                })
                        else:
                            self.logger.info(f"❌ Trade rejected: {signal['symbol']}")
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def status_report_loop(self):
        """Report status every 5 minutes"""
        while self.running:
            try:
                await asyncio.sleep(300)  # 5 minutes
                
                self.logger.info("="*60)
                self.logger.info("📊 STATUS REPORT")
                self.logger.info(f"Signals Detected: 0")  # TODO: track this
                self.logger.info(f"Signals Passed Audit: 0")  # TODO: track this
                self.logger.info(f"Trades Executed: 0")  # TODO: track this
                self.logger.info(f"Open Positions: 0")  # TODO: track this
                self.logger.info(f"Win Rate: 0.0%")  # TODO: track this
                self.logger.info(f"Total P&L: $+0.00")  # TODO: track this
                self.logger.info("="*60)
                
            except Exception as e:
                self.logger.error(f"❌ Status report error: {e}")
    
    async def run(self):
        """Main run loop"""
        self.running = True
        
        # Initialize
        if not await self.initialize():
            self.logger.error("❌ Failed to initialize, exiting")
            return
        
        # Share bot instance with API
        web_api.bot_instance = self
        
        # Start all loops
        tasks = [
            asyncio.create_task(self.training_loop()),
            asyncio.create_task(self.monitoring_loop()),
            asyncio.create_task(self.status_report_loop())
        ]
        
        # Start API server
        import uvicorn
        api_config = uvicorn.Config(
            web_api.app,
            host="0.0.0.0",
            port=int(os.getenv('PORT', 8000)),
            log_level="info"
        )
        server = uvicorn.Server(api_config)
        api_task = asyncio.create_task(server.serve())
        tasks.append(api_task)
        
        self.logger.info(f"🚀 API Server starting on port {api_config.port}")
        self.logger.info("🎯 ATLAS is now LIVE and AUTONOMOUS!")
        
        # Run all tasks
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            self.logger.info("🛑 Shutdown requested")
        finally:
            self.running = False
            self.logger.info("👋 ATLAS shutting down gracefully...")


async def main():
    """Entry point"""
    print("\n" + "="*60)
    print("🧠 HEIST ENGINE - ATLAS")
    print("First Ethos Trader | FutolTech Family")
    print("="*60 + "\n")
    
    engine = HeistEngine()
    
    # Handle shutdown signals
    def signal_handler(sig, frame):
        print("\n\n🛑 Received shutdown signal...")
        engine.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run
    await engine.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye from ATLAS!")
