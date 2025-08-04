"""
Module for managing Users
"""

from typing import Optional, Dict, Any
from ..client import HttpClient
from ..types import (
    User,
    CreateUserRequest,
    UpdateUserRequest,
    UserUsage,
    ApiKey,
    ApiResponse,
    PaginatedResponse,
    RequestOptions,
)


class UsersModule:
    """
    Module for managing Users
    """
    
    def __init__(self, client: HttpClient):
        """
        Initialize the users module
        
        Args:
            client: HTTP client instance
        """
        self.client = client
    
    def list(self, options: Optional[RequestOptions] = None) -> PaginatedResponse:
        """
        Lists all users for the client
        
        Args:
            options: Additional request options
            
        Returns:
            Paginated response with users
        """
        response = self.client.get("/users", options)
        return PaginatedResponse(**response)
    
    def create(
        self,
        data: CreateUserRequest,
        options: Optional[RequestOptions] = None
    ) -> ApiResponse:
        """
        Creates a new user
        
        Args:
            data: User creation data
            options: Additional request options
            
        Returns:
            API response with created user
        """
        response = self.client.post("/users", data.__dict__, options)
        return ApiResponse(**response)
    
    def get(self, user_id: int, options: Optional[RequestOptions] = None) -> ApiResponse:
        """
        Gets a specific user by ID
        
        Args:
            user_id: The user ID
            options: Additional request options
            
        Returns:
            API response with user details
        """
        response = self.client.get(f"/users/{user_id}", options)
        return ApiResponse(**response)
    
    def update(
        self,
        user_id: int,
        data: UpdateUserRequest,
        options: Optional[RequestOptions] = None
    ) -> ApiResponse:
        """
        Updates an existing user
        
        Args:
            user_id: The user ID
            data: Update data
            options: Additional request options
            
        Returns:
            API response with updated user
        """
        response = self.client.put(f"/users/{user_id}", data.__dict__, options)
        return ApiResponse(**response)
    
    def delete(self, user_id: int, options: Optional[RequestOptions] = None) -> ApiResponse:
        """
        Deletes a user
        
        Args:
            user_id: The user ID
            options: Additional request options
            
        Returns:
            API response with deletion confirmation
        """
        response = self.client.delete(f"/users/{user_id}", options)
        return ApiResponse(**response)
    
    def get_usage(self, user_id: int, options: Optional[RequestOptions] = None) -> ApiResponse:
        """
        Gets usage for a specific user
        
        Args:
            user_id: The user ID
            options: Additional request options
            
        Returns:
            API response with user usage
        """
        response = self.client.get(f"/users/{user_id}/usage", options)
        return ApiResponse(**response)
    
    def get_keys(self, user_id: int, options: Optional[RequestOptions] = None) -> PaginatedResponse:
        """
        Gets all API Keys assigned to a specific user
        
        Args:
            user_id: The user ID
            options: Additional request options
            
        Returns:
            Paginated response with user API keys
        """
        response = self.client.get(f"/users/{user_id}/keys", options)
        return PaginatedResponse(**response)
    
    def create_key(
        self,
        user_id: int,
        data: Dict[str, str],
        options: Optional[RequestOptions] = None
    ) -> ApiResponse:
        """
        Creates a new API Key for a specific user
        
        Args:
            user_id: The user ID
            data: API key creation data (must contain 'name')
            options: Additional request options
            
        Returns:
            API response with created API key
        """
        response = self.client.post(f"/users/{user_id}/keys", data, options)
        return ApiResponse(**response) 