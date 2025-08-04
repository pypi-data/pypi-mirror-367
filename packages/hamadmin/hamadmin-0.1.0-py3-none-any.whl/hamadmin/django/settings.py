"""
Default settings for hamadmin_middleware
"""

# Required settings that must be defined in your Django settings
REQUIRED_SETTINGS = [
    'HAMADMIN_OAUTH_JWKS_URL',  # URL to fetch JWKS (JSON Web Key Set)
    'ADMIN_URL',       # Admin URL path (e.g., 'admin' or 'django-admin')
]

# Optional settings with defaults
DEFAULT_SETTINGS = {
    'HAMADMIN_JWT_LEEWAY': 10,  # JWT time leeway in seconds
    'HAMADMIN_JWT_ALGORITHMS': None,  # Will use algorithm from JWT header
    'HAMADMIN_AUTH_HEADER': 'HTTP_X_ADMIN_ACCESS_TOKEN',  # Custom auth header name
    'HAMADMIN_CREATE_USER_FUNC': None,  # Custom user creation function
    'HAMADMIN_USER_IDENTIFIER': 'email',  # Field from claims to use as user identifier
} 