"""
Report templates and utilities for professional financial analysis reports
"""
from typing import Dict, List, Any
from datetime import datetime


class ReportTemplates:
    """Templates for professional financial reports"""
    
    @staticmethod
    def get_executive_summary_template() -> str:
        """Template for executive summary section"""
        return """
## Executive Summary

### Investment Thesis
[Brief 2-3 sentence summary of the investment opportunity and key thesis]

### Key Findings
- **Financial Performance**: [Summary of recent financial performance trends]
- **Market Position**: [Company's competitive position and market share]
- **Growth Prospects**: [Key growth drivers and strategic initiatives]
- **Risk Factors**: [Primary risk considerations]

### Recommendation
[Clear investment recommendation with rationale and time horizon]
        """.strip()
    
    @staticmethod
    def get_fundamental_analysis_template() -> str:
        """Template for fundamental analysis section"""
        return """
## Fundamental Analysis

### Financial Health Metrics
| Metric | Current | Industry Avg | Trend | Assessment |
|--------|---------|--------------|-------|------------|
| Revenue Growth | [%] | [%] | [↗/↘/→] | [Strong/Moderate/Weak] |
| Gross Margin | [%] | [%] | [↗/↘/→] | [Strong/Moderate/Weak] |
| Operating Margin | [%] | [%] | [↗/↘/→] | [Strong/Moderate/Weak] |
| Net Margin | [%] | [%] | [↗/↘/→] | [Strong/Moderate/Weak] |
| ROE | [%] | [%] | [↗/↘/→] | [Strong/Moderate/Weak] |
| ROA | [%] | [%] | [↗/↘/→] | [Strong/Moderate/Weak] |
| Debt-to-Equity | [ratio] | [ratio] | [↗/↘/→] | [Strong/Moderate/Weak] |
| Current Ratio | [ratio] | [ratio] | [↗/↘/→] | [Strong/Moderate/Weak] |

### Key Financial Highlights
- **Revenue**: [Analysis of revenue trends and drivers]
- **Profitability**: [Analysis of margin trends and cost management]
- **Cash Flow**: [Analysis of cash generation and capital allocation]
- **Balance Sheet**: [Analysis of financial position and leverage]
        """.strip()
    
    @staticmethod
    def get_technical_analysis_template() -> str:
        """Template for technical analysis section"""
        return """
## Technical Analysis

### Price Action Analysis
- **Current Price**: $[price] ([change]% from 52-week high/low)
- **Support Levels**: $[level1], $[level2], $[level3]
- **Resistance Levels**: $[level1], $[level2], $[level3]
- **Trend**: [Bullish/Bearish/Sideways] - [Brief explanation]

### Technical Indicators
| Indicator | Value | Signal | Interpretation |
|-----------|-------|--------|----------------|
| RSI (14) | [value] | [Overbought/Neutral/Oversold] | [Analysis] |
| MACD | [value] | [Bullish/Bearish/Neutral] | [Analysis] |
| Moving Average (50) | $[price] | [Above/Below] | [Analysis] |
| Moving Average (200) | $[price] | [Above/Below] | [Analysis] |
| Bollinger Bands | [Position] | [Squeeze/Expansion] | [Analysis] |

### Chart Patterns
[Description of any significant chart patterns, breakouts, or formations]
        """.strip()
    
    @staticmethod
    def get_valuation_analysis_template() -> str:
        """Template for valuation analysis section"""
        return """
## Valuation Analysis

### Valuation Metrics
| Metric | Current | Industry Avg | Premium/Discount | Assessment |
|--------|---------|--------------|------------------|------------|
| P/E Ratio | [ratio] | [ratio] | [%] | [Overvalued/Fair/Undervalued] |
| P/B Ratio | [ratio] | [ratio] | [%] | [Overvalued/Fair/Undervalued] |
| P/S Ratio | [ratio] | [ratio] | [%] | [Overvalued/Fair/Undervalued] |
| EV/EBITDA | [ratio] | [ratio] | [%] | [Overvalued/Fair/Undervalued] |
| PEG Ratio | [ratio] | [ratio] | [%] | [Overvalued/Fair/Undervalued] |

### DCF Analysis
- **Assumptions**:
  - Growth Rate: [%] (Years 1-5), [%] (Terminal)
  - Discount Rate: [%]
  - Terminal Growth: [%]
- **DCF Value**: $[price] per share
- **Current Price**: $[price]
- **Upside/Downside**: [%]

### Price Targets
| Method | Target Price | Upside/Downside |
|--------|--------------|-----------------|
| DCF Model | $[price] | [%] |
| P/E Multiple | $[price] | [%] |
| P/B Multiple | $[price] | [%] |
| **Consensus Target** | **$[price]** | **[%]** |
        """.strip()
    
    @staticmethod
    def get_risk_assessment_template() -> str:
        """Template for risk assessment section"""
        return """
## Risk Assessment

### Risk Factors
#### High Impact Risks
1. **[Risk Category]**: [Description and potential impact]
2. **[Risk Category]**: [Description and potential impact]
3. **[Risk Category]**: [Description and potential impact]

#### Medium Impact Risks
1. **[Risk Category]**: [Description and potential impact]
2. **[Risk Category]**: [Description and potential impact]

#### Low Impact Risks
1. **[Risk Category]**: [Description and potential impact]

### Risk Mitigation
- **Company Level**: [How the company is addressing risks]
- **Investment Level**: [How investors can mitigate risks]
- **Portfolio Level**: [Diversification considerations]

### Scenario Analysis
| Scenario | Probability | Price Impact | Key Drivers |
|----------|-------------|--------------|-------------|
| Bull Case | [%] | [+%] | [Key factors] |
| Base Case | [%] | [%] | [Key factors] |
| Bear Case | [%] | [-%] | [Key factors] |
        """.strip()
    
    @staticmethod
    def get_disclaimer_template() -> str:
        """Standard financial analysis disclaimer"""
        return """
## Disclaimer

This report is for informational purposes only and does not constitute investment advice, 
a recommendation to buy, sell, or hold any security, or an offer to buy or sell any security. 
The information contained herein is based on sources believed to be reliable but is not 
guaranteed to be accurate or complete. Past performance is not indicative of future results. 
Investors should conduct their own research and consult with qualified financial advisors 
before making investment decisions. The author and publisher of this report disclaim any 
liability for any direct or indirect loss arising from the use of this information.

**Report Date**: {date}
**Data Sources**: {sources}
**Analyst**: Professional Financial Writer Agent
        """.strip()
    
    @staticmethod
    def get_full_report_template() -> str:
        """Template for the complete report structure"""
        return """
# Financial Analysis Report: {company_name} ({ticker})

**Report Date**: {date}
**Analyst**: Professional Financial Writer Agent
**Rating**: {rating}
**Target Price**: ${target_price}
**Current Price**: ${current_price}

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Investment Recommendation](#investment-recommendation)
3. [Risk Assessment](#risk-assessment)
4. [Market Context](#market-context)
5. [Company Overview](#company-overview)
6. [Financial Performance Analysis](#financial-performance-analysis)
7. [Fundamental Analysis](#fundamental-analysis)
8. [Technical Analysis](#technical-analysis)
9. [Competitive Analysis](#competitive-analysis)
10. [Growth Prospects](#growth-prospects)
11. [Valuation Analysis](#valuation-analysis)
12. [Key Metrics Summary](#key-metrics-summary)
13. [Charts and Visualizations](#charts-and-visualizations)
14. [Follow-up Research](#follow-up-research)
15. [Data Sources](#data-sources)
16. [Disclaimer](#disclaimer)

---

{content}

---

{disclaimer}
        """.strip()


class ReportHelpers:
    """Helper functions for report generation"""
    
    @staticmethod
    def format_currency(value: float, currency: str = "USD") -> str:
        """Format currency values"""
        if currency == "USD":
            return f"${value:,.2f}"
        return f"{value:,.2f} {currency}"
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 2) -> str:
        """Format percentage values"""
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def format_ratio(value: float, decimals: int = 2) -> str:
        """Format ratio values"""
        return f"{value:.{decimals}f}x"
    
    @staticmethod
    def get_trend_arrow(value: float, threshold: float = 0.05) -> str:
        """Get trend arrow based on value change"""
        if value > threshold:
            return "↗"
        elif value < -threshold:
            return "↘"
        else:
            return "→"
    
    @staticmethod
    def get_rating_color(rating: str) -> str:
        """Get color code for investment rating"""
        rating_colors = {
            "Strong Buy": "🟢",
            "Buy": "🟢",
            "Hold": "🟡",
            "Sell": "🔴",
            "Strong Sell": "🔴"
        }
        return rating_colors.get(rating, "⚪")
    
    @staticmethod
    def get_risk_color(risk_level: str) -> str:
        """Get color code for risk level"""
        risk_colors = {
            "Low": "🟢",
            "Medium": "🟡",
            "High": "🟠",
            "Very High": "🔴"
        }
        return risk_colors.get(risk_level, "⚪")
    
    @staticmethod
    def generate_report_metadata(company_name: str, ticker: str) -> Dict[str, Any]:
        """Generate metadata for the report"""
        return {
            "company_name": company_name,
            "ticker": ticker,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }
