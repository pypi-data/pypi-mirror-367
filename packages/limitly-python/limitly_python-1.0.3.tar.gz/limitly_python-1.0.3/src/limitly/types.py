"""
Type definitions for the Limitly Python SDK
"""

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LimitlyConfig:
    """Configuration for the Limitly client"""
    api_key: str
    base_url: Optional[str] = None
    timeout: int = 30


@dataclass
class RequestOptions:
    """Options for API requests"""
    timeout: Optional[int] = None
    headers: Optional[Dict[str, str]] = None


# Base response types
@dataclass
class ApiResponse:
    """Base API response"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


@dataclass
class PaginatedResponse:
    """Paginated API response"""
    success: bool
    data: Optional[List[Any]] = None
    count: Optional[int] = None
    error: Optional[str] = None
    message: Optional[str] = None


# API Keys types
@dataclass
class ApiKey:
    """API Key information"""
    id: str
    name: str
    status: str  # 'active' | 'inactive'
    created_at: str
    api_key: Optional[str] = None  # Only included in creation/regeneration
    last_used_at: Optional[str] = None
    user_id: Optional[int] = None
    plan_id: Optional[str] = None
    user: Optional['User'] = None
    plan: Optional['Plan'] = None


@dataclass
class CreateApiKeyRequest:
    """Request to create an API Key"""
    name: str
    user_id: Optional[int] = None
    plan_id: Optional[str] = None
    status: Optional[str] = None  # 'active' | 'inactive'


@dataclass
class UpdateApiKeyRequest:
    """Request to update an API Key"""
    name: Optional[str] = None
    user_id: Optional[int] = None
    plan_id: Optional[str] = None
    status: Optional[str] = None  # 'active' | 'inactive'


@dataclass
class ApiKeyUsage:
    """API Key usage statistics"""
    apiKeyId: str
    apiKeyName: str
    created_at: str
    periodStart: str
    periodEnd: str
    totalRequests: int
    requestsInPeriod: int
    percentageUsed: float
    limit: int
    planName: str
    isUnlimited: bool


@dataclass
class ApiKeyRequest:
    """Individual API Key request"""
    api_key_id: str
    created_at: str
    endpoint: str
    method: str
    status_code: int
    response_time_ms: int


@dataclass
class ApiKeyRequestsResponse:
    """API Key requests history"""
    apiKeyId: str
    apiKeyName: str
    created_at: str
    periodStart: str
    periodEnd: str
    totalRequests: int
    requestsInPeriod: int
    requestsInPeriodDetails: List[ApiKeyRequest]


@dataclass
class LimitInfo:
    """Information about API Key limits"""
    can_create: bool
    current_count: int
    max_allowed: int
    remaining_keys: int
    plan_type: str


# Plans types
@dataclass
class Plan:
    """Plan information"""
    id: str
    owner_id: str
    name: str
    max_requests: int
    request_period: str  # 'day' | 'week' | 'month' | 'year'
    is_active: bool
    created_at: str
    updated_at: str
    description: Optional[str] = None


@dataclass
class CreatePlanRequest:
    """Request to create a plan"""
    name: str
    max_requests: int
    request_period: str  # 'day' | 'week' | 'month' | 'year'
    description: Optional[str] = None
    is_active: Optional[bool] = None


@dataclass
class UpdatePlanRequest:
    """Request to update a plan"""
    name: Optional[str] = None
    description: Optional[str] = None
    max_requests: Optional[int] = None
    request_period: Optional[str] = None  # 'day' | 'week' | 'month' | 'year'
    is_active: Optional[bool] = None


@dataclass
class PlanUsage:
    """Plan usage statistics"""
    plan_id: str
    plan_name: str
    max_requests: int
    request_period: str
    total_requests: int
    percentage_used: float
    users_count: int
    api_keys_count: int
    is_unlimited: bool


@dataclass
class PlanUsersResponse:
    """Plan users response"""
    plan: Plan
    users: List['User']


@dataclass
class PlanKeysResponse:
    """Plan API keys response"""
    plan: Plan
    api_keys: List[ApiKey]


# Users types
@dataclass
class User:
    """User information"""
    user_id: int
    name: str
    is_disabled: bool
    created_at: str
    updated_at: str
    email: Optional[str] = None
    custom_start: Optional[str] = None
    plan: Optional[Plan] = None


@dataclass
class CreateUserRequest:
    """Request to create a user"""
    name: str
    email: Optional[str] = None
    plan_id: Optional[str] = None
    custom_start: Optional[str] = None


@dataclass
class UpdateUserRequest:
    """Request to update a user"""
    name: Optional[str] = None
    email: Optional[str] = None
    is_disabled: Optional[bool] = None
    plan_id: Optional[str] = None
    custom_start: Optional[str] = None


@dataclass
class UserUsage:
    """User usage statistics"""
    type: str  # 'user'
    user_name: str
    current_usage: Optional[int] = None
    limit: Optional[int] = None
    percentage_used: Optional[float] = None
    plan_name: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    is_unlimited: Optional[bool] = None


# Request validation types
@dataclass
class ValidateRequestRequest:
    """Request to validate an API request"""
    api_key: str
    endpoint: str
    method: str


@dataclass
class ValidateRequestResponse:
    """Response from request validation"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    details: Optional['ValidationDetails'] = None


@dataclass
class ValidationDetails:
    """Details from request validation"""
    current_usage: int
    limit: int
    plan_name: str
    period_start: str
    period_end: str


# Error types
class LimitlyError(Exception):
    """Custom exception for Limitly API errors"""
    
    def __init__(self, message: str, status_code: int = 0, response: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response
        self.name = 'LimitlyError'


# Type aliases for backward compatibility
ApiResponseType = ApiResponse
PaginatedResponseType = PaginatedResponse 