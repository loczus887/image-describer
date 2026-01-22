# Production Setup Guide

This guide covers deploying the Image Describer application to a production environment.

## Table of Contents

1. [HTTPS Configuration](#https-configuration)
2. [Environment Variables](#environment-variables)
3. [Security Hardening](#security-hardening)
4. [Performance Optimization](#performance-optimization)
5. [Monitoring & Logging](#monitoring--logging)
6. [Backup & Recovery](#backup--recovery)

---

## HTTPS Configuration

### Option 1: Self-Signed Certificate (Development/Testing Only)

Generate a self-signed certificate:

```bash
# Generate private key and certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout key.pem \
  -out cert.pem \
  -days 365 \
  -subj "/CN=localhost"
```

Run backend with HTTPS:

```bash
uvicorn backend.api_controller:app \
  --host 0.0.0.0 \
  --port 8000 \
  --ssl-keyfile=key.pem \
  --ssl-certfile=cert.pem
```

### Option 2: Let's Encrypt (Production)

Install Certbot:

```bash
# Ubuntu/Debian
sudo apt-get install certbot

# macOS
brew install certbot
```

Obtain certificate:

```bash
sudo certbot certonly --standalone -d yourdomain.com
```

Certificates will be saved to:
- Certificate: `/etc/letsencrypt/live/yourdomain.com/fullchain.pem`
- Private Key: `/etc/letsencrypt/live/yourdomain.com/privkey.pem`

Run backend with Let's Encrypt:

```bash
uvicorn backend.api_controller:app \
  --host 0.0.0.0 \
  --port 8000 \
  --ssl-keyfile=/etc/letsencrypt/live/yourdomain.com/privkey.pem \
  --ssl-certfile=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
```

### Option 3: Reverse Proxy with Nginx (Recommended)

Install Nginx:

```bash
sudo apt-get install nginx
```

Create Nginx configuration:

```nginx
# /etc/nginx/sites-available/image-describer
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeouts for AI processing
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Frontend
    location / {
        root /var/www/image-describer/dist;
        try_files $uri $uri/ /index.html;
    }

    # File upload size limit
    client_max_body_size 5M;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/image-describer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Environment Variables

Create a production `.env` file in the `backend/` directory:

```bash
# backend/.env

# JWT Configuration (REQUIRED)
JWT_SECRET_KEY=<generate-secure-random-key-here>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# SMTP Configuration (Optional - for email notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourdomain.com

# Database (Optional - defaults to SQLite)
DATABASE_URL=sqlite:///./image_describer.db

# CORS (Optional - restrict origins in production)
ALLOWED_ORIGINS=https://yourdomain.com
```

### Generate Secure JWT Secret

```python
import secrets
print(secrets.token_urlsafe(32))
# Copy the output to JWT_SECRET_KEY
```

---

## Security Hardening

### 1. CORS Configuration

Update `backend/api_controller.py` to restrict CORS origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domain only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 2. Rate Limiting

Install slowapi:

```bash
pip install slowapi
```

Add to `backend/api_controller.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/login")
@limiter.limit("5/minute")  # 5 login attempts per minute
async def login(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    # ...
```

### 3. Secure Headers

Install secure:

```bash
pip install secure
```

Add middleware:

```python
from secure import Secure

secure_headers = Secure()

@app.middleware("http")
async def set_secure_headers(request, call_next):
    response = await call_next(request)
    secure_headers.framework.fastapi(response)
    return response
```

### 4. Password Policy

Update `backend/services/auth_service.py`:

```python
def validate_password(self, password: str) -> Tuple[bool, Optional[str]]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, None
```

### 5. Token Blacklist (Optional)

For logout token invalidation, implement Redis-based token blacklist:

```bash
pip install redis
```

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def blacklist_token(token: str):
    redis_client.setex(f"blacklist:{token}", 1800, "1")  # 30 min

def is_token_blacklisted(token: str) -> bool:
    return redis_client.exists(f"blacklist:{token}")
```

---

## Performance Optimization

### 1. Gunicorn for Production

Install Gunicorn:

```bash
pip install gunicorn
```

Run with multiple workers:

```bash
gunicorn backend.api_controller:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300
```

### 2. Database Connection Pooling

For SQLite, consider switching to PostgreSQL for production:

```python
# backend/data/database.py
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/image_describer")

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### 3. AI Model Optimization

Load model at startup (not per request):

```python
# backend/api_controller.py
@app.on_event("startup")
async def startup_event():
    from .services.ai_model_integration import AIModelIntegration
    global ai_model
    ai_model = AIModelIntegration()
    ai_model.loadModel()  # Pre-load model
```

### 4. Frontend Build Optimization

Build for production:

```bash
cd frontend
npm run build
```

Enable gzip compression in Nginx:

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;
gzip_min_length 1000;
```

---

## Monitoring & Logging

### 1. Application Logging

Configure structured logging:

```python
# backend/utils/logger.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_data)

logger = logging.getLogger("image_describer")
handler = logging.FileHandler("app.log")
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### 2. Prometheus Metrics (Optional)

Install prometheus-fastapi-instrumentator:

```bash
pip install prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### 3. Health Check

Already implemented at `/health` endpoint. Monitor with:

```bash
curl https://yourdomain.com/api/health
```

### 4. Uptime Monitoring

Use services like:
- UptimeRobot
- Pingdom
- StatusCake

---

## Backup & Recovery

### 1. Database Backup

Create backup script:

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/image-describer"
DB_FILE="image_describer.db"

mkdir -p "$BACKUP_DIR"
cp "$DB_FILE" "$BACKUP_DIR/image_describer_$DATE.db"

# Keep only last 7 days
find "$BACKUP_DIR" -name "*.db" -mtime +7 -delete
```

Schedule with cron:

```bash
# Run backup daily at 2 AM
0 2 * * * /path/to/backup.sh
```

### 2. Automated Testing

Run tests before deployment:

```bash
# Backend tests
pytest backend/tests/

# Frontend tests
npm run test
```

### 3. Rollback Strategy

Tag releases:

```bash
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0
```

Rollback if needed:

```bash
git checkout v1.0.0
# Rebuild and redeploy
```

---

## Deployment Checklist

Before deploying to production:

- [ ] HTTPS configured with valid certificate
- [ ] JWT_SECRET_KEY changed to secure random value
- [ ] CORS origins restricted to production domain
- [ ] Rate limiting enabled on sensitive endpoints
- [ ] Database backups configured
- [ ] Monitoring and logging set up
- [ ] .env file secured (not in version control)
- [ ] Frontend built for production (`npm run build`)
- [ ] Backend running with Gunicorn/multiple workers
- [ ] Nginx reverse proxy configured
- [ ] Firewall rules configured (only 80/443 open)
- [ ] Error pages customized
- [ ] Security headers enabled
- [ ] Load testing completed
- [ ] SSL Labs test passed (A+ rating)

---

## Troubleshooting

### HTTPS Certificate Issues

```bash
# Check certificate validity
openssl x509 -in cert.pem -text -noout

# Test HTTPS endpoint
curl -v https://yourdomain.com/api/health
```

### Permission Errors

```bash
# Ensure correct file ownership
sudo chown -R www-data:www-data /var/www/image-describer

# Ensure correct permissions
sudo chmod 755 /var/www/image-describer
```

### Database Locked

If using SQLite with multiple workers:

```python
# Switch to PostgreSQL for production
DATABASE_URL = "postgresql://user:pass@localhost/image_describer"
```

---

## Support

For issues or questions:
- GitHub Issues: [Your repository URL]
- Documentation: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- Requirements Check: [REQUIREMENTS_CHECK.md](REQUIREMENTS_CHECK.md)
