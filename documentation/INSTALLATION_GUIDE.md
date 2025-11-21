# Installation & Setup Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Step-by-Step Installation](#step-by-step-installation)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Running the Project](#running-the-project)
6. [Troubleshooting](#troubleshooting)
7. [Production Deployment](#production-deployment)

---

## System Requirements

### Minimum Requirements
- **Python**: 3.10 or higher
- **Node.js**: 14.0 or higher
- **npm**: 6.0 or higher
- **Database**: SQLite3 (included) or PostgreSQL
- **RAM**: 2GB minimum, 4GB recommended
- **Disk Space**: 500MB for project + dependencies

### Supported Platforms
- **macOS**: 10.14+
- **Windows**: 10+ (including WSL2)
- **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 9+

### Required Software
```bash
# Check Python version
python --version        # Should be 3.10+

# Check Node.js version
node --version          # Should be 14.0+
npm --version           # Should be 6.0+

# Check pip
pip --version           # Python 3.10+ pip
```

---

## Step-by-Step Installation

### Step 1: Clone Repository

```bash
# Clone the project
git clone <repository-url>
cd Dreambook-Salon

# Verify directory structure
ls -la
# Should see: chatbot/, services/, payments/, etc.
```

### Step 2: Create Virtual Environment

**On macOS/Linux**:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show "venv" in prompt)
```

**On Windows**:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (should show "(venv)" in prompt)
```

### Step 3: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install from requirements.txt
pip install -r requirements.txt

# Verify installation
pip list | grep -E "Django|anthropic|psycopg"

# Should output:
# Django                5.2.8
# anthropic            ...
# psycopg              ...
```

### Step 4: Install Frontend Dependencies

```bash
# Install Node packages
npm install

# Verify (should see node_modules folder)
ls node_modules | head -10
```

### Step 5: Build CSS

```bash
# Build Tailwind CSS
npm run build:css

# Check output file was created
ls -lh static/css/output.css

# Should show a file > 100KB
```

### Step 6: Environment Configuration

**Create `.env` file in project root**:

```bash
# Create .env file
cat > .env << 'EOF'
# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (default is SQLite)
DATABASE_URL=sqlite:///db.sqlite3
# For PostgreSQL: postgresql://user:password@localhost/dbname

# Anthropic Claude API (optional but recommended)
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# Email Configuration (for password resets)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# For Gmail:
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password

# Application Settings
SITE_NAME=Dreambook Salon
SITE_URL=http://localhost:8000

# Payment Demo Settings
DEMO_PAYMENT_MODE=deterministic  # or "random"
DEMO_PAYMENT_SUCCESS_RATE=0.8

# Feature Flags
PREVENT_COMPLETION_ON_INSUFFICIENT_STOCK=True
MAX_CONCURRENT_APPOINTMENTS=3
BOOKING_WINDOW_DAYS=30
EOF

# Verify .env was created
cat .env
```

### Step 7: Database Setup

```bash
# Run migrations
python manage.py migrate

# Should see output like:
# Running migrations:
#   Applying contenttypes.0001_initial...
#   Applying auth.0001_initial...
#   ...
#   Applying chatbot.0001_initial...
#   ...
```

### Step 8: Create Superuser (Admin Account)

```bash
# Create superuser
python manage.py createsuperuser

# Follow prompts:
# Email address: admin@example.com
# Password: (enter secure password)
# Password (again): (confirm password)

# Superuser created successfully!
```

### Step 9: Load Demo Data (Optional)

```bash
# Load demo data
python manage.py seed_demo

# Output:
# Creating demo users...
# Creating demo services...
# Creating demo appointments...
# Demo data loaded successfully!

# To clear and reload:
python manage.py seed_demo --clear
```

### Step 10: Collect Static Files

```bash
# Collect static files for production
python manage.py collectstatic --noinput

# Output should show:
# ...
# 1234 static files copied to 'staticfiles'
```

---

## Configuration

### Environment Variables Explained

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | True | Show detailed error pages (set False in production) |
| `SECRET_KEY` | - | Django secret key (change in production!) |
| `ALLOWED_HOSTS` | localhost,127.0.0.1 | Hosts allowed to serve |
| `DATABASE_URL` | sqlite:///db.sqlite3 | Database connection string |
| `ANTHROPIC_API_KEY` | - | Claude API key (optional) |
| `EMAIL_BACKEND` | console | Email backend type |
| `DEMO_PAYMENT_MODE` | deterministic | Payment simulation mode |

### Django Settings

Edit `salon_system/settings.py` for:
- **Timezone**: `TIME_ZONE = 'UTC'` or `'Asia/Manila'`
- **Language**: `LANGUAGE_CODE = 'en-us'`
- **Static Files**: `STATIC_URL = '/static/'`
- **Media Files**: `MEDIA_URL = '/media/'`
- **Session Timeout**: `SESSION_COOKIE_AGE = 1209600` (2 weeks)

### API Keys Setup

#### Anthropic Claude API
1. Visit https://console.anthropic.com/
2. Sign up or log in
3. Create API key
4. Copy to `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

#### Email Configuration (Gmail)
1. Enable 2-Factor Authentication
2. Generate App Password
3. Add to `.env`:
```bash
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## Database Setup

### SQLite (Default - Development)

Already configured, no additional setup needed:
```bash
DATABASE_URL=sqlite:///db.sqlite3
```

### PostgreSQL (Production)

```bash
# Install PostgreSQL
# macOS: brew install postgresql
# Ubuntu: apt-get install postgresql
# Windows: Download from postgresql.org

# Create database
createdb dreambook_salon

# Create user
createuser dreambook_user --pwprompt

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dreambook_salon TO dreambook_user;"

# Update .env
DATABASE_URL=postgresql://dreambook_user:password@localhost:5432/dreambook_salon

# Install Python PostgreSQL driver
pip install psycopg2-binary

# Run migrations
python manage.py migrate
```

---

## Running the Project

### Development Server

```bash
# Start Django development server
python manage.py runserver

# Access at: http://localhost:8000
# Admin panel: http://localhost:8000/admin

# With custom port:
python manage.py runserver 8080

# With all interfaces (network):
python manage.py runserver 0.0.0.0:8000
```

### Access Points

| URL | Purpose | Requires Auth |
|-----|---------|---|
| http://localhost:8000/ | Home page | No |
| http://localhost:8000/admin/ | Admin panel | Yes (staff) |
| http://localhost:8000/dashboard/ | User dashboard | Yes |
| http://localhost:8000/appointments/book/ | Book appointment | No |
| http://localhost:8000/services/ | View services | No |
| http://localhost:8000/chatbot/ | AI chatbot | No |
| http://localhost:8000/analytics/ | Analytics | Yes (staff) |

### Demo Credentials

After running `python manage.py seed_demo`:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@dreambook.com | admin123 |
| Staff | staff@dreambook.com | staff123 |
| Customer 1 | customer1@example.com | customer123 |
| Customer 2 | customer2@example.com | customer123 |

**Note**: Change these passwords in production!

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_chatbot.py

# Run with coverage
pytest --cov=chatbot tests/

# Run specific test function
pytest tests/test_chatbot.py::test_intent_detection

# Verbose output
pytest -v

# Show print statements
pytest -s
```

### Building Frontend Assets

```bash
# Watch CSS changes
npm run watch:css

# Build for production (minified)
npm run build:css

# Check if output is minified
wc -c static/css/output.css  # Should be much smaller than input
```

---

## Troubleshooting

### Python/Virtual Environment Issues

**Problem**: `python: command not found`
```bash
# Solution: Use python3 on macOS/Linux
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

**Problem**: `ModuleNotFoundError: No module named 'django'`
```bash
# Solution: Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Database Issues

**Problem**: `sqlite3.DatabaseError: database is locked`
```bash
# Solution: Delete and recreate database
rm db.sqlite3
python manage.py migrate
```

**Problem**: `ProgrammingError: relation "chatbot_conversation" does not exist`
```bash
# Solution: Run migrations
python manage.py migrate
python manage.py migrate chatbot
```

### Claude API Issues

**Problem**: `ANTHROPIC_API_KEY environment variable not set`
```bash
# Solution: Add to .env
ANTHROPIC_API_KEY=sk-ant-your-key

# Verify
python -c "import os; print(os.getenv('ANTHROPIC_API_KEY'))"
```

**Problem**: `RateLimitError: 429 Too Many Requests`
```bash
# Solution: Wait and retry, or upgrade API plan
# Check usage: https://console.anthropic.com/account/usage
```

### Static Files Issues

**Problem**: CSS not loading (404 errors)
```bash
# Solution: Rebuild CSS
npm run build:css

# Verify file exists
ls -lh static/css/output.css

# Check DEBUG setting
cat salon_system/settings.py | grep DEBUG
```

**Problem**: Images not displaying
```bash
# Solution: Collect static files
python manage.py collectstatic --noinput

# Check STATIC_URL and STATIC_ROOT
```

### Port Already in Use

**Problem**: `Address already in use: :8000`
```bash
# Solution 1: Use different port
python manage.py runserver 8080

# Solution 2: Kill process using port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## Production Deployment

### Pre-Deployment Checklist

```bash
# 1. Security checks
DEBUG=False                          # Disable debug mode
SECRET_KEY=<generate-new-secure>    # Generate new secret key

# 2. Database
DATABASE_URL=postgresql://...       # Use PostgreSQL
python manage.py migrate            # Run migrations

# 3. Static files
npm run build:css                   # Build minified CSS
python manage.py collectstatic      # Collect all static files

# 4. Environment
ALLOWED_HOSTS=yourdomain.com        # Set production domain
SECURE_SSL_REDIRECT=True            # Force HTTPS
SESSION_COOKIE_SECURE=True          # Secure session cookies

# 5. Email
EMAIL_BACKEND=smtp backend          # Configure real email

# 6. API Keys
ANTHROPIC_API_KEY=<your-key>        # Set Claude API key
```

### Deployment Platforms

#### Heroku
```bash
# Install Heroku CLI
# Create app
heroku create dreambook-salon

# Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=<new-key>
heroku config:set ANTHROPIC_API_KEY=<key>

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Access
heroku open
```

#### PythonAnywhere
1. Create account at pythonanywhere.com
2. Upload code via Git or ZIP
3. Configure virtual environment
4. Set up WSGI file
5. Configure domain

#### DigitalOcean/AWS/Google Cloud
```bash
# Typical deployment steps
1. Create VPS
2. Install Python, Node.js, PostgreSQL
3. Clone repository
4. Setup virtual environment
5. Configure gunicorn/nginx
6. Setup SSL certificate (Let's Encrypt)
7. Configure supervisor/systemd for auto-restart
```

### WSGI Application (for production)

```python
# salon_system/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'salon_system.settings')
application = get_wsgi_application()
```

### Running with Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run application
gunicorn salon_system.wsgi:application --bind 0.0.0.0:8000 --workers 4

# With supervisor for auto-restart
# Create /etc/supervisor/conf.d/dreambook.conf
```

---

## Verification Checklist

After installation, verify everything works:

```bash
# 1. Virtual environment is activated
echo $VIRTUAL_ENV  # Should show path to venv

# 2. Dependencies are installed
pip list | wc -l  # Should show 50+ packages

# 3. Database exists and migrations are applied
ls -lh db.sqlite3  # Should exist
python manage.py showmigrations  # Should show all migrated

# 4. Static files are collected
ls -lh static/css/output.css  # Should be > 100KB

# 5. Environment variables are set
echo $ANTHROPIC_API_KEY  # Should show key (or be empty if not needed)

# 6. Server starts successfully
python manage.py runserver  # Should show "Starting development server"

# 7. Access application
curl http://localhost:8000  # Should return HTML (not 500 error)

# 8. Admin panel is accessible
curl http://localhost:8000/admin  # Should redirect to login

# 9. API endpoints work
curl -X POST http://localhost:8000/api/chatbot/respond/ \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'  # Should return JSON

# 10. Database has data
python manage.py dbshell  # sqlite> select count(*) from services_service;
```

---

## Next Steps

After successful installation:

1. **Read Documentation**
   - Start with `README.md`
   - Review `LLM_INTEGRATION.md`
   - Study `FORECASTING.md`

2. **Explore Admin Panel**
   - Create services
   - Manage users
   - Configure settings

3. **Test Features**
   - Book appointment
   - Test chatbot
   - View analytics

4. **Customize**
   - Add your business data
   - Configure salon hours
   - Upload service images

5. **Deploy**
   - Choose hosting platform
   - Configure production settings
   - Deploy to cloud

---

## Support Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **Anthropic Claude Docs**: https://docs.anthropic.com/
- **Tailwind CSS Docs**: https://tailwindcss.com/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Project Issues**: Check GitHub issues
- **Community Help**: Django forums, Stack Overflow

---

**Last Updated**: November 2025
**Version**: 1.0.0
