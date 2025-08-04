"""
HTTP client for making requests to the Limitly API
"""

import json
import requests
from typing import Any, Dict, Optional
from .types import LimitlyConfig, LimitlyError, RequestOptions


class HttpClient:
    """
    HTTP client for making requests to the Limitly API
    """
    
    def __init__(self, config: LimitlyConfig):
        """
        Initialize the HTTP client
        
        Args:
            config: Configuration for the client
        """
        self.api_key = config.api_key
        self.base_url = config.base_url or "https://xfkyofkqbukqtxcuapvf.supabase.co/functions/v1"
        self.timeout = config.timeout or 30
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        request_options: Optional[RequestOptions] = None
    ) -> Dict[str, Any]:
        """
        Makes an HTTP request to the Limitly API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: The API endpoint to call
            data: Request body data
            request_options: Additional request options
            
        Returns:
            Response data as dictionary
            
        Raises:
            LimitlyError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        if request_options and request_options.headers:
            headers.update(request_options.headers)
        
        timeout = (request_options.timeout if request_options else None) or self.timeout
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise LimitlyError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            # Server response error
            try:
                error_data = e.response.json()
                error_message = error_data.get("error", f"HTTP {e.response.status_code}: {e.response.reason}")
            except (ValueError, KeyError):
                error_message = f"HTTP {e.response.status_code}: {e.response.reason}"
            
            raise LimitlyError(
                error_message,
                e.response.status_code,
                error_data if 'error_data' in locals() else None
            )
            
        except requests.exceptions.RequestException as e:
            # Network error
            raise LimitlyError(
                f"Network error: {str(e)}",
                0,
                {"originalError": str(e)}
            )
    
    def get(self, endpoint: str, request_options: Optional[RequestOptions] = None) -> Dict[str, Any]:
        """
        Makes a GET request to the API
        
        Args:
            endpoint: The API endpoint
            request_options: Additional request options
            
        Returns:
            Response data as dictionary
        """
        return self._make_request("GET", endpoint, request_options=request_options)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        request_options: Optional[RequestOptions] = None
    ) -> Dict[str, Any]:
        """
        Makes a POST request to the API
        
        Args:
            endpoint: The API endpoint
            data: Request body data
            request_options: Additional request options
            
        Returns:
            Response data as dictionary
        """
        return self._make_request("POST", endpoint, data, request_options)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        request_options: Optional[RequestOptions] = None
    ) -> Dict[str, Any]:
        """
        Makes a PUT request to the API
        
        Args:
            endpoint: The API endpoint
            data: Request body data
            request_options: Additional request options
            
        Returns:
            Response data as dictionary
        """
        return self._make_request("PUT", endpoint, data, request_options)
    
    def delete(self, endpoint: str, request_options: Optional[RequestOptions] = None) -> Dict[str, Any]:
        """
        Makes a DELETE request to the API
        
        Args:
            endpoint: The API endpoint
            request_options: Additional request options
            
        Returns:
            Response data as dictionary
        """
        return self._make_request("DELETE", endpoint, request_options=request_options) 