"""
Module for managing API Keys
"""

from typing import Optional, Dict, Any
from ..client import HttpClient
from ..types import (
    ApiKey,
    CreateApiKeyRequest,
    UpdateApiKeyRequest,
    ApiKeyUsage,
    ApiKeyRequestsResponse,
    ApiResponse,
    PaginatedResponse,
    LimitInfo,
    RequestOptions,
)


class ApiKeysModule:
    """
    Module for managing API Keys
    """
    
    def __init__(self, client: HttpClient):
        """
        Initialize the API keys module
        
        Args:
            client: HTTP client instance
        """
        self.client = client
    
    def list(self, options: Optional[RequestOptions] = None) -> PaginatedResponse:
        """
        Lists all API Keys for the authenticated owner
        
        Args:
            options: Additional request options
            
        Returns:
            Paginated response with API keys
        """
        response = self.client.get("/keys", options)
        return PaginatedResponse(**response)
    
    def create(
        self,
        data: CreateApiKeyRequest,
        options: Optional[RequestOptions] = None
    ) -> ApiResponse:
        """
        Creates a new API Key
        
        Args:
            data: API key creation data
            options: Additional request options
            
        Returns:
            API response with created API key
        """
        response = self.client.post("/keys", data.__dict__, options)
        return ApiResponse(**response)
    
    def get(self, key_id: str, options: Optional[RequestOptions] = None) -> ApiResponse:
        """
        Gets a specific API Key by ID
        
        Args:
            key_id: The API key ID
            options: Additional request options
            
        Returns:
            API response with API key details
        """
        response = self.client.get(f"/keys/{key_id}", options)
        return ApiResponse(**response)
    
    def update(
        self,
        key_id: str,
        data: UpdateApiKeyRequest,
        options: Optional[RequestOptions] = None
    ) -> ApiResponse:
        """
        Updates an existing API Key
        
        Args:
            key_id: The API key ID
            data: Update data
            options: Additional request options
            
        Returns:
            API response with updated API key
        """
        response = self.client.put(f"/keys/{key_id}", data.__dict__, options)
        return ApiResponse(**response)
    
    def delete(self, key_id: str, options: Optional[RequestOptions] = None) -> ApiResponse:
        """
        Deletes an API Key (soft delete)
        
        Args:
            key_id: The API key ID
            options: Additional request options
            
        Returns:
            API response with deletion confirmation
        """
        response = self.client.delete(f"/keys/{key_id}", options)
        return ApiResponse(**response)
    
    def regenerate(self, key_id: str, options: Optional[RequestOptions] = None) -> ApiResponse:
        """
        Regenerates an existing API Key
        
        Args:
            key_id: The API key ID
            options: Additional request options
            
        Returns:
            API response with regenerated API key
        """
        response = self.client.post(f"/keys/{key_id}/regenerate", None, options)
        return ApiResponse(**response)
    
    def get_usage(self, key_id: str, options: Optional[RequestOptions] = None) -> ApiResponse:
        """
        Gets usage statistics for an API Key
        
        Args:
            key_id: The API key ID
            options: Additional request options
            
        Returns:
            API response with usage statistics
        """
        response = self.client.get(f"/keys/{key_id}/usage", options)
        return ApiResponse(**response)
    
    def get_requests(
        self,
        key_id: str,
        options: Optional[RequestOptions] = None
    ) -> ApiResponse:
        """
        Gets detailed request history for an API Key
        
        Args:
            key_id: The API key ID
            options: Additional request options
            
        Returns:
            API response with request history
        """
        response = self.client.get(f"/keys/{key_id}/requests", options)
        return ApiResponse(**response) 