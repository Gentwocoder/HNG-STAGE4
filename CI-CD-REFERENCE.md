# CI/CD Pipeline Quick Reference

## 🚀 Pipeline Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Code Push/PR                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  Stage 1: CODE QUALITY & LINTING                           │
│  ├─ Flake8 (Python linting)                                │
│  ├─ Black (Code formatting)                                │
│  └─ isort (Import sorting)                                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  Stage 2: SECURITY SCANNING                                │
│  ├─ Safety (Vulnerability check)                           │
│  └─ Bandit (Security linter)                               │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  Stage 3: TESTING                                          │
│  ├─ Setup PostgreSQL & Redis                              │
│  ├─ Run Django checks                                      │
│  ├─ Apply migrations                                       │
│  ├─ Run pytest with coverage                              │
│  └─ Upload coverage report                                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  Stage 4: BUILD DOCKER IMAGE                               │
│  ├─ Build multi-arch image                                │
│  ├─ Tag (branch, sha, latest)                             │
│  ├─ Push to GitHub Container Registry                     │
│  └─ Cache for faster builds                               │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼────────┐    ┌──────▼───────┐
│  STAGING       │    │ PRODUCTION   │
│  (develop)     │    │ (main/master)│
└───────┬────────┘    └──────┬───────┘
        │                     │
        │                     ├─ Database backup
        ├─ Deploy             ├─ Rolling update
        ├─ Migrate            ├─ Migrate
        ├─ Health check       ├─ Health check (5x)
        └─ Smoke tests        ├─ Smoke tests
                              └─ Auto-rollback (on fail)
```

## 📋 Required GitHub Secrets

### Staging Environment
| Secret | Description | Example |
|--------|-------------|---------|
| `STAGING_HOST` | Server hostname/IP | `staging.example.com` |
| `STAGING_USERNAME` | SSH username | `deploy` |
| `STAGING_SSH_KEY` | Private SSH key | `-----BEGIN OPENSSH...` |
| `STAGING_PORT` | SSH port (optional) | `22` |
| `STAGING_URL` | Service URL | `https://staging.user-service.example.com` |

### Production Environment
| Secret | Description | Example |
|--------|-------------|---------|
| `PROD_HOST` | Server hostname/IP | `prod.example.com` |
| `PROD_USERNAME` | SSH username | `deploy` |
| `PROD_SSH_KEY` | Private SSH key | `-----BEGIN OPENSSH...` |
| `PROD_PORT` | SSH port (optional) | `22` |
| `PROD_URL` | Service URL | `https://user-service.example.com` |


## 🔄 Deployment Triggers

### Automatic Triggers
| Branch | Environment | Trigger |
|--------|-------------|---------|
| `develop` | Staging | Push to develop |
| `main` or `master` | Production | Push to main/master |
| Any branch | Tests only | Pull request |

### Manual Trigger
```bash
# Go to GitHub Actions tab
# Select "User Service CI/CD Pipeline"
# Click "Run workflow"
# Choose branch
```

## ⚡ Quick Commands

### View Pipeline Status
```bash
# GitHub CLI
gh run list --workflow=ci-cd.yml

# View specific run
gh run view <run-id>
```

### Force Re-run
```bash
# Re-run failed jobs
gh run rerun <run-id> --failed

# Re-run all jobs
gh run rerun <run-id>
```

### Cancel Running Pipeline
```bash
gh run cancel <run-id>
```

## 🎯 Pipeline Stages Breakdown

### Stage 1: Lint (~ 2 min)
```yaml
✓ Checkout code
✓ Setup Python 3.11
✓ Install linting tools
✓ Run flake8
✓ Check black formatting
✓ Check isort
```

### Stage 2: Security (~ 2 min)
```yaml
✓ Checkout code
✓ Setup Python 3.11
✓ Install safety & bandit
✓ Check vulnerabilities
✓ Security linting
```

### Stage 3: Test (~ 5 min)
```yaml
✓ Checkout code
✓ Setup Python 3.11
✓ Start PostgreSQL container
✓ Start Redis container
✓ Install dependencies
✓ Django system checks
✓ Run migrations
✓ Run tests with coverage
✓ Upload coverage reports
```

### Stage 4: Build (~ 3 min)
```yaml
✓ Checkout code
✓ Setup Docker Buildx
✓ Login to GHCR
✓ Extract metadata
✓ Build & push image
✓ Cache layers
```

### Stage 5: Deploy Staging (~ 3 min)
```yaml
✓ Checkout code
✓ SSH to staging server
✓ Pull latest code
✓ Pull Docker images
✓ Deploy with zero downtime
✓ Run migrations
✓ Collect static files
✓ Health check
✓ Smoke tests
```

### Stage 6: Deploy Production (~ 5 min)
```yaml
✓ Checkout code
✓ SSH to production server
✓ Create database backup
✓ Pull latest code
✓ Pull Docker images
✓ Rolling update deployment
✓ Run migrations
✓ Collect static files
✓ Health checks (5 attempts)
✓ Smoke tests
✓ Auto-rollback on failure
```

## 🔍 Monitoring Pipeline

### Check Status Badge
Add to README.md:
```markdown
![CI/CD](https://github.com/Gentwocoder/HNG-STAGE4/actions/workflows/ci-cd.yml/badge.svg)
```

### View Logs
1. Go to repository on GitHub
2. Click **Actions** tab
3. Select workflow run
4. Click on specific job
5. View logs

### Download Artifacts
- Coverage reports are uploaded as artifacts
- Download from workflow run page

## ⚠️ Troubleshooting

### Pipeline Fails at Lint
```bash
# Fix locally
cd hngstage4
black core/ hngstage4/
isort core/ hngstage4/
flake8 core/ hngstage4/

# Commit and push
git add .
git commit -m "fix: code formatting"
git push
```

### Pipeline Fails at Tests
```bash
# Run tests locally
cd hngstage4
pytest -v

# Fix issues and push
git add .
git commit -m "fix: test failures"
git push
```

### Deployment Fails
1. Check SSH connection
2. Verify server has enough disk space
3. Check Docker daemon is running
4. Review deployment logs

### Rollback Needed
```bash
# Automatic rollback on production failure

# Manual rollback
ssh deploy@server
cd /app/user-service
git reset --hard HEAD~1
docker-compose up -d --force-recreate
```

## 📊 Performance Metrics

| Stage | Average Time | Status |
|-------|--------------|--------|
| Lint | ~2 min | ✅ Fast |
| Security | ~2 min | ✅ Fast |
| Test | ~5 min | ✅ Good |
| Build | ~3 min | ✅ Good |
| Deploy Staging | ~3 min | ✅ Good |
| Deploy Production | ~5 min | ✅ Good |
| **Total** | **~20 min** | ✅ **Excellent** |

## 🎓 Best Practices

### Before Pushing
```bash
# Run local checks
make lint
make test
make format
```

### Branch Strategy
```
main/master  → Production (auto-deploy)
develop      → Staging (auto-deploy)  
feature/*    → Tests only
hotfix/*     → Tests only
```

### Commit Messages
```
feat: add new feature
fix: fix bug
docs: update documentation
test: add tests
refactor: refactor code
chore: update dependencies
```

### Pull Requests
1. Create feature branch
2. Make changes
3. Push to GitHub
4. Open PR to develop
5. Wait for checks ✅
6. Merge to develop
7. Test on staging
8. Merge to main for production

## 🔒 Security Notes

- SSH keys are encrypted in GitHub Secrets
- No credentials in code or logs
- Database backups before production deploy
- Auto-rollback on production failures
- SSL/TLS for all connections

## 📞 Emergency Contacts

### Pipeline Issues
- Check GitHub Actions logs
- Review deployment guide: `DEPLOYMENT.md`
- Check server logs: `docker-compose logs -f`

### Server Issues
```bash
# SSH to server
ssh deploy@server

# Check services
docker-compose ps
docker-compose logs -f

# Restart if needed
docker-compose restart
```

---

**Pipeline Status**: https://github.com/Gentwocoder/HNG-STAGE4/actions

**Total Pipeline Time**: ~20 minutes from code push to production 🚀
