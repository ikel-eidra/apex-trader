"""
APEX TRADER - Technical Indicators Module
Calculates RSI, MACD, Bollinger Bands, and other indicators
Engineer: Mane 🔥💙
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import config

class Indicators:
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = None) -> float:
        """Calculate RSI (Relative Strength Index)"""
        period = period or config.RSI_PERIOD
        
        if len(prices) < period + 1:
            return 50  # Neutral if not enough data
        
        prices = np.array(prices)
        deltas = np.diff(prices)
        
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_macd(prices: List[float]) -> Dict:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < config.MACD_SLOW:
            return {'macd': 0, 'signal': 0, 'histogram': 0, 'crossover': False}
        
        prices = pd.Series(prices)
        
        ema_fast = prices.ewm(span=config.MACD_FAST, adjust=False).mean()
        ema_slow = prices.ewm(span=config.MACD_SLOW, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=config.MACD_SIGNAL, adjust=False).mean()
        histogram = macd_line - signal_line
        
        # Check for bullish crossover (MACD crosses above signal)
        crossover = False
        if len(histogram) >= 2:
            crossover = histogram.iloc[-2] < 0 and histogram.iloc[-1] > 0
        
        return {
            'macd': macd_line.iloc[-1],
            'signal': signal_line.iloc[-1],
            'histogram': histogram.iloc[-1],
            'crossover': crossover
        }
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float]) -> Dict:
        """Calculate Bollinger Bands"""
        period = config.BB_PERIOD
        std_dev = config.BB_STD
        
        if len(prices) < period:
            current_price = prices[-1]
            return {
                'upper': current_price * 1.02,
                'middle': current_price,
                'lower': current_price * 0.98,
                'position': 0.5
            }
        
        prices = pd.Series(prices)
        
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        # Calculate position (0 = at lower band, 1 = at upper band)
        current_price = prices.iloc[-1]
        band_width = upper.iloc[-1] - lower.iloc[-1]
        position = (current_price - lower.iloc[-1]) / band_width if band_width > 0 else 0.5
        
        return {
            'upper': upper.iloc[-1],
            'middle': middle.iloc[-1],
            'lower': lower.iloc[-1],
            'position': position
        }
    
    @staticmethod
    def calculate_volatility(prices: List[float], period: int = 20) -> float:
        """Calculate price volatility (standard deviation)"""
        if len(prices) < 2:
            return 0
        
        prices = np.array(prices[-period:])
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns) * 100  # As percentage
        
        return volatility
    
    @staticmethod
    def calculate_momentum(prices: List[float], periods: List[int] = [15, 60, 240]) -> Dict:
        """Calculate momentum over multiple timeframes (in minutes)"""
        momentum = {}
        
        for period in periods:
            if len(prices) > period:
                old_price = prices[-period]
                current_price = prices[-1]
                change = ((current_price - old_price) / old_price) * 100
                momentum[f'{period}m'] = change
            else:
                momentum[f'{period}m'] = 0
        
        return momentum
    
    @staticmethod
    def get_technical_score(prices: List[float]) -> Dict:
        """Calculate overall technical score based on all indicators"""
        if len(prices) < 2:
            return {'score': 5, 'signals': {}}
        
        # Calculate all indicators
        rsi = Indicators.calculate_rsi(prices)
        macd = Indicators.calculate_macd(prices)
        bb = Indicators.calculate_bollinger_bands(prices)
        
        signals = {
            'rsi': rsi,
            'macd_bullish': macd['crossover'],
            'macd_histogram': macd['histogram'],
            'bb_position': bb['position']
        }
        
        # Score each indicator (0-10)
        rsi_score = 0
        if config.RSI_OVERSOLD < rsi < config.RSI_OVERBOUGHT:
            rsi_score = 10  # Healthy range
        elif rsi < config.RSI_OVERSOLD:
            rsi_score = 8  # Oversold (buy signal)
        elif rsi > config.RSI_OVERBOUGHT:
            rsi_score = 3  # Overbought (avoid)
        
        macd_score = 0
        if macd['crossover']:
            macd_score = 10  # Strong buy signal
        elif macd['histogram'] > 0:
            macd_score = 7  # Bullish
        elif macd['histogram'] < 0:
            macd_score = 3  # Bearish
        
        bb_score = 0
        if bb['position'] < 0.3:
            bb_score = 9  # Near lower band (buy signal)
        elif bb['position'] < 0.5:
            bb_score = 7  # Below middle
        elif bb['position'] < 0.7:
            bb_score = 5  # Above middle
        else:
            bb_score = 2  # Near upper band (overbought)
        
        # Average score
        total_score = (rsi_score + macd_score + bb_score) / 3
        
        return {
            'score': total_score,
            'signals': signals,
            'breakdown': {
                'rsi_score': rsi_score,
                'macd_score': macd_score,
                'bb_score': bb_score
            }
        }

if __name__ == "__main__":
    # Test indicators
    test_prices = [100, 101, 102, 101, 103, 105, 104, 106, 108, 107, 109, 111, 110, 112, 115]
    
    print("Testing Indicators:")
    print(f"RSI: {Indicators.calculate_rsi(test_prices):.2f}")
    print(f"MACD: {Indicators.calculate_macd(test_prices)}")
    print(f"Bollinger Bands: {Indicators.calculate_bollinger_bands(test_prices)}")
    print(f"Volatility: {Indicators.calculate_volatility(test_prices):.2f}%")
    print(f"Momentum: {Indicators.calculate_momentum(test_prices)}")
    print(f"Technical Score: {Indicators.get_technical_score(test_prices)}")

