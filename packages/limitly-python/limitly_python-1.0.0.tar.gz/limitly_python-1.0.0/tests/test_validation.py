"""
Tests for the validation module
"""

import pytest
from unittest.mock import Mock, patch
from limitly.modules.validation import ValidationModule
from limitly.types import (
    ValidateRequestRequest,
    ValidateRequestResponse,
    ValidationDetails,
    RequestOptions
)


class TestValidationModule:
    """Test cases for ValidationModule"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.validation = ValidationModule(self.mock_client)
    
    def test_init(self):
        """Test ValidationModule initialization"""
        assert self.validation.client == self.mock_client
    
    def test_validate_request(self):
        """Test validate_request method"""
        # Mock response
        mock_response = {
            "success": True,
            "message": "Request allowed",
            "details": {
                "current_usage": 5,
                "limit": 100,
                "plan_name": "Basic Plan",
                "period_start": "2024-01-01T00:00:00Z",
                "period_end": "2024-02-01T00:00:00Z"
            }
        }
        self.mock_client.post.return_value = mock_response
        
        # Test data
        request_data = ValidateRequestRequest(
            api_key="test_key",
            endpoint="/api/users",
            method="GET"
        )
        
        result = self.validation.validate_request(request_data)
        
        # Verify client was called correctly
        self.mock_client.post.assert_called_once_with(
            "/validate",
            request_data.__dict__,
            None
        )
        
        # Verify result
        assert isinstance(result, ValidateRequestResponse)
        assert result.success is True
        assert result.message == "Request allowed"
        assert result.details is not None
        assert result.details.current_usage == 5
        assert result.details.limit == 100
        assert result.details.plan_name == "Basic Plan"
    
    def test_validate_request_with_options(self):
        """Test validate_request method with options"""
        mock_response = {"success": True}
        self.mock_client.post.return_value = mock_response
        
        request_data = ValidateRequestRequest(
            api_key="test_key",
            endpoint="/api/users",
            method="GET"
        )
        options = RequestOptions(timeout=10)
        
        result = self.validation.validate_request(request_data, options)
        
        self.mock_client.post.assert_called_once_with(
            "/validate",
            request_data.__dict__,
            options
        )
        assert result.success is True
    
    def test_validate(self):
        """Test validate convenience method"""
        mock_response = {
            "success": False,
            "error": "Rate limit exceeded"
        }
        self.mock_client.post.return_value = mock_response
        
        result = self.validation.validate(
            "test_key",
            "/api/users",
            "GET"
        )
        
        # Verify the request data was created correctly
        call_args = self.mock_client.post.call_args
        request_data = call_args[0][1]  # Second argument is the data
        
        assert request_data["api_key"] == "test_key"
        assert request_data["endpoint"] == "/api/users"
        assert request_data["method"] == "GET"
        
        # Verify result
        assert isinstance(result, ValidateRequestResponse)
        assert result.success is False
        assert result.error == "Rate limit exceeded"
    
    def test_validate_with_options(self):
        """Test validate method with options"""
        mock_response = {"success": True}
        self.mock_client.post.return_value = mock_response
        
        options = RequestOptions(
            timeout=15,
            headers={"X-Custom-Header": "value"}
        )
        
        result = self.validation.validate(
            "test_key",
            "/api/users",
            "POST",
            options
        )
        
        # Verify options were passed correctly
        call_args = self.mock_client.post.call_args
        passed_options = call_args[0][2]  # Third argument is options
        
        assert passed_options == options
        assert result.success is True


if __name__ == "__main__":
    pytest.main([__file__]) 