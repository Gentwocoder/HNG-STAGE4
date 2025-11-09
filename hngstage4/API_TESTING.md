# API Testing Guide

This document provides examples of how to test the User Service API endpoints.

## Base URL
```
http://localhost:8000/api/v1/users/
```

## Authentication

Most endpoints require JWT authentication. Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## 1. Health Check

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/users/health/
```

**Response:**
```json
{
  "success": true,
  "message": "Health check completed",
  "data": {
    "service": "user-service",
    "status": "healthy",
    "timestamp": 1699545600.123,
    "version": "1.0.0",
    "checks": {
      "database": "healthy",
      "cache": "healthy"
    },
    "response_time_ms": 45.23
  },
  "meta": {...}
}
```

## 2. User Registration

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "phone_number": "+1234567890",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": "uuid-here",
    "email": "user@example.com",
    "username": "testuser",
    "tokens": {
      "refresh": "refresh_token_here",
      "access": "access_token_here"
    },
    "profile": {...}
  },
  "meta": {...}
}
```

## 3. User Login

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "id": "uuid-here",
    "email": "user@example.com",
    "tokens": {
      "refresh": "refresh_token_here",
      "access": "access_token_here"
    }
  },
  "meta": {...}
}
```

## 4. Get User Profile

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/users/profile/ \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "success": true,
  "message": "User profile retrieved successfully",
  "data": {
    "id": "uuid-here",
    "email": "user@example.com",
    "username": "testuser",
    "profile": {
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "avatar_url": null,
      "timezone": "UTC",
      "language": "en"
    },
    "notification_preferences": {...},
    "push_tokens_count": 2
  },
  "meta": {...}
}
```

## 5. Update User Profile

**Request:**
```bash
curl -X PUT http://localhost:8000/api/v1/users/profile/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newusername",
    "profile": {
      "first_name": "Jane",
      "last_name": "Smith",
      "timezone": "America/New_York"
    }
  }'
```

## 6. Get Notification Preferences

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/users/preferences/ \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "success": true,
  "message": "Preferences retrieved successfully",
  "data": {
    "id": "uuid-here",
    "email_enabled": true,
    "email_marketing": true,
    "email_transactional": true,
    "email_security": true,
    "push_enabled": true,
    "push_marketing": false,
    "push_transactional": true,
    "do_not_disturb_start": null,
    "do_not_disturb_end": null,
    "frequency_limit": 50
  },
  "meta": {...}
}
```

## 7. Update Notification Preferences

**Request:**
```bash
curl -X PUT http://localhost:8000/api/v1/users/preferences/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email_marketing": false,
    "push_marketing": false,
    "frequency_limit": 30
  }'
```

## 8. Register Push Token

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/users/push-tokens/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "fcm_token_here_1234567890",
    "token_type": "fcm",
    "platform": "android",
    "device_id": "device_unique_id",
    "device_name": "Samsung Galaxy S21"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Push token created successfully",
  "data": {
    "id": "uuid-here",
    "token_type": "fcm",
    "platform": "android",
    "device_id": "device_unique_id",
    "device_name": "Samsung Galaxy S21",
    "is_active": true
  },
  "meta": {...}
}
```

## 9. List Push Tokens

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/users/push-tokens/?page=1&limit=10 \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "success": true,
  "message": "Push tokens retrieved successfully",
  "data": [
    {
      "id": "uuid-1",
      "token_type": "fcm",
      "platform": "android",
      "device_name": "Samsung Galaxy S21",
      "is_active": true
    },
    {
      "id": "uuid-2",
      "token_type": "fcm",
      "platform": "ios",
      "device_name": "iPhone 13",
      "is_active": true
    }
  ],
  "meta": {
    "total": 2,
    "limit": 10,
    "page": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

## 10. Delete Push Token

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/v1/users/push-tokens/<token_id>/ \
  -H "Authorization: Bearer <access_token>"
```

## 11. Change Password

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/users/change-password/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "OldPass123!",
    "new_password": "NewSecurePass123!",
    "new_password_confirm": "NewSecurePass123!"
  }'
```

## 12. Refresh Token

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/users/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<refresh_token>"
  }'
```

**Response:**
```json
{
  "access": "new_access_token_here",
  "refresh": "new_refresh_token_here"
}
```

## 13. Logout

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/users/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

## Error Responses

All errors follow the standard format:

```json
{
  "success": false,
  "message": "Error",
  "error": "Detailed error message",
  "data": null,
  "meta": {...}
}
```

### Common Status Codes
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
