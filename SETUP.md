# Dreambook Salon - Setup Guide

This guide will walk you through setting up the Dreambook Salon Management System on your local machine.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Creating Your First User](#creating-your-first-user)
- [Loading Sample Data](#loading-sample-data)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** and npm - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **PostgreSQL 14+** (optional, for production) - [Download PostgreSQL](https://www.postgresql.org/download/)

### Verify Installation

```bash
python --version  # Should show Python 3.10 or higher
node --version    # Should show Node.js 18 or higher
npm --version     # Should show npm version
git --version     # Should show git version
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/property360-2/Dreambook-Salon.git
cd Dreambook-Salon
```

### 2. Create Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt when the virtual environment is activated.

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Node.js Dependencies

```bash
npm install
```

### 5. Build Tailwind CSS

```bash
npm run build:css
```

For development with auto-rebuild on file changes:
```bash
npm run watch:css
```

## Database Setup

### Option 1: SQLite (Development - Easiest)

SQLite requires no additional setup. The database file will be created automatically.

### Option 2: PostgreSQL (Production - Recommended)

1. **Install PostgreSQL** (if not already installed)

2. **Create Database and User**

```bash
# Access PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE salon_db;

# Create user with password
CREATE USER salon_user WITH PASSWORD 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE salon_db TO salon_user;

# Exit PostgreSQL
\q
```

## Environment Configuration

### 1. Create Environment File

Copy the example environment file:

```bash
# On Windows
copy .env.example .env

# On macOS/Linux
cp .env.example .env
```

### 2. Edit Environment Variables

Open `.env` in your text editor and configure:

#### Essential Settings

```env
# Django Core
SECRET_KEY=your-unique-secret-key-here-change-this
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database - Choose ONE option:

# Option 1: SQLite (Development)
DATABASE_URL=sqlite:///db.sqlite3

# Option 2: PostgreSQL (Production)
# DATABASE_URL=postgres://salon_user:your_secure_password@localhost:5432/salon_db
```

#### Generate a Secret Key

Run this command to generate a secure secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste it as your `SECRET_KEY` in `.env`.

#### Optional Settings

```env
# Email Configuration (for notifications)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password

# Application Settings
SITE_NAME=Dreambook Salon
SITE_URL=http://localhost:8000

# Feature Flags
PREVENT_COMPLETION_ON_INSUFFICIENT_STOCK=True
MAX_CONCURRENT_APPOINTMENTS=3
BOOKING_WINDOW_DAYS=30
```

## Running the Application

### 1. Run Database Migrations

```bash
python manage.py migrate
```

This creates all necessary database tables.

### 2. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 3. Start the Development Server

```bash
python manage.py runserver
```

The application will be available at: **http://localhost:8000**

### 4. Open in Browser

Navigate to http://localhost:8000 in your web browser.

## Creating Your First User

### Create a Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to set:
- Username
- Email
- Password

### Access Admin Panel

Visit http://localhost:8000/admin and log in with your superuser credentials.

### Create Additional Users

You can create users through the admin panel or by registering through the application.

**User Roles:**
- `CUSTOMER` - Can book appointments and view their own data
- `STAFF` - Can manage appointments, services, and inventory
- `ADMIN` - Full system access including analytics and user management

## Loading Sample Data

To populate your database with sample data for testing:

### Option 1: Django Admin

1. Log in to http://localhost:8000/admin
2. Create entries for:
   - Services (hair treatments, spa services, etc.)
   - Inventory items (products, supplies)
   - Service-Inventory associations

### Option 2: Django Shell

```bash
python manage.py shell
```

Then run:

```python
from services.models import Service, Category
from inventory.models import Item
from decimal import Decimal

# Create sample category
category = Category.objects.create(
    name="Hair Treatment",
    description="Professional hair care services"
)

# Create sample service
service = Service.objects.create(
    name="Hair Spa Treatment",
    category=category,
    description="Deep conditioning and relaxing hair treatment",
    duration=90,
    price=Decimal('1500.00')
)

# Create sample inventory item
item = Item.objects.create(
    name="Hair Conditioner",
    description="Professional grade deep conditioner",
    unit="ml",
    stock=Decimal('5000'),
    threshold=Decimal('1000'),
    cost_per_unit=Decimal('2.50')
)

print("Sample data created successfully!")
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

If port 8000 is already in use:

```bash
# Use a different port
python manage.py runserver 8080
```

#### 2. Migration Errors

If you encounter migration errors:

```bash
# Reset migrations (WARNING: This will delete data!)
python manage.py migrate --run-syncdb
```

#### 3. Static Files Not Loading

Rebuild Tailwind CSS:

```bash
npm run build:css
python manage.py collectstatic --noinput
```

Clear browser cache and hard reload (Ctrl+Shift+R or Cmd+Shift+R).

#### 4. Module Not Found Errors

Ensure virtual environment is activated and dependencies are installed:

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### 5. Database Connection Errors

For PostgreSQL:
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists

```bash
# Check PostgreSQL status
# Windows
pg_ctl status

# macOS
brew services list | grep postgresql

# Linux
sudo systemctl status postgresql
```

#### 6. Node.js / npm Errors

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Getting Help

If you encounter issues not covered here:

1. Check the [TODO.md](TODO.md) for known issues
2. Review error messages carefully
3. Check Django documentation: https://docs.djangoproject.com/
4. Check Tailwind CSS documentation: https://tailwindcss.com/docs

## Next Steps

Once your setup is complete:

1. **Explore the Application**
   - Create services and inventory items
   - Set up your business profile
   - Test the booking flow

2. **Customize Settings**
   - Configure email notifications
   - Adjust business hours
   - Set up payment options

3. **Review Documentation**
   - [README.md](README.md) - Project overview
   - [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical details
   - [UI_UX_IMPROVEMENTS.md](UI_UX_IMPROVEMENTS.md) - Design guidelines

## Development Workflow

### Daily Development

```bash
# 1. Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 2. Start Tailwind CSS watcher (in one terminal)
npm run watch:css

# 3. Start Django server (in another terminal)
python manage.py runserver
```

### Making Changes

1. **Models:** After changing models, create and run migrations
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Static Files:** Rebuild CSS after template changes
   ```bash
   npm run build:css
   ```

3. **Templates:** Changes are reflected immediately (just refresh browser)

### Code Quality

Run code formatters and linters:

```bash
# Format Python code
black .
isort .

# Lint Python code
flake8

# Format Django templates
djlint --reformat templates/
```

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Configure proper `ALLOWED_HOSTS`
3. Use PostgreSQL instead of SQLite
4. Set up proper email backend
5. Configure static file serving (WhiteNoise or CDN)
6. Use environment-specific secret keys
7. Enable HTTPS
8. Set up proper logging

See Django deployment documentation for detailed guidance: https://docs.djangoproject.com/en/5.0/howto/deployment/

---

**Congratulations!** Your Dreambook Salon system is now set up and ready to use. 🎉
