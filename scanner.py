"""
APEX TRADER - Coin Scanner Module
Fetches and analyzes Top 100 coins from Binance
Engineer: Mane 🔥💙
"""

import time
from typing import List, Dict, Optional
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
import numpy as np
from indicators import Indicators
import config

class CoinScanner:
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = True):
        """Initialize Binance client"""
        self.api_key = api_key or config.BINANCE_API_KEY
        self.api_secret = api_secret or config.BINANCE_API_SECRET
        self.testnet = testnet or config.BINANCE_TESTNET
        
        if self.testnet:
            self.client = Client(self.api_key, self.api_secret, testnet=True)
        else:
            self.client = Client(self.api_key, self.api_secret)
        
        self.price_cache = {}  # Cache for price history
        self.volume_cache = {}  # Cache for volume data
    
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
    
    def get_price_history(self, symbol: str, interval: str = '1m', limit: int = 100) -> List[float]:
        """Get recent price history for a symbol"""
        try:
            # Check cache first
            cache_key = f"{symbol}_{interval}_{limit}"
            if cache_key in self.price_cache:
                cached_time, cached_prices = self.price_cache[cache_key]
                # Use cache if less than 30 seconds old
                if time.time() - cached_time < 30:
                    return cached_prices
            
            # Fetch from API
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            # Extract close prices
            prices = [float(k[4]) for k in klines]
            
            # Update cache
            self.price_cache[cache_key] = (time.time(), prices)
            
            return prices
        
        except BinanceAPIException as e:
            print(f"❌ Error fetching price history for {symbol}: {e}")
            return []
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except BinanceAPIException as e:
            print(f"❌ Error fetching current price for {symbol}: {e}")
            return None
    
    def get_24h_stats(self, symbol: str) -> Dict:
        """Get 24h statistics for a symbol"""
        try:
            stats = self.client.get_ticker(symbol=symbol)
            return {
                'price_change_percent': float(stats['priceChangePercent']),
                'volume': float(stats['volume']),
                'quote_volume': float(stats['quoteVolume']),
                'high': float(stats['highPrice']),
                'low': float(stats['lowPrice']),
                'trades': int(stats['count'])
            }
        except BinanceAPIException as e:
            print(f"❌ Error fetching 24h stats for {symbol}: {e}")
            return {}
    
    def calculate_volatility_score(self, prices: List[float]) -> float:
        """Calculate volatility score (0-10)"""
        if len(prices) < 2:
            return 0
        
        volatility = Indicators.calculate_volatility(prices, period=60)
        
        # Score based on volatility
        # High volatility (>3% hourly) = 10
        # Medium volatility (1-3% hourly) = 5-9
        # Low volatility (<1% hourly) = 1-4
        
        if volatility >= 3:
            score = 10
        elif volatility >= 2:
            score = 8
        elif volatility >= 1:
            score = 6
        elif volatility >= 0.5:
            score = 4
        else:
            score = 2
        
        return score
    
    def calculate_volume_score(self, stats: Dict) -> float:
        """Calculate volume score (0-10)"""
        if not stats:
            return 5
        
        volume = stats.get('quote_volume', 0)
        
        # Score based on 24h volume (USDT)
        # >100M = 10
        # >50M = 8
        # >10M = 6
        # >1M = 4
        # <1M = 2
        
        if volume >= 100_000_000:
            score = 10
        elif volume >= 50_000_000:
            score = 8
        elif volume >= 10_000_000:
            score = 6
        elif volume >= 1_000_000:
            score = 4
        else:
            score = 2
        
        return score
    
    def calculate_momentum_score(self, prices: List[float]) -> float:
        """Calculate momentum score (0-10)"""
        if len(prices) < 60:
            return 5
        
        momentum = Indicators.calculate_momentum(prices, periods=[15, 60, 240])
        
        # Count positive momentum across timeframes
        positive_count = sum(1 for v in momentum.values() if v > 0)
        total_count = len(momentum)
        
        # Average momentum
        avg_momentum = sum(momentum.values()) / total_count if total_count > 0 else 0
        
        # Score based on momentum
        if positive_count == total_count and avg_momentum > 1:
            score = 10  # Strong uptrend
        elif positive_count == total_count:
            score = 8  # Moderate uptrend
        elif positive_count >= total_count / 2:
            score = 6  # Mixed
        elif avg_momentum < -1:
            score = 3  # Strong downtrend
        else:
            score = 4  # Weak downtrend
        
        return score
    
    def calculate_technical_score(self, prices: List[float]) -> float:
        """Calculate technical indicators score (0-10)"""
        result = Indicators.get_technical_score(prices)
        return result['score']
    
    def calculate_risk_score(self, symbol: str, stats: Dict) -> float:
        """Calculate risk score (0-10)"""
        # Base score
        score = 5
        
        # Check volume (higher volume = lower risk)
        volume = stats.get('quote_volume', 0)
        if volume >= 50_000_000:
            score += 3
        elif volume >= 10_000_000:
            score += 2
        elif volume >= 1_000_000:
            score += 1
        else:
            score -= 2
        
        # Check if it's a major coin (BTC, ETH, BNB, etc.)
        major_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT']
        if symbol in major_coins:
            score += 2
        
        # Cap at 10
        return min(score, 10)
    
    def scan_coin(self, symbol: str) -> Optional[Dict]:
        """Scan a single coin and return all scores"""
        try:
            # Get data
            prices = self.get_price_history(symbol, interval='1m', limit=300)
            if not prices or len(prices) < 60:
                return None
            
            stats = self.get_24h_stats(symbol)
            if not stats:
                return None
            
            current_price = prices[-1]
            
            # Calculate scores
            volatility_score = self.calculate_volatility_score(prices)
            volume_score = self.calculate_volume_score(stats)
            momentum_score = self.calculate_momentum_score(prices)
            technical_score = self.calculate_technical_score(prices)
            risk_score = self.calculate_risk_score(symbol, stats)
            
            # Calculate final score
            final_score = (
                volatility_score * config.VOLATILITY_WEIGHT +
                volume_score * config.VOLUME_WEIGHT +
                momentum_score * config.MOMENTUM_WEIGHT +
                technical_score * config.TECHNICAL_WEIGHT +
                risk_score * config.RISK_WEIGHT
            )
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'final_score': final_score,
                'scores': {
                    'volatility': volatility_score,
                    'volume': volume_score,
                    'momentum': momentum_score,
                    'technical': technical_score,
                    'risk': risk_score
                },
                'stats': stats,
                'price_history': prices[-60:]  # Last hour
            }
        
        except Exception as e:
            print(f"❌ Error scanning {symbol}: {e}")
            return None
    
    def scan_all_coins(self) -> List[Dict]:
        """Scan all top coins and return sorted by score"""
        print(f"🔍 Scanning Top {config.TOP_N_COINS} coins...")
        
        top_coins = self.get_top_coins()
        if not top_coins:
            print("❌ Failed to get top coins")
            return []
        
        results = []
        for i, symbol in enumerate(top_coins, 1):
            print(f"  [{i}/{len(top_coins)}] Scanning {symbol}...", end='\r')
            
            coin_data = self.scan_coin(symbol)
            if coin_data:
                results.append(coin_data)
            
            # Rate limiting (avoid API bans)
            time.sleep(0.1)
        
        print(f"\n✅ Scanned {len(results)} coins successfully")
        
        # Sort by final score (highest first)
        results.sort(key=lambda x: x['final_score'], reverse=True)
        
        return results
    
    def get_best_opportunity(self) -> Optional[Dict]:
        """Get the single best trading opportunity right now"""
        results = self.scan_all_coins()
        
        if not results:
            return None
        
        # Get top coin
        best = results[0]
        
        # Check if score meets minimum threshold
        if best['final_score'] < config.MIN_SCORE_TO_TRADE:
            print(f"⚠️ Best score ({best['final_score']:.2f}) below threshold ({config.MIN_SCORE_TO_TRADE})")
            return None
        
        return best

if __name__ == "__main__":
    # Test scanner
    print("🔥 APEX TRADER - Coin Scanner Test 🔥\n")
    
    scanner = CoinScanner()
    
    print("Testing scanner...")
    opportunity = scanner.get_best_opportunity()
    
    if opportunity:
        print(f"\n✅ Best Opportunity Found!")
        print(f"Symbol: {opportunity['symbol']}")
        print(f"Price: ${opportunity['current_price']:.4f}")
        print(f"Final Score: {opportunity['final_score']:.2f}/10")
        print(f"\nScore Breakdown:")
        for key, value in opportunity['scores'].items():
            print(f"  {key.capitalize()}: {value:.2f}/10")
    else:
        print("\n❌ No opportunities found")

