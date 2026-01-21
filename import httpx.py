import httpx
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class RetrievalResult(BaseModel):
    content: str
    title: str
    url: str
    site: Optional[str] = None
    score: Optional[float] = None

class M365RetrievalClient:
    """Handles retrieval from Microsoft 365 Copilot Retrieval API."""
    
    BASE_URL = "https://graph.microsoft.com/v1.0"
    
    def __init__(self, access_token: str):
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search_content(
        self,
        query: str,
        top: int = 5,
        site_filter: Optional[str] = None
    ) -> List[RetrievalResult]:
        """
        Search M365 content using semantic search.
        
        Args:
            query: User's search query
            top: Maximum number of results (5-10 recommended)
            site_filter: Optional SharePoint site URL filter
        """
        try:
            # Build KQL filter if site specified
            kql_filter = f"site:{site_filter}" if site_filter else None
            
            request_body = {
                "requests": [
                    {
                        "entityTypes": ["driveItem", "listItem", "site"],
                        "query": {
                            "queryString": query
                        },
                        "from": 0,
                        "size": top
                    }
                ]
            }
            
            # Add KQL filter if present
            if kql_filter:
                request_body["requests"][0]["query"]["kql"] = kql_filter
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/search/query",
                    headers=self.headers,
                    json=request_body
                )
                
                # Log diagnostics on errors or high latency
                if response.status_code != 200 or response.elapsed.total_seconds() > 2:
                    logger.warning(f"Search diagnostics - Status: {response.status_code}, "
                                 f"Latency: {response.elapsed.total_seconds():.2f}s")
                
                response.raise_for_status()
                data = response.json()
                
                return self._parse_results(data)
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error("Rate limit hit - implement retry-after logic")
            logger.error(f"Search failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during search: {str(e)}")
            return []
    
    def _parse_results(self, data: Dict) -> List[RetrievalResult]:
        """Parse Microsoft Graph search response into structured results."""
        results = []
        
        try:
            for value in data.get("value", []):
                for hit_container in value.get("hitsContainers", []):
                    for hit in hit_container.get("hits", []):
                        resource = hit.get("resource", {})
                        
                        # Extract content snippet
                        content = hit.get("summary", "") or resource.get("body", {}).get("content", "")
                        
                        result = RetrievalResult(
                            content=content[:1000],  # Limit chunk size
                            title=resource.get("name", "Untitled"),
                            url=resource.get("webUrl", ""),
                            site=resource.get("parentReference", {}).get("siteId"),
                            score=hit.get("rank")
                        )
                        results.append(result)
                        
        except Exception as e:
            logger.error(f"Error parsing results: {str(e)}")
        
        return results
