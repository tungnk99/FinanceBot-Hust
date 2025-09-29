"""
YFinance Data Tool - Lấy dữ liệu giá từ Yahoo Finance
"""
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from agents import function_tool
import yfinance as yf

logger = logging.getLogger(__name__)


class MarketDataRequest(BaseModel):
    """Request model for market data"""
    symbol: str = Field(..., description="Stock symbol (e.g., 'AAPL', 'VIC.VN')")
    period: str = Field(default="1y", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
    interval: str = Field(default="1d", description="Interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")


@function_tool
async def get_stock_data(
    symbol: str,
    period: str = "1y",
    interval: str = "1d"
) -> str:
    """
    Lấy dữ liệu giá cổ phiếu từ Yahoo Finance.
    
    Args:
        symbol: Mã cổ phiếu (ví dụ: 'AAPL', 'VIC.VN', 'MSFT')
        period: Khoảng thời gian (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Khoảng thời gian giữa các điểm dữ liệu (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    Returns:
        JSON string chứa dữ liệu giá và thông tin cơ bản về cổ phiếu
    """
    try:
        # Tạo ticker object
        ticker = yf.Ticker(symbol)
        
        # Lấy dữ liệu lịch sử
        hist_data = ticker.history(period=period, interval=interval)
        
        if hist_data.empty:
            return json.dumps({
                "success": False,
                "error": f"Không tìm thấy dữ liệu cho symbol: {symbol}",
                "suggestion": "Kiểm tra lại mã cổ phiếu hoặc thử với symbol khác"
            }, ensure_ascii=False, indent=2)
        
        # Lấy thông tin cơ bản
        info = ticker.info
        
        # Chuyển đổi dữ liệu thành list
        prices = hist_data['Close'].tolist()
        highs = hist_data['High'].tolist()
        lows = hist_data['Low'].tolist()
        opens = hist_data['Open'].tolist()
        volumes = hist_data['Volume'].tolist()
        dates = hist_data.index.strftime('%Y-%m-%d').tolist()
        
        # Tính toán một số metrics cơ bản
        current_price = prices[-1] if prices else 0
        price_change = (current_price - prices[-2]) if len(prices) > 1 else 0
        price_change_percent = (price_change / prices[-2] * 100) if len(prices) > 1 and prices[-2] != 0 else 0
        
        # Tính moving averages đơn giản
        sma_20 = sum(prices[-20:]) / min(20, len(prices)) if len(prices) >= 20 else None
        sma_50 = sum(prices[-50:]) / min(50, len(prices)) if len(prices) >= 50 else None
        
        result = {
            "success": True,
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data_points": len(prices),
            "current_price": current_price,
            "price_change": price_change,
            "price_change_percent": round(price_change_percent, 2),
            "sma_20": round(sma_20, 2) if sma_20 else None,
            "sma_50": round(sma_50, 2) if sma_50 else None,
            "price_data": {
                "dates": dates,
                "prices": [round(p, 2) for p in prices],
                "highs": [round(h, 2) for h in highs],
                "lows": [round(l, 2) for l in lows],
                "opens": [round(o, 2) for o in opens],
                "volumes": volumes
            },
            "basic_info": {
                "company_name": info.get('longName', 'N/A'),
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A'),
                "market_cap": info.get('marketCap', 'N/A'),
                "pe_ratio": info.get('trailingPE', 'N/A'),
                "dividend_yield": info.get('dividendYield', 'N/A'),
                "52_week_high": info.get('fiftyTwoWeekHigh', 'N/A'),
                "52_week_low": info.get('fiftyTwoWeekLow', 'N/A')
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"Lỗi khi lấy dữ liệu cho {symbol}: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg,
            "symbol": symbol
        }, ensure_ascii=False, indent=2)


@function_tool
async def get_stock_with_technical_analysis(
    symbol: str,
    period: str = "1y",
    interval: str = "1d"
) -> str:
    """
    Lấy dữ liệu cổ phiếu từ yfinance và tính toán technical indicators trong một bước.
    Tool này tự động thực hiện cả việc lấy dữ liệu và tính toán indicators.
    
    Args:
        symbol: Mã cổ phiếu (ví dụ: 'AAPL', 'VIC.VN', 'MSFT')
        period: Khoảng thời gian (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Khoảng thời gian (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    Returns:
        JSON string chứa dữ liệu giá + technical indicators đã tính toán
    """
    try:
        # Bước 1: Lấy dữ liệu từ yfinance
        ticker = yf.Ticker(symbol)
        hist_data = ticker.history(period=period, interval=interval)
        
        if hist_data.empty:
            return json.dumps({
                "success": False,
                "error": f"Không tìm thấy dữ liệu cho symbol: {symbol}",
                "suggestion": "Kiểm tra lại mã cổ phiếu hoặc thử với symbol khác"
            }, ensure_ascii=False, indent=2)
        
        # Lấy thông tin cơ bản
        info = ticker.info
        
        # Chuyển đổi dữ liệu
        prices = hist_data['Close'].tolist()
        highs = hist_data['High'].tolist()
        lows = hist_data['Low'].tolist()
        opens = hist_data['Open'].tolist()
        volumes = hist_data['Volume'].tolist()
        dates = hist_data.index.strftime('%Y-%m-%d').tolist()
        
        # Bước 2: Tính toán technical indicators
        from src.tools.technical_analysis import TechnicalAnalyzer
        
        analyzer = TechnicalAnalyzer()
        
        # Tính Moving Averages
        sma_5 = analyzer.calculate_sma(prices, 5)
        sma_10 = analyzer.calculate_sma(prices, 10)
        sma_20 = analyzer.calculate_sma(prices, 20)
        sma_50 = analyzer.calculate_sma(prices, 50)
        sma_200 = analyzer.calculate_sma(prices, 200)
        
        # Tính EMAs
        ema_12 = analyzer.calculate_ema(prices, 12)
        ema_26 = analyzer.calculate_ema(prices, 26)
        
        # Tính RSI
        rsi_values, rsi_signals = analyzer.calculate_rsi(prices, 14)
        
        # Tính MACD
        macd_line, signal_line, histogram = analyzer.calculate_macd(prices)
        
        # Tính Bollinger Bands
        bb_upper, bb_middle, bb_lower = analyzer.calculate_bollinger_bands(prices)
        
        # Tính Stochastic (nếu có high/low data)
        k_values, d_values = [], []
        if len(highs) > 0 and len(lows) > 0:
            k_values, d_values = analyzer.calculate_stochastic(highs, lows, prices)
        
        # Tính Support/Resistance
        support_levels, resistance_levels = analyzer.calculate_support_resistance(prices)
        
        # Detect patterns
        patterns = analyzer.detect_patterns(prices, volumes)
        
        # Bước 3: Tổng hợp kết quả
        current_price = prices[-1] if prices else 0
        price_change = (current_price - prices[-2]) if len(prices) > 1 else 0
        price_change_percent = (price_change / prices[-2] * 100) if len(prices) > 1 and prices[-2] != 0 else 0
        
        result = {
            "success": True,
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data_points": len(prices),
            "current_price": current_price,
            "price_change": price_change,
            "price_change_percent": round(price_change_percent, 2),
            
            # Basic info
            "basic_info": {
                "company_name": info.get('longName', 'N/A'),
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A'),
                "market_cap": info.get('marketCap', 'N/A'),
                "pe_ratio": info.get('trailingPE', 'N/A'),
                "dividend_yield": info.get('dividendYield', 'N/A'),
                "52_week_high": info.get('fiftyTwoWeekHigh', 'N/A'),
                "52_week_low": info.get('fiftyTwoWeekLow', 'N/A')
            },
            
            # Price data
            "price_data": {
                "dates": dates,
                "prices": [round(p, 2) for p in prices],
                "highs": [round(h, 2) for h in highs],
                "lows": [round(l, 2) for l in lows],
                "opens": [round(o, 2) for o in opens],
                "volumes": volumes
            },
            
            # Technical Indicators (đã tính toán sẵn)
            "technical_indicators": {
                "moving_averages": {
                    "sma_5": round(sma_5[-1], 2) if sma_5 else None,
                    "sma_10": round(sma_10[-1], 2) if sma_10 else None,
                    "sma_20": round(sma_20[-1], 2) if sma_20 else None,
                    "sma_50": round(sma_50[-1], 2) if sma_50 else None,
                    "sma_200": round(sma_200[-1], 2) if sma_200 else None,
                    "ema_12": round(ema_12[-1], 2) if ema_12 else None,
                    "ema_26": round(ema_26[-1], 2) if ema_26 else None
                },
                "oscillators": {
                    "rsi": round(rsi_values[-1], 2) if rsi_values else None,
                    "rsi_signal": rsi_signals[-1] if rsi_signals else None,
                    "stochastic_k": round(k_values[-1], 2) if k_values else None,
                    "stochastic_d": round(d_values[-1], 2) if d_values else None
                },
                "trend_indicators": {
                    "macd": round(macd_line[-1], 2) if macd_line else None,
                    "macd_signal": round(signal_line[-1], 2) if signal_line else None,
                    "macd_histogram": round(histogram[-1], 2) if histogram else None
                },
                "volatility": {
                    "bollinger_upper": round(bb_upper[-1], 2) if bb_upper else None,
                    "bollinger_middle": round(bb_middle[-1], 2) if bb_middle else None,
                    "bollinger_lower": round(bb_lower[-1], 2) if bb_lower else None,
                    "bollinger_position": "Above Upper" if current_price > bb_upper[-1] else 
                                        "Below Lower" if current_price < bb_lower[-1] else 
                                        "Within Bands" if bb_upper and bb_lower else None
                },
                "support_resistance": {
                    "support_levels": [round(s, 2) for s in support_levels[-5:]] if support_levels else [],
                    "resistance_levels": [round(r, 2) for r in resistance_levels[-5:]] if resistance_levels else []
                },
                "patterns": patterns,
                "analysis_summary": {
                    "trend": "Uptrend" if sma_20 and sma_50 and sma_20[-1] > sma_50[-1] else 
                            "Downtrend" if sma_20 and sma_50 and sma_20[-1] < sma_50[-1] else "Sideways",
                    "rsi_level": rsi_signals[-1] if rsi_signals else "Neutral",
                    "macd_signal": "Bullish" if macd_line and signal_line and macd_line[-1] > signal_line[-1] else
                                  "Bearish" if macd_line and signal_line and macd_line[-1] < signal_line[-1] else "Neutral"
                }
            },
            
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"Lỗi khi lấy dữ liệu và tính technical analysis cho {symbol}: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg,
            "symbol": symbol
        }, ensure_ascii=False, indent=2)


@function_tool
async def get_crypto_data(
    symbol: str,
    period: str = "1y",
    interval: str = "1d"
) -> str:
    """
    Lấy dữ liệu giá cryptocurrency từ Yahoo Finance.
    
    Args:
        symbol: Mã crypto (ví dụ: 'BTC-USD', 'ETH-USD', 'ADA-USD')
        period: Khoảng thời gian (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Khoảng thời gian giữa các điểm dữ liệu (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    Returns:
        JSON string chứa dữ liệu giá crypto
    """
    try:
        # Tạo ticker object
        ticker = yf.Ticker(symbol)
        
        # Lấy dữ liệu lịch sử
        hist_data = ticker.history(period=period, interval=interval)
        
        if hist_data.empty:
            return json.dumps({
                "success": False,
                "error": f"Không tìm thấy dữ liệu cho crypto: {symbol}",
                "suggestion": "Kiểm tra lại mã crypto (thường có format BTC-USD, ETH-USD)"
            }, ensure_ascii=False, indent=2)
        
        # Lấy thông tin cơ bản
        info = ticker.info
        
        # Chuyển đổi dữ liệu thành list
        prices = hist_data['Close'].tolist()
        highs = hist_data['High'].tolist()
        lows = hist_data['Low'].tolist()
        opens = hist_data['Open'].tolist()
        volumes = hist_data['Volume'].tolist()
        dates = hist_data.index.strftime('%Y-%m-%d').tolist()
        
        # Tính toán metrics cơ bản
        current_price = prices[-1] if prices else 0
        price_change = (current_price - prices[-2]) if len(prices) > 1 else 0
        price_change_percent = (price_change / prices[-2] * 100) if len(prices) > 1 and prices[-2] != 0 else 0
        
        result = {
            "success": True,
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data_points": len(prices),
            "current_price": current_price,
            "price_change": price_change,
            "price_change_percent": round(price_change_percent, 2),
            "price_data": {
                "dates": dates,
                "prices": [round(p, 2) for p in prices],
                "highs": [round(h, 2) for h in highs],
                "lows": [round(l, 2) for l in lows],
                "opens": [round(o, 2) for o in opens],
                "volumes": volumes
            },
            "crypto_info": {
                "name": info.get('longName', 'N/A'),
                "market_cap": info.get('marketCap', 'N/A'),
                "circulating_supply": info.get('circulatingSupply', 'N/A'),
                "total_supply": info.get('totalSupply', 'N/A'),
                "24h_volume": info.get('volume24Hr', 'N/A'),
                "52_week_high": info.get('fiftyTwoWeekHigh', 'N/A'),
                "52_week_low": info.get('fiftyTwoWeekLow', 'N/A')
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"Lỗi khi lấy dữ liệu crypto cho {symbol}: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg,
            "symbol": symbol
        }, ensure_ascii=False, indent=2)


@function_tool
async def get_stock_with_technical_analysis(
    symbol: str,
    period: str = "1y",
    interval: str = "1d"
) -> str:
    """
    Lấy dữ liệu cổ phiếu từ yfinance và tính toán technical indicators trong một bước.
    Tool này tự động thực hiện cả việc lấy dữ liệu và tính toán indicators.
    
    Args:
        symbol: Mã cổ phiếu (ví dụ: 'AAPL', 'VIC.VN', 'MSFT')
        period: Khoảng thời gian (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Khoảng thời gian (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    Returns:
        JSON string chứa dữ liệu giá + technical indicators đã tính toán
    """
    try:
        # Bước 1: Lấy dữ liệu từ yfinance
        ticker = yf.Ticker(symbol)
        hist_data = ticker.history(period=period, interval=interval)
        
        if hist_data.empty:
            return json.dumps({
                "success": False,
                "error": f"Không tìm thấy dữ liệu cho symbol: {symbol}",
                "suggestion": "Kiểm tra lại mã cổ phiếu hoặc thử với symbol khác"
            }, ensure_ascii=False, indent=2)
        
        # Lấy thông tin cơ bản
        info = ticker.info
        
        # Chuyển đổi dữ liệu
        prices = hist_data['Close'].tolist()
        highs = hist_data['High'].tolist()
        lows = hist_data['Low'].tolist()
        opens = hist_data['Open'].tolist()
        volumes = hist_data['Volume'].tolist()
        dates = hist_data.index.strftime('%Y-%m-%d').tolist()
        
        # Bước 2: Tính toán technical indicators
        from src.tools.technical_analysis import TechnicalAnalyzer
        
        analyzer = TechnicalAnalyzer()
        
        # Tính Moving Averages
        sma_5 = analyzer.calculate_sma(prices, 5)
        sma_10 = analyzer.calculate_sma(prices, 10)
        sma_20 = analyzer.calculate_sma(prices, 20)
        sma_50 = analyzer.calculate_sma(prices, 50)
        sma_200 = analyzer.calculate_sma(prices, 200)
        
        # Tính EMAs
        ema_12 = analyzer.calculate_ema(prices, 12)
        ema_26 = analyzer.calculate_ema(prices, 26)
        
        # Tính RSI
        rsi_values, rsi_signals = analyzer.calculate_rsi(prices, 14)
        
        # Tính MACD
        macd_line, signal_line, histogram = analyzer.calculate_macd(prices)
        
        # Tính Bollinger Bands
        bb_upper, bb_middle, bb_lower = analyzer.calculate_bollinger_bands(prices)
        
        # Tính Stochastic (nếu có high/low data)
        k_values, d_values = [], []
        if len(highs) > 0 and len(lows) > 0:
            k_values, d_values = analyzer.calculate_stochastic(highs, lows, prices)
        
        # Tính Support/Resistance
        support_levels, resistance_levels = analyzer.calculate_support_resistance(prices)
        
        # Detect patterns
        patterns = analyzer.detect_patterns(prices, volumes)
        
        # Bước 3: Tổng hợp kết quả
        current_price = prices[-1] if prices else 0
        price_change = (current_price - prices[-2]) if len(prices) > 1 else 0
        price_change_percent = (price_change / prices[-2] * 100) if len(prices) > 1 and prices[-2] != 0 else 0
        
        result = {
            "success": True,
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data_points": len(prices),
            "current_price": current_price,
            "price_change": price_change,
            "price_change_percent": round(price_change_percent, 2),
            
            # Basic info
            "basic_info": {
                "company_name": info.get('longName', 'N/A'),
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A'),
                "market_cap": info.get('marketCap', 'N/A'),
                "pe_ratio": info.get('trailingPE', 'N/A'),
                "dividend_yield": info.get('dividendYield', 'N/A'),
                "52_week_high": info.get('fiftyTwoWeekHigh', 'N/A'),
                "52_week_low": info.get('fiftyTwoWeekLow', 'N/A')
            },
            
            # Price data
            "price_data": {
                "dates": dates,
                "prices": [round(p, 2) for p in prices],
                "highs": [round(h, 2) for h in highs],
                "lows": [round(l, 2) for l in lows],
                "opens": [round(o, 2) for o in opens],
                "volumes": volumes
            },
            
            # Technical Indicators (đã tính toán sẵn)
            "technical_indicators": {
                "moving_averages": {
                    "sma_5": round(sma_5[-1], 2) if sma_5 else None,
                    "sma_10": round(sma_10[-1], 2) if sma_10 else None,
                    "sma_20": round(sma_20[-1], 2) if sma_20 else None,
                    "sma_50": round(sma_50[-1], 2) if sma_50 else None,
                    "sma_200": round(sma_200[-1], 2) if sma_200 else None,
                    "ema_12": round(ema_12[-1], 2) if ema_12 else None,
                    "ema_26": round(ema_26[-1], 2) if ema_26 else None
                },
                "oscillators": {
                    "rsi": round(rsi_values[-1], 2) if rsi_values else None,
                    "rsi_signal": rsi_signals[-1] if rsi_signals else None,
                    "stochastic_k": round(k_values[-1], 2) if k_values else None,
                    "stochastic_d": round(d_values[-1], 2) if d_values else None
                },
                "trend_indicators": {
                    "macd": round(macd_line[-1], 2) if macd_line else None,
                    "macd_signal": round(signal_line[-1], 2) if signal_line else None,
                    "macd_histogram": round(histogram[-1], 2) if histogram else None
                },
                "volatility": {
                    "bollinger_upper": round(bb_upper[-1], 2) if bb_upper else None,
                    "bollinger_middle": round(bb_middle[-1], 2) if bb_middle else None,
                    "bollinger_lower": round(bb_lower[-1], 2) if bb_lower else None,
                    "bollinger_position": "Above Upper" if current_price > bb_upper[-1] else 
                                        "Below Lower" if current_price < bb_lower[-1] else 
                                        "Within Bands" if bb_upper and bb_lower else None
                },
                "support_resistance": {
                    "support_levels": [round(s, 2) for s in support_levels[-5:]] if support_levels else [],
                    "resistance_levels": [round(r, 2) for r in resistance_levels[-5:]] if resistance_levels else []
                },
                "patterns": patterns,
                "analysis_summary": {
                    "trend": "Uptrend" if sma_20 and sma_50 and sma_20[-1] > sma_50[-1] else 
                            "Downtrend" if sma_20 and sma_50 and sma_20[-1] < sma_50[-1] else "Sideways",
                    "rsi_level": rsi_signals[-1] if rsi_signals else "Neutral",
                    "macd_signal": "Bullish" if macd_line and signal_line and macd_line[-1] > signal_line[-1] else
                                  "Bearish" if macd_line and signal_line and macd_line[-1] < signal_line[-1] else "Neutral"
                }
            },
            
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"Lỗi khi lấy dữ liệu và tính technical analysis cho {symbol}: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg,
            "symbol": symbol
        }, ensure_ascii=False, indent=2)


@function_tool
async def get_market_data_for_technical_analysis(
    symbol: str,
    period: str = "1y",
    interval: str = "1d"
) -> str:
    """
    Lấy dữ liệu thị trường từ yfinance và chuẩn bị cho technical analysis.
    Tool này lấy dữ liệu giá và trả về format phù hợp để sử dụng với perform_technical_analysis.
    
    Args:
        symbol: Mã cổ phiếu hoặc crypto (ví dụ: 'AAPL', 'BTC-USD', 'VIC.VN')
        period: Khoảng thời gian (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Khoảng thời gian (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    Returns:
        JSON string chứa dữ liệu giá được format sẵn cho technical analysis
    """
    try:
        # Tạo ticker object
        ticker = yf.Ticker(symbol)
        
        # Lấy dữ liệu lịch sử
        hist_data = ticker.history(period=period, interval=interval)
        
        if hist_data.empty:
            return json.dumps({
                "success": False,
                "error": f"Không tìm thấy dữ liệu cho {symbol}",
                "symbol": symbol
            }, ensure_ascii=False, indent=2)
        
        # Chuyển đổi dữ liệu thành list
        prices = hist_data['Close'].tolist()
        highs = hist_data['High'].tolist()
        lows = hist_data['Low'].tolist()
        opens = hist_data['Open'].tolist()
        volumes = hist_data['Volume'].tolist()
        dates = hist_data.index.strftime('%Y-%m-%d').tolist()
        
        # Lấy thông tin cơ bản
        info = ticker.info
        
        result = {
            "success": True,
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data_points": len(prices),
            "current_price": prices[-1] if prices else 0,
            "price_data": {
                "dates": dates,
                "prices": prices,  # Raw prices for technical analysis
                "highs": highs,
                "lows": lows,
                "opens": opens,
                "volumes": volumes
            },
            "basic_info": {
                "company_name": info.get('longName', 'N/A'),
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A'),
                "market_cap": info.get('marketCap', 'N/A')
            },
            "technical_analysis_ready": True,
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"Lỗi khi lấy dữ liệu cho technical analysis {symbol}: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg,
            "symbol": symbol
        }, ensure_ascii=False, indent=2)


@function_tool
async def get_stock_with_technical_analysis(
    symbol: str,
    period: str = "1y",
    interval: str = "1d"
) -> str:
    """
    Lấy dữ liệu cổ phiếu từ yfinance và tính toán technical indicators trong một bước.
    Tool này tự động thực hiện cả việc lấy dữ liệu và tính toán indicators.
    
    Args:
        symbol: Mã cổ phiếu (ví dụ: 'AAPL', 'VIC.VN', 'MSFT')
        period: Khoảng thời gian (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Khoảng thời gian (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    Returns:
        JSON string chứa dữ liệu giá + technical indicators đã tính toán
    """
    try:
        # Bước 1: Lấy dữ liệu từ yfinance
        ticker = yf.Ticker(symbol)
        hist_data = ticker.history(period=period, interval=interval)
        
        if hist_data.empty:
            return json.dumps({
                "success": False,
                "error": f"Không tìm thấy dữ liệu cho symbol: {symbol}",
                "suggestion": "Kiểm tra lại mã cổ phiếu hoặc thử với symbol khác"
            }, ensure_ascii=False, indent=2)
        
        # Lấy thông tin cơ bản
        info = ticker.info
        
        # Chuyển đổi dữ liệu
        prices = hist_data['Close'].tolist()
        highs = hist_data['High'].tolist()
        lows = hist_data['Low'].tolist()
        opens = hist_data['Open'].tolist()
        volumes = hist_data['Volume'].tolist()
        dates = hist_data.index.strftime('%Y-%m-%d').tolist()
        
        # Bước 2: Tính toán technical indicators
        from src.tools.technical_analysis import TechnicalAnalyzer
        
        analyzer = TechnicalAnalyzer()
        
        # Tính Moving Averages
        sma_5 = analyzer.calculate_sma(prices, 5)
        sma_10 = analyzer.calculate_sma(prices, 10)
        sma_20 = analyzer.calculate_sma(prices, 20)
        sma_50 = analyzer.calculate_sma(prices, 50)
        sma_200 = analyzer.calculate_sma(prices, 200)
        
        # Tính EMAs
        ema_12 = analyzer.calculate_ema(prices, 12)
        ema_26 = analyzer.calculate_ema(prices, 26)
        
        # Tính RSI
        rsi_values, rsi_signals = analyzer.calculate_rsi(prices, 14)
        
        # Tính MACD
        macd_line, signal_line, histogram = analyzer.calculate_macd(prices)
        
        # Tính Bollinger Bands
        bb_upper, bb_middle, bb_lower = analyzer.calculate_bollinger_bands(prices)
        
        # Tính Stochastic (nếu có high/low data)
        k_values, d_values = [], []
        if len(highs) > 0 and len(lows) > 0:
            k_values, d_values = analyzer.calculate_stochastic(highs, lows, prices)
        
        # Tính Support/Resistance
        support_levels, resistance_levels = analyzer.calculate_support_resistance(prices)
        
        # Detect patterns
        patterns = analyzer.detect_patterns(prices, volumes)
        
        # Bước 3: Tổng hợp kết quả
        current_price = prices[-1] if prices else 0
        price_change = (current_price - prices[-2]) if len(prices) > 1 else 0
        price_change_percent = (price_change / prices[-2] * 100) if len(prices) > 1 and prices[-2] != 0 else 0
        
        result = {
            "success": True,
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data_points": len(prices),
            "current_price": current_price,
            "price_change": price_change,
            "price_change_percent": round(price_change_percent, 2),
            
            # Basic info
            "basic_info": {
                "company_name": info.get('longName', 'N/A'),
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A'),
                "market_cap": info.get('marketCap', 'N/A'),
                "pe_ratio": info.get('trailingPE', 'N/A'),
                "dividend_yield": info.get('dividendYield', 'N/A'),
                "52_week_high": info.get('fiftyTwoWeekHigh', 'N/A'),
                "52_week_low": info.get('fiftyTwoWeekLow', 'N/A')
            },
            
            # Price data
            "price_data": {
                "dates": dates,
                "prices": [round(p, 2) for p in prices],
                "highs": [round(h, 2) for h in highs],
                "lows": [round(l, 2) for l in lows],
                "opens": [round(o, 2) for o in opens],
                "volumes": volumes
            },
            
            # Technical Indicators (đã tính toán sẵn)
            "technical_indicators": {
                "moving_averages": {
                    "sma_5": round(sma_5[-1], 2) if sma_5 else None,
                    "sma_10": round(sma_10[-1], 2) if sma_10 else None,
                    "sma_20": round(sma_20[-1], 2) if sma_20 else None,
                    "sma_50": round(sma_50[-1], 2) if sma_50 else None,
                    "sma_200": round(sma_200[-1], 2) if sma_200 else None,
                    "ema_12": round(ema_12[-1], 2) if ema_12 else None,
                    "ema_26": round(ema_26[-1], 2) if ema_26 else None
                },
                "oscillators": {
                    "rsi": round(rsi_values[-1], 2) if rsi_values else None,
                    "rsi_signal": rsi_signals[-1] if rsi_signals else None,
                    "stochastic_k": round(k_values[-1], 2) if k_values else None,
                    "stochastic_d": round(d_values[-1], 2) if d_values else None
                },
                "trend_indicators": {
                    "macd": round(macd_line[-1], 2) if macd_line else None,
                    "macd_signal": round(signal_line[-1], 2) if signal_line else None,
                    "macd_histogram": round(histogram[-1], 2) if histogram else None
                },
                "volatility": {
                    "bollinger_upper": round(bb_upper[-1], 2) if bb_upper else None,
                    "bollinger_middle": round(bb_middle[-1], 2) if bb_middle else None,
                    "bollinger_lower": round(bb_lower[-1], 2) if bb_lower else None,
                    "bollinger_position": "Above Upper" if current_price > bb_upper[-1] else 
                                        "Below Lower" if current_price < bb_lower[-1] else 
                                        "Within Bands" if bb_upper and bb_lower else None
                },
                "support_resistance": {
                    "support_levels": [round(s, 2) for s in support_levels[-5:]] if support_levels else [],
                    "resistance_levels": [round(r, 2) for r in resistance_levels[-5:]] if resistance_levels else []
                },
                "patterns": patterns,
                "analysis_summary": {
                    "trend": "Uptrend" if sma_20 and sma_50 and sma_20[-1] > sma_50[-1] else 
                            "Downtrend" if sma_20 and sma_50 and sma_20[-1] < sma_50[-1] else "Sideways",
                    "rsi_level": rsi_signals[-1] if rsi_signals else "Neutral",
                    "macd_signal": "Bullish" if macd_line and signal_line and macd_line[-1] > signal_line[-1] else
                                  "Bearish" if macd_line and signal_line and macd_line[-1] < signal_line[-1] else "Neutral"
                }
            },
            
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"Lỗi khi lấy dữ liệu và tính technical analysis cho {symbol}: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg,
            "symbol": symbol
        }, ensure_ascii=False, indent=2)
