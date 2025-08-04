#!/usr/bin/env python3
"""
Command Line Interface for the Limitly Python SDK
"""

import asyncio
import argparse
import os
import sys
from typing import Optional
from . import Limitly, LimitlyError


async def validate_request(api_key: str, endpoint: str, method: str, limitly_api_key: str):
    """Validate a request using the Limitly API"""
    try:
        limitly = Limitly(api_key=limitly_api_key)
        result = await limitly.validation.validate(api_key, endpoint, method)
        
        if result.success:
            print("✅ Request allowed")
            if result.details:
                print(f"Current usage: {result.details.current_usage}")
                print(f"Limit: {result.details.limit}")
                print(f"Plan: {result.details.plan_name}")
        else:
            print(f"❌ Request denied: {result.error}")
            return 1
    except LimitlyError as e:
        print(f"❌ Error: {e.message}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0


async def list_api_keys(limitly_api_key: str):
    """List all API keys"""
    try:
        limitly = Limitly(api_key=limitly_api_key)
        keys = await limitly.api_keys.list()
        
        print(f"Found {keys.count or 0} API Keys:")
        if keys.data:
            for key in keys.data:
                print(f"  - {key.name} (ID: {key.id}, Status: {key.status})")
        else:
            print("  No API keys found")
    except LimitlyError as e:
        print(f"❌ Error: {e.message}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0


async def create_api_key(name: str, user_id: Optional[int], limitly_api_key: str):
    """Create a new API key"""
    try:
        limitly = Limitly(api_key=limitly_api_key)
        from . import CreateApiKeyRequest
        
        data = CreateApiKeyRequest(name=name, user_id=user_id)
        result = await limitly.api_keys.create(data)
        
        if result.success and result.data:
            print("✅ API Key created successfully")
            print(f"Name: {result.data.name}")
            print(f"ID: {result.data.id}")
            if result.data.api_key:
                print(f"API Key: {result.data.api_key}")
        else:
            print(f"❌ Failed to create API key: {result.error}")
            return 1
    except LimitlyError as e:
        print(f"❌ Error: {e.message}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0


async def list_plans(limitly_api_key: str):
    """List all plans"""
    try:
        limitly = Limitly(api_key=limitly_api_key)
        plans = await limitly.plans.list()
        
        print(f"Found {plans.count or 0} Plans:")
        if plans.data:
            for plan in plans.data:
                print(f"  - {plan.name} (ID: {plan.id}, Limit: {plan.max_requests} requests/{plan.request_period})")
        else:
            print("  No plans found")
    except LimitlyError as e:
        print(f"❌ Error: {e.message}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0


async def create_plan(name: str, description: str, max_requests: int, request_period: str, limitly_api_key: str):
    """Create a new plan"""
    try:
        limitly = Limitly(api_key=limitly_api_key)
        from . import CreatePlanRequest
        
        data = CreatePlanRequest(
            name=name,
            description=description,
            max_requests=max_requests,
            request_period=request_period
        )
        result = await limitly.plans.create(data)
        
        if result.success and result.data:
            print("✅ Plan created successfully")
            print(f"Name: {result.data.name}")
            print(f"ID: {result.data.id}")
            print(f"Limit: {result.data.max_requests} requests/{result.data.request_period}")
        else:
            print(f"❌ Failed to create plan: {result.error}")
            return 1
    except LimitlyError as e:
        print(f"❌ Error: {e.message}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Limitly Python SDK CLI")
    parser.add_argument("--api-key", help="Your Limitly API key", default=os.getenv("LIMITLY_API_KEY"))
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a request")
    validate_parser.add_argument("user_api_key", help="User API key to validate")
    validate_parser.add_argument("endpoint", help="Endpoint being accessed")
    validate_parser.add_argument("method", help="HTTP method", choices=["GET", "POST", "PUT", "DELETE"])
    
    # List API keys command
    list_keys_parser = subparsers.add_parser("list-keys", help="List all API keys")
    
    # Create API key command
    create_key_parser = subparsers.add_parser("create-key", help="Create a new API key")
    create_key_parser.add_argument("name", help="Name for the API key")
    create_key_parser.add_argument("--user-id", type=int, help="User ID to associate with the key")
    
    # List plans command
    list_plans_parser = subparsers.add_parser("list-plans", help="List all plans")
    
    # Create plan command
    create_plan_parser = subparsers.add_parser("create-plan", help="Create a new plan")
    create_plan_parser.add_argument("name", help="Name for the plan")
    create_plan_parser.add_argument("description", help="Description for the plan")
    create_plan_parser.add_argument("max_requests", type=int, help="Maximum number of requests")
    create_plan_parser.add_argument("request_period", help="Request period", choices=["day", "week", "month", "year"])
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("❌ Error: LIMITLY_API_KEY environment variable or --api-key argument is required")
        sys.exit(1)
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Run the appropriate command
    if args.command == "validate":
        exit_code = asyncio.run(validate_request(args.user_api_key, args.endpoint, args.method, args.api_key))
    elif args.command == "list-keys":
        exit_code = asyncio.run(list_api_keys(args.api_key))
    elif args.command == "create-key":
        exit_code = asyncio.run(create_api_key(args.name, args.user_id, args.api_key))
    elif args.command == "list-plans":
        exit_code = asyncio.run(list_plans(args.api_key))
    elif args.command == "create-plan":
        exit_code = asyncio.run(create_plan(args.name, args.description, args.max_requests, args.request_period, args.api_key))
    else:
        print(f"❌ Unknown command: {args.command}")
        sys.exit(1)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 