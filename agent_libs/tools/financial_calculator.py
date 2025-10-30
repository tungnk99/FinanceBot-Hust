"""
Financial Calculator Tool - Công cụ tính toán các chỉ số tài chính
"""
import math
import json
import logging
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from agents import function_tool

logger = logging.getLogger(__name__)


class FinancialMetrics(BaseModel):
    """Financial metrics calculation result"""
    
    # Profitability Ratios
    gross_profit_margin: Optional[float] = None
    operating_profit_margin: Optional[float] = None
    net_profit_margin: Optional[float] = None
    roe: Optional[float] = None  # Return on Equity
    roa: Optional[float] = None  # Return on Assets
    roic: Optional[float] = None  # Return on Invested Capital
    
    # Liquidity Ratios
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    cash_ratio: Optional[float] = None
    
    # Leverage Ratios
    debt_to_equity: Optional[float] = None
    debt_to_assets: Optional[float] = None
    interest_coverage: Optional[float] = None
    equity_ratio: Optional[float] = None
    
    # Efficiency Ratios
    asset_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    receivables_turnover: Optional[float] = None
    payables_turnover: Optional[float] = None
    
    # Valuation Ratios
    pe_ratio: Optional[float] = None  # Price-to-Earnings
    pb_ratio: Optional[float] = None  # Price-to-Book
    ps_ratio: Optional[float] = None  # Price-to-Sales
    peg_ratio: Optional[float] = None  # PEG Ratio
    ev_ebitda: Optional[float] = None  # EV/EBITDA
    ev_sales: Optional[float] = None  # EV/Sales
    
    # Growth Ratios
    revenue_growth: Optional[float] = None
    profit_growth: Optional[float] = None
    eps_growth: Optional[float] = None
    book_value_growth: Optional[float] = None
    
    # Per Share Metrics
    eps: Optional[float] = None  # Earnings Per Share
    book_value_per_share: Optional[float] = None
    cash_per_share: Optional[float] = None
    dividend_yield: Optional[float] = None
    
    # Risk Metrics
    beta: Optional[float] = None
    volatility: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    
    # Technical Indicators
    rsi: Optional[float] = None
    macd: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_lower: Optional[float] = None
    moving_average_20: Optional[float] = None
    moving_average_50: Optional[float] = None
    moving_average_200: Optional[float] = None


class FinancialCalculator:
    """Financial calculator for various financial metrics"""
    
    @staticmethod
    def calculate_profitability_ratios(
        revenue: float,
        gross_profit: float,
        operating_income: float,
        net_income: float,
        total_assets: float,
        total_equity: float,
        invested_capital: Optional[float] = None
    ) -> Dict[str, float]:
        """Calculate profitability ratios"""
        ratios = {}
        
        if revenue > 0:
            ratios["gross_profit_margin"] = (gross_profit / revenue) * 100
            ratios["operating_profit_margin"] = (operating_income / revenue) * 100
            ratios["net_profit_margin"] = (net_income / revenue) * 100
        
        if total_equity > 0:
            ratios["roe"] = (net_income / total_equity) * 100
        
        if total_assets > 0:
            ratios["roa"] = (net_income / total_assets) * 100
        
        if invested_capital and invested_capital > 0:
            ratios["roic"] = (operating_income / invested_capital) * 100
        
        return ratios
    
    @staticmethod
    def calculate_liquidity_ratios(
        current_assets: float,
        current_liabilities: float,
        inventory: float = 0,
        cash_and_equivalents: float = 0
    ) -> Dict[str, float]:
        """Calculate liquidity ratios"""
        ratios = {}
        
        if current_liabilities > 0:
            ratios["current_ratio"] = current_assets / current_liabilities
            ratios["quick_ratio"] = (current_assets - inventory) / current_liabilities
            ratios["cash_ratio"] = cash_and_equivalents / current_liabilities
        
        return ratios
    
    @staticmethod
    def calculate_leverage_ratios(
        total_debt: float,
        total_equity: float,
        total_assets: float,
        ebit: float = 0,
        interest_expense: float = 0
    ) -> Dict[str, float]:
        """Calculate leverage ratios"""
        ratios = {}
        
        if total_equity > 0:
            ratios["debt_to_equity"] = total_debt / total_equity
            ratios["equity_ratio"] = total_equity / total_assets
        
        if total_assets > 0:
            ratios["debt_to_assets"] = total_debt / total_assets
        
        if interest_expense > 0:
            ratios["interest_coverage"] = ebit / interest_expense
        
        return ratios
    
    @staticmethod
    def calculate_efficiency_ratios(
        revenue: float,
        total_assets: float,
        inventory: float = 0,
        accounts_receivable: float = 0,
        accounts_payable: float = 0,
        cogs: float = 0
    ) -> Dict[str, float]:
        """Calculate efficiency ratios"""
        ratios = {}
        
        if total_assets > 0:
            ratios["asset_turnover"] = revenue / total_assets
        
        if inventory > 0 and cogs > 0:
            ratios["inventory_turnover"] = cogs / inventory
        
        if accounts_receivable > 0:
            ratios["receivables_turnover"] = revenue / accounts_receivable
        
        if accounts_payable > 0 and cogs > 0:
            ratios["payables_turnover"] = cogs / accounts_payable
        
        return ratios
    
    @staticmethod
    def calculate_valuation_ratios(
        market_price: float,
        eps: float,
        book_value_per_share: float,
        revenue_per_share: float,
        market_cap: float,
        ebitda: float = 0,
        total_sales: float = 0,
        ev: float = 0,
        growth_rate: float = 0
    ) -> Dict[str, float]:
        """Calculate valuation ratios"""
        ratios = {}
        
        if eps > 0:
            ratios["pe_ratio"] = market_price / eps
            if growth_rate > 0:
                ratios["peg_ratio"] = (market_price / eps) / growth_rate
        
        if book_value_per_share > 0:
            ratios["pb_ratio"] = market_price / book_value_per_share
        
        if revenue_per_share > 0:
            ratios["ps_ratio"] = market_price / revenue_per_share
        
        if ebitda > 0:
            if ev > 0:
                ratios["ev_ebitda"] = ev / ebitda
            else:
                ratios["ev_ebitda"] = market_cap / ebitda
        
        if total_sales > 0:
            if ev > 0:
                ratios["ev_sales"] = ev / total_sales
            else:
                ratios["ev_sales"] = market_cap / total_sales
        
        return ratios
    
    @staticmethod
    def calculate_growth_ratios(
        current_revenue: float,
        previous_revenue: float,
        current_profit: float,
        previous_profit: float,
        current_eps: float,
        previous_eps: float,
        current_book_value: float,
        previous_book_value: float
    ) -> Dict[str, float]:
        """Calculate growth ratios"""
        ratios = {}
        
        if previous_revenue > 0:
            ratios["revenue_growth"] = ((current_revenue - previous_revenue) / previous_revenue) * 100
        
        if previous_profit > 0:
            ratios["profit_growth"] = ((current_profit - previous_profit) / previous_profit) * 100
        
        if previous_eps > 0:
            ratios["eps_growth"] = ((current_eps - previous_eps) / previous_eps) * 100
        
        if previous_book_value > 0:
            ratios["book_value_growth"] = ((current_book_value - previous_book_value) / previous_book_value) * 100
        
        return ratios
    
    @staticmethod
    def calculate_per_share_metrics(
        net_income: float,
        total_shares: float,
        total_equity: float,
        cash_and_equivalents: float,
        dividends_paid: float = 0,
        market_price: float = 0
    ) -> Dict[str, float]:
        """Calculate per share metrics"""
        metrics = {}
        
        if total_shares > 0:
            metrics["eps"] = net_income / total_shares
            metrics["book_value_per_share"] = total_equity / total_shares
            metrics["cash_per_share"] = cash_and_equivalents / total_shares
            
            if market_price > 0 and dividends_paid > 0:
                metrics["dividend_yield"] = (dividends_paid / total_shares) / market_price * 100
        
        return metrics
    
    @staticmethod
    def calculate_technical_indicators(
        prices: List[float],
        volumes: Optional[List[float]] = None,
        period: int = 14
    ) -> Dict[str, float]:
        """Calculate technical indicators"""
        indicators = {}
        
        if len(prices) < period:
            return indicators
        
        # RSI calculation
        if len(prices) >= period + 1:
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
            
            if len(gains) >= period:
                avg_gain = sum(gains[-period:]) / period
                avg_loss = sum(losses[-period:]) / period
                
                if avg_loss > 0:
                    rs = avg_gain / avg_loss
                    indicators["rsi"] = 100 - (100 / (1 + rs))
        
        # Moving averages
        if len(prices) >= 20:
            indicators["moving_average_20"] = sum(prices[-20:]) / 20
        
        if len(prices) >= 50:
            indicators["moving_average_50"] = sum(prices[-50:]) / 50
        
        if len(prices) >= 200:
            indicators["moving_average_200"] = sum(prices[-200:]) / 200
        
        # Bollinger Bands
        if len(prices) >= 20:
            ma20 = sum(prices[-20:]) / 20
            variance = sum((p - ma20) ** 2 for p in prices[-20:]) / 20
            std_dev = math.sqrt(variance)
            
            indicators["bollinger_upper"] = ma20 + (2 * std_dev)
            indicators["bollinger_lower"] = ma20 - (2 * std_dev)
        
        return indicators


@function_tool
async def calculate_financial_ratios(
    # Basic financial data
    revenue: float,
    gross_profit: float,
    operating_income: float,
    net_income: float,
    total_assets: float,
    total_equity: float,
    total_debt: float,
    current_assets: float,
    current_liabilities: float,
    
    # Optional data for more detailed calculations
    inventory: float = 0,
    cash_and_equivalents: float = 0,
    accounts_receivable: float = 0,
    accounts_payable: float = 0,
    cogs: float = 0,
    ebit: float = 0,
    interest_expense: float = 0,
    invested_capital: Optional[float] = None,
    
    # Market data
    market_price: Optional[float] = None,
    market_cap: Optional[float] = None,
    total_shares: Optional[float] = None,
    dividends_paid: float = 0,
    
    # Historical data for growth calculations
    previous_revenue: Optional[float] = None,
    previous_profit: Optional[float] = None,
    previous_eps: Optional[float] = None,
    previous_book_value: Optional[float] = None,
    
    # Price data for technical analysis
    price_history: Optional[List[float]] = None,
    volume_history: Optional[List[float]] = None,
    
    # Risk data
    beta: Optional[float] = None,
    risk_free_rate: float = 0.03,
    market_return: float = 0.10
) -> str:
    """
    Calculate comprehensive financial ratios and metrics for financial analysis.
    
    Args:
        revenue: Total revenue
        gross_profit: Gross profit
        operating_income: Operating income (EBIT)
        net_income: Net income
        total_assets: Total assets
        total_equity: Total equity
        total_debt: Total debt
        current_assets: Current assets
        current_liabilities: Current liabilities
        inventory: Inventory value
        cash_and_equivalents: Cash and cash equivalents
        accounts_receivable: Accounts receivable
        accounts_payable: Accounts payable
        cogs: Cost of goods sold
        ebit: Earnings before interest and taxes
        interest_expense: Interest expense
        invested_capital: Invested capital for ROIC calculation
        market_price: Current market price per share
        market_cap: Market capitalization
        total_shares: Total number of shares outstanding
        dividends_paid: Total dividends paid
        previous_revenue: Previous period revenue for growth calculation
        previous_profit: Previous period profit for growth calculation
        previous_eps: Previous period EPS for growth calculation
        previous_book_value: Previous period book value for growth calculation
        price_history: Historical price data for technical analysis
        volume_history: Historical volume data
        beta: Beta coefficient for risk calculation
        risk_free_rate: Risk-free rate for Sharpe ratio
        market_return: Expected market return for Sharpe ratio
    """
    try:
        calculator = FinancialCalculator()
        metrics = FinancialMetrics()
        
        # Calculate profitability ratios
        profit_ratios = calculator.calculate_profitability_ratios(
            revenue, gross_profit, operating_income, net_income,
            total_assets, total_equity, invested_capital
        )
        metrics.gross_profit_margin = profit_ratios.get("gross_profit_margin")
        metrics.operating_profit_margin = profit_ratios.get("operating_profit_margin")
        metrics.net_profit_margin = profit_ratios.get("net_profit_margin")
        metrics.roe = profit_ratios.get("roe")
        metrics.roa = profit_ratios.get("roa")
        metrics.roic = profit_ratios.get("roic")
        
        # Calculate liquidity ratios
        liquidity_ratios = calculator.calculate_liquidity_ratios(
            current_assets, current_liabilities, inventory, cash_and_equivalents
        )
        metrics.current_ratio = liquidity_ratios.get("current_ratio")
        metrics.quick_ratio = liquidity_ratios.get("quick_ratio")
        metrics.cash_ratio = liquidity_ratios.get("cash_ratio")
        
        # Calculate leverage ratios
        leverage_ratios = calculator.calculate_leverage_ratios(
            total_debt, total_equity, total_assets, ebit, interest_expense
        )
        metrics.debt_to_equity = leverage_ratios.get("debt_to_equity")
        metrics.debt_to_assets = leverage_ratios.get("debt_to_assets")
        metrics.interest_coverage = leverage_ratios.get("interest_coverage")
        metrics.equity_ratio = leverage_ratios.get("equity_ratio")
        
        # Calculate efficiency ratios
        efficiency_ratios = calculator.calculate_efficiency_ratios(
            revenue, total_assets, inventory, accounts_receivable,
            accounts_payable, cogs
        )
        metrics.asset_turnover = efficiency_ratios.get("asset_turnover")
        metrics.inventory_turnover = efficiency_ratios.get("inventory_turnover")
        metrics.receivables_turnover = efficiency_ratios.get("receivables_turnover")
        metrics.payables_turnover = efficiency_ratios.get("payables_turnover")
        
        # Calculate valuation ratios
        if market_price and total_shares:
            book_value_per_share = total_equity / total_shares
            revenue_per_share = revenue / total_shares
            eps = net_income / total_shares
            
            valuation_ratios = calculator.calculate_valuation_ratios(
                market_price, eps, book_value_per_share, revenue_per_share,
                market_cap or (market_price * total_shares), ebit, revenue,
                market_cap or (market_price * total_shares)
            )
            metrics.pe_ratio = valuation_ratios.get("pe_ratio")
            metrics.pb_ratio = valuation_ratios.get("pb_ratio")
            metrics.ps_ratio = valuation_ratios.get("ps_ratio")
            metrics.peg_ratio = valuation_ratios.get("peg_ratio")
            metrics.ev_ebitda = valuation_ratios.get("ev_ebitda")
            metrics.ev_sales = valuation_ratios.get("ev_sales")
            
            # Per share metrics
            per_share_metrics = calculator.calculate_per_share_metrics(
                net_income, total_shares, total_equity, cash_and_equivalents,
                dividends_paid, market_price
            )
            metrics.eps = per_share_metrics.get("eps")
            metrics.book_value_per_share = per_share_metrics.get("book_value_per_share")
            metrics.cash_per_share = per_share_metrics.get("cash_per_share")
            metrics.dividend_yield = per_share_metrics.get("dividend_yield")
        
        # Calculate growth ratios
        if all([previous_revenue, previous_profit, previous_eps, previous_book_value]):
            growth_ratios = calculator.calculate_growth_ratios(
                revenue, previous_revenue, net_income, previous_profit,
                metrics.eps or 0, previous_eps, metrics.book_value_per_share or 0, previous_book_value
            )
            metrics.revenue_growth = growth_ratios.get("revenue_growth")
            metrics.profit_growth = growth_ratios.get("profit_growth")
            metrics.eps_growth = growth_ratios.get("eps_growth")
            metrics.book_value_growth = growth_ratios.get("book_value_growth")
        
        # Calculate technical indicators
        if price_history:
            technical_indicators = calculator.calculate_technical_indicators(price_history, volume_history)
            metrics.rsi = technical_indicators.get("rsi")
            metrics.moving_average_20 = technical_indicators.get("moving_average_20")
            metrics.moving_average_50 = technical_indicators.get("moving_average_50")
            metrics.moving_average_200 = technical_indicators.get("moving_average_200")
            metrics.bollinger_upper = technical_indicators.get("bollinger_upper")
            metrics.bollinger_lower = technical_indicators.get("bollinger_lower")
        
        # Risk metrics
        if beta is not None:
            metrics.beta = beta
            if market_price and total_shares:
                expected_return = risk_free_rate + beta * (market_return - risk_free_rate)
                # Simplified Sharpe ratio calculation
                metrics.sharpe_ratio = expected_return / (beta * 0.2)  # Simplified volatility
        
        # Convert to dict and filter out None values
        result_dict = metrics.model_dump(exclude_none=True)
        
        return json.dumps({
            "success": True,
            "metrics": result_dict,
            "timestamp": datetime.now().isoformat(),
            "calculation_summary": {
                "total_metrics_calculated": len(result_dict),
                "profitability_ratios": len([k for k in result_dict.keys() if k in [
                    "gross_profit_margin", "operating_profit_margin", "net_profit_margin", "roe", "roa", "roic"
                ]]),
                "liquidity_ratios": len([k for k in result_dict.keys() if k in [
                    "current_ratio", "quick_ratio", "cash_ratio"
                ]]),
                "leverage_ratios": len([k for k in result_dict.keys() if k in [
                    "debt_to_equity", "debt_to_assets", "interest_coverage", "equity_ratio"
                ]]),
                "efficiency_ratios": len([k for k in result_dict.keys() if k in [
                    "asset_turnover", "inventory_turnover", "receivables_turnover", "payables_turnover"
                ]]),
                "valuation_ratios": len([k for k in result_dict.keys() if k in [
                    "pe_ratio", "pb_ratio", "ps_ratio", "peg_ratio", "ev_ebitda", "ev_sales"
                ]])
            }
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"Error in calculate_financial_ratios: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg
        }, ensure_ascii=False, indent=2)


@function_tool
async def calculate_valuation_metrics(
    current_price: float,
    eps: float,
    growth_rate: float,
    risk_free_rate: float = 0.03,
    market_risk_premium: float = 0.07,
    beta: float = 1.0,
    dividend_yield: float = 0.0,
    payout_ratio: float = 0.0
) -> str:
    """
    Calculate comprehensive valuation metrics including DCF, P/E analysis, and target price.
    
    Args:
        current_price: Current stock price
        eps: Earnings per share
        growth_rate: Expected growth rate (decimal, e.g., 0.10 for 10%)
        risk_free_rate: Risk-free rate (default 3%)
        market_risk_premium: Market risk premium (default 7%)
        beta: Beta coefficient (default 1.0)
        dividend_yield: Current dividend yield (default 0%)
        payout_ratio: Dividend payout ratio (default 0%)
    """
    try:
        # Calculate required return using CAPM
        required_return = risk_free_rate + beta * market_risk_premium
        
        # Calculate P/E ratios
        pe_ratio = current_price / eps if eps > 0 else None
        peg_ratio = pe_ratio / (growth_rate * 100) if pe_ratio and growth_rate > 0 else None
        
        # DCF Valuation (simplified Gordon Growth Model)
        if growth_rate < required_return and dividend_yield > 0:
            dcf_value = (eps * payout_ratio * (1 + growth_rate)) / (required_return - growth_rate)
        else:
            dcf_value = None
        
        # Target price based on P/E analysis
        if pe_ratio:
            # Assume fair P/E is 15-20 for stable companies
            fair_pe = 17.5  # Mid-point
            target_price_pe = eps * fair_pe
            
            # Adjust for growth
            growth_adjusted_pe = fair_pe * (1 + growth_rate)
            target_price_growth = eps * growth_adjusted_pe
        else:
            target_price_pe = None
            target_price_growth = None
        
        # Risk assessment
        risk_level = "Low"
        if beta > 1.5:
            risk_level = "High"
        elif beta > 1.0:
            risk_level = "Medium"
        
        # Investment recommendation
        recommendation = "Hold"
        if dcf_value and current_price < dcf_value * 0.8:
            recommendation = "Strong Buy"
        elif dcf_value and current_price < dcf_value * 0.9:
            recommendation = "Buy"
        elif dcf_value and current_price > dcf_value * 1.2:
            recommendation = "Sell"
        elif dcf_value and current_price > dcf_value * 1.1:
            recommendation = "Hold"
        
        result = {
            "success": True,
            "valuation_metrics": {
                "current_price": current_price,
                "eps": eps,
                "pe_ratio": pe_ratio,
                "peg_ratio": peg_ratio,
                "required_return": required_return,
                "dcf_value": dcf_value,
                "target_price_pe": target_price_pe,
                "target_price_growth": target_price_growth,
                "upside_potential": ((dcf_value - current_price) / current_price * 100) if dcf_value else None,
                "risk_level": risk_level,
                "recommendation": recommendation
            },
            "assumptions": {
                "growth_rate": growth_rate,
                "risk_free_rate": risk_free_rate,
                "market_risk_premium": market_risk_premium,
                "beta": beta,
                "dividend_yield": dividend_yield,
                "payout_ratio": payout_ratio
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"Error in calculate_valuation_metrics: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg
        }, ensure_ascii=False, indent=2)
