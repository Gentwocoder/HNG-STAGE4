# User Service - Project Summary

## Project Overview

The User Service is a microservice component of a Distributed Notification System built for HNG Stage 4 Backend Task. It handles user authentication, profile management, notification preferences, and push token management.

## ✅ Completed Features

### 1. **Core Models** ✓
- `User`: Custom user model with email authentication
- `UserProfile`: Extended user information
- `NotificationPreference`: Granular notification settings
- `PushToken`: Multi-device push notification support

### 2. **Authentication System** ✓
- JWT-based authentication (access + refresh tokens)
- User registration with validation
- Secure login/logout
- Password change functionality
- Token refresh mechanism
- Token blacklisting on logout

### 3. **API Endpoints** ✓

#### Authentication
- `POST /api/v1/users/register/` - User registration
- `POST /api/v1/users/login/` - User login
- `POST /api/v1/users/logout/` - User logout
- `POST /api/v1/users/token/refresh/` - Refresh access token

#### User Management
- `GET /api/v1/users/profile/` - Get user profile
- `PUT /api/v1/users/profile/` - Update user profile
- `POST /api/v1/users/change-password/` - Change password

#### Notification Preferences
- `GET /api/v1/users/preferences/` - Get preferences
- `PUT /api/v1/users/preferences/` - Update preferences

#### Push Tokens
- `GET /api/v1/users/push-tokens/` - List tokens (paginated)
- `POST /api/v1/users/push-tokens/` - Register new token
- `GET /api/v1/users/push-tokens/{id}/` - Get specific token
- `PUT /api/v1/users/push-tokens/{id}/` - Update token
- `DELETE /api/v1/users/push-tokens/{id}/` - Delete token
- `POST /api/v1/users/push-tokens/deactivate_all/` - Deactivate all

#### Monitoring
- `GET /api/v1/users/health/` - Health check endpoint

### 4. **Response Format** ✓
Standardized JSON response format:
```json
{
  "success": boolean,
  "message": string,
  "data": object | null,
  "error": string | null,
  "meta": {
    "total": number,
    "limit": number,
    "page": number,
    "total_pages": number,
    "has_next": boolean,
    "has_previous": boolean
  }
}
```

### 5. **Caching Layer** ✓
- Redis integration for performance
- User data caching (1 hour TTL)
- Preferences caching (24 hours TTL)
- Profile caching (1 hour TTL)
- Cache invalidation on updates
- Graceful degradation on cache failures

### 6. **Rate Limiting** ✓
- Registration: 5 attempts/hour/IP
- Login: 10 attempts/5 minutes/user
- Configurable per endpoint
- Redis-backed rate limiter

### 7. **Security Features** ✓
- JWT authentication with token rotation
- Password hashing (PBKDF2)
- SQL injection prevention (Django ORM)
- XSS protection
- CSRF protection
- CORS configuration
- Rate limiting
- Input validation
- HTTPS enforcement (production)

### 8. **Database Support** ✓
- PostgreSQL for production
- SQLite for development
- Proper indexing for performance
- Database migrations

### 9. **Admin Interface** ✓
- Django admin for all models
- Custom admin configurations
- Search and filter capabilities
- User-friendly interface

### 10. **Testing Setup** ✓
- Pytest configuration
- Model tests included
- Coverage reporting
- Test fixtures

### 11. **CI/CD Pipeline** ✓
GitHub Actions workflow includes:
- Automated testing on push/PR
- Code linting (flake8, black, isort)
- Security vulnerability scanning
- Docker image building
- Automated deployment
- Health check verification

### 12. **Docker Support** ✓
- Dockerfile for containerization
- Docker Compose with:
  - PostgreSQL database
  - Redis cache
  - RabbitMQ (prepared)
  - Nginx reverse proxy
  - Web application
- Multi-container orchestration
- Health checks
- Volume management

### 13. **Documentation** ✓
- `README.md` - Complete setup and usage guide
- `ARCHITECTURE.md` - System design documentation
- `API_TESTING.md` - API endpoint testing examples
- `.env.example` - Environment configuration template
- Inline code documentation

### 14. **Development Tools** ✓
- `setup.sh` - Automated setup script
- `Makefile` - Common command shortcuts
- `pytest.ini` - Test configuration
- `.gitignore` - Version control configuration

## 📁 Project Structure

```
hngstage4/
├── core/                          # Main application
│   ├── models.py                  # Database models
│   ├── serializers.py             # DRF serializers
│   ├── views.py                   # API views
│   ├── urls.py                    # URL routing
│   ├── admin.py                   # Admin configuration
│   ├── response_utils.py          # Response helpers
│   ├── cache_manager.py           # Cache management
│   ├── tests/                     # Test files
│   │   ├── __init__.py
│   │   └── test_models.py
│   └── migrations/                # Database migrations
├── hngstage4/                     # Project settings
│   ├── settings.py                # Configuration
│   ├── urls.py                    # Root URLs
│   └── wsgi.py                    # WSGI config
├── .github/
│   └── workflows/
│       └── ci-cd.yml              # CI/CD pipeline
├── requirements.txt               # Dependencies
├── Dockerfile                     # Docker config
├── docker-compose.yml             # Docker orchestration
├── nginx.conf                     # Nginx configuration
├── pytest.ini                     # Test configuration
├── Makefile                       # Command shortcuts
├── setup.sh                       # Setup script
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── README.md                      # Main documentation
├── ARCHITECTURE.md                # Architecture docs
└── API_TESTING.md                 # API testing guide
```

## 🚀 Quick Start

### Local Development
```bash
# Clone repository
git clone <repo-url>
cd hngstage4

# Run setup script
chmod +x setup.sh
./setup.sh

# Or use Makefile
make install
make migrate
make run
```

### Docker Deployment
```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Check health
curl http://localhost:8000/api/v1/users/health/
```

## 🔧 Configuration

Key environment variables (see `.env.example`):
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode
- `USE_POSTGRES` - Use PostgreSQL
- `USE_REDIS` - Enable Redis
- `DB_*` - Database configuration
- `REDIS_URL` - Redis connection
- `RABBITMQ_*` - RabbitMQ settings

## 📊 Performance Targets

✅ Handle 1,000+ requests per minute
✅ API Gateway response under 100ms
✅ 99.5% uptime target
✅ Horizontal scaling support
✅ Efficient caching strategy
✅ Optimized database queries

## 🔐 Security Compliance

✅ JWT authentication
✅ Password hashing
✅ Rate limiting
✅ Input validation
✅ CORS configuration
✅ XSS/CSRF protection
✅ SQL injection prevention
✅ HTTPS enforcement

## 📈 Monitoring & Observability

✅ Health check endpoint
✅ Structured JSON logging
✅ Request/response logging
✅ Error tracking
✅ Performance metrics
✅ Database connectivity monitoring
✅ Cache connectivity monitoring

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov-report=html

# Run linting
make lint

# Format code
make format
```

## 🚢 Deployment

### Prerequisites
- Server with Docker support
- PostgreSQL 15+
- Redis 7+
- Domain name (optional)
- SSL certificate (optional)

### Deployment Steps
1. Request server: `/request-server`
2. Clone repository
3. Configure environment variables
4. Run Docker Compose
5. Setup reverse proxy (Nginx)
6. Configure SSL (Let's Encrypt)
7. Monitor health endpoint

## 🔄 Integration Points

### Current
- API Gateway (REST/HTTP)
- PostgreSQL (Data storage)
- Redis (Caching)

### Prepared For
- RabbitMQ (Message queue)
- Email Service (User events)
- Push Service (Token events)
- Template Service (Email templates)

## 📝 Naming Conventions

✅ snake_case for:
- Request/response fields
- Database columns
- Function names
- File names

✅ PascalCase for:
- Class names
- Model names

✅ UPPER_CASE for:
- Constants
- Environment variables

## 🎯 Key Technical Features

1. **Circuit Breaker Pattern**: Prepared for service failures
2. **Retry System**: Exponential backoff ready
3. **Service Discovery**: Docker networking
4. **Health Checks**: `/health` endpoint
5. **Idempotency**: Unique request handling
6. **Async Communication**: RabbitMQ prepared
7. **Sync Communication**: REST APIs
8. **Cache-First Strategy**: Performance optimization

## 📦 Dependencies

### Core
- Django 4.2
- Django REST Framework 3.14
- djangorestframework-simplejwt 5.3

### Database
- psycopg2-binary 2.9

### Cache
- redis 5.0
- django-redis 5.4

### Message Queue
- pika 1.3 (RabbitMQ)

### Security
- django-cors-headers 4.3
- python-decouple 3.8

### Testing
- pytest 7.4
- pytest-django 4.7
- pytest-cov 4.1

### Production
- gunicorn 21.2
- whitenoise 6.6

## 🐛 Known Limitations

1. Email verification not implemented (planned)
2. Password reset not implemented (planned)
3. OAuth integration not available (planned)
4. 2FA not implemented (planned)

## 🔮 Future Enhancements

- [ ] Email verification system
- [ ] Password reset flow
- [ ] OAuth providers (Google, GitHub)
- [ ] Two-factor authentication
- [ ] User activity logging
- [ ] GraphQL API
- [ ] WebSocket support
- [ ] Advanced analytics

## 👥 Team Collaboration

This service is part of a 4-person team project:
- **User Service** (This service)
- **API Gateway Service**
- **Email Service**
- **Push Service**
- **Template Service**

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [DRF Documentation](https://www.django-rest-framework.org/)
- [JWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Run tests and linting
5. Submit pull request

## 📄 License

Part of HNG Stage 4 Backend Task

## 📞 Support

For issues and questions:
- Create GitHub issue
- Contact team members
- Check documentation

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: November 9, 2025

Built with ❤️ for HNG Stage 4 Backend Task
