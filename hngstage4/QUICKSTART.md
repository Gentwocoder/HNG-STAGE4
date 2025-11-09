# Quick Start Guide - User Service

## ✅ Setup Complete!

Your User Service is now ready to use. Here's how to get started:

## 1. Verify Installation

The following has been set up:
- ✅ Django project configured
- ✅ Database migrations applied
- ✅ Logs directory created
- ✅ All models created (User, UserProfile, NotificationPreference, PushToken)
- ✅ API endpoints configured
- ✅ Authentication system ready (JWT)

## 2. Start the Development Server

```bash
cd /home/gentle/Documents/HNG-STAGE4/hngstage4
python manage.py runserver
```

The server will start at: `http://127.0.0.1:8000`

## 3. Test the Health Endpoint

Open a new terminal and run:

```bash
curl http://127.0.0.1:8000/api/v1/users/health/
```

You should see:
```json
{
  "success": true,
  "message": "Health check completed",
  "data": {
    "service": "user-service",
    "status": "healthy",
    ...
  }
}
```

## 4. Create a Superuser (Optional)

To access the Django admin panel:

```bash
python manage.py createsuperuser
```

Then visit: `http://127.0.0.1:8000/admin/`

## 5. Test User Registration

```bash
curl -X POST http://127.0.0.1:8000/api/v1/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "username": "testuser",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

## 6. Test User Login

```bash
curl -X POST http://127.0.0.1:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123!"
  }'
```

Save the `access` token from the response for authenticated requests.

## 7. Test Authenticated Endpoint

```bash
# Replace YOUR_ACCESS_TOKEN with the token from login
curl -X GET http://127.0.0.1:8000/api/v1/users/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 8. Available API Endpoints

### Public Endpoints (No Authentication)
- `GET /api/v1/users/health/` - Health check
- `POST /api/v1/users/register/` - User registration
- `POST /api/v1/users/login/` - User login
- `POST /api/v1/users/token/refresh/` - Refresh token

### Protected Endpoints (Require Authentication)
- `GET /api/v1/users/profile/` - Get user profile
- `PUT /api/v1/users/profile/` - Update profile
- `POST /api/v1/users/logout/` - Logout
- `POST /api/v1/users/change-password/` - Change password
- `GET /api/v1/users/preferences/` - Get notification preferences
- `PUT /api/v1/users/preferences/` - Update preferences
- `GET /api/v1/users/push-tokens/` - List push tokens
- `POST /api/v1/users/push-tokens/` - Register push token
- `GET /api/v1/users/push-tokens/{id}/` - Get push token
- `PUT /api/v1/users/push-tokens/{id}/` - Update push token
- `DELETE /api/v1/users/push-tokens/{id}/` - Delete push token

## 9. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 10. Using Docker (Alternative)

```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Common Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
pytest

# Lint code
make lint

# Format code
make format

# Run server
make run
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Database Issues
```bash
# Delete database and start fresh
rm db.sqlite3
python manage.py migrate
```

### Cache Issues
```bash
# Clear Redis cache (if using Redis)
redis-cli FLUSHALL
```

## Next Steps

1. ✅ Test all API endpoints (see API_TESTING.md)
2. ✅ Configure environment variables for production (.env)
3. ✅ Set up PostgreSQL database (optional for development)
4. ✅ Set up Redis cache (optional for development)
5. ✅ Deploy using Docker Compose
6. ✅ Request deployment server: `/request-server`

## Need Help?

- Check `README.md` for detailed documentation
- Check `API_TESTING.md` for API examples
- Check `ARCHITECTURE.md` for system design
- Check `PROJECT_SUMMARY.md` for project overview

---

**Your User Service is ready! 🚀**

Start the server and begin testing the APIs!
