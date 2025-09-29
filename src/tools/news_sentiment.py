"""
News Sentiment Analysis Tool - Công cụ phân tích sentiment tin tức tài chính
"""
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum

from agents import function_tool

logger = logging.getLogger(__name__)


class SentimentType(str, Enum):
    """Sentiment classification"""
    VERY_POSITIVE = "Very Positive"
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"
    VERY_NEGATIVE = "Very Negative"


class NewsSource(str, Enum):
    """News source types"""
    FINANCIAL_NEWS = "Financial News"
    SOCIAL_MEDIA = "Social Media"
    BLOG = "Blog"
    FORUM = "Forum"
    PRESS_RELEASE = "Press Release"
    ANALYST_REPORT = "Analyst Report"
    GOVERNMENT = "Government"
    OTHER = "Other"


class SentimentScore(BaseModel):
    """Sentiment analysis result"""
    text: str
    sentiment: SentimentType
    confidence: float
    positive_score: float
    negative_score: float
    neutral_score: float
    keywords: List[str]
    source: Optional[NewsSource] = None
    timestamp: Optional[str] = None


class NewsItem(BaseModel):
    """News item structure"""
    title: str
    content: str
    source: str
    url: Optional[str] = None
    published_date: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None


class SentimentAnalyzer:
    """Financial news sentiment analyzer"""
    
    def __init__(self):
        """Initialize sentiment analyzer with financial keywords"""
        # Financial positive keywords
        self.positive_keywords = {
            # Growth and performance
            "tăng trưởng", "growth", "tăng", "increase", "rise", "up", "surge", "rally",
            "profit", "lợi nhuận", "earnings", "revenue", "doanh thu", "success", "thành công",
            "breakthrough", "đột phá", "milestone", "cột mốc", "record", "kỷ lục",
            "expansion", "mở rộng", "acquisition", "mua lại", "merger", "sáp nhập",
            "innovation", "đổi mới", "development", "phát triển", "progress", "tiến bộ",
            
            # Market positive
            "bullish", "tăng giá", "uptrend", "xu hướng tăng", "momentum", "đà tăng",
            "optimistic", "lạc quan", "confident", "tự tin", "strong", "mạnh mẽ",
            "outperform", "vượt trội", "beat", "vượt", "exceed", "vượt quá",
            "upgrade", "nâng cấp", "buy", "mua", "recommend", "khuyến nghị",
            
            # Financial stability
            "stable", "ổn định", "solid", "vững chắc", "robust", "mạnh mẽ",
            "resilient", "kiên cường", "sustainable", "bền vững", "healthy", "lành mạnh",
            "improvement", "cải thiện", "recovery", "phục hồi", "rebound", "bật dậy"
        }
        
        # Financial negative keywords
        self.negative_keywords = {
            # Decline and problems
            "giảm", "decrease", "decline", "fall", "drop", "down", "plunge", "crash",
            "loss", "lỗ", "losses", "thua lỗ", "deficit", "thâm hụt", "debt", "nợ",
            "crisis", "khủng hoảng", "recession", "suy thoái", "depression", "trầm cảm",
            "bankruptcy", "phá sản", "default", "vỡ nợ", "insolvency", "mất khả năng thanh toán",
            
            # Market negative
            "bearish", "giảm giá", "downtrend", "xu hướng giảm", "volatility", "biến động",
            "pessimistic", "bi quan", "concern", "lo ngại", "worry", "lo lắng",
            "underperform", "kém hiệu quả", "miss", "bỏ lỡ", "disappoint", "thất vọng",
            "downgrade", "hạ cấp", "sell", "bán", "avoid", "tránh", "warning", "cảnh báo",
            
            # Risk and uncertainty
            "risk", "rủi ro", "uncertainty", "không chắc chắn", "volatile", "biến động",
            "unstable", "không ổn định", "weak", "yếu", "fragile", "mong manh",
            "deterioration", "suy giảm", "decline", "suy giảm", "struggle", "khó khăn",
            "challenge", "thách thức", "threat", "mối đe dọa", "concern", "lo ngại"
        }
        
        # Neutral keywords (context-dependent)
        self.neutral_keywords = {
            "maintain", "duy trì", "stable", "ổn định", "unchanged", "không đổi",
            "neutral", "trung tính", "mixed", "hỗn hợp", "moderate", "vừa phải",
            "expected", "dự kiến", "forecast", "dự báo", "projection", "dự án",
            "analysis", "phân tích", "report", "báo cáo", "data", "dữ liệu"
        }
        
        # Financial intensity modifiers
        self.intensity_modifiers = {
            "very": 2.0, "rất": 2.0, "extremely": 2.5, "cực kỳ": 2.5,
            "highly": 1.8, "cao": 1.8, "significantly": 1.5, "đáng kể": 1.5,
            "slightly": 0.5, "hơi": 0.5, "somewhat": 0.7, "khá": 0.7,
            "moderately": 1.0, "vừa phải": 1.0
        }
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep Vietnamese diacritics
        text = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant financial keywords from text"""
        words = text.split()
        keywords = []
        
        for word in words:
            if word in self.positive_keywords or word in self.negative_keywords or word in self.neutral_keywords:
                keywords.append(word)
        
        return keywords
    
    def calculate_sentiment_scores(self, text: str) -> Tuple[float, float, float, List[str]]:
        """Calculate sentiment scores for text"""
        processed_text = self.preprocess_text(text)
        words = processed_text.split()
        
        positive_score = 0.0
        negative_score = 0.0
        neutral_score = 0.0
        keywords = []
        
        for i, word in enumerate(words):
            # Check for intensity modifiers
            intensity = 1.0
            if i > 0 and words[i-1] in self.intensity_modifiers:
                intensity = self.intensity_modifiers[words[i-1]]
            
            # Check word sentiment
            if word in self.positive_keywords:
                positive_score += intensity
                keywords.append(word)
            elif word in self.negative_keywords:
                negative_score += intensity
                keywords.append(word)
            elif word in self.neutral_keywords:
                neutral_score += intensity
                keywords.append(word)
        
        # Normalize scores
        total_words = len(words)
        if total_words > 0:
            positive_score = positive_score / total_words
            negative_score = negative_score / total_words
            neutral_score = neutral_score / total_words
        
        return positive_score, negative_score, neutral_score, keywords
    
    def classify_sentiment(self, positive_score: float, negative_score: float, neutral_score: float) -> Tuple[SentimentType, float]:
        """Classify sentiment based on scores"""
        # Calculate confidence based on score differences
        max_score = max(positive_score, negative_score, neutral_score)
        total_score = positive_score + negative_score + neutral_score
        
        if total_score == 0:
            return SentimentType.NEUTRAL, 0.5
        
        confidence = max_score / total_score if total_score > 0 else 0.5
        
        # Determine sentiment type
        if positive_score > negative_score and positive_score > neutral_score:
            if positive_score > 0.1:
                return SentimentType.VERY_POSITIVE if positive_score > 0.2 else SentimentType.POSITIVE
            else:
                return SentimentType.NEUTRAL
        elif negative_score > positive_score and negative_score > neutral_score:
            if negative_score > 0.1:
                return SentimentType.VERY_NEGATIVE if negative_score > 0.2 else SentimentType.NEGATIVE
            else:
                return SentimentType.NEUTRAL
        else:
            return SentimentType.NEUTRAL
    
    def analyze_text(self, text: str, source: Optional[NewsSource] = None) -> SentimentScore:
        """Analyze sentiment of a single text"""
        positive_score, negative_score, neutral_score, keywords = self.calculate_sentiment_scores(text)
        sentiment, confidence = self.classify_sentiment(positive_score, negative_score, neutral_score)
        
        return SentimentScore(
            text=text[:200] + "..." if len(text) > 200 else text,  # Truncate for display
            sentiment=sentiment,
            confidence=confidence,
            positive_score=positive_score,
            negative_score=negative_score,
            neutral_score=neutral_score,
            keywords=keywords,
            source=source,
            timestamp=datetime.now().isoformat()
        )
    
    def analyze_news_batch(self, news_items: List[NewsItem]) -> List[SentimentScore]:
        """Analyze sentiment for multiple news items"""
        results = []
        
        for item in news_items:
            # Combine title and content for analysis
            full_text = f"{item.title} {item.content}"
            
            # Determine source type
            source_type = NewsSource.OTHER
            if any(keyword in item.source.lower() for keyword in ["reuters", "bloomberg", "wsj", "financial"]):
                source_type = NewsSource.FINANCIAL_NEWS
            elif any(keyword in item.source.lower() for keyword in ["twitter", "facebook", "social"]):
                source_type = NewsSource.SOCIAL_MEDIA
            elif any(keyword in item.source.lower() for keyword in ["blog", "medium"]):
                source_type = NewsSource.BLOG
            
            result = self.analyze_text(full_text, source_type)
            results.append(result)
        
        return results
    
    def calculate_market_sentiment(self, sentiment_scores: List[SentimentScore]) -> Dict[str, Any]:
        """Calculate overall market sentiment from multiple scores"""
        if not sentiment_scores:
            return {
                "overall_sentiment": SentimentType.NEUTRAL,
                "confidence": 0.0,
                "sentiment_distribution": {},
                "average_confidence": 0.0
            }
        
        # Count sentiment types
        sentiment_counts = {}
        total_confidence = 0.0
        
        for score in sentiment_scores:
            sentiment = score.sentiment.value
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            total_confidence += score.confidence
        
        # Calculate weighted sentiment
        sentiment_weights = {
            SentimentType.VERY_POSITIVE.value: 2,
            SentimentType.POSITIVE.value: 1,
            SentimentType.NEUTRAL.value: 0,
            SentimentType.NEGATIVE.value: -1,
            SentimentType.VERY_NEGATIVE.value: -2
        }
        
        weighted_sum = sum(sentiment_counts.get(sent, 0) * weight for sent, weight in sentiment_weights.items())
        total_items = len(sentiment_scores)
        
        if total_items == 0:
            overall_sentiment = SentimentType.NEUTRAL
        elif weighted_sum > 0.5:
            overall_sentiment = SentimentType.POSITIVE
        elif weighted_sum > 1.5:
            overall_sentiment = SentimentType.VERY_POSITIVE
        elif weighted_sum < -0.5:
            overall_sentiment = SentimentType.NEGATIVE
        elif weighted_sum < -1.5:
            overall_sentiment = SentimentType.VERY_NEGATIVE
        else:
            overall_sentiment = SentimentType.NEUTRAL
        
        # Calculate confidence
        average_confidence = total_confidence / total_items if total_items > 0 else 0.0
        
        # Calculate distribution percentages
        sentiment_distribution = {
            sent: (count / total_items) * 100 for sent, count in sentiment_counts.items()
        }
        
        return {
            "overall_sentiment": overall_sentiment,
            "confidence": average_confidence,
            "sentiment_distribution": sentiment_distribution,
            "average_confidence": average_confidence,
            "total_articles": total_items,
            "weighted_score": weighted_sum / total_items if total_items > 0 else 0
        }


@function_tool
async def analyze_news_sentiment(
    news_text: str,
    title: Optional[str] = None,
    source: Optional[str] = None
) -> str:
    """
    Analyze sentiment of financial news text.
    
    Args:
        news_text: The news content to analyze
        title: Optional news title
        source: Optional news source
    """
    try:
        analyzer = SentimentAnalyzer()
        
        # Combine title and content if provided
        full_text = f"{title} {news_text}" if title else news_text
        
        # Determine source type
        source_type = NewsSource.OTHER
        if source:
            if any(keyword in source.lower() for keyword in ["reuters", "bloomberg", "wsj", "financial", "tài chính"]):
                source_type = NewsSource.FINANCIAL_NEWS
            elif any(keyword in source.lower() for keyword in ["twitter", "facebook", "social", "mạng xã hội"]):
                source_type = NewsSource.SOCIAL_MEDIA
            elif any(keyword in source.lower() for keyword in ["blog", "medium"]):
                source_type = NewsSource.BLOG
        
        # Analyze sentiment
        result = analyzer.analyze_text(full_text, source_type)
        
        return json.dumps({
            "success": True,
            "sentiment_analysis": result.model_dump(),
            "summary": {
                "sentiment": result.sentiment.value,
                "confidence": result.confidence,
                "keywords_found": len(result.keywords),
                "source_type": result.source.value if result.source else "Unknown"
            },
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"Error in analyze_news_sentiment: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg
        }, ensure_ascii=False, indent=2)


@function_tool
async def analyze_market_sentiment(
    news_items: List[Dict[str, Any]]
) -> str:
    """
    Analyze overall market sentiment from multiple news items.
    
    Args:
        news_items: List of news items with 'title', 'content', 'source' fields
    """
    try:
        analyzer = SentimentAnalyzer()
        
        # Convert dict items to NewsItem objects
        news_objects = []
        for item in news_items:
            news_obj = NewsItem(
                title=item.get("title", ""),
                content=item.get("content", ""),
                source=item.get("source", "Unknown"),
                url=item.get("url"),
                published_date=item.get("published_date"),
                author=item.get("author"),
                category=item.get("category")
            )
            news_objects.append(news_obj)
        
        # Analyze sentiment for all items
        sentiment_scores = analyzer.analyze_news_batch(news_objects)
        
        # Calculate overall market sentiment
        market_sentiment = analyzer.calculate_market_sentiment(sentiment_scores)
        
        # Prepare detailed results
        detailed_results = []
        for i, score in enumerate(sentiment_scores):
            detailed_results.append({
                "index": i,
                "title": news_objects[i].title[:100] + "..." if len(news_objects[i].title) > 100 else news_objects[i].title,
                "sentiment": score.sentiment.value,
                "confidence": score.confidence,
                "keywords": score.keywords[:5],  # Top 5 keywords
                "source": news_objects[i].source
            })
        
        return json.dumps({
            "success": True,
            "market_sentiment": market_sentiment,
            "detailed_analysis": detailed_results,
            "summary": {
                "total_articles": len(news_items),
                "overall_sentiment": market_sentiment["overall_sentiment"].value,
                "confidence": market_sentiment["confidence"],
                "sentiment_breakdown": market_sentiment["sentiment_distribution"]
            },
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"Error in analyze_market_sentiment: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg
        }, ensure_ascii=False, indent=2)


@function_tool
async def extract_financial_keywords(
    text: str,
    keyword_type: str = "all"  # "positive", "negative", "neutral", "all"
) -> str:
    """
    Extract financial keywords from text for analysis.
    
    Args:
        text: Text to extract keywords from
        keyword_type: Type of keywords to extract ("positive", "negative", "neutral", "all")
    """
    try:
        analyzer = SentimentAnalyzer()
        processed_text = analyzer.preprocess_text(text)
        words = processed_text.split()
        
        positive_keywords = []
        negative_keywords = []
        neutral_keywords = []
        
        for word in words:
            if word in analyzer.positive_keywords:
                positive_keywords.append(word)
            elif word in analyzer.negative_keywords:
                negative_keywords.append(word)
            elif word in analyzer.neutral_keywords:
                neutral_keywords.append(word)
        
        result = {
            "success": True,
            "text_length": len(text),
            "processed_length": len(processed_text),
            "total_words": len(words),
            "keywords": {}
        }
        
        if keyword_type in ["positive", "all"]:
            result["keywords"]["positive"] = list(set(positive_keywords))
        if keyword_type in ["negative", "all"]:
            result["keywords"]["negative"] = list(set(negative_keywords))
        if keyword_type in ["neutral", "all"]:
            result["keywords"]["neutral"] = list(set(neutral_keywords))
        
        result["keywords"]["total_found"] = len(positive_keywords) + len(negative_keywords) + len(neutral_keywords)
        result["timestamp"] = datetime.now().isoformat()
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"Error in extract_financial_keywords: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg
        }, ensure_ascii=False, indent=2)
