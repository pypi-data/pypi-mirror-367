"""Lightdash API client for MCP integration"""

import logging
from typing import Any, Dict, List, Optional
import httpx
import json

from dbt_mcp.config.config import LightdashConfig

logger = logging.getLogger(__name__)


class LightdashAPIClient:
    """Async client for interacting with Lightdash API"""
    
    def __init__(self, config: LightdashConfig):
        self.config = config
        self.base_url = config.api_url.rstrip('/')
        self.headers = {
            "Authorization": f"ApiKey {config.api_key}",
            "Content-Type": "application/json"
        }
        self.project_id = config.project_id
        self.default_space_id = config.default_space_id
        
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        use_v2: bool = False
    ) -> Dict[str, Any]:
        """Make an async HTTP request to Lightdash API"""
        if use_v2:
            # For v2 endpoints, replace /api/v1 with /api/v2
            base_url = self.base_url.replace('/api/v1', '/api/v2')
            url = f"{base_url}{endpoint}"
        else:
            url = f"{self.base_url}{endpoint}"
        
        # Merge headers if extra headers provided
        headers = self.headers.copy()
        if extra_headers:
            headers.update(extra_headers)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params
                )
                
                response_text = response.text
                
                if response.status_code >= 400:
                    logger.error(f"API error {response.status_code}: {response_text}")
                    
                    # Try to parse error message from response
                    error_msg = response_text
                    try:
                        if response_text:
                            error_data = response.json()
                            if isinstance(error_data, dict):
                                error_msg = (
                                    error_data.get('message') or 
                                    error_data.get('error', {}).get('message') or
                                    response_text
                                )
                    except:
                        pass
                    
                    raise Exception(f"Lightdash API error {response.status_code}: {error_msg}")
                
                if response_text:
                    return response.json()
                return {}
                    
            except httpx.HTTPError as e:
                logger.error(f"Client error making request to {url}: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error making request to {url}: {str(e)}")
                raise
    
    async def list_spaces(self) -> List[Dict[str, Any]]:
        """List all spaces in the project"""
        endpoint = f"/projects/{self.project_id}/spaces"
        result = await self._make_request("GET", endpoint)
        return result.get("results", [])
    
    async def get_space(self, space_id: str) -> Dict[str, Any]:
        """Get details of a specific space"""
        endpoint = f"/projects/{self.project_id}/spaces/{space_id}"
        result = await self._make_request("GET", endpoint)
        return result.get("results", {})
    
    async def list_charts(self, space_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all charts, optionally filtered by space"""
        endpoint = f"/projects/{self.project_id}/charts"
        params = {"spaceUuid": space_id} if space_id else None
        result = await self._make_request("GET", endpoint, params=params)
        return result.get("results", [])
    
    async def get_chart(self, chart_id: str) -> Dict[str, Any]:
        """Get details of a specific chart"""
        endpoint = f"/saved/{chart_id}"
        result = await self._make_request("GET", endpoint)
        return result.get("results", {})
    
    async def create_chart(
        self, 
        name: str,
        description: Optional[str],
        table_name: str,
        metric_query: Dict[str, Any],
        chart_config: Dict[str, Any],
        space_uuid: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new chart in Lightdash"""
        space_id = space_uuid or self.default_space_id
        if not space_id:
            # Get the first available space if no default
            spaces = await self.list_spaces()
            if not spaces:
                raise Exception("No spaces available in Lightdash project")
            space_id = spaces[0]["uuid"]
        
        data = {
            "name": name,
            "description": description,
            "tableName": table_name,
            "metricQuery": metric_query,
            "chartConfig": chart_config,
            "tableConfig": {
                "columnOrder": []
            },
            "spaceUuid": space_id
        }
        
        endpoint = f"/projects/{self.project_id}/saved"
        result = await self._make_request("POST", endpoint, data=data)
        return result.get("results", {})
    
    async def update_chart(self, chart_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing chart"""
        endpoint = f"/saved/{chart_id}"
        result = await self._make_request("PATCH", endpoint, data=updates)
        return result.get("results", {})
    
    async def delete_chart(self, chart_id: str) -> None:
        """Delete a chart"""
        endpoint = f"/saved/{chart_id}"
        await self._make_request("DELETE", endpoint)
    
    async def list_explores(self) -> List[Dict[str, Any]]:
        """List all explores (dbt models) in the project"""
        endpoint = f"/projects/{self.project_id}/explores"
        result = await self._make_request("GET", endpoint)
        return result.get("results", [])
    
    async def get_explore(self, explore_id: str) -> Dict[str, Any]:
        """Get details of a specific explore"""
        endpoint = f"/projects/{self.project_id}/explores/{explore_id}"
        result = await self._make_request("GET", endpoint)
        return result.get("results", {})
    
    async def run_query(self, explore_id: str, metric_query: Dict[str, Any]) -> Dict[str, Any]:
        """Run a metric query against an explore"""
        endpoint = f"/projects/{self.project_id}/explores/{explore_id}/runQuery"
        result = await self._make_request("POST", endpoint, data=metric_query)
        return result.get("results", {})
    
    async def get_catalog_metrics(self, table_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available metrics from the catalog"""
        endpoint = f"/projects/{self.project_id}/dataCatalog/metrics"
        params = {"table": table_name} if table_name else None
        result = await self._make_request("GET", endpoint, params=params)
        return result.get("results", [])
    
    async def get_user(self) -> Dict[str, Any]:
        """Get current user information including organizationUuid"""
        endpoint = "/user"
        result = await self._make_request("GET", endpoint)
        return result.get("results", {})