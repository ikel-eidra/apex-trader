"""
APEX TRADER - Coin Scanner Module
Fetches and analyzes Top 100 coins from Binance (Async)
Engineer: Mane 🔥💙
"""

import time
import asyncio
import aiohttp
from typing import List, Dict, Optional
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
import numpy as np
from indicators import Indicators
import config

class AsyncCoinScanner:
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = True):
        """Initialize Binance client"""
        self.api_key = api_key or config.BINANCE_API_KEY
        self.api_secret = api_secret or config.BINANCE_API_SECRET
        self.testnet = testnet or config.BINANCE_TESTNET
        
        # Keep sync client for initial top coin fetch (lightweight)
        if self.testnet:
            self.client = Client(self.api_key, self.api_secret, testnet=True)
            self.base_url = "https://testnet.binance.vision/api/v3"
        else:
            self.client = Client(self.api_key, self.api_secret)
            self.base_url = "https://api.binance.com/api/v3"
        
        self.price_cache = {}  # Cache for price history
    
    def get_top_coins(self, limit: int = None) -> List[str]:
        """Get top N coins by 24h volume on Binance (USDT pairs)"""
        limit = limit or config.TOP_N_COINS
        
        try:
            # Get all tickers
            tickers = self.client.get_ticker()
            
            # Filter for USDT pairs only
            usdt_pairs = [
                t for t in tickers 
                if t['symbol'].endswith('USDT') and 
                not any(x in t['symbol'] for x in ['UP', 'DOWN', 'BULL', 'BEAR'])
            ]
            
            # Sort by quote volume (USDT volume)
            usdt_pairs.sort(key=lambda x: float(x['quoteVolume']), reverse=True)
            
            # Get top N symbols
            top_symbols = [t['symbol'] for t in usdt_pairs[:limit]]
            
            return top_symbols
        
        except BinanceAPIException as e:
            print(f"❌ Error fetching top coins: {e}")
            return []
    
    async def fetch_klines(self, session, symbol: str, interval: str = '1m', limit: int = 100) -> List[float]:
        """Async fetch price history"""
        url = f"{self.base_url}/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    # Extract close prices (index 4)
                    return [float(k[4]) for k in data]
                else:
                    # print(f"⚠️ Error fetching klines for {symbol}: {response.status}")
                    return []
        except Exception as e:
            print(f"❌ Async error fetching klines for {symbol}: {e}")
            return []

    async def fetch_24h_stats(self, session, symbol: str) -> Dict:
        """Async fetch 24h stats"""
        url = f"{self.base_url}/ticker/24hr"
        params = {'symbol': symbol}
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    stats = await response.json()
                    return {
                        'price_change_percent': float(stats['priceChangePercent']),
                        'volume': float(stats['volume']),
                        'quote_volume': float(stats['quoteVolume']),
                        'high': float(stats['highPrice']),
                        'low': float(stats['lowPrice']),
                        'trades': int(stats['count'])
                    }
                else:
                    return {}
        except Exception as e:
            print(f"❌ Async error fetching stats for {symbol}: {e}")
            return {}

    def calculate_scores(self, symbol: str, prices: List[float], stats: Dict) -> Dict:
        """Calculate all scores for a coin"""
        if len(prices) < 60:
            return None
            
        # Calculate individual scores
        # 1. Volatility
        volatility = Indicators.calculate_volatility(prices)
        vol_score = 0
        if volatility >= 3: vol_score = 10
        elif volatility >= 2: vol_score = 8
        elif volatility >= 1: vol_score = 6
        elif volatility >= 0.5: vol_score = 4
        else: vol_score = 2
        
        # 2. Volume
        volume = stats.get('quote_volume', 0)
        vol_score_val = 0
        if volume >= 100_000_000: vol_score_val = 10
        elif volume >= 50_000_000: vol_score_val = 8
        elif volume >= 10_000_000: vol_score_val = 6
        elif volume >= 1_000_000: vol_score_val = 4
        else: vol_score_val = 2
        
        # 3. Momentum
        momentum = Indicators.calculate_momentum(prices)
        mom_score = 5
        pos_count = sum(1 for v in momentum.values() if v > 0)
        if pos_count == 3: mom_score = 10
        elif pos_count == 2: mom_score = 7
        elif pos_count == 0: mom_score = 2
        
        # 4. Technical (Advanced)
        tech_result = Indicators.get_technical_score(prices)
        tech_score = tech_result['score']
        
        # 5. Risk
        risk_score = 5
        if volume >= 50_000_000: risk_score += 3
        elif volume >= 10_000_000: risk_score += 2
        major_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
        if symbol in major_coins: risk_score += 2
        risk_score = min(risk_score, 10)
        
        # Final Weighted Score
        final_score = (
            vol_score * config.VOLATILITY_WEIGHT +
            vol_score_val * config.VOLUME_WEIGHT +
            mom_score * config.MOMENTUM_WEIGHT +
            tech_score * config.TECHNICAL_WEIGHT +
            risk_score * config.RISK_WEIGHT
        )
        
        return {
            'symbol': symbol,
            'current_price': prices[-1],
            'final_score': final_score,
            'scores': {
                'volatility': vol_score,
                'volume': vol_score_val,
                'momentum': mom_score,
                'technical': tech_score,
                'risk': risk_score
            },
            'stats': stats,
            'price_history': prices[-60:],
            'signals': tech_result['signals']
        }

    async def scan_coin_async(self, session, symbol: str) -> Optional[Dict]:
        """Scan a single coin asynchronously"""
        # Fetch prices and stats in parallel
        prices, stats = await asyncio.gather(
            self.fetch_klines(session, symbol, interval='1m', limit=300),
            self.fetch_24h_stats(session, symbol)
        )
        
        if not prices or not stats:
            return None
            
        return self.calculate_scores(symbol, prices, stats)

    async def scan_all_coins(self) -> List[Dict]:
        """Scan all top coins in parallel"""
        print(f"🔍 Scanning Top {config.TOP_N_COINS} coins (Async)...")
        start_time = time.time()
        
        top_coins = self.get_top_coins()
        if not top_coins:
            print("❌ Failed to get top coins")
            return []
        
        results = []
        async with aiohttp.ClientSession() as session:
            tasks = [self.scan_coin_async(session, symbol) for symbol in top_coins]
            
            # Process in batches to avoid hitting rate limits too hard
            batch_size = 20
            for i in range(0, len(tasks), batch_size):
                batch = tasks[i:i+batch_size]
                batch_results = await asyncio.gather(*batch)
                results.extend([r for r in batch_results if r])
                print(f"  Processed {min(i+batch_size, len(tasks))}/{len(tasks)} coins...", end='\r')
                await asyncio.sleep(0.5) # Slight delay between batches
        
        duration = time.time() - start_time
        print(f"\n✅ Scanned {len(results)} coins in {duration:.2f}s")
        
        # Sort by final score
        results.sort(key=lambda x: x['final_score'], reverse=True)
        
        return results
    
    async def get_best_opportunity(self) -> Optional[Dict]:
        """Get the single best trading opportunity right now"""
        results = await self.scan_all_coins()
        
        if not results:
            return None
        
        best = results[0]
        
        if best['final_score'] < config.MIN_SCORE_TO_TRADE:
            print(f"⚠️ Best score ({best['final_score']:.2f}) below threshold ({config.MIN_SCORE_TO_TRADE})")
            return None
            
        return best

if __name__ == "__main__":
    # Test async scanner
    print("🔥 APEX TRADER - Async Scanner Test 🔥\n")
    
    async def test():
        scanner = AsyncCoinScanner()
        opp = await scanner.get_best_opportunity()
        
        if opp:
            print(f"\n✅ Best Opportunity Found!")
            print(f"Symbol: {opp['symbol']}")
            print(f"Price: ${opp['current_price']:.4f}")
            print(f"Final Score: {opp['final_score']:.2f}/10")
            print(f"Signals: {opp['signals']}")
        else:
            print("\n❌ No opportunities found")
            
    asyncio.run(test())
