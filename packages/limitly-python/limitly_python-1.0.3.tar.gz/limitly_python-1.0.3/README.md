# limitly-python

Official Python SDK for [Limitly](https://www.limitly.dev) - API Key management, plans, users and request validation.

## 🚀 Installation

```bash
pip install limitly-python
```

```bash
poetry add limitly-python
```

```bash
pipenv install limitly-python
```

## 📖 Basic Usage

### Initialization

```python
from limitly import Limitly

limitly = Limitly(api_key="your_limitly_api_key")
```

### Request Validation

The most common use case is validating your users' requests:

```python
# Validate a request
result = await limitly.validation.validate(
    "user_api_key",
    "/api/users",
    "GET"
)

if result.success:
    print("Request allowed")
    print(f"Current usage: {result.details.current_usage}")
    print(f"Limit: {result.details.limit}")
else:
    print(f"Request denied: {result.error}")
```

### API Key Management

```python
# List all API Keys
keys = await limitly.api_keys.list()
print(f"API Keys: {keys.data}")

# Create a new API Key
new_key = await limitly.api_keys.create(
    name="New API Key",
    user_id=123
)
print(f"New API Key: {new_key.data.api_key}")

# Get usage for an API Key
usage = await limitly.api_keys.get_usage("key-id")
print(f"Usage: {usage.data}")
```

### Plan Management

```python
# Create a plan
plan = await limitly.plans.create(
    name="Basic Plan",
    description="Plan for basic users",
    max_requests=10000,
    request_period="month"
)

# Get plan usage statistics
plan_usage = await limitly.plans.get_usage(plan.data.id)
print(f"Plan usage: {plan_usage.data}")
```

### User Management

```python
# Create a user
user = await limitly.users.create(
    name="John Doe",
    email="john@example.com",
    plan_id="plan-id"
)

# Get user usage
user_usage = await limitly.users.get_usage(user.data.user_id)
print(f"User usage: {user_usage.data}")
```

## 🔧 Configuration

### Configuration Options

```python
from limitly import Limitly

limitly = Limitly(
    api_key="your_limitly_api_key",
    base_url="https://your-project.supabase.co/functions/v1",  # optional
    timeout=30  # optional, default: 30 seconds
)
```

### Request Options

You can pass additional options to any method:

```python
result = await limitly.api_keys.list(
    timeout=10,
    headers={"X-Custom-Header": "value"}
)
```

## 📚 Complete API

### Request Validation

#### `validation.validate(api_key, endpoint, method, options=None)`
Validates a user request.

```python
result = await limitly.validation.validate(
    "user_api_key",
    "/api/users",
    "GET"
)
```

#### `validation.validate_request(data, options=None)`
Validates a request with data object.

```python
result = await limitly.validation.validate_request({
    "api_key": "user_api_key",
    "endpoint": "/api/users",
    "method": "GET"
})
```

### API Keys

#### `api_keys.list(options=None)`
Lists all API Keys.

#### `api_keys.create(data, options=None)`
Creates a new API Key.

```python
key = await limitly.api_keys.create({
    "name": "New API Key",
    "user_id": 123,  # optional
    "plan_id": "plan-id",  # optional
    "status": "active"  # optional
})
```

#### `api_keys.get(key_id, options=None)`
Gets a specific API Key.

#### `api_keys.update(key_id, data, options=None)`
Updates an API Key.

#### `api_keys.delete(key_id, options=None)`
Deletes an API Key (soft delete).

#### `api_keys.regenerate(key_id, options=None)`
Regenerates an API Key.

#### `api_keys.get_usage(key_id, options=None)`
Gets usage statistics for an API Key.

#### `api_keys.get_requests(key_id, options=None)`
Gets request history for an API Key.

### Plans

#### `plans.list(options=None)`
Lists all plans.

#### `plans.create(data, options=None)`
Creates a new plan.

```python
plan = await limitly.plans.create({
    "name": "Basic Plan",
    "description": "Plan for basic users",
    "max_requests": 10000,
    "request_period": "month",  # 'day', 'week', 'month', 'year'
    "is_active": True
})
```

#### `plans.get(plan_id, options=None)`
Gets a specific plan.

#### `plans.update(plan_id, data, options=None)`
Updates a plan.

#### `plans.delete(plan_id, options=None)`
Deletes a plan.

#### `plans.get_usage(plan_id, options=None)`
Gets usage statistics for a plan.

#### `plans.get_users(plan_id, options=None)`
Gets all users assigned to a plan.

#### `plans.get_keys(plan_id, options=None)`
Gets all API Keys assigned to a plan.

### Users

#### `users.list(options=None)`
Lists all users.

#### `users.create(data, options=None)`
Creates a new user.

```python
user = await limitly.users.create({
    "name": "John Doe",
    "email": "john@example.com",  # optional
    "plan_id": "plan-id",  # optional
    "custom_start": "2024-01-01T00:00:00.000Z"  # optional
})
```

#### `users.get(user_id, options=None)`
Gets a specific user.

#### `users.update(user_id, data, options=None)`
Updates a user.

#### `users.delete(user_id, options=None)`
Deletes a user.

#### `users.get_usage(user_id, options=None)`
Gets user usage.

#### `users.get_keys(user_id, options=None)`
Gets all API Keys for a user.

#### `users.create_key(user_id, data, options=None)`
Creates a new API Key for a user.

```python
key = await limitly.users.create_key(123, {
    "name": "API Key for John"
})
```

## 🛠️ Error Handling

The SDK throws specific errors that you can catch:

```python
from limitly import Limitly, LimitlyError

try:
    result = await limitly.validation.validate(
        "invalid_api_key",
        "/api/users",
        "GET"
    )
except LimitlyError as error:
    print(f"Limitly error: {error.message}")
    print(f"Status code: {error.status_code}")
    print(f"Full response: {error.response}")
except Exception as error:
    print(f"Unexpected error: {error}")
```

## 🔍 Advanced Examples

### FastAPI Middleware

```python
from fastapi import FastAPI, HTTPException, Request
from limitly import Limitly

app = FastAPI()
limitly = Limitly(api_key=os.getenv("LIMITLY_API_KEY"))

@app.middleware("http")
async def limitly_middleware(request: Request, call_next):
    api_key = request.headers.get("authorization", "").replace("Bearer ", "")
    
    if not api_key:
        raise HTTPException(status_code=401, detail="API Key required")
    
    try:
        result = await limitly.validation.validate(
            api_key,
            request.url.path,
            request.method
        )
        
        if not result.success:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "details": result.details
                }
            )
        
        response = await call_next(request)
        return response
    except LimitlyError as error:
        print(f"Validation error: {error}")
        raise HTTPException(status_code=500, detail="Internal error")
```

### Usage Monitoring

```python
# Monitor API Key usage
async def monitor_usage():
    keys = await limitly.api_keys.list()
    
    for key in keys.data or []:
        usage = await limitly.api_keys.get_usage(key.id)
        
        if usage.data and usage.data.percentage_used > 80:
            print(f"⚠️ API Key {key.name} is at {usage.data.percentage_used}% usage")
```

### Automatic Plan Management

```python
# Create predefined plans
async def setup_default_plans():
    plans = [
        {
            "name": "Basic Plan",
            "description": "For new users",
            "max_requests": 1000,
            "request_period": "month"
        },
        {
            "name": "Pro Plan",
            "description": "For advanced users",
            "max_requests": 10000,
            "request_period": "month"
        },
        {
            "name": "Enterprise Plan",
            "description": "Unlimited",
            "max_requests": -1,
            "request_period": "month"
        }
    ]
    
    for plan_data in plans:
        await limitly.plans.create(plan_data)
```

## 📦 Project Structure

```
src/limitly/
├── __init__.py          # Main SDK class
├── client.py            # Base HTTP client
├── types.py             # Type definitions
└── modules/             # Specific modules
    ├── __init__.py
    ├── api_keys.py
    ├── plans.py
    ├── users.py
    └── validation.py
```

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 🆘 Support

- 📧 Email: hi@limitly.dev
- 💻 Limitly: https://www.limitly.dev
- 📖 Documentation: https://docs.limitly.com
- 🐛 Issues: https://github.com/limitlydev/limitly-python/issues 