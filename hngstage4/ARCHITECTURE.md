# User Service Architecture

## System Overview

The User Service is a critical microservice in the Distributed Notification System that handles all user-related operations, authentication, and preference management.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          API GATEWAY SERVICE                             │
│                    (Routes requests to services)                         │
└────────────────┬────────────────────────────────────────────────────────┘
                 │
                 │ HTTP/REST
                 │
┌────────────────▼────────────────────────────────────────────────────────┐
│                          USER SERVICE                                    │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Django REST API                                │  │
│  │                                                                   │  │
│  │  • Authentication (JWT)        • User Profile Management         │  │
│  │  • User Registration           • Notification Preferences        │  │
│  │  • Login/Logout                • Push Token Management           │  │
│  │  • Password Management         • Health Check                    │  │
│  └───────────┬──────────────────────────────────┬───────────────────┘  │
│              │                                   │                      │
│              │                                   │                      │
│  ┌───────────▼──────────┐           ┌───────────▼──────────────────┐  │
│  │  Cache Manager       │           │    Response Utils            │  │
│  │  (Redis Integration) │           │    (Standardized Responses)  │  │
│  └───────────┬──────────┘           └──────────────────────────────┘  │
└──────────────┼──────────────────────────────────────────────────────────┘
               │
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼──────┐      ┌──────▼─────┐
│  Redis   │      │ PostgreSQL │
│  Cache   │      │  Database  │
└──────────┘      └────────────┘
```

## Component Details

### 1. API Layer
- **Django REST Framework**: Provides RESTful endpoints
- **JWT Authentication**: Secure token-based authentication
- **Request Validation**: Input validation using serializers
- **Rate Limiting**: Protection against abuse

### 2. Business Logic Layer
- **User Management**: Registration, login, profile updates
- **Preference Management**: Email and push notification preferences
- **Token Management**: Device push token registration and management
- **Password Security**: Hashing and validation

### 3. Data Access Layer
- **Models**: User, UserProfile, NotificationPreference, PushToken
- **ORM**: Django ORM for database operations
- **Migrations**: Version-controlled schema changes

### 4. Cache Layer (Redis)
- **User Data Caching**: Reduce database queries
- **Session Management**: JWT token storage
- **Rate Limiting**: Track API usage
- **Preference Caching**: Fast preference lookups

### 5. Database (PostgreSQL)
- **User Data**: Authentication credentials
- **Profile Data**: User information
- **Preferences**: Notification settings
- **Push Tokens**: Device registration tokens

## Data Flow

### 1. User Registration Flow
```
Client Request
    ↓
API Gateway
    ↓
User Service (Validation)
    ↓
Create User → Create Profile → Create Preferences
    ↓
Save to PostgreSQL
    ↓
Generate JWT Tokens
    ↓
Cache User Data (Redis)
    ↓
Response to Client
```

### 2. User Login Flow
```
Client Request (Email + Password)
    ↓
API Gateway
    ↓
User Service (Authentication)
    ↓
Check Credentials (PostgreSQL)
    ↓
Generate JWT Tokens
    ↓
Cache User Data (Redis)
    ↓
Update Last Login Info
    ↓
Response with Tokens
```

### 3. Get User Preferences Flow
```
Client Request (with JWT)
    ↓
API Gateway
    ↓
User Service (Token Validation)
    ↓
Check Cache (Redis) ──┐
    │                 │ Cache Hit
    ↓                 │
Cache Miss?           │
    │                 │
    ↓                 │
Query Database        │
    │                 │
    ↓                 │
Cache Result          │
    │                 │
    └─────────────────┘
    ↓
Response to Client
```

### 4. Push Token Registration Flow
```
Client Request (Token + Device Info)
    ↓
API Gateway
    ↓
User Service (Validation)
    ↓
Check Existing Token
    │
    ├─ Exists → Update Token
    │
    └─ New → Create Token
    ↓
Save to PostgreSQL
    ↓
Invalidate User Cache
    ↓
Response to Client
```

## Integration Points

### 1. With API Gateway
- **Protocol**: HTTP/REST
- **Authentication**: JWT tokens
- **Data Format**: JSON
- **Endpoints**: All `/api/v1/users/*` endpoints

### 2. With Email Service (Future)
- **Protocol**: Message Queue (RabbitMQ)
- **Exchange**: `user.events`
- **Events**: 
  - `user.registered`
  - `user.password_changed`
  - `user.preferences_updated`

### 3. With Push Service (Future)
- **Protocol**: Message Queue (RabbitMQ)
- **Exchange**: `user.events`
- **Events**:
  - `user.token_registered`
  - `user.token_updated`
  - `user.token_deleted`

### 4. With Template Service (Future)
- **Protocol**: HTTP/REST (Synchronous)
- **Purpose**: Fetch email templates for user notifications
- **Endpoints**: Template retrieval based on user language

## Security Measures

### 1. Authentication
- JWT-based token authentication
- Refresh token rotation
- Token blacklisting on logout

### 2. Authorization
- Permission-based access control
- User can only access their own data
- Admin endpoints protected

### 3. Data Protection
- Password hashing (PBKDF2)
- SQL injection prevention (ORM)
- XSS protection
- CSRF protection

### 4. Rate Limiting
- Registration: 5 attempts/hour/IP
- Login: 10 attempts/5 minutes/user
- API calls: Configurable per endpoint

## Scaling Strategy

### Horizontal Scaling
```
┌─────────────┐
│ Load        │
│ Balancer    │
└──────┬──────┘
       │
       ├──────┬──────┬──────┐
       │      │      │      │
   ┌───▼──┐ ┌─▼───┐ ┌▼────┐│
   │User  │ │User │ │User ││
   │Svc 1 │ │Svc 2│ │Svc 3││
   └───┬──┘ └─┬───┘ └┬────┘│
       │      │      │      │
       └──────┴──────┴──────┘
              │
       ┌──────┴──────┐
       │             │
   ┌───▼──┐     ┌───▼────┐
   │Redis │     │Postgres│
   └──────┘     └────────┘
```

### Database Scaling
- **Read Replicas**: For read-heavy operations
- **Connection Pooling**: Efficient database connections
- **Indexing**: Optimized queries

### Cache Scaling
- **Redis Cluster**: Distributed caching
- **Cache Warming**: Pre-populate frequently accessed data
- **TTL Strategy**: Smart expiration policies

## Performance Optimization

### 1. Caching Strategy
- **User Data**: 1 hour TTL
- **Preferences**: 24 hours TTL
- **Profile Data**: 1 hour TTL
- **Invalidation**: On updates

### 2. Database Optimization
- Indexes on frequently queried fields
- Pagination for list endpoints
- Selective field queries
- Connection pooling

### 3. Response Optimization
- Gzip compression
- Minimal payload size
- Efficient serialization

## Monitoring & Observability

### 1. Health Checks
- Database connectivity
- Cache connectivity
- Service status
- Response time

### 2. Metrics
- Request rate
- Error rate
- Response time
- Cache hit ratio
- Active users

### 3. Logging
- Structured JSON logs
- Request/response logging
- Error tracking
- Audit trails

## Failure Handling

### 1. Database Failures
- Connection retry with exponential backoff
- Fallback to read replicas
- Circuit breaker pattern

### 2. Cache Failures
- Graceful degradation (query database)
- Cache bypass on errors
- Service continues without cache

### 3. Network Failures
- Request timeout handling
- Retry logic
- Error responses

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│          Docker Container               │
│  ┌───────────────────────────────────┐ │
│  │       Nginx (Reverse Proxy)       │ │
│  └───────────────┬───────────────────┘ │
│                  │                      │
│  ┌───────────────▼───────────────────┐ │
│  │   Gunicorn (WSGI Server)          │ │
│  │   ┌───────────────────────────┐   │ │
│  │   │   Django Application      │   │ │
│  │   └───────────────────────────┘   │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
         │                    │
         │                    │
    ┌────▼────┐         ┌────▼─────┐
    │  Redis  │         │PostgreSQL│
    │Container│         │Container │
    └─────────┘         └──────────┘
```

## API Response Format

All endpoints follow a standardized response format:

```json
{
  "success": true/false,
  "message": "Operation result message",
  "data": {
    // Response data
  },
  "error": "Error message (if applicable)",
  "meta": {
    "total": 100,
    "limit": 10,
    "page": 1,
    "total_pages": 10,
    "has_next": true,
    "has_previous": false
  }
}
```

## Future Enhancements

1. **OAuth Integration**: Google, Facebook, GitHub login
2. **2FA Support**: Two-factor authentication
3. **Email Verification**: Verify user emails
4. **Password Reset**: Forgot password flow
5. **User Activity Logs**: Audit trail
6. **GraphQL API**: Alternative to REST
7. **WebSocket Support**: Real-time updates
8. **Multi-tenancy**: Support for organizations

---

This architecture ensures:
- ✅ High availability
- ✅ Horizontal scalability
- ✅ Fast response times (<100ms target)
- ✅ Secure authentication
- ✅ Data consistency
- ✅ Fault tolerance
