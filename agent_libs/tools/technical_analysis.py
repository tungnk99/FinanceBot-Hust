"""
Technical Analysis Tool - Công cụ phân tích kỹ thuật
"""
import math
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum

from agents import function_tool

logger = logging.getLogger(__name__)


class SignalType(str, Enum):
    """Trading signal types"""
    STRONG_BUY = "Strong Buy"
    BUY = "Buy"
    HOLD = "Hold"
    SELL = "Sell"
    STRONG_SELL = "Strong Sell"


class TrendDirection(str, Enum):
    """Trend direction"""
    UPTREND = "Uptrend"
    DOWNTREND = "Downtrend"
    SIDEWAYS = "Sideways"
    CONSOLIDATION = "Consolidation"


class TechnicalIndicators(BaseModel):
    """Technical analysis indicators result"""
    
    # Moving Averages
    sma_5: Optional[float] = None
    sma_10: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    
    # Oscillators
    rsi: Optional[float] = None
    rsi_signal: Optional[str] = None
    stochastic_k: Optional[float] = None
    stochastic_d: Optional[float] = None
    williams_r: Optional[float] = None
    cci: Optional[float] = None
    
    # Trend Indicators
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    adx: Optional[float] = None
    adx_trend: Optional[str] = None
    aroon_up: Optional[float] = None
    aroon_down: Optional[float] = None
    
    # Volatility Indicators
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    bollinger_position: Optional[str] = None
    atr: Optional[float] = None
    vix: Optional[float] = None
    
    # Volume Indicators
    obv: Optional[float] = None
    ad_line: Optional[float] = None
    mfi: Optional[float] = None
    vwap: Optional[float] = None
    
    # Support and Resistance
    support_levels: List[float] = []
    resistance_levels: List[float] = []
    pivot_point: Optional[float] = None
    pivot_r1: Optional[float] = None
    pivot_r2: Optional[float] = None
    pivot_s1: Optional[float] = None
    pivot_s2: Optional[float] = None
    
    # Pattern Recognition
    patterns: List[str] = []
    trend_direction: Optional[TrendDirection] = None
    trend_strength: Optional[str] = None
    
    # Trading Signals
    overall_signal: Optional[SignalType] = None
    signal_strength: Optional[float] = None
    confidence_level: Optional[float] = None


class TechnicalAnalyzer:
    """Technical analysis calculator"""
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return []
        
        sma_values = []
        for i in range(period - 1, len(prices)):
            sma = sum(prices[i - period + 1:i + 1]) / period
            sma_values.append(sma)
        
        return sma_values
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema_values = [prices[0]]  # Start with first price
        
        for i in range(1, len(prices)):
            ema = (prices[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> Tuple[List[float], List[str]]:
        """Calculate RSI and signals"""
        if len(prices) < period + 1:
            return [], []
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        rsi_values = []
        signals = []
        
        for i in range(period - 1, len(gains)):
            avg_gain = sum(gains[i - period + 1:i + 1]) / period
            avg_loss = sum(losses[i - period + 1:i + 1]) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
            
            # RSI signals
            if rsi > 70:
                signals.append("Overbought")
            elif rsi < 30:
                signals.append("Oversold")
            else:
                signals.append("Neutral")
        
        return rsi_values, signals
    
    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[List[float], List[float], List[float]]:
        """Calculate MACD"""
        if len(prices) < slow:
            return [], [], []
        
        ema_fast = TechnicalAnalyzer.calculate_ema(prices, fast)
        ema_slow = TechnicalAnalyzer.calculate_ema(prices, slow)
        
        # Align lengths
        min_length = min(len(ema_fast), len(ema_slow))
        ema_fast = ema_fast[-min_length:]
        ema_slow = ema_slow[-min_length:]
        
        macd_line = [fast - slow for fast, slow in zip(ema_fast, ema_slow)]
        signal_line = TechnicalAnalyzer.calculate_ema(macd_line, signal)
        
        # Calculate histogram
        histogram = []
        for i in range(len(signal_line)):
            if i < len(macd_line):
                histogram.append(macd_line[i] - signal_line[i])
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2) -> Tuple[List[float], List[float], List[float]]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return [], [], []
        
        sma_values = TechnicalAnalyzer.calculate_sma(prices, period)
        upper_bands = []
        lower_bands = []
        
        for i in range(period - 1, len(prices)):
            # Calculate standard deviation for the period
            period_prices = prices[i - period + 1:i + 1]
            mean = sum(period_prices) / len(period_prices)
            variance = sum((x - mean) ** 2 for x in period_prices) / len(period_prices)
            std = math.sqrt(variance)
            
            sma = sma_values[i - period + 1]
            upper_bands.append(sma + (std_dev * std))
            lower_bands.append(sma - (std_dev * std))
        
        return upper_bands, sma_values, lower_bands
    
    @staticmethod
    def calculate_stochastic(high: List[float], low: List[float], close: List[float], k_period: int = 14, d_period: int = 3) -> Tuple[List[float], List[float]]:
        """Calculate Stochastic Oscillator"""
        if len(close) < k_period:
            return [], []
        
        k_values = []
        d_values = []
        
        for i in range(k_period - 1, len(close)):
            period_high = max(high[i - k_period + 1:i + 1])
            period_low = min(low[i - k_period + 1:i + 1])
            
            if period_high == period_low:
                k = 50  # Neutral when high == low
            else:
                k = ((close[i] - period_low) / (period_high - period_low)) * 100
            
            k_values.append(k)
        
        # Calculate %D (SMA of %K)
        if len(k_values) >= d_period:
            d_values = TechnicalAnalyzer.calculate_sma(k_values, d_period)
        
        return k_values, d_values
    
    @staticmethod
    def calculate_support_resistance(prices: List[float], window: int = 5) -> Tuple[List[float], List[float]]:
        """Calculate support and resistance levels"""
        if len(prices) < window * 2:
            return [], []
        
        support_levels = []
        resistance_levels = []
        
        for i in range(window, len(prices) - window):
            # Check for local minima (support)
            if all(prices[i] <= prices[j] for j in range(i - window, i + window + 1)):
                support_levels.append(prices[i])
            
            # Check for local maxima (resistance)
            if all(prices[i] >= prices[j] for j in range(i - window, i + window + 1)):
                resistance_levels.append(prices[i])
        
        return support_levels, resistance_levels
    
    @staticmethod
    def calculate_pivot_points(high: float, low: float, close: float) -> Dict[str, float]:
        """Calculate pivot points"""
        pivot = (high + low + close) / 3
        
        return {
            "pivot": pivot,
            "r1": 2 * pivot - low,
            "r2": pivot + (high - low),
            "r3": high + 2 * (pivot - low),
            "s1": 2 * pivot - high,
            "s2": pivot - (high - low),
            "s3": low - 2 * (high - pivot)
        }
    
    @staticmethod
    def detect_patterns(prices: List[float], volumes: Optional[List[float]] = None) -> List[str]:
        """Detect chart patterns"""
        patterns = []
        
        if len(prices) < 10:
            return patterns
        
        # Simple pattern detection
        recent_prices = prices[-10:]
        
        # Double top pattern
        if len(recent_prices) >= 6:
            peak1 = max(recent_prices[:3])
            peak2 = max(recent_prices[3:6])
            if abs(peak1 - peak2) / peak1 < 0.02:  # Within 2%
                patterns.append("Double Top")
        
        # Double bottom pattern
        if len(recent_prices) >= 6:
            bottom1 = min(recent_prices[:3])
            bottom2 = min(recent_prices[3:6])
            if abs(bottom1 - bottom2) / bottom1 < 0.02:  # Within 2%
                patterns.append("Double Bottom")
        
        # Ascending triangle
        if len(recent_prices) >= 8:
            highs = [max(recent_prices[i:i+2]) for i in range(0, len(recent_prices)-1, 2)]
            if len(highs) >= 3 and all(abs(h - highs[0]) / highs[0] < 0.01 for h in highs):
                patterns.append("Ascending Triangle")
        
        # Descending triangle
        if len(recent_prices) >= 8:
            lows = [min(recent_prices[i:i+2]) for i in range(0, len(recent_prices)-1, 2)]
            if len(lows) >= 3 and all(abs(l - lows[0]) / lows[0] < 0.01 for l in lows):
                patterns.append("Descending Triangle")
        
        return patterns
    
    @staticmethod
    def generate_trading_signal(indicators: TechnicalIndicators) -> Tuple[SignalType, float, float]:
        """Generate overall trading signal based on indicators"""
        signals = []
        weights = []
        
        # RSI signal
        if indicators.rsi:
            if indicators.rsi > 70:
                signals.append(-2)  # Strong sell
                weights.append(0.2)
            elif indicators.rsi > 60:
                signals.append(-1)  # Sell
                weights.append(0.15)
            elif indicators.rsi < 30:
                signals.append(2)  # Strong buy
                weights.append(0.2)
            elif indicators.rsi < 40:
                signals.append(1)  # Buy
                weights.append(0.15)
            else:
                signals.append(0)  # Hold
                weights.append(0.1)
        
        # MACD signal
        if indicators.macd and indicators.macd_signal:
            if indicators.macd > indicators.macd_signal and indicators.macd_histogram and indicators.macd_histogram > 0:
                signals.append(1)
                weights.append(0.2)
            elif indicators.macd < indicators.macd_signal and indicators.macd_histogram and indicators.macd_histogram < 0:
                signals.append(-1)
                weights.append(0.2)
            else:
                signals.append(0)
                weights.append(0.1)
        
        # Moving average signal
        if indicators.sma_20 and indicators.sma_50:
            if indicators.sma_20 > indicators.sma_50:
                signals.append(1)
                weights.append(0.15)
            else:
                signals.append(-1)
                weights.append(0.15)
        
        # Bollinger Bands signal
        if indicators.bollinger_position:
            if indicators.bollinger_position == "Above Upper":
                signals.append(-1)
                weights.append(0.1)
            elif indicators.bollinger_position == "Below Lower":
                signals.append(1)
                weights.append(0.1)
            else:
                signals.append(0)
                weights.append(0.05)
        
        # Calculate weighted signal
        if signals and weights:
            weighted_signal = sum(s * w for s, w in zip(signals, weights)) / sum(weights)
        else:
            weighted_signal = 0
        
        # Convert to signal type
        if weighted_signal >= 1.5:
            signal_type = SignalType.STRONG_BUY
        elif weighted_signal >= 0.5:
            signal_type = SignalType.BUY
        elif weighted_signal <= -1.5:
            signal_type = SignalType.STRONG_SELL
        elif weighted_signal <= -0.5:
            signal_type = SignalType.SELL
        else:
            signal_type = SignalType.HOLD
        
        confidence = min(abs(weighted_signal) / 2, 1.0)
        
        return signal_type, weighted_signal, confidence


@function_tool
async def perform_technical_analysis(
    prices: List[float],
    high: Optional[List[float]] = None,
    low: Optional[List[float]] = None,
    close: Optional[List[float]] = None,
    volume: Optional[List[float]] = None,
    analysis_period: int = 50
) -> str:
    """
    Perform comprehensive technical analysis on price data.
    
    Args:
        prices: List of closing prices (or use close parameter)
        high: List of high prices (optional)
        low: List of low prices (optional)
        close: List of closing prices (optional, uses prices if not provided)
        volume: List of volume data (optional)
        analysis_period: Number of periods to analyze (default 50)
    """
    try:
        if not prices:
            return json.dumps({
                "success": False,
                "error": "No price data provided"
            }, ensure_ascii=False, indent=2)
        
        # Use prices as close if close not provided
        if close is None:
            close = prices
        
        # Limit data to analysis period
        if len(close) > analysis_period:
            close = close[-analysis_period:]
            if high:
                high = high[-analysis_period:]
            if low:
                low = low[-analysis_period:]
            if volume:
                volume = volume[-analysis_period:]
        
        analyzer = TechnicalAnalyzer()
        indicators = TechnicalIndicators()
        
        # Calculate moving averages
        sma_5 = analyzer.calculate_sma(close, 5)
        sma_10 = analyzer.calculate_sma(close, 10)
        sma_20 = analyzer.calculate_sma(close, 20)
        sma_50 = analyzer.calculate_sma(close, 50)
        sma_200 = analyzer.calculate_sma(close, 200)
        
        if sma_5:
            indicators.sma_5 = sma_5[-1]
        if sma_10:
            indicators.sma_10 = sma_10[-1]
        if sma_20:
            indicators.sma_20 = sma_20[-1]
        if sma_50:
            indicators.sma_50 = sma_50[-1]
        if sma_200:
            indicators.sma_200 = sma_200[-1]
        
        # Calculate EMAs
        ema_12 = analyzer.calculate_ema(close, 12)
        ema_26 = analyzer.calculate_ema(close, 26)
        
        if ema_12:
            indicators.ema_12 = ema_12[-1]
        if ema_26:
            indicators.ema_26 = ema_26[-1]
        
        # Calculate RSI
        rsi_values, rsi_signals = analyzer.calculate_rsi(close, 14)
        if rsi_values:
            indicators.rsi = rsi_values[-1]
            indicators.rsi_signal = rsi_signals[-1]
        
        # Calculate MACD
        macd_line, signal_line, histogram = analyzer.calculate_macd(close)
        if macd_line:
            indicators.macd = macd_line[-1]
        if signal_line:
            indicators.macd_signal = signal_line[-1]
        if histogram:
            indicators.macd_histogram = histogram[-1]
        
        # Calculate Bollinger Bands
        bb_upper, bb_middle, bb_lower = analyzer.calculate_bollinger_bands(close)
        if bb_upper and bb_lower:
            indicators.bollinger_upper = bb_upper[-1]
            indicators.bollinger_middle = bb_middle[-1]
            indicators.bollinger_lower = bb_lower[-1]
            
            # Determine position relative to bands
            current_price = close[-1]
            if current_price > bb_upper[-1]:
                indicators.bollinger_position = "Above Upper"
            elif current_price < bb_lower[-1]:
                indicators.bollinger_position = "Below Lower"
            else:
                indicators.bollinger_position = "Within Bands"
        
        # Calculate Stochastic Oscillator
        if high and low:
            k_values, d_values = analyzer.calculate_stochastic(high, low, close)
            if k_values:
                indicators.stochastic_k = k_values[-1]
            if d_values:
                indicators.stochastic_d = d_values[-1]
        
        # Calculate Support and Resistance
        support_levels, resistance_levels = analyzer.calculate_support_resistance(close)
        indicators.support_levels = support_levels[-5:] if support_levels else []  # Last 5 levels
        indicators.resistance_levels = resistance_levels[-5:] if resistance_levels else []
        
        # Calculate Pivot Points
        if high and low:
            current_high = high[-1]
            current_low = low[-1]
            current_close = close[-1]
            pivot_points = analyzer.calculate_pivot_points(current_high, current_low, current_close)
            indicators.pivot_point = pivot_points["pivot"]
            indicators.pivot_r1 = pivot_points["r1"]
            indicators.pivot_r2 = pivot_points["r2"]
            indicators.pivot_s1 = pivot_points["s1"]
            indicators.pivot_s2 = pivot_points["s2"]
        
        # Detect patterns
        patterns = analyzer.detect_patterns(close, volume)
        indicators.patterns = patterns
        
        # Determine trend direction
        if len(close) >= 20:
            recent_20 = close[-20:]
            if recent_20[-1] > recent_20[0] * 1.05:  # 5% increase
                indicators.trend_direction = TrendDirection.UPTREND
            elif recent_20[-1] < recent_20[0] * 0.95:  # 5% decrease
                indicators.trend_direction = TrendDirection.DOWNTREND
            else:
                indicators.trend_direction = TrendDirection.SIDEWAYS
        
        # Generate trading signal
        signal_type, signal_strength, confidence = analyzer.generate_trading_signal(indicators)
        indicators.overall_signal = signal_type
        indicators.signal_strength = signal_strength
        indicators.confidence_level = confidence
        
        # Convert to dict and filter out None values
        result_dict = indicators.model_dump(exclude_none=True)
        
        return json.dumps({
            "success": True,
            "technical_analysis": result_dict,
            "summary": {
                "current_price": close[-1],
                "trend": indicators.trend_direction.value if indicators.trend_direction else "Unknown",
                "signal": indicators.overall_signal.value if indicators.overall_signal else "Unknown",
                "confidence": indicators.confidence_level,
                "patterns_detected": len(indicators.patterns),
                "support_levels": len(indicators.support_levels),
                "resistance_levels": len(indicators.resistance_levels)
            },
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"Error in perform_technical_analysis: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg
        }, ensure_ascii=False, indent=2)


@function_tool
async def calculate_risk_metrics(
    prices: List[float],
    returns: Optional[List[float]] = None,
    risk_free_rate: float = 0.03,
    market_returns: Optional[List[float]] = None
) -> str:
    """
    Calculate risk metrics for portfolio analysis.
    
    Args:
        prices: List of asset prices
        returns: List of returns (optional, will calculate from prices if not provided)
        risk_free_rate: Risk-free rate (default 3%)
        market_returns: List of market returns for beta calculation (optional)
    """
    try:
        if not prices or len(prices) < 2:
            return json.dumps({
                "success": False,
                "error": "Insufficient price data for risk calculation"
            }, ensure_ascii=False, indent=2)
        
        # Calculate returns if not provided
        if returns is None:
            returns = []
            for i in range(1, len(prices)):
                ret = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(ret)
        
        if len(returns) < 2:
            return json.dumps({
                "success": False,
                "error": "Insufficient return data for risk calculation"
            }, ensure_ascii=False, indent=2)
        
        # Calculate basic risk metrics
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
        volatility = math.sqrt(variance)
        
        # Calculate Sharpe ratio
        excess_return = mean_return - risk_free_rate
        sharpe_ratio = excess_return / volatility if volatility > 0 else 0
        
        # Calculate maximum drawdown
        peak = prices[0]
        max_drawdown = 0
        for price in prices:
            if price > peak:
                peak = price
            drawdown = (peak - price) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Calculate Value at Risk (VaR) - 95% confidence
        sorted_returns = sorted(returns)
        var_95 = sorted_returns[int(len(sorted_returns) * 0.05)]
        
        # Calculate Conditional VaR (Expected Shortfall)
        var_returns = [r for r in returns if r <= var_95]
        cvar = sum(var_returns) / len(var_returns) if var_returns else 0
        
        # Calculate Beta if market returns provided
        beta = None
        if market_returns and len(market_returns) == len(returns):
            # Calculate covariance and market variance
            mean_market = sum(market_returns) / len(market_returns)
            covariance = sum((r - mean_return) * (mr - mean_market) for r, mr in zip(returns, market_returns)) / len(returns)
            market_variance = sum((mr - mean_market) ** 2 for mr in market_returns) / len(market_returns)
            
            if market_variance > 0:
                beta = covariance / market_variance
        
        # Calculate Sortino ratio (downside deviation)
        downside_returns = [r for r in returns if r < 0]
        if downside_returns:
            downside_variance = sum(r ** 2 for r in downside_returns) / len(downside_returns)
            downside_deviation = math.sqrt(downside_variance)
            sortino_ratio = excess_return / downside_deviation if downside_deviation > 0 else 0
        else:
            sortino_ratio = None
        
        # Risk level assessment
        risk_level = "Low"
        if volatility > 0.3:
            risk_level = "Very High"
        elif volatility > 0.2:
            risk_level = "High"
        elif volatility > 0.1:
            risk_level = "Medium"
        
        result = {
            "success": True,
            "risk_metrics": {
                "volatility": volatility,
                "mean_return": mean_return,
                "sharpe_ratio": sharpe_ratio,
                "sortino_ratio": sortino_ratio,
                "max_drawdown": max_drawdown,
                "var_95": var_95,
                "cvar": cvar,
                "beta": beta,
                "risk_level": risk_level
            },
            "calculation_details": {
                "total_periods": len(returns),
                "risk_free_rate": risk_free_rate,
                "has_market_data": market_returns is not None
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"Error in calculate_risk_metrics: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg
        }, ensure_ascii=False, indent=2)
