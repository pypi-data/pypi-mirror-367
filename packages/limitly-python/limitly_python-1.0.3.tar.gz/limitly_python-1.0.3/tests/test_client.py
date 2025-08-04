"""
Tests for the HTTP client
"""

import pytest
from unittest.mock import Mock, patch
from limitly.client import HttpClient
from limitly.types import LimitlyConfig, LimitlyError


class TestHttpClient:
    """Test cases for HttpClient"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = LimitlyConfig(
            api_key="test_api_key",
            base_url="https://test.example.com",
            timeout=30
        )
        self.client = HttpClient(self.config)
    
    def test_init(self):
        """Test HttpClient initialization"""
        assert self.client.api_key == "test_api_key"
        assert self.client.base_url == "https://test.example.com"
        assert self.client.timeout == 30
    
    def test_init_defaults(self):
        """Test HttpClient initialization with defaults"""
        config = LimitlyConfig(api_key="test_key")
        client = HttpClient(config)
        
        assert client.api_key == "test_key"
        assert client.base_url == "https://xfkyofkqbukqtxcuapvf.supabase.co/functions/v1"
        assert client.timeout == 30
    
    @patch('requests.get')
    def test_get_success(self, mock_get):
        """Test successful GET request"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "data": "test"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.get("/test")
        
        assert result == {"success": True, "data": "test"}
        mock_get.assert_called_once()
    
    @patch('requests.post')
    def test_post_success(self, mock_post):
        """Test successful POST request"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "data": "created"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        data = {"name": "test"}
        result = self.client.post("/test", data)
        
        assert result == {"success": True, "data": "created"}
        mock_post.assert_called_once()
    
    @patch('requests.get')
    def test_get_http_error(self, mock_get):
        """Test GET request with HTTP error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        mock_response.json.return_value = {"error": "Resource not found"}
        
        mock_get.side_effect = requests.exceptions.HTTPError(response=mock_response)
        
        with pytest.raises(LimitlyError) as exc_info:
            self.client.get("/test")
        
        assert exc_info.value.status_code == 404
        assert "Resource not found" in exc_info.value.message
    
    @patch('requests.get')
    def test_get_network_error(self, mock_get):
        """Test GET request with network error"""
        mock_get.side_effect = requests.exceptions.RequestException("Connection failed")
        
        with pytest.raises(LimitlyError) as exc_info:
            self.client.get("/test")
        
        assert exc_info.value.status_code == 0
        assert "Network error" in exc_info.value.message
    
    def test_unsupported_method(self):
        """Test unsupported HTTP method"""
        with pytest.raises(LimitlyError) as exc_info:
            self.client._make_request("PATCH", "/test")
        
        assert "Unsupported HTTP method" in exc_info.value.message


if __name__ == "__main__":
    pytest.main([__file__]) 