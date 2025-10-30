import asyncio
import httpx
import json
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from agents import RunContextWrapper, function_tool


class RetrievalQuery(BaseModel):
    """Schema for retrieval operations queries"""
    
    query: str = Field(
        ..., 
        description="The search query or question to retrieve information for",
        min_length=1,
        max_length=1000
    )
    
    data_sources: Optional[List[str]] = Field(
        default=None,
        description="Specific data sources to search in (documents, databases, apis, web)",
        max_items=10
    )
    
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional filters to apply to the search (date_range, category, type, etc.)"
    )
    
    max_results: int = Field(
        default=10,
        description="Maximum number of results to return",
        ge=1,
        le=100
    )
    
    include_metadata: bool = Field(
        default=True,
        description="Include metadata with results (source, timestamp, confidence, etc.)"
    )
    
    include_snippets: bool = Field(
        default=True,
        description="Include text snippets or summaries with results"
    )
    
    language: Optional[str] = Field(
        default="vi",
        description="Language preference for results (vi, en, auto)",
        pattern="^(vi|en|auto)$"
    )
    
    sort_by: Optional[str] = Field(
        default="relevance",
        description="Sort results by (relevance, date, score, title)",
        pattern="^(relevance|date|score|title)$"
    )
    
    sort_order: str = Field(
        default="desc",
        description="Sort order (asc, desc)",
        pattern="^(asc|desc)$"
    )
    
    class Config:
        extra = "forbid"


logger = logging.getLogger(__name__)


class RetrievalService:
    """Service class to handle retrieval operations"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Initialize RetrievalService
        
        Args:
            api_base_url: Base URL for the retrieval API
            api_key: API key for authentication (optional)
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {}
        )
    
    async def retrieve_data(self, retrieval_query: RetrievalQuery) -> str:
        """
        Retrieve data from API service
        
        Args:
            retrieval_query: RetrievalQuery object containing all query parameters
            
        Returns:
            JSON string containing retrieved information and results
        """
        try:
            # Prepare request payload with all schema fields
            payload = {
                "query": retrieval_query.query,
                "data_sources": retrieval_query.data_sources,
                "filters": retrieval_query.filters,
                "max_results": retrieval_query.max_results,
                "include_metadata": retrieval_query.include_metadata,
                "include_snippets": retrieval_query.include_snippets,
                "language": retrieval_query.language,
                "sort_by": retrieval_query.sort_by,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Make API request
            response = await self.client.post(
                f"{self.api_base_url}/api/v1/retrieve",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Process results based on schema flags
                processed_results = result.get("results", [])
                
                # Apply max_results limit
                if len(processed_results) > retrieval_query.max_results:
                    processed_results = processed_results[:retrieval_query.max_results]
                
                # Filter metadata and snippets based on flags
                if not retrieval_query.include_metadata:
                    processed_results = [
                        {k: v for k, v in item.items() if k not in ["source", "timestamp", "confidence", "metadata"]}
                        for item in processed_results
                    ]
                
                if not retrieval_query.include_snippets:
                    processed_results = [
                        {k: v for k, v in item.items() if k not in ["snippet", "summary", "excerpt"]}
                        for item in processed_results
                    ]
                
                # Sort results based on sort_by parameter
                if retrieval_query.sort_by == "date":
                    processed_results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                elif retrieval_query.sort_by == "score":
                    processed_results.sort(key=lambda x: x.get("score", 0), reverse=True)
                elif retrieval_query.sort_by == "title":
                    processed_results.sort(key=lambda x: x.get("title", ""))
                # relevance is default, no sorting needed
                
                return json.dumps({
                    "success": True,
                    "results": processed_results,
                    "query": retrieval_query.dict(),
                    "total_count": len(processed_results),
                    "language": retrieval_query.language,
                    "sort_by": retrieval_query.sort_by
                }, ensure_ascii=False, indent=2)
            else:
                error_msg = f"Retrieval API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return json.dumps({
                    "success": False,
                    "error": error_msg,
                    "query": retrieval_query.dict()
                }, ensure_ascii=False, indent=2)
                
        except Exception as e:
            error_msg = f"Error in retrieve_data: {str(e)}"
            logger.error(error_msg)
            return json.dumps({
                "success": False,
                "error": error_msg
            }, ensure_ascii=False, indent=2)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global service instance
retrieval_service = RetrievalService()


@function_tool
async def retrieve_information(
    query: str,
    data_sources: Optional[List[str]] = None,
    max_results: int = 10,
    include_metadata: bool = True,
    filters: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "desc"
) -> str:
    """
    Retrieve information from various data sources using structured queries with filters and metadata.
    
    Args:
        query: The search query or question to retrieve information for
        data_sources: List of data sources to search (news, reports, filings, social_media, web)
        max_results: Maximum number of results to return (1-100)
        include_metadata: Include metadata like source, timestamp, confidence score
        filters: Additional filters to apply (date_range, language, category, etc.)
        sort_by: Field to sort results by (relevance, date, confidence)
        sort_order: Sort order (asc, desc)
        
    Returns:
        JSON string containing retrieval results
    """
    try:
        # Parse filters if provided as JSON string
        parsed_filters = None
        if filters:
            try:
                parsed_filters = json.loads(filters)
            except json.JSONDecodeError:
                # If not valid JSON, treat as simple string filter
                parsed_filters = {"type": filters}
        
        # Create query object
        retrieval_query = RetrievalQuery(
            query=query,
            data_sources=data_sources,
            max_results=max_results,
            include_metadata=include_metadata,
            filters=parsed_filters,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Call retrieval service
        result = await retrieval_service.retrieve_data(retrieval_query)
        
        return result
        
    except Exception as e:
        error_msg = f"Error in retrieve_information: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg
        }, ensure_ascii=False, indent=2)


# Export alias for backward compatibility
retrieval_tool = retrieve_information
