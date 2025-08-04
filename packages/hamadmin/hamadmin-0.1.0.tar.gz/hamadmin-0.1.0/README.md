# HamAdmin

A collection of utilities and middleware for various frameworks.

## Installation

### Core Package
```bash
pip install hamadmin
```

### Django Components
```bash
pip install hamadmin[django]
```

## Components

### Django Components

#### JWT Admin Guard Middleware
Protects Django admin routes with JWT authentication.

**Usage:**
```python
# In your Django settings.py
MIDDLEWARE = [
    # ... other middleware
    'hamadmin.django.middleware.HamAdminJWTGuard',
]

# Required settings
OAUTH_JWKS_URL = 'https://your-auth-provider.com/.well-known/jwks.json'
ADMIN_URL = 'admin'  # or whatever your admin URL is

# Optional settings
HAMADMIN_JWT_LEEWAY = 10  # JWT time leeway in seconds
HAMADMIN_AUTH_HEADER = 'HTTP_X_ADMIN_ACCESS_TOKEN'  # Custom auth header name
HAMADMIN_CREATE_USER_FUNC = 'myapp.utils.create_admin_user'  # Custom user creation function
HAMADMIN_USER_IDENTIFIER = 'sub'  # Use 'sub' claim instead of 'email'
```

**Import:**
```python
from hamadmin.django.middleware import HamAdminJWTGuard
from hamadmin.django.utils import import_from_settings
from hamadmin.django import HamAdminJWTGuard, import_from_settings
```

## Future Components

This package is designed to accommodate additional HamAdmin utilities and components for other frameworks as needed. 