# Deployment Guide - User Service

## Overview

This guide covers the complete deployment process for the User Service using the CI/CD pipeline.

## CI/CD Pipeline Stages

### 1. **Code Quality & Linting** 
✅ Runs on every push and pull request
- Flake8 linting
- Black code formatting check
- isort import sorting check

### 2. **Security Scanning**
✅ Identifies vulnerabilities
- Safety check for package vulnerabilities
- Bandit security linter

### 3. **Testing**
✅ Comprehensive test suite
- PostgreSQL service container
- Redis service container
- Django system checks
- Database migrations
- Unit tests with coverage
- Coverage reports to Codecov

### 4. **Build Docker Image**
✅ Builds on push events
- Multi-platform Docker build
- GitHub Container Registry (GHCR)
- Automatic tagging (branch, SHA, latest)
- Build caching for speed

### 5. **Deploy to Staging**
✅ Automatic deployment from `develop` branch
- SSH deployment
- Zero-downtime deployment
- Database migrations
- Health checks
- Smoke tests

### 6. **Deploy to Production**
✅ Automatic deployment from `main/master` branch
- Database backup before deployment
- Rolling update strategy
- Zero-downtime deployment
- Health checks with retries
- Automatic rollback on failure
- Post-deployment smoke tests

### 7. **Notifications**
✅ Slack notifications
- Deployment status
- Success/failure alerts

## Prerequisites

### GitHub Secrets Required

#### Staging Environment
```
STAGING_HOST              # staging.example.com
STAGING_USERNAME          # deploy
STAGING_SSH_KEY          # Private SSH key
STAGING_PORT             # 22 (optional)
STAGING_URL              # https://staging.user-service.example.com
```

#### Production Environment
```
PROD_HOST                # prod.example.com
PROD_USERNAME            # deploy
PROD_SSH_KEY             # Private SSH key
PROD_PORT                # 22 (optional)
PROD_URL                 # https://user-service.example.com
```

### Setting Up GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with its value

### Setting Up SSH Access

1. **Generate SSH key pair** on your local machine:
   ```bash
   ssh-keygen -t ed25519 -C "github-actions@user-service" -f ~/.ssh/deploy_key
   ```

2. **Add public key to server**:
   ```bash
   ssh-copy-id -i ~/.ssh/deploy_key.pub user@server
   # Or manually add to ~/.ssh/authorized_keys
   ```

3. **Add private key to GitHub Secrets**:
   ```bash
   cat ~/.ssh/deploy_key
   # Copy the entire output including header/footer
   ```

## Server Setup

### 1. Initial Server Configuration

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Create deploy user
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy
sudo usermod -aG sudo deploy

# Create application directory
sudo mkdir -p /app/user-service
sudo chown deploy:deploy /app/user-service
```

### 2. Clone Repository on Server

```bash
# SSH into server as deploy user
ssh deploy@your-server

# Clone repository
cd /app
git clone https://github.com/Gentwocoder/HNG-STAGE4.git user-service
cd user-service/hngstage4

# Create .env file
cp .env.example .env
# Edit .env with production values
nano .env
```

### 3. Configure Environment Variables

Create `/app/user-service/hngstage4/.env`:

```bash
# Django Settings
SECRET_KEY=your-super-secret-production-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (PostgreSQL)
USE_POSTGRES=True
DB_NAME=user_service_db
DB_USER=postgres
DB_PASSWORD=your-secure-db-password
DB_HOST=db
DB_PORT=5432

# Redis
USE_REDIS=True
REDIS_URL=redis://redis:6379/1

# JWT
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7

# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend.com

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=your-rabbitmq-password

# Logging
LOG_LEVEL=INFO

# Service
PORT=8000
```

### 4. Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 5. Initial Database Setup

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

## Nginx Configuration (Reverse Proxy)

### Install Nginx

```bash
sudo apt install nginx -y
```

### Configure Nginx

Create `/etc/nginx/sites-available/user-service`:

```nginx
upstream user_service {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000" always;
    
    # Max upload size
    client_max_body_size 10M;
    
    # Static files
    location /static/ {
        alias /app/user-service/hngstage4/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /app/user-service/hngstage4/media/;
        expires 7d;
    }
    
    # Proxy to Django
    location / {
        proxy_pass http://user_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check (no logging)
    location /api/v1/users/health/ {
        access_log off;
        proxy_pass http://user_service;
    }
}
```

### Enable Site

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/user-service /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## Deployment Workflow

### Staging Deployment

1. **Push to develop branch**:
   ```bash
   git checkout develop
   git add .
   git commit -m "feat: new feature"
   git push origin develop
   ```

2. **GitHub Actions automatically**:
   - Runs tests
   - Builds Docker image
   - Deploys to staging
   - Runs health checks
   - Sends notifications

3. **Verify deployment**:
   ```bash
   curl https://staging.user-service.example.com/api/v1/users/health/
   ```

### Production Deployment

1. **Merge to main/master**:
   ```bash
   git checkout main
   git merge develop
   git push origin main
   ```

2. **GitHub Actions automatically**:
   - Runs tests
   - Builds Docker image
   - Creates database backup
   - Deploys with zero downtime
   - Runs migrations
   - Runs health checks
   - Rolls back on failure
   - Sends notifications

3. **Verify deployment**:
   ```bash
   curl https://user-service.example.com/api/v1/users/health/
   ```

## Manual Deployment (Fallback)

### Deploy Manually

```bash
# SSH into server
ssh deploy@your-server

# Navigate to app directory
cd /app/user-service

# Pull latest changes
git pull origin main

# Rebuild and restart services
docker-compose down
docker-compose up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check health
curl http://localhost:8000/api/v1/users/health/
```

## Monitoring & Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail=100 web
```

### Database Backup

```bash
# Manual backup
docker-compose exec db pg_dump -U postgres user_service_db > backup.sql

# Automated daily backups (add to cron)
0 2 * * * cd /app/user-service && docker-compose exec -T db pg_dump -U postgres user_service_db > backups/backup_$(date +\%Y\%m\%d).sql
```

### Database Restore

```bash
# Restore from backup
docker-compose exec -T db psql -U postgres user_service_db < backup.sql
```

### Service Status

```bash
# Check service status
docker-compose ps

# Check resource usage
docker stats

# Check disk space
df -h
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart web

# Recreate services
docker-compose up -d --force-recreate
```

## Rollback Procedure

### Automatic Rollback

The CI/CD pipeline automatically rolls back on deployment failure.

### Manual Rollback

```bash
# SSH into server
ssh deploy@your-server
cd /app/user-service

# Revert to previous commit
git log --oneline -5  # Find commit to rollback to
git reset --hard <commit-hash>

# Restart services
docker-compose down
docker-compose up -d --build

# Restore database if needed
docker-compose exec -T db psql -U postgres user_service_db < backups/backup_YYYYMMDD.sql
```

## Troubleshooting

### Deployment Fails

1. Check GitHub Actions logs
2. Verify SSH connection:
   ```bash
   ssh deploy@your-server
   ```
3. Check server disk space:
   ```bash
   df -h
   ```
4. Check Docker status:
   ```bash
   docker-compose ps
   ```

### Health Check Fails

1. Check application logs:
   ```bash
   docker-compose logs web
   ```
2. Check database connection:
   ```bash
   docker-compose exec web python manage.py check --database default
   ```
3. Check Redis connection:
   ```bash
   docker-compose exec web python manage.py shell
   >>> from django.core.cache import cache
   >>> cache.set('test', 'value')
   >>> cache.get('test')
   ```

### Database Migration Issues

```bash
# Check migration status
docker-compose exec web python manage.py showmigrations

# Fake a migration if needed
docker-compose exec web python manage.py migrate --fake <app_name> <migration_name>

# Reset migrations (CAUTION: data loss)
docker-compose exec web python manage.py migrate <app_name> zero
```

## Performance Optimization

### Enable Docker Build Cache

Already configured in CI/CD pipeline.

### Scale Services

```bash
# Scale web service
docker-compose up -d --scale web=3

# Use load balancer (Nginx upstream)
```

### Database Optimization

```bash
# Vacuum database
docker-compose exec db vacuumdb -U postgres -d user_service_db -v

# Analyze database
docker-compose exec db psql -U postgres -d user_service_db -c "ANALYZE;"
```

## Security Checklist

- [x] SECRET_KEY is strong and unique
- [x] DEBUG is False in production
- [x] ALLOWED_HOSTS is configured
- [x] SSL/TLS certificates installed
- [x] Database credentials are secure
- [x] SSH keys are properly configured
- [x] Firewall is enabled (UFW)
- [x] Regular backups are automated
- [x] Logs are monitored
- [x] Security updates are applied

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Nginx Security Guide](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

## Support

For deployment issues:
1. Check GitHub Actions logs
2. Review server logs
3. Check `PROJECT_SUMMARY.md`
4. Create an issue in the repository

---

**Your User Service is production-ready! 🚀**

Deploy with confidence using the automated CI/CD pipeline.
