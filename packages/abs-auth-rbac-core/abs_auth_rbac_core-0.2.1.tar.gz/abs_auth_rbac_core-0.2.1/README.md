# ABS Auth RBAC Core

A comprehensive authentication and Role-Based Access Control (RBAC) package for FastAPI applications. This package provides robust JWT-based authentication and flexible role-based permission management using Casbin with Redis support for real-time policy updates.

## Features

- **JWT-based Authentication**: Secure token-based authentication with customizable expiration
- **Password Hashing**: Secure password storage using bcrypt
- **Role-Based Access Control (RBAC)**: Flexible permission management using Casbin
- **Real-time Policy Updates**: Redis integration for live policy synchronization
- **User-Role Management**: Dynamic role assignment and revocation
- **Permission Enforcement**: Decorator-based permission checking
- **Middleware Integration**: Seamless FastAPI middleware integration
- **Comprehensive Error Handling**: Built-in exception handling for security scenarios

## Installation

```bash
pip install abs-auth-rbac-core
```

## Quick Start

### 1. Basic Setup

```python
from abs_auth_rbac_core.auth.jwt_functions import JWTFunctions
from abs_auth_rbac_core.rbac import RBACService
import os

# Initialize JWT functions
jwt_functions = JWTFunctions(
    secret_key=os.getenv("JWT_SECRET_KEY"),
    algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
    expire_minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
)

# Initialize RBAC service with database session
rbac_service = RBACService(
    session=your_db_session,
    redis_config=RedisWatcherSchema(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        channel=os.getenv("REDIS_CHANNEL", "casbin_policy_updates"),
        password=os.getenv("REDIS_PASSWORD"),
        ssl=os.getenv("REDIS_SSL", "false").lower() == "true"
    )
)
```

### 2. Authentication Setup

The auth middleware can be implemented in two ways:

#### Option 1: Using the Package Middleware (Recommended)

The package middleware automatically handles JWT token validation and sets the user in the request state:

```python
from abs_auth_rbac_core.auth.middleware import auth_middleware

# Create authentication middleware
auth_middleware = auth_middleware(
    db_session=your_db_session,
    jwt_secret_key=os.getenv("JWT_SECRET_KEY"),
    jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256")
)

# Apply to specific routers (recommended approach)
app.include_router(
    protected_router,
    dependencies=[Depends(auth_middleware)]
)

# Public routes (no middleware)
app.include_router(public_router)
```

**How it works:**
1. The middleware validates the JWT token from the Authorization header
2. Extracts the user UUID from the token payload
3. Fetches the user from the database using the UUID
4. **Sets the user object in `request.state.user`**
5. Returns the user object for use in route handlers

**Accessing the user in routes:**
```python
@router.get("/profile")
async def get_profile(request: Request):
    # User is automatically available in request.state.user
    user = request.state.user
    return {"user_id": user.uuid, "email": user.email}
```

#### Option 2: Custom Authentication Function

```python
from abs_auth_rbac_core.auth import JWTFunctions
from fastapi import Security, HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from abs_exception_core.exceptions import UnauthorizedError

# Create security scheme
security = HTTPBearer(auto_error=False)
jwt_functions = JWTFunctions(
    secret_key=os.getenv("JWT_SECRET_KEY"),
    algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
    expire_minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Dict:
    try:
        if not credentials:
            raise UnauthorizedError(detail="No authorization token provided")

        token = credentials.credentials
        # Remove 'Bearer ' prefix if present
        if token.lower().startswith("bearer "):
            token = token[7:]

        decoded_token = jwt_functions.decode_jwt(token)
        if not decoded_token:
            raise UnauthorizedError(detail="Invalid or expired token")

        return decoded_token
    except Exception as e:
        raise UnauthorizedError(detail=str(e))

# Use in individual routes
@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user.get('name')}"}
```

### 3. RBAC Operations

```python
# Create a role with permissions
role = rbac_service.create_role(
    name="admin",
    description="Administrator role with full access",
    permission_ids=["permission_uuid1", "permission_uuid2"]
)

# Assign roles to user
rbac_service.bulk_assign_roles_to_user(
    user_uuid="user_uuid",
    role_uuids=["role_uuid1", "role_uuid2"]
)

# Check user permissions
has_permission = rbac_service.check_permission(
    user_uuid="user_uuid",
    resource="USER_MANAGEMENT",
    action="VIEW",
    module="USER_MANAGEMENT"
)

# Get user permissions
user_permissions = rbac_service.get_user_permissions(user_uuid="user_uuid")
user_roles = rbac_service.get_user_roles(user_uuid="user_uuid")
```

## Core Components

### Authentication (`auth/`)
- `jwt_functions.py`: JWT token management and password hashing
- `middleware.py`: Authentication middleware for FastAPI
- `auth_functions.py`: Core authentication functions

### RBAC (`rbac/`)
- `service.py`: Main RBAC service with role and permission management
- `decorator.py`: Decorators for permission checking

### Models (`models/`)
- `user.py`: User model
- `roles.py`: Role model
- `permissions.py`: Permission model
- `user_role.py`: User-Role association model
- `role_permission.py`: Role-Permission association model
- `rbac_model.py`: Base RBAC model
- `base_model.py`: Base model with common fields

### Utilities (`util/`)
- `permission_constants.py`: Predefined permission constants and enums

## Complete Implementation Example

### 1. Dependency Injection Setup

```python
from dependency_injector import containers, providers
from abs_auth_rbac_core.auth.middleware import auth_middleware
from abs_auth_rbac_core.rbac import RBACService
from abs_auth_rbac_core.util.permission_constants import (
    PermissionAction,
    PermissionModule,
    PermissionResource
)

class Container(containers.DeclarativeContainer):
    # Configure wiring for dependency injection
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.api.auth_route",
            "src.api.endpoints.rbac.permission_route",
            "src.api.endpoints.rbac.role_route",
            "src.api.endpoints.rbac.users_route",
            # Add other modules that need dependency injection
        ]
    )
    
    # Database session provider
    db_session = providers.Factory(your_db_session_factory)
    
    # RBAC service provider
    rbac_service = providers.Singleton(
        RBACService,
        session=db_session,
        redis_config=RedisWatcherSchema(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            channel=os.getenv("REDIS_CHANNEL", "casbin_policy_updates"),
            password=os.getenv("REDIS_PASSWORD"),
            ssl=os.getenv("REDIS_SSL", "false").lower() == "true"
        )
    )
    
    # Auth middleware provider
    get_auth_middleware = providers.Factory(
        auth_middleware,
        db_session=db_session,
        jwt_secret_key=os.getenv("JWT_SECRET_KEY"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256")
    )

# Initialize container
container = Container()
app.container = container
```

### 2. Complete Application Setup

```python
from fastapi import FastAPI, Depends
from dependency_injector.wiring import Provide, inject
from src.core.container import Container

@singleton
class CreateApp:
    def __init__(self):
        self.container = Container()
        self.db = self.container.db()
        # Get the auth middleware factory
        self.auth_middleware = self.container.get_auth_middleware()

        self.app = FastAPI(
            title="Your Service",
            description="Service Description", 
            version="0.0.1"
        )
        
        # Apply CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in configs.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Public routes (no authentication required)
        self.app.include_router(auth_router, tags=["Auth"])
        self.app.include_router(public_router_v1)
        
        # Protected routes (authentication required)
        self.app.include_router(
            router_v1,
            dependencies=[Depends(self.auth_middleware)]
        )
        
        # Register exception handlers
        register_exception_handlers(self.app)

# Initialize application
application = CreateApp()
app = application.app
```

### 3. Route Implementation with Permissions

```python
from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import Provide, inject
from abs_auth_rbac_core.rbac import rbac_require_permission
from abs_auth_rbac_core.util.permission_constants import (
    PermissionAction,
    PermissionModule,
    PermissionResource
)

# Protected router (requires authentication)
router = APIRouter(prefix="/users")

# Public router (no authentication required)
public_router = APIRouter(prefix="/users")

# Public route example (no authentication or permissions required)
@public_router.post("/all", response_model=FindUserResult)
@inject
async def get_user_list(
    request: Request,
    find_query: FindUser = Body(...),
    rbac_service: RBACService = Depends(Provide[Container.rbac_service]),
    service: UserService = Depends(Provide[Container.user_service]),
):
    """Get the list of users with filtering, sorting and pagination"""
    find_query.searchable_fields = find_query.searchable_fields or ["name"]
    users = service.get_list(schema=find_query)
    return users

# Protected route with permission check
@router.get("/{user_id}", response_model=UserProfile)
@inject
@rbac_require_permission(
    f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.USER_MANAGEMENT.value}:{PermissionAction.VIEW.value}"
)
async def get_user(
    user_id: int,
    request: Request,
    service: UserService = Depends(Provide[Container.user_service]),
    rbac_service: RBACService = Depends(Provide[Container.rbac_service]),
):
    """Get user profile with permissions and roles"""
    return service.get_user_profile("id", user_id, rbac_service)
```

**How the RBAC decorator works:**
1. The `@rbac_require_permission` decorator automatically extracts the user from `request.state.user`
2. Gets the user's UUID: `current_user_uuid = request.state.user.uuid`
3. Checks if the user has the required permissions using the RBAC service
4. If permission is denied, raises `PermissionDeniedError`
5. If permission is granted, the route handler executes normally

**Important:** The `request: Request` parameter is required in routes that use the `@rbac_require_permission` decorator because it needs access to `request.state.user`.

### Authentication Flow Overview

```
1. Client sends request with Authorization header
   Authorization: Bearer <jwt_token>

2. Auth middleware intercepts the request
   ├── Validates JWT token
   ├── Extracts user UUID from token
   ├── Fetches user from database
   └── Sets user in request.state.user

3. RBAC decorator checks permissions
   ├── Gets user UUID from request.state.user
   ├── Checks permissions against Casbin policies
   └── Allows/denies access based on permissions

4. Route handler executes (if permissions granted)
   └── Can access user via request.state.user
```

### Accessing Current User

#### In Routes with RBAC Decorator
```python
@router.get("/my-profile")
@inject
@rbac_require_permission(
    f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.USER_MANAGEMENT.value}:{PermissionAction.VIEW.value}"
)
async def get_my_profile(
    request: Request,
    rbac_service: RBACService = Depends(Provide[Container.rbac_service]),
):
    # Access current user from request state
    current_user = request.state.user
    return service.get_user_profile("uuid", current_user.uuid, rbac_service)
```

#### In Routes with Custom Auth Function
```python
@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    # current_user is the decoded JWT payload
    return {"user_id": current_user["uuid"], "email": current_user["email"]}
```

#### In Service Methods
```python
def some_service_method(self, user_uuid: str, rbac_service: RBACService):
    # Get user permissions
    permissions = rbac_service.get_user_permissions(user_uuid=user_uuid)
    # Get user roles
    roles = rbac_service.get_user_roles(user_uuid=user_uuid)
    return {"permissions": permissions, "roles": roles}
```

@router.post("/create")
@inject
@rbac_require_permission(
    f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.USER_MANAGEMENT.value}:{PermissionAction.CREATE.value}"
)
async def create_user(
    user: CreateUserWithRoles,
    request: Request,
    rbac_service: RBACService = Depends(Provide[Container.rbac_service]),
):
    """Create a new user with roles"""
    new_user = service.add_user(user)
    
    # Assign roles if provided
    if user.role_uuids and len(user.role_uuids) > 0 and new_user.uuid:
        rbac_service.bulk_assign_roles_to_user(
            user_uuid=new_user.uuid,
            role_uuids=user.role_uuids,
        )
    return new_user

@router.patch("/{user_id}")
@inject
@rbac_require_permission(
    f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.USER_MANAGEMENT.value}:{PermissionAction.EDIT.value}"
)
async def update_user(
    user_id: int,
    user: UpdateUserWithRoles,
    request: Request,
    rbac_service: RBACService = Depends(Provide[Container.rbac_service]),
):
    """Update user with new attributes and roles"""
    return service.patch_user(user_id, user, rbac_service)

@router.delete("/{user_id}")
@inject
@rbac_require_permission(
    f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.USER_MANAGEMENT.value}:{PermissionAction.DELETE.value}"
)
async def delete_user(
    user_id: int,
    request: Request,
    rbac_service: RBACService = Depends(Provide[Container.rbac_service]),
):
    """Delete user"""
    return service.remove_user(user_id, rbac_service)
```

### 3. Role and Permission Management

```python
@router.get("/roles")
@inject
@rbac_require_permission(
    f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.ROLE_MANAGEMENT.value}:{PermissionAction.VIEW.value}"
)
async def get_roles(
    request: Request,
    rbac_service: RBACService = Depends(Provide[Container.rbac_service]),
):
    """Get all roles"""
    return rbac_service.list_roles()

@router.post("/roles")
@inject
@rbac_require_permission(
    f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.ROLE_MANAGEMENT.value}:{PermissionAction.CREATE.value}"
)
async def create_role(
    role: CreateRoleSchema,
    request: Request,
    rbac_service: RBACService = Depends(Provide[Container.rbac_service]),
):
    """Create a new role with permissions"""
    return rbac_service.create_role(
        name=role.name,
        description=role.description,
        permission_ids=role.permission_ids
    )

@router.get("/user-permissions/{user_uuid}")
@inject
@rbac_require_permission([
    f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.USER_MANAGEMENT.value}:{PermissionAction.VIEW.value}",
    f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.ROLE_MANAGEMENT.value}:{PermissionAction.VIEW.value}"
])
async def get_user_permissions(
    user_uuid: str,
    request: Request,
    rbac_service: RBACService = Depends(Provide[Container.rbac_service]),
):
    """Get all permissions for a user"""
    return rbac_service.get_user_permissions(user_uuid)
```

### 4. User Profile with Permissions

```python
def get_user_profile(self, attr: str, value: any, rbac_service: RBACService) -> UserProfile:
    """Get user profile with permissions and roles"""
    user = self.user_repository.read_by_attr(attr, value, eager=True)
    
    # Get user permissions and roles
    permissions = rbac_service.get_user_permissions(user_uuid=user.uuid)
    user_permissions = rbac_service.get_user_only_permissions(user_uuid=user.uuid)
    roles = rbac_service.get_user_roles(user_uuid=user.uuid)
    
    # Convert roles to response models
    role_models = [UserRoleResponse.model_validate(role) for role in roles]
    
    return UserProfile(
        id=user.id,
        uuid=user.uuid,
        email=user.email,
        name=user.name,
        is_active=user.is_active,
        last_login_at=user.last_login_at,
        permissions=permissions,
        user_permissions=user_permissions,
        roles=role_models,
    )
```

## Permission System

### Permission Format
Permissions follow the format: `module:resource:action`

- **Module**: The system module (e.g., `USER_MANAGEMENT`, `EMAIL_PROCESS`)
- **Resource**: The specific resource within the module (e.g., `USER_MANAGEMENT`, `ROLE_MANAGEMENT`)
- **Action**: The action being performed (e.g., `VIEW`, `CREATE`, `EDIT`, `DELETE`)

### Using Permission Constants

```python
from abs_auth_rbac_core.util.permission_constants import (
    PermissionAction,
    PermissionModule,
    PermissionResource,
    PermissionConstants
)

# Using enums
permission_string = f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.USER_MANAGEMENT.value}:{PermissionAction.VIEW.value}"

# Using predefined constants
user_view_permission = PermissionConstants.RBAC_USER_MANAGEMENT_VIEW
permission_string = f"{user_view_permission.module}:{user_view_permission.resource}:{user_view_permission.action}"
```

### Multiple Permissions

```python
@rbac_require_permission([
    f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.USER_MANAGEMENT.value}:{PermissionAction.VIEW.value}",
    f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.ROLE_MANAGEMENT.value}:{PermissionAction.VIEW.value}"
])
async def get_user_with_roles():
    # User needs both permissions to access this endpoint
    pass
```

## Configuration

### Environment Variables

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_MINUTES=1440

# Redis Configuration (for real-time policy updates)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_CHANNEL=casbin_policy_updates
REDIS_SSL=false

# Database Configuration
DATABASE_URI=postgresql://user:password@localhost/dbname
```

### Casbin Policy Configuration

The package uses a default policy configuration that supports:
- Role-based access control
- Resource-based permissions
- Module-based organization
- Super admin bypass

Policy format: `[role] [resource] [action] [module]`

## Error Handling

The package includes comprehensive error handling:

```python
from abs_exception_core.exceptions import (
    UnauthorizedError,
    PermissionDeniedError,
    ValidationError,
    DuplicatedError,
    NotFoundError
)

# Handle authentication errors
try:
    user = await auth_middleware(request)
except UnauthorizedError as e:
    return {"error": "Authentication failed", "detail": str(e)}

# Handle permission errors
try:
    # Protected operation
    pass
except PermissionDeniedError as e:
    return {"error": "Permission denied", "detail": str(e)}
```

## Best Practices

### 1. Security
- Always use environment variables for sensitive data
- Implement proper password policies
- Regularly rotate JWT secret keys
- Use HTTPS in production
- Implement rate limiting for authentication endpoints

### 2. Permission Design
- Use descriptive permission names
- Group related permissions by module
- Implement least privilege principle
- Document permission requirements

### 3. Performance
- Use Redis for real-time policy updates
- Implement caching for frequently accessed permissions
- Optimize database queries with eager loading
- Monitor policy enforcement performance

### 4. Maintenance
- Regularly audit user permissions
- Implement permission cleanup for inactive users
- Monitor and log security events
- Keep dependencies updated

### 5. Testing
- Test all permission combinations
- Mock external dependencies
- Test error scenarios
- Implement integration tests

## Monitoring and Logging

```python
import logging
from abs_utils.logger import setup_logger

logger = setup_logger(__name__)

# Log authentication events
logger.info(f"User {user_uuid} authenticated successfully")

# Log permission checks
logger.info(f"Permission check: {user_uuid} -> {resource}:{action}:{module}")

# Log role assignments
logger.info(f"Roles assigned to user {user_uuid}: {role_uuids}")
```

## Migration and Deployment

### Database Migrations
Ensure your database has the required tables:
- `users`
- `roles`
- `permissions`
- `user_roles`
- `role_permissions`
- `gov_casbin_rules`

### Redis Setup
For real-time policy updates, configure Redis:
```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis
redis-cli config set requirepass your-password
redis-cli config set notify-keyspace-events KEA
```

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "rbac_watcher": rbac_service.is_watcher_active(),
        "policy_count": rbac_service.get_policy_count()
    }
```

## Troubleshooting

### Common Issues

1. **Authentication Fails**
   - Check JWT secret key configuration
   - Verify token expiration settings
   - Ensure user exists in database

2. **Permission Denied**
   - Verify user has required roles
   - Check role-permission assignments
   - Validate permission format

3. **Redis Connection Issues**
   - Check Redis server status
   - Verify connection parameters
   - Ensure Redis supports pub/sub

4. **Policy Not Updating**
   - Check Redis watcher configuration
   - Verify policy format
   - Monitor Redis logs

## License

This project is licensed under the MIT License - see the LICENSE file for details.
