"""
Module for validating requests
"""

from typing import Optional, Dict, Any
from ..client import HttpClient
from ..types import (
    ValidateRequestRequest,
    ValidateRequestResponse,
    RequestOptions,
)


class ValidationModule:
    """
    Module for validating requests
    """
    
    def __init__(self, client: HttpClient):
        """
        Initialize the validation module
        
        Args:
            client: HTTP client instance
        """
        self.client = client
    
    def validate_request(
        self,
        data: ValidateRequestRequest,
        options: Optional[RequestOptions] = None
    ) -> ValidateRequestResponse:
        """
        Validates a user request using their API Key
        
        Args:
            data: Request validation data
            options: Additional request options
            
        Returns:
            Validation response
        """
        response = self.client.post("/validate", data.__dict__, options)
        return ValidateRequestResponse(**response)
    
    def validate(
        self,
        api_key: str,
        endpoint: str,
        method: str,
        options: Optional[RequestOptions] = None
    ) -> ValidateRequestResponse:
        """
        Convenience method to validate a request with individual parameters
        
        Args:
            api_key: The API key to validate
            endpoint: The endpoint being accessed
            method: The HTTP method being used
            options: Additional request options
            
        Returns:
            Validation response
        """
        return self.validate_request(
            ValidateRequestRequest(
                api_key=api_key,
                endpoint=endpoint,
                method=method
            ),
            options
        ) 