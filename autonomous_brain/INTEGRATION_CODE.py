#!/usr/bin/env python3
"""
Heist Engine Integration with Autonomous Brain
===============================================

This file patches the main heist_engine.py to include:
1. Autonomous Brain initialization
2. Position sizing with compounding
3. Daily training scheduler
4. Approval system

Upload this to GitHub in the main branch.
"""

# Add to imports section (after existing imports)
IMPORTS_TO_ADD = """
# Autonomous Brain imports
from modules.autonomous.position_sizer import AdaptivePositionSizer, PositionSizingStrategy
from modules.autonomous.brain import AutonomousBrain
from modules.autonomous.trainer import TrainingScheduler
from modules.autonomous.approval import ApprovalSystem, KillSwitch
"""

# Add to HeistEngine.__init__ (after existing initialization)
INIT_TO_ADD = """
        # Autonomous capabilities
        self.position_sizer: Optional[AdaptivePositionSizer] = None
        self.autonomous_brain: Optional[AutonomousBrain] = None
        self.trainer: Optional[TrainingScheduler] = None
        self.approval_system: Optional[ApprovalSystem] = None
        self.kill_switch = KillSwitch()
"""

# Add to HeistEngine.initialize() (after Brain initialization)
INITIALIZE_TO_ADD = """
        # Initialize Position Sizer
        self.logger.info("Initializing Position Sizer...")
        try:
            strategy_name = os.getenv('POSITION_SIZING_STRATEGY', 'balanced')
            strategy = PositionSizingStrategy(strategy_name)
            self.position_sizer = AdaptivePositionSizer(strategy)
            self.logger.info(f"✅ Position Sizer ready: {strategy_name}")
        except Exception as e:
            self.logger.warning(f"⚠️ Position Sizer disabled: {e}")

        # Initialize Autonomous Brain
        self.logger.info("Initializing Autonomous Brain...")
        try:
            self.autonomous_brain = AutonomousBrain()
            asyncio.create_task(self.autonomous_brain.start())
            self.logger.info("✅ Autonomous Brain monitoring started")
        except Exception as e:
            self.logger.warning(f"⚠️ Autonomous Brain disabled: {e}")

        # Initialize Daily Trainer
        self.logger.info("Initializing Daily Trainer...")
        try:
            training_time = os.getenv('TRAINING_TIME', '23:00')
            self.trainer = TrainingScheduler(training_time=training_time)
            asyncio.create_task(self._run_daily_training())
            self.logger.info(f"✅ Daily training scheduled: {training_time}")
        except Exception as e:
            self.logger.warning(f"⚠️ Daily training disabled: {e}")

        # Initialize Approval System
        self.logger.info("Initializing Approval System...")
        try:
            self.approval_system = ApprovalSystem()
            await self.approval_system.initialize()
            self.logger.info("✅ Approval system ready")
        except Exception as e:
            self.logger.warning(f"⚠️ Approval system disabled: {e}")
"""

# Add new method to HeistEngine class
DAILY_TRAINING_METHOD = """
    async def _run_daily_training(self):
        \"\"\"Run daily training at scheduled time\"\"\"
        if not self.trainer:
            return
        
        while self.is_running:
            try:
                # Wait until training time
                await asyncio.sleep(60)  # Check every minute
                
                current_time = datetime.now().strftime("%H:%M")
                if current_time == self.trainer.training_time:
                    self.logger.info("🧠 Starting daily training session...")
                    await self.trainer.run_daily_training()
                    self.logger.info("✅ Daily training complete!")
                    
                    # Sleep for a bit to avoid duplicate runs
                    await self.sleep(120)
            except Exception as e:
                self.logger.error(f"❌ Training error: {e}")
                await asyncio.sleep(3600)  # Wait an hour on error
"""

# Instructions for updating the_hand.py
THE_HAND_UPDATES = """
# In the_hand.py, update execute_buy to use position sizer:

# Add after class initialization:
def set_position_sizer(self, sizer):
    \"\"\"Set the position sizer for compounding\"\"\"
    self.position_sizer = sizer

# Update execute_buy method to calculate dynamic amount:
async def execute_buy(...):
    # OLD:
    # amount_usd = amount_usd or self.config.TRADE_AMOUNT_USD
    
    # NEW:
    if self.position_sizer:
        # Use compounding position sizing
        wallet_balance = await self._get_total_wallet_balance()
        amount_usd = self.position_sizer.calculate_position_size(
            wallet_balance_usd=wallet_balance,
            current_open_positions=len(self.open_positions)
        )
        if not amount_usd:
            return TradeResult(
                success=False,
                error_message="Position sizer blocked trade (risk limits)"
            )
    else:
        # Fallback to fixed amount
        amount_usd = amount_usd or self.config.TRADE_AMOUNT_USD
"""

print("Integration code ready!")
print("\nFiles to update:")
print("1. heist_engine.py - Add autonomous brain initialization")
print("2. the_hand.py - Add position sizing")
print("\nThis will be done via GitHub Manager...")
