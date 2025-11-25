#!/usr/bin/env python3
"""
Signal Monitor
==============

Monitors Telegram channels and Discord servers for trading signals.
Parses messages and extracts token addresses and sentiment.
"""

import os
import asyncio
import logging
import re
from typing import List, Dict, Optional, Callable
from datetime import datetime

# Import Telethon for Telegram
try:
    from telethon import TelegramClient, events
except ImportError:
    TelegramClient = None
    events = None

# Import Discord for Discord monitoring
try:
    import discord
except ImportError:
    discord = None

class SignalMonitor:
    """Monitors social platforms for trading signals"""
    
    def __init__(self):
        self.logger = logging.getLogger("SignalMonitor")
        self.running = False
        self.telegram_client = None
        self.discord_client = None
        self.signal_callback = None
        
        # Configuration
        self.telegram_api_id = os.getenv('TELEGRAM_API_ID')
        self.telegram_api_hash = os.getenv('TELEGRAM_API_HASH')
        self.telegram_phone = os.getenv('TELEGRAM_PHONE')
        
        # Channels to monitor (can be loaded from config/db)
        self.telegram_channels = [
            'call_channel_1', 'call_channel_2'  # Placeholders
        ]
        
    async def start(self, callback: Callable):
        """Start monitoring"""
        self.signal_callback = callback
        self.running = True
        
        tasks = []
        
        # Start Telegram Monitor
        if self.telegram_api_id and self.telegram_api_hash:
            tasks.append(self._start_telegram())
        else:
            self.logger.warning("⚠️ Telegram credentials missing")
            
        # Start Discord Monitor (if configured)
        # tasks.append(self._start_discord())
        
        if not tasks:
            self.logger.warning("⚠️ No monitoring services configured")
            return
            
        await asyncio.gather(*tasks)
        
    async def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.telegram_client:
            await self.telegram_client.disconnect()
        if self.discord_client:
            await self.discord_client.close()
            
    async def _start_telegram(self):
        """Start Telegram client"""
        try:
            if not TelegramClient:
                self.logger.error("❌ Telethon not installed")
                return

            self.logger.info("Connecting to Telegram...")
            self.telegram_client = TelegramClient(
                'anon', 
                int(self.telegram_api_id), 
                self.telegram_api_hash
            )
            
            await self.telegram_client.start(phone=self.telegram_phone)
            self.logger.info("✅ Telegram connected!")
            
            @self.telegram_client.on(events.NewMessage)
            async def handler(event):
                if not self.running:
                    return
                await self._process_telegram_message(event)
                
            await self.telegram_client.run_until_disconnected()
            
        except Exception as e:
            self.logger.error(f"❌ Telegram error: {e}")
            
    async def _process_telegram_message(self, event):
        """Process incoming Telegram message"""
        try:
            message_text = event.message.message
            sender = await event.get_sender()
            sender_name = getattr(sender, 'username', 'Unknown') or getattr(sender, 'title', 'Unknown')
            
            # Simple signal detection logic
            signal_data = self._parse_signal(message_text)
            
            if signal_data:
                signal_data['source'] = 'telegram'
                signal_data['channel'] = sender_name
                signal_data['timestamp'] = datetime.now().isoformat()
                
                self.logger.info(f"🚨 SIGNAL DETECTED from {sender_name}: {signal_data['symbol']}")
                
                if self.signal_callback:
                    await self.signal_callback(signal_data)
                    
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            
    def _parse_signal(self, text: str) -> Optional[Dict]:
        """Parse message text for trading signals"""
        # Basic regex for Solana addresses (simplified)
        sol_address_pattern = r'[1-9A-HJ-NP-Za-km-z]{32,44}'
        
        # Check for CA (Contract Address)
        match = re.search(sol_address_pattern, text)
        if match:
            return {
                'token_address': match.group(0),
                'symbol': 'UNKNOWN',  # Would need API to fetch symbol
                'type': 'BUY',
                'raw_text': text
            }
            
        return None
