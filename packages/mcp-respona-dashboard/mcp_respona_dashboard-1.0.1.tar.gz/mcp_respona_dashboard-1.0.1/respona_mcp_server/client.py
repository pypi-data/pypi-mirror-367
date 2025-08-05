"""HTTP client for Respona Dashboard API."""

import asyncio
import logging
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin, urlencode

import httpx
from pydantic import BaseModel

from .config import config

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom exception for API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)


class ResponaAPIClient:
    """HTTP client for interacting with the Respona Dashboard API."""
    
    def __init__(self, base_url: Optional[str] = None):
        """Initialize the API client.
        
        Args:
            base_url: Override the default API base URL
        """
        self.base_url = base_url or config.api_base_url
        self.timeout = config.request_timeout
        self.max_retries = config.max_retries
        
        # Ensure base URL ends with /
        if not self.base_url.endswith('/'):
            self.base_url += '/'
            
        logger.info(f"Initialized Respona API client with base URL: {self.base_url}")
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        retries: int = 0
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            retries: Current retry count
            
        Returns:
            Parsed JSON response
            
        Raises:
            APIError: If the request fails
        """
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        
        # Clean up parameters - remove None values and convert to strings
        if params:
            params = {k: str(v) for k, v in params.items() if v is not None}
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add API key to headers if configured
        if config.api_key:
            headers["Authorization"] = f"Bearer {config.api_key}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"Making {method} request to {url} with params: {params}")
                
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=headers
                )
                
                # Check for HTTP errors
                if response.status_code >= 400:
                    error_message = f"HTTP {response.status_code}: {response.reason_phrase}"
                    
                    try:
                        error_data = response.json()
                        if isinstance(error_data, dict):
                            error_message = error_data.get('message', error_message)
                    except Exception:
                        # If we can't parse JSON, use the text content
                        error_message = response.text or error_message
                    
                    raise APIError(
                        message=error_message,
                        status_code=response.status_code,
                        response_data=error_data if 'error_data' in locals() else None
                    )
                
                # Parse JSON response
                try:
                    response_data = response.json()
                    logger.debug(f"Successful response from {url}")
                    return response_data
                except Exception as e:
                    raise APIError(f"Failed to parse JSON response: {str(e)}")
                    
        except httpx.TimeoutException:
            if retries < self.max_retries:
                logger.warning(f"Request timeout, retrying... ({retries + 1}/{self.max_retries})")
                await asyncio.sleep(2 ** retries)  # Exponential backoff
                return await self._make_request(method, endpoint, params, data, retries + 1)
            raise APIError("Request timeout after all retries")
            
        except httpx.ConnectError:
            if retries < self.max_retries:
                logger.warning(f"Connection error, retrying... ({retries + 1}/{self.max_retries})")
                await asyncio.sleep(2 ** retries)  # Exponential backoff
                return await self._make_request(method, endpoint, params, data, retries + 1)
            raise APIError(f"Failed to connect to API server at {self.base_url}")
            
        except APIError:
            # Re-raise API errors without modification
            raise
            
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}")
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            Parsed JSON response
        """
        return await self._make_request("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request.
        
        Args:
            endpoint: API endpoint path
            data: Request body data
            
        Returns:
            Parsed JSON response
        """
        return await self._make_request("POST", endpoint, data=data)
    
    async def health_check(self) -> bool:
        """Check if the API server is healthy.
        
        Returns:
            True if the server is healthy, False otherwise
        """
        try:
            # Try to make a simple request to check connectivity
            await self.get("/api/tickets/stats")
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False


# Global client instance
client = ResponaAPIClient() 