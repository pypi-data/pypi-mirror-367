"""
Official Python SDK for Limitly - API Key management, plans, users and request validation.

This module provides a comprehensive interface to the Limitly API, allowing you to:
- Validate API requests and manage rate limiting
- Create and manage API keys
- Manage user accounts and their usage
- Create and configure usage plans
"""

from .client import HttpClient
from .modules.api_keys import ApiKeysModule
from .modules.plans import PlansModule
from .modules.users import UsersModule
from .modules.validation import ValidationModule
from .types import LimitlyConfig


class Limitly:
    """
    Main Limitly SDK client
    
    Example:
        ```python
        from limitly import Limitly
        
        limitly = Limitly(api_key="your_limitly_api_key")
        
        # Validate a request
        result = await limitly.validation.validate(
            "user_api_key",
            "/api/users",
            "GET"
        )
        
        if result.success:
            print("Request allowed")
        else:
            print(f"Request denied: {result.error}")
        ```
    """
    
    def __init__(self, api_key: str, base_url: str = None, timeout: int = 30):
        """
        Initialize the Limitly client
        
        Args:
            api_key: Your Limitly API key
            base_url: Custom base URL for the API (optional)
            timeout: Request timeout in seconds (default: 30)
        """
        config = LimitlyConfig(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout
        )
        
        self._client = HttpClient(config)
        
        # Initialize modules
        self.api_keys = ApiKeysModule(self._client)
        self.plans = PlansModule(self._client)
        self.users = UsersModule(self._client)
        self.validation = ValidationModule(self._client)
    
    def get_client(self) -> HttpClient:
        """
        Gets the internal HTTP client
        Useful for debugging and testing
        """
        return self._client


# Export main classes and types
__all__ = [
    "Limitly",
    "HttpClient",
    "ApiKeysModule",
    "PlansModule", 
    "UsersModule",
    "ValidationModule",
    "LimitlyConfig",
    "LimitlyError",
    "ApiResponse",
    "PaginatedResponse",
    "ApiKey",
    "CreateApiKeyRequest",
    "UpdateApiKeyRequest",
    "ApiKeyUsage",
    "ApiKeyRequestsResponse",
    "LimitInfo",
    "Plan",
    "CreatePlanRequest",
    "UpdatePlanRequest",
    "PlanUsage",
    "PlanUsersResponse",
    "PlanKeysResponse",
    "User",
    "CreateUserRequest",
    "UpdateUserRequest",
    "UserUsage",
    "ValidateRequestRequest",
    "ValidateRequestResponse",
    "RequestOptions",
]

# Import types for easier access
from .types import (
    LimitlyConfig,
    LimitlyError,
    ApiResponse,
    PaginatedResponse,
    ApiKey,
    CreateApiKeyRequest,
    UpdateApiKeyRequest,
    ApiKeyUsage,
    ApiKeyRequestsResponse,
    LimitInfo,
    Plan,
    CreatePlanRequest,
    UpdatePlanRequest,
    PlanUsage,
    PlanUsersResponse,
    PlanKeysResponse,
    User,
    CreateUserRequest,
    UpdateUserRequest,
    UserUsage,
    ValidateRequestRequest,
    ValidateRequestResponse,
    RequestOptions,
)

# Import modules for easier access
from .modules.api_keys import ApiKeysModule
from .modules.plans import PlansModule
from .modules.users import UsersModule
from .modules.validation import ValidationModule
from .client import HttpClient

# Import version
from .version import __version__ 