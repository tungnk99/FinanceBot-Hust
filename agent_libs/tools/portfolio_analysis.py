"""
Portfolio Analysis Tool - Công cụ phân tích danh mục đầu tư
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


class AssetType(str, Enum):
    """Asset type classification"""
    STOCK = "Stock"
    BOND = "Bond"
    CRYPTO = "Cryptocurrency"
    COMMODITY = "Commodity"
    CASH = "Cash"
    ETF = "ETF"
    MUTUAL_FUND = "Mutual Fund"
    REIT = "REIT"
    OTHER = "Other"


class RiskLevel(str, Enum):
    """Risk level classification"""
    VERY_LOW = "Very Low"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"


class Asset(BaseModel):
    """Portfolio asset structure"""
    symbol: str
    name: str
    asset_type: AssetType
    quantity: float
    current_price: float
    market_value: float
    weight: float
    expected_return: Optional[float] = None
    volatility: Optional[float] = None
    beta: Optional[float] = None


class PortfolioMetrics(BaseModel):
    """Portfolio analysis metrics"""
    
    # Basic metrics
    total_value: float
    total_investment: float
    total_return: float
    total_return_percent: float
    
    # Risk metrics
    portfolio_volatility: float
    portfolio_beta: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    var_95: float
    cvar_95: float
    
    # Diversification metrics
    diversification_ratio: float
    concentration_risk: float
    sector_concentration: Dict[str, float]
    asset_type_concentration: Dict[str, float]
    
    # Performance metrics
    alpha: float
    information_ratio: float
    treynor_ratio: float
    calmar_ratio: float
    
    # Risk level
    risk_level: RiskLevel
    risk_score: float


class PortfolioAnalyzer:
    """Portfolio analysis calculator"""
    
    @staticmethod
    def calculate_returns(prices: List[float]) -> List[float]:
        """Calculate returns from price series"""
        if len(prices) < 2:
            return []
        
        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        
        return returns
    
    @staticmethod
    def calculate_portfolio_volatility(weights: List[float], cov_matrix: List[List[float]]) -> float:
        """Calculate portfolio volatility using covariance matrix"""
        if not weights or not cov_matrix:
            return 0.0
        
        n = len(weights)
        if n != len(cov_matrix) or n != len(cov_matrix[0]):
            return 0.0
        
        # Calculate portfolio variance: w^T * Cov * w
        variance = 0.0
        for i in range(n):
            for j in range(n):
                variance += weights[i] * weights[j] * cov_matrix[i][j]
        
        return math.sqrt(variance)
    
    @staticmethod
    def calculate_correlation_matrix(returns_data: List[List[float]]) -> List[List[float]]:
        """Calculate correlation matrix from returns data"""
        n_assets = len(returns_data)
        if n_assets == 0:
            return []
        
        # Ensure all return series have the same length
        min_length = min(len(returns) for returns in returns_data)
        if min_length < 2:
            return [[1.0] * n_assets for _ in range(n_assets)]
        
        # Truncate all series to minimum length
        aligned_returns = [returns[-min_length:] for returns in returns_data]
        
        # Calculate correlation matrix
        corr_matrix = []
        for i in range(n_assets):
            row = []
            for j in range(n_assets):
                if i == j:
                    row.append(1.0)
                else:
                    corr = PortfolioAnalyzer.calculate_correlation(
                        aligned_returns[i], aligned_returns[j]
                    )
                    row.append(corr)
            corr_matrix.append(row)
        
        return corr_matrix
    
    @staticmethod
    def calculate_correlation(returns1: List[float], returns2: List[float]) -> float:
        """Calculate correlation between two return series"""
        if len(returns1) != len(returns2) or len(returns1) < 2:
            return 0.0
        
        n = len(returns1)
        mean1 = sum(returns1) / n
        mean2 = sum(returns2) / n
        
        numerator = sum((r1 - mean1) * (r2 - mean2) for r1, r2 in zip(returns1, returns2))
        
        var1 = sum((r1 - mean1) ** 2 for r1 in returns1)
        var2 = sum((r2 - mean2) ** 2 for r2 in returns2)
        
        denominator = math.sqrt(var1 * var2)
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    @staticmethod
    def calculate_covariance_matrix(returns_data: List[List[float]]) -> List[List[float]]:
        """Calculate covariance matrix from returns data"""
        n_assets = len(returns_data)
        if n_assets == 0:
            return []
        
        # Ensure all return series have the same length
        min_length = min(len(returns) for returns in returns_data)
        if min_length < 2:
            return [[0.0] * n_assets for _ in range(n_assets)]
        
        # Truncate all series to minimum length
        aligned_returns = [returns[-min_length:] for returns in returns_data]
        
        # Calculate covariance matrix
        cov_matrix = []
        for i in range(n_assets):
            row = []
            for j in range(n_assets):
                if i == j:
                    # Variance
                    returns = aligned_returns[i]
                    mean = sum(returns) / len(returns)
                    variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
                    row.append(variance)
                else:
                    # Covariance
                    cov = PortfolioAnalyzer.calculate_covariance(
                        aligned_returns[i], aligned_returns[j]
                    )
                    row.append(cov)
            cov_matrix.append(row)
        
        return cov_matrix
    
    @staticmethod
    def calculate_covariance(returns1: List[float], returns2: List[float]) -> float:
        """Calculate covariance between two return series"""
        if len(returns1) != len(returns2) or len(returns1) < 2:
            return 0.0
        
        n = len(returns1)
        mean1 = sum(returns1) / n
        mean2 = sum(returns2) / n
        
        covariance = sum((r1 - mean1) * (r2 - mean2) for r1, r2 in zip(returns1, returns2)) / (n - 1)
        
        return covariance
    
    @staticmethod
    def calculate_max_drawdown(portfolio_values: List[float]) -> float:
        """Calculate maximum drawdown"""
        if not portfolio_values:
            return 0.0
        
        peak = portfolio_values[0]
        max_dd = 0.0
        
        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    @staticmethod
    def calculate_var(returns: List[float], confidence_level: float = 0.05) -> float:
        """Calculate Value at Risk"""
        if not returns:
            return 0.0
        
        sorted_returns = sorted(returns)
        index = int(len(sorted_returns) * confidence_level)
        return sorted_returns[index]
    
    @staticmethod
    def calculate_cvar(returns: List[float], confidence_level: float = 0.05) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        if not returns:
            return 0.0
        
        var = PortfolioAnalyzer.calculate_var(returns, confidence_level)
        var_returns = [r for r in returns if r <= var]
        
        if not var_returns:
            return 0.0
        
        return sum(var_returns) / len(var_returns)
    
    @staticmethod
    def calculate_diversification_ratio(weights: List[float], volatilities: List[float], 
                                      cov_matrix: List[List[float]]) -> float:
        """Calculate diversification ratio"""
        if not weights or not volatilities:
            return 0.0
        
        # Weighted average volatility
        weighted_avg_vol = sum(w * vol for w, vol in zip(weights, volatilities))
        
        # Portfolio volatility
        portfolio_vol = PortfolioAnalyzer.calculate_portfolio_volatility(weights, cov_matrix)
        
        if portfolio_vol == 0:
            return 0.0
        
        return weighted_avg_vol / portfolio_vol
    
    @staticmethod
    def calculate_concentration_risk(weights: List[float]) -> float:
        """Calculate concentration risk using Herfindahl-Hirschman Index"""
        if not weights:
            return 0.0
        
        # Normalize weights to sum to 1
        total_weight = sum(weights)
        if total_weight == 0:
            return 0.0
        
        normalized_weights = [w / total_weight for w in weights]
        
        # Calculate HHI
        hhi = sum(w ** 2 for w in normalized_weights)
        
        # Convert to concentration risk (0 = perfectly diversified, 1 = completely concentrated)
        n = len(weights)
        max_hhi = 1.0  # When all weight is in one asset
        min_hhi = 1.0 / n  # When perfectly diversified
        
        if max_hhi == min_hhi:
            return 0.0
        
        concentration_risk = (hhi - min_hhi) / (max_hhi - min_hhi)
        return concentration_risk


@function_tool
async def analyze_portfolio(
    assets: List[Dict[str, Any]],
    historical_returns: Optional[Dict[str, List[float]]] = None,
    risk_free_rate: float = 0.03,
    market_return: float = 0.10,
    market_volatility: float = 0.15
) -> str:
    """
    Perform comprehensive portfolio analysis.
    
    Args:
        assets: List of assets with 'symbol', 'name', 'asset_type', 'quantity', 'current_price', 'weight'
        historical_returns: Optional dict of symbol -> returns list for risk calculations
        risk_free_rate: Risk-free rate (default 3%)
        market_return: Expected market return (default 10%)
        market_volatility: Market volatility (default 15%)
    """
    try:
        if not assets:
            return json.dumps({
                "success": False,
                "error": "No assets provided for portfolio analysis"
            }, ensure_ascii=False, indent=2)
        
        # Convert assets to Asset objects
        portfolio_assets = []
        total_value = 0.0
        
        for asset_data in assets:
            market_value = asset_data.get("quantity", 0) * asset_data.get("current_price", 0)
            total_value += market_value
            
            asset = Asset(
                symbol=asset_data.get("symbol", ""),
                name=asset_data.get("name", ""),
                asset_type=AssetType(asset_data.get("asset_type", "Other")),
                quantity=asset_data.get("quantity", 0),
                current_price=asset_data.get("current_price", 0),
                market_value=market_value,
                weight=asset_data.get("weight", 0),
                expected_return=asset_data.get("expected_return"),
                volatility=asset_data.get("volatility"),
                beta=asset_data.get("beta")
            )
            portfolio_assets.append(asset)
        
        # Normalize weights
        for asset in portfolio_assets:
            asset.weight = asset.market_value / total_value if total_value > 0 else 0
        
        # Calculate basic metrics
        total_investment = sum(asset.market_value for asset in portfolio_assets)
        total_return = total_value - total_investment
        total_return_percent = (total_return / total_investment * 100) if total_investment > 0 else 0
        
        # Calculate portfolio expected return
        portfolio_expected_return = sum(
            asset.weight * (asset.expected_return or 0) for asset in portfolio_assets
        )
        
        # Calculate portfolio volatility
        portfolio_volatility = 0.0
        portfolio_beta = 0.0
        
        if historical_returns:
            # Get returns for assets that have historical data
            returns_data = []
            weights_for_vol = []
            
            for asset in portfolio_assets:
                if asset.symbol in historical_returns:
                    returns_data.append(historical_returns[asset.symbol])
                    weights_for_vol.append(asset.weight)
            
            if returns_data and len(returns_data) > 1:
                # Calculate covariance matrix
                cov_matrix = PortfolioAnalyzer.calculate_covariance_matrix(returns_data)
                
                # Calculate portfolio volatility
                portfolio_volatility = PortfolioAnalyzer.calculate_portfolio_volatility(
                    weights_for_vol, cov_matrix
                )
        
        # Calculate portfolio beta
        portfolio_beta = sum(asset.weight * (asset.beta or 1.0) for asset in portfolio_assets)
        
        # Calculate risk metrics
        sharpe_ratio = 0.0
        if portfolio_volatility > 0:
            sharpe_ratio = (portfolio_expected_return - risk_free_rate) / portfolio_volatility
        
        # Calculate Sortino ratio (simplified)
        sortino_ratio = sharpe_ratio  # Simplified - would need downside deviation
        
        # Calculate max drawdown (simplified)
        max_drawdown = 0.0
        if historical_returns:
            # Calculate portfolio value series
            portfolio_values = []
            for i in range(len(list(historical_returns.values())[0])):
                value = 0.0
                for asset in portfolio_assets:
                    if asset.symbol in historical_returns:
                        returns = historical_returns[asset.symbol]
                        if i < len(returns):
                            value += asset.market_value * (1 + returns[i])
                portfolio_values.append(value)
            
            max_drawdown = PortfolioAnalyzer.calculate_max_drawdown(portfolio_values)
        
        # Calculate VaR and CVaR
        var_95 = 0.0
        cvar_95 = 0.0
        if historical_returns:
            # Calculate portfolio returns
            portfolio_returns = []
            for i in range(len(list(historical_returns.values())[0])):
                portfolio_return = 0.0
                for asset in portfolio_assets:
                    if asset.symbol in historical_returns:
                        returns = historical_returns[asset.symbol]
                        if i < len(returns):
                            portfolio_return += asset.weight * returns[i]
                portfolio_returns.append(portfolio_return)
            
            var_95 = PortfolioAnalyzer.calculate_var(portfolio_returns, 0.05)
            cvar_95 = PortfolioAnalyzer.calculate_cvar(portfolio_returns, 0.05)
        
        # Calculate diversification metrics
        weights = [asset.weight for asset in portfolio_assets]
        volatilities = [asset.volatility or 0.2 for asset in portfolio_assets]  # Default 20% volatility
        
        diversification_ratio = 1.0
        concentration_risk = 0.0
        
        if len(weights) > 1:
            if historical_returns:
                returns_data = [historical_returns.get(asset.symbol, []) for asset in portfolio_assets]
                returns_data = [r for r in returns_data if r]  # Filter out empty lists
                if returns_data:
                    cov_matrix = PortfolioAnalyzer.calculate_covariance_matrix(returns_data)
                    diversification_ratio = PortfolioAnalyzer.calculate_diversification_ratio(
                        weights, volatilities, cov_matrix
                    )
            
            concentration_risk = PortfolioAnalyzer.calculate_concentration_risk(weights)
        
        # Calculate sector and asset type concentration
        sector_concentration = {}
        asset_type_concentration = {}
        
        for asset in portfolio_assets:
            # Asset type concentration
            asset_type = asset.asset_type.value
            asset_type_concentration[asset_type] = asset_type_concentration.get(asset_type, 0) + asset.weight
        
        # Calculate performance metrics
        alpha = portfolio_expected_return - (risk_free_rate + portfolio_beta * (market_return - risk_free_rate))
        information_ratio = alpha / portfolio_volatility if portfolio_volatility > 0 else 0
        treynor_ratio = (portfolio_expected_return - risk_free_rate) / portfolio_beta if portfolio_beta > 0 else 0
        calmar_ratio = portfolio_expected_return / max_drawdown if max_drawdown > 0 else 0
        
        # Determine risk level
        risk_score = portfolio_volatility
        if risk_score < 0.1:
            risk_level = RiskLevel.VERY_LOW
        elif risk_score < 0.15:
            risk_level = RiskLevel.LOW
        elif risk_score < 0.25:
            risk_level = RiskLevel.MEDIUM
        elif risk_score < 0.35:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.VERY_HIGH
        
        # Create metrics object
        metrics = PortfolioMetrics(
            total_value=total_value,
            total_investment=total_investment,
            total_return=total_return,
            total_return_percent=total_return_percent,
            portfolio_volatility=portfolio_volatility,
            portfolio_beta=portfolio_beta,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            var_95=var_95,
            cvar_95=cvar_95,
            diversification_ratio=diversification_ratio,
            concentration_risk=concentration_risk,
            sector_concentration=sector_concentration,
            asset_type_concentration=asset_type_concentration,
            alpha=alpha,
            information_ratio=information_ratio,
            treynor_ratio=treynor_ratio,
            calmar_ratio=calmar_ratio,
            risk_level=risk_level,
            risk_score=risk_score
        )
        
        # Prepare asset details
        asset_details = []
        for asset in portfolio_assets:
            asset_details.append({
                "symbol": asset.symbol,
                "name": asset.name,
                "asset_type": asset.asset_type.value,
                "quantity": asset.quantity,
                "current_price": asset.current_price,
                "market_value": asset.market_value,
                "weight": asset.weight,
                "expected_return": asset.expected_return,
                "volatility": asset.volatility,
                "beta": asset.beta
            })
        
        return json.dumps({
            "success": True,
            "portfolio_analysis": metrics.model_dump(),
            "assets": asset_details,
            "summary": {
                "total_value": total_value,
                "total_assets": len(portfolio_assets),
                "risk_level": risk_level.value,
                "expected_return": portfolio_expected_return,
                "volatility": portfolio_volatility,
                "sharpe_ratio": sharpe_ratio,
                "diversification_ratio": diversification_ratio
            },
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"Error in analyze_portfolio: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg
        }, ensure_ascii=False, indent=2)


@function_tool
async def optimize_portfolio(
    assets: List[Dict[str, Any]],
    historical_returns: Dict[str, List[float]],
    target_return: Optional[float] = None,
    risk_tolerance: float = 0.5,
    risk_free_rate: float = 0.03
) -> str:
    """
    Optimize portfolio allocation using mean-variance optimization.
    
    Args:
        assets: List of assets with 'symbol', 'expected_return', 'volatility'
        historical_returns: Dict of symbol -> returns list
        target_return: Target portfolio return (optional)
        risk_tolerance: Risk tolerance (0 = risk-averse, 1 = risk-seeking)
        risk_free_rate: Risk-free rate
    """
    try:
        if not assets or not historical_returns:
            return json.dumps({
                "success": False,
                "error": "Assets and historical returns required for optimization"
            }, ensure_ascii=False, indent=2)
        
        # Filter assets that have historical data
        available_assets = []
        for asset in assets:
            if asset["symbol"] in historical_returns:
                available_assets.append(asset)
        
        if len(available_assets) < 2:
            return json.dumps({
                "success": False,
                "error": "At least 2 assets with historical data required for optimization"
            }, ensure_ascii=False, indent=2)
        
        # Calculate expected returns and volatilities
        expected_returns = []
        volatilities = []
        returns_data = []
        
        for asset in available_assets:
            symbol = asset["symbol"]
            returns = historical_returns[symbol]
            
            # Calculate expected return from historical data
            expected_return = sum(returns) / len(returns) if returns else 0
            
            # Calculate volatility
            if len(returns) > 1:
                mean_return = expected_return
                variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
                volatility = math.sqrt(variance)
            else:
                volatility = 0.2  # Default 20%
            
            expected_returns.append(expected_return)
            volatilities.append(volatility)
            returns_data.append(returns)
        
        # Calculate covariance matrix
        cov_matrix = PortfolioAnalyzer.calculate_covariance_matrix(returns_data)
        
        # Simple optimization: maximize Sharpe ratio
        # For simplicity, we'll use equal weights as a starting point
        n_assets = len(available_assets)
        equal_weights = [1.0 / n_assets] * n_assets
        
        # Calculate portfolio metrics with equal weights
        portfolio_return = sum(w * r for w, r in zip(equal_weights, expected_returns))
        portfolio_volatility = PortfolioAnalyzer.calculate_portfolio_volatility(equal_weights, cov_matrix)
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
        
        # Simple optimization: adjust weights based on risk tolerance
        # Higher risk tolerance = more weight on high-return assets
        optimized_weights = []
        
        if risk_tolerance > 0.5:
            # Risk-seeking: weight more towards high-return assets
            total_expected_return = sum(expected_returns)
            for i, expected_return in enumerate(expected_returns):
                weight = (expected_return / total_expected_return) * (1 + risk_tolerance)
                optimized_weights.append(weight)
        else:
            # Risk-averse: weight more towards low-volatility assets
            total_volatility = sum(volatilities)
            for i, volatility in enumerate(volatilities):
                weight = (1 / volatility) / sum(1 / v for v in volatilities)
                optimized_weights.append(weight)
        
        # Normalize weights
        total_weight = sum(optimized_weights)
        optimized_weights = [w / total_weight for w in optimized_weights]
        
        # Calculate optimized portfolio metrics
        opt_portfolio_return = sum(w * r for w, r in zip(optimized_weights, expected_returns))
        opt_portfolio_volatility = PortfolioAnalyzer.calculate_portfolio_volatility(optimized_weights, cov_matrix)
        opt_sharpe_ratio = (opt_portfolio_return - risk_free_rate) / opt_portfolio_volatility if opt_portfolio_volatility > 0 else 0
        
        # Prepare results
        optimization_results = []
        for i, asset in enumerate(available_assets):
            optimization_results.append({
                "symbol": asset["symbol"],
                "name": asset.get("name", ""),
                "expected_return": expected_returns[i],
                "volatility": volatilities[i],
                "current_weight": equal_weights[i],
                "optimized_weight": optimized_weights[i],
                "weight_change": optimized_weights[i] - equal_weights[i]
            })
        
        return json.dumps({
            "success": True,
            "optimization_results": optimization_results,
            "portfolio_metrics": {
                "current_return": portfolio_return,
                "current_volatility": portfolio_volatility,
                "current_sharpe_ratio": sharpe_ratio,
                "optimized_return": opt_portfolio_return,
                "optimized_volatility": opt_portfolio_volatility,
                "optimized_sharpe_ratio": opt_sharpe_ratio,
                "improvement": opt_sharpe_ratio - sharpe_ratio
            },
            "optimization_parameters": {
                "target_return": target_return,
                "risk_tolerance": risk_tolerance,
                "risk_free_rate": risk_free_rate
            },
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"Error in optimize_portfolio: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg
        }, ensure_ascii=False, indent=2)
