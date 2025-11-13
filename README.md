# User Service - Distributed Notification System

## Overview

The User Service is a core microservice component of a distributed notification system that manages user authentication, profiles, notification preferences, and push notification tokens. It provides RESTful APIs for user management and integrates with Redis for caching and RabbitMQ for asynchronous message processing.

## Features

- **User Authentication**: JWT-based authentication with access and refresh tokens
- **User Management**: Complete CRUD operations for user profiles
- **Notification Preferences**: Granular control over email and push notification preferences
- **Push Token Management**: Support for multiple devices and platforms (Web, Android, iOS)
- **Caching**: Redis integration for improved performance
- **Rate Limiting**: Protection against abuse with configurable rate limits
- **Health Monitoring**: Health check endpoint for service monitoring
- **API Versioning**: Clean API versioning (v1)

## Tech Stack

- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL (production) / SQLite (development)
- **Cache**: Redis
- **Message Queue**: RabbitMQ (prepared for integration)
- **Authentication**: JWT (Simple JWT)
- **Web Server**: Gunicorn
- **Containerization**: Docker & Docker Compose

## Project Structure

```
hngstage4/
├── core/                           # Main application
│   ├── models.py                   # User, Profile, Preferences, PushToken models
│   ├── serializers.py              # DRF serializers
│   ├── views.py                    # API views
│   ├── urls.py                     # URL routing
│   ├── admin.py                    # Django admin configuration
│   ├── response_utils.py           # Standardized API responses
│   └── cache_manager.py            # Redis cache management
├── hngstage4/                      # Project settings
│   ├── settings.py                 # Django settings
│   ├── urls.py                     # Root URL configuration
│   └── wsgi.py                     # WSGI application
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker Compose setup
├── .env.example                    # Environment variables template
└── README.md                       # This file
```

## API Endpoints

### Authentication

- `POST /api/v1/users/register/` - Register new user
- `POST /api/v1/users/login/` - User login
- `POST /api/v1/users/logout/` - User logout
- `POST /api/v1/users/token/refresh/` - Refresh access token

### User Management

- `GET /api/v1/users/profile/` - Get current user profile
- `PUT /api/v1/users/profile/` - Update user profile
- `POST /api/v1/users/change-password/` - Change password

### Notification Preferences

- `GET /api/v1/users/preferences/` - Get notification preferences
- `PUT /api/v1/users/preferences/` - Update notification preferences

### Push Tokens

- `GET /api/v1/users/push-tokens/` - List all push tokens
- `POST /api/v1/users/push-tokens/` - Register new push token
- `GET /api/v1/users/push-tokens/{id}/` - Get specific push token
- `PUT /api/v1/users/push-tokens/{id}/` - Update push token
- `DELETE /api/v1/users/push-tokens/{id}/` - Delete push token
- `POST /api/v1/users/push-tokens/deactivate_all/` - Deactivate all tokens

### Monitoring

- `GET /health/` - Health check endpoint

## Response Format

All API responses follow a standardized format:

```json
{
  "success": true/false,
  "message": "Success message",
  "data": {...},
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

## Installation & Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- RabbitMQ 3.12+ (for message queue)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hngstage4
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

The service will be available at `http://localhost:8000`

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

The service will be available at `http://localhost:8000`

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key configurations:

- **SECRET_KEY**: Django secret key (required)
- **DEBUG**: Debug mode (True/False)
- **USE_POSTGRES**: Use PostgreSQL instead of SQLite (True/False)
- **USE_REDIS**: Enable Redis caching (True/False)
- **DATABASE_URL**: PostgreSQL connection string
- **REDIS_URL**: Redis connection string
- **ALLOWED_HOSTS**: Comma-separated list of allowed hosts

### Database Configuration

**Development (SQLite)**:
```env
USE_POSTGRES=False
```

**Production (PostgreSQL)**:
```env
USE_POSTGRES=True
DB_NAME=user_service_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

### Redis Configuration

```env
USE_REDIS=True
REDIS_URL=redis://localhost:6379/1
```

### JWT Configuration

```env
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7
```

## Testing

### Run tests

```bash
pytest
```

### Run tests with coverage

```bash
pytest --cov=core --cov-report=html
```

### Linting

```bash
# Flake8
flake8 core/ hngstage4/

# Black
black --check core/ hngstage4/

# isort
isort --check-only core/ hngstage4/
```

## Performance & Scalability

### Caching Strategy

- User data cached for 1 hour
- Notification preferences cached for 24 hours
- Profile data cached for 1 hour
- Cache invalidation on updates

### Rate Limiting

- Registration: 5 attempts per hour per IP
- Login: 10 attempts per 5 minutes per user
- Configurable per endpoint

### Horizontal Scaling

The service is stateless and can be horizontally scaled:

```bash
docker-compose up --scale web=3
```

## Monitoring & Logging

### Health Check

```bash
curl http://localhost:8000/health/
```

### Logs

Logs are stored in:
- Console (development)
- `logs/user_service.log` (production)

### Metrics Tracking

- Service response time
- Database connection status
- Cache connection status
- API endpoint usage

## Security Features

- JWT-based authentication
- Password hashing with Django's PBKDF2
- Rate limiting on sensitive endpoints
- CORS configuration
- SQL injection protection (Django ORM)
- XSS protection
- CSRF protection
- HTTPS enforcement in production

## Integration with Other Services

### API Gateway Integration

The User Service is designed to be called by an API Gateway service for:
- User authentication validation
- User preference lookup
- Push token retrieval

### Message Queue Integration

Prepared for RabbitMQ integration to:
- Publish user events (registration, preference changes)
- Subscribe to notification status updates

### Cache Layer

Redis is used for:
- User data caching
- Session management
- Rate limiting
- Distributed locking

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure strong `SECRET_KEY`
- [ ] Setup PostgreSQL database
- [ ] Configure Redis
- [ ] Setup HTTPS/SSL certificates
- [ ] Configure firewall rules
- [ ] Setup monitoring and alerting
- [ ] Configure backup strategy
- [ ] Setup log aggregation
- [ ] Configure CORS properly

## API Documentation

Detailed API documentation can be generated using:

```bash
python manage.py spectacular --file schema.yml
```

Or access interactive API docs at:
- Swagger UI: `/api/docs/swagger`
- ReDoc: `/api/docs/redoc/`

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is part of the HNG Stage 4 Backend Task.

## Support

For issues and questions:
- Create an issue in the repository
- Contact the development team

## Related Services

- **API Gateway Service**: Entry point for all requests
- **Email Service**: Handles email notifications
- **Push Service**: Handles push notifications
- **Template Service**: Manages notification templates

---

**Built with ❤️ for HNG Stage 4 Backend Task**
