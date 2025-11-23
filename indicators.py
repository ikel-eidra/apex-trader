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
    def calculate_stoch_rsi(prices: List[float], period: int = 14, k_period: int = 3, d_period: int = 3) -> Dict:
        """Calculate Stochastic RSI"""
        if len(prices) < period + 1:
            return {'k': 50, 'd': 50}
        
        rsi_values = []
        # Calculate RSI for the last (period + k + d) points to get enough data for smoothing
        lookback = period + k_period + d_period + 10
        if len(prices) < lookback:
            lookback = len(prices)
            
        # We need a series of RSI values
        for i in range(lookback - period):
            slice_prices = prices[-(lookback-i):]
            if len(slice_prices) > period:
                rsi_values.append(Indicators.calculate_rsi(slice_prices, period))
        
        if not rsi_values:
            return {'k': 50, 'd': 50}
            
        rsi_series = pd.Series(rsi_values)
        
        # Calculate Stoch RSI
        min_rsi = rsi_series.rolling(window=period).min()
        max_rsi = rsi_series.rolling(window=period).max()
        
        stoch = ((rsi_series - min_rsi) / (max_rsi - min_rsi)) * 100
        
        # Smooth K and D
        k = stoch.rolling(window=k_period).mean()
        d = k.rolling(window=d_period).mean()
        
        return {
            'k': k.iloc[-1] if not k.empty and not pd.isna(k.iloc[-1]) else 50,
            'd': d.iloc[-1] if not d.empty and not pd.isna(d.iloc[-1]) else 50
        }

    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        return float(pd.Series(prices).ewm(span=period, adjust=False).mean().iloc[-1])

    @staticmethod
    def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """Calculate Average True Range (ATR)"""
        if len(closes) < period + 1:
            return 0
            
        highs = np.array(highs)
        lows = np.array(lows)
        closes = np.array(closes)
        
        # TR = Max(High-Low, Abs(High-PrevClose), Abs(Low-PrevClose))
        tr1 = highs[1:] - lows[1:]
        tr2 = np.abs(highs[1:] - closes[:-1])
        tr3 = np.abs(lows[1:] - closes[:-1])
        
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        
        # ATR = Moving Average of TR
        atr = pd.Series(tr).rolling(window=period).mean().iloc[-1]
        
        return float(atr) if not pd.isna(atr) else 0

    @staticmethod
    def get_technical_score(prices: List[float], highs: List[float] = None, lows: List[float] = None) -> Dict:
        """Calculate overall technical score based on all indicators"""
        if len(prices) < 50:
            return {'score': 5, 'signals': {}}
        
        # Calculate all indicators
        rsi = Indicators.calculate_rsi(prices)
        stoch = Indicators.calculate_stoch_rsi(prices)
        macd = Indicators.calculate_macd(prices)
        bb = Indicators.calculate_bollinger_bands(prices)
        ema_50 = Indicators.calculate_ema(prices, 50)
        ema_200 = Indicators.calculate_ema(prices, 200)
        
        # Trend detection
        trend = "NEUTRAL"
        if ema_50 > ema_200:
            trend = "BULLISH"
        elif ema_50 < ema_200:
            trend = "BEARISH"
            
        current_price = prices[-1]
        
        signals = {
            'rsi': rsi,
            'stoch_k': stoch['k'],
            'stoch_d': stoch['d'],
            'macd_bullish': macd['crossover'],
            'macd_histogram': macd['histogram'],
            'bb_position': bb['position'],
            'trend': trend,
            'above_ema200': current_price > ema_200
        }
        
        # Score each indicator (0-10)
        
        # 1. RSI Score (Reversal logic)
        rsi_score = 5
        if rsi < 30: rsi_score = 9      # Oversold -> Buy
        elif rsi < 40: rsi_score = 7    # Weak -> Buy
        elif rsi > 70: rsi_score = 2    # Overbought -> Sell/Avoid
        elif rsi > 60: rsi_score = 4    # Strong -> Caution
        
        # 2. Stochastic RSI Score
        stoch_score = 5
        if stoch['k'] < 20 and stoch['k'] > stoch['d']: stoch_score = 10  # Bullish crossover in oversold
        elif stoch['k'] < 20: stoch_score = 8                             # Oversold
        elif stoch['k'] > 80: stoch_score = 2                             # Overbought
        
        # 3. MACD Score
        macd_score = 5
        if macd['crossover']: macd_score = 10        # Bullish crossover
        elif macd['histogram'] > 0: macd_score = 7   # Bullish momentum
        elif macd['histogram'] < 0: macd_score = 3   # Bearish momentum
        
        # 4. Bollinger Bands Score
        bb_score = 5
        if bb['position'] < 0.1: bb_score = 10       # Below lower band (Mean reversion)
        elif bb['position'] < 0.3: bb_score = 8      # Near lower band
        elif bb['position'] > 0.9: bb_score = 2      # Above upper band
        
        # 5. Trend Score
        trend_score = 5
        if trend == "BULLISH" and current_price > ema_50: trend_score = 8
        elif trend == "BEARISH": trend_score = 3
        
        # Weighted Average Score
        # RSI: 20%, Stoch: 20%, MACD: 25%, BB: 15%, Trend: 20%
        total_score = (
            (rsi_score * 0.20) +
            (stoch_score * 0.20) +
            (macd_score * 0.25) +
            (bb_score * 0.15) +
            (trend_score * 0.20)
        )
        
        return {
            'score': total_score,
            'signals': signals,
            'breakdown': {
                'rsi_score': rsi_score,
                'stoch_score': stoch_score,
                'macd_score': macd_score,
                'bb_score': bb_score,
                'trend_score': trend_score
            }
        }

if __name__ == "__main__":
    # Test indicators
    test_prices = [100 + i + (i%5)*2 for i in range(100)] # Generate dummy data
    test_highs = [p * 1.01 for p in test_prices]
    test_lows = [p * 0.99 for p in test_prices]
    
    print("🔥 Testing Advanced Indicators...")
    print(f"RSI: {Indicators.calculate_rsi(test_prices):.2f}")
    print(f"Stoch RSI: {Indicators.calculate_stoch_rsi(test_prices)}")
    print(f"EMA 50: {Indicators.calculate_ema(test_prices, 50):.2f}")
    print(f"ATR: {Indicators.calculate_atr(test_highs, test_lows, test_prices):.2f}")
    print(f"Technical Score: {Indicators.get_technical_score(test_prices)['score']:.2f}/10")

