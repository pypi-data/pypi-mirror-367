"""
Module for managing Plans
"""

from typing import Optional, Dict, Any
from ..client import HttpClient
from ..types import (
    Plan,
    CreatePlanRequest,
    UpdatePlanRequest,
    PlanUsage,
    PlanUsersResponse,
    PlanKeysResponse,
    ApiResponse,
    PaginatedResponse,
    RequestOptions,
)


class PlansModule:
    """
    Module for managing Plans
    """
    
    def __init__(self, client: HttpClient):
        """
        Initialize the plans module
        
        Args:
            client: HTTP client instance
        """
        self.client = client
    
    def list(self, options: Optional[RequestOptions] = None) -> PaginatedResponse:
        """
        Lists all plans for the client
        
        Args:
            options: Additional request options
            
        Returns:
            Paginated response with plans
        """
        response = self.client.get("/plans", options)
        return PaginatedResponse(**response)
    
    def create(
        self,
        data: CreatePlanRequest,
        options: Optional[RequestOptions] = None
    ) -> ApiResponse:
        """
        Creates a new plan
        
        Args:
            data: Plan creation data
            options: Additional request options
            
        Returns:
            API response with created plan
        """
        response = self.client.post("/plans", data.__dict__, options)
        return ApiResponse(**response)
    
    def get(self, plan_id: str, options: Optional[RequestOptions] = None) -> ApiResponse:
        """
        Gets a specific plan by ID
        
        Args:
            plan_id: The plan ID
            options: Additional request options
            
        Returns:
            API response with plan details
        """
        response = self.client.get(f"/plans/{plan_id}", options)
        return ApiResponse(**response)
    
    def update(
        self,
        plan_id: str,
        data: UpdatePlanRequest,
        options: Optional[RequestOptions] = None
    ) -> ApiResponse:
        """
        Updates an existing plan
        
        Args:
            plan_id: The plan ID
            data: Update data
            options: Additional request options
            
        Returns:
            API response with updated plan
        """
        response = self.client.put(f"/plans/{plan_id}", data.__dict__, options)
        return ApiResponse(**response)
    
    def delete(self, plan_id: str, options: Optional[RequestOptions] = None) -> ApiResponse:
        """
        Deletes a plan
        
        Args:
            plan_id: The plan ID
            options: Additional request options
            
        Returns:
            API response with deletion confirmation
        """
        response = self.client.delete(f"/plans/{plan_id}", options)
        return ApiResponse(**response)
    
    def get_usage(self, plan_id: str, options: Optional[RequestOptions] = None) -> ApiResponse:
        """
        Gets usage statistics for a plan
        
        Args:
            plan_id: The plan ID
            options: Additional request options
            
        Returns:
            API response with usage statistics
        """
        response = self.client.get(f"/plans/{plan_id}/usage", options)
        return ApiResponse(**response)
    
    def get_users(self, plan_id: str, options: Optional[RequestOptions] = None) -> ApiResponse:
        """
        Gets all users assigned to a plan
        
        Args:
            plan_id: The plan ID
            options: Additional request options
            
        Returns:
            API response with plan users
        """
        response = self.client.get(f"/plans/{plan_id}/users", options)
        return ApiResponse(**response)
    
    def get_keys(self, plan_id: str, options: Optional[RequestOptions] = None) -> ApiResponse:
        """
        Gets all API Keys directly assigned to a plan
        
        Args:
            plan_id: The plan ID
            options: Additional request options
            
        Returns:
            API response with plan API keys
        """
        response = self.client.get(f"/plans/{plan_id}/keys", options)
        return ApiResponse(**response) 