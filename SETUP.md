# 📚 Dreambook Salon - Complete Setup Guide

A comprehensive guide to set up and run the Dreambook Salon appointment booking system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Running the Application](#running-the-application)
6. [Demo Data](#demo-data)
7. [Frontend Build](#frontend-build)
8. [Troubleshooting](#troubleshooting)
9. [Production Deployment](#production-deployment)
10. [API Endpoints](#api-endpoints)

---

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.10 or higher
- **Node.js**: 14 or higher (for frontend assets)
- **npm**: 6 or higher
- **Database**: PostgreSQL 12+ (recommended for production)

### Required Software

#### Windows
```powershell
# Download and install:
# 1. Python from https://www.python.org/downloads/
# 2. Node.js from https://nodejs.org/
# 3. PostgreSQL from https://www.postgresql.org/download/windows/
# 4. Git from https://git-scm.com/download/win
```

#### macOS
```bash
# Using Homebrew
brew install python@3.10
brew install node
brew install postgresql
brew install git
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
sudo apt install nodejs npm
sudo apt install postgresql postgresql-contrib
sudo apt install git
```

---

## Installation

### Step 1: Clone the Repository

```bash
# HTTPS
git clone https://github.com/property360-2/Dreambook-Salon.git
cd dreambook-salon

# Or SSH
git clone git@github.com:property360-2/Dreambook-Salon.git
cd dreambook-salon
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
venv\Scripts\activate.bat
```

### Step 3: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installation
python -m django --version
```

### Step 4: Install Node.js Dependencies

```bash
# Install frontend dependencies
npm install

# Verify installation
npm --version
node --version
```

---

## Configuration

### Step 1: Create Environment File

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# On Linux/macOS:
nano .env

# On Windows:
notepad .env
```

### Step 2: Configure Environment Variables

Edit `.env` with appropriate values:

```env
# Django Core Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True  # Set to False in production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
# For SQLite (development only - easier to start)
DATABASE_URL=sqlite:///db.sqlite3

# For PostgreSQL (recommended for production)
# DATABASE_URL=postgres://username:password@localhost:5432/salon_db

# CDN and Static Files (optional)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name

# Email Configuration (for notifications)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password

# Application Settings
SITE_NAME=Dreambook Salon
SITE_URL=http://localhost:8000

# Feature Flags
PREVENT_COMPLETION_ON_INSUFFICIENT_STOCK=True
MAX_CONCURRENT_APPOINTMENTS=3
BOOKING_WINDOW_DAYS=30
```

### Step 3: Generate Secret Key

```bash
# Generate a secure secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Copy the output and paste it in .env as SECRET_KEY
```

### Database Setup

#### Option A: SQLite (Development - Recommended for Quick Start)

SQLite is pre-configured in `.env.example`. It creates a local database file:

```bash
# No additional setup needed
# The database will be created when you run migrations
```

**Advantages:**
- Easy to set up
- No external server needed
- Good for development and testing

**Disadvantages:**
- Not suitable for production
- Limited concurrent user support
- Single-user access

#### Option B: PostgreSQL (Production - Recommended)

```bash
# Step 1: Create Database and User (on your PostgreSQL server)
sudo -u postgres psql

# Inside psql:
CREATE DATABASE salon_db;
CREATE USER salon_user WITH PASSWORD 'secure_password_here';
ALTER ROLE salon_user SET client_encoding TO 'utf8';
ALTER ROLE salon_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE salon_user SET default_transaction_deferrable TO on;
ALTER ROLE salon_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE salon_db TO salon_user;
\q

# Step 2: Update .env
DATABASE_URL=postgres://salon_user:secure_password_here@localhost:5432/salon_db

# Step 3: Verify connection
python manage.py dbshell
```

---

## Running the Application

### Step 1: Run Database Migrations

```bash
# Apply all migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations

# Create migration for app changes (if needed)
python manage.py makemigrations app_name
```

### Step 2: Create Superuser (Admin Account)

```bash
python manage.py createsuperuser

# Follow the prompts:
# Username: admin
# Email: admin@example.com
# Password: (enter secure password)
```

### Step 3: Load Demo Data (Optional)

```bash
# Seed with demo data
python manage.py seed_demo

# Output will show:
# Creating users...
# Creating inventory items...
# Creating services...
# Creating appointment settings...
# Creating blocked ranges...
# Creating appointments...
# Creating payments...
# Creating chatbot rules...
# Database seeding completed successfully!
```

**What Gets Created:**
- 5 Users (1 admin, 1 staff, 3 customers)
- 15 Inventory Items
- 14 Services
- 40 Demo Appointments
- 107 Chatbot Rules

### Step 4: Build Frontend Assets

```bash
# Build Tailwind CSS
npm run build:css

# Watch for changes (development)
npm run build:css -- --watch

# Check available scripts
npm run
```

### Step 5: Start Development Server

```bash
# Start Django development server
python manage.py runserver

# Or specify port
python manage.py runserver 0.0.0.0:8000

# Server will be available at http://localhost:8000
```

### Step 6: Access the Application

Open your browser and visit:

| URL | Purpose |
|-----|---------|
| http://localhost:8000 | Main application |
| http://localhost:8000/admin/ | Django admin panel |
| http://localhost:8000/appointments/book/ | Book appointment |
| http://localhost:8000/appointments/my/ | My appointments |

---

## Demo Data

### Demo Credentials

After running `seed_demo`, login with:

#### Admin Account
- **Email**: admin@dreambook.com
- **Password**: admin123
- **Access**: Full system access, user management, analytics

#### Staff Account
- **Email**: staff@dreambook.com
- **Password**: staff123
- **Access**: Appointment management, inventory updates

#### Customer Accounts
- **Email**: customer1@example.com, Password: customer123
- **Email**: customer2@example.com, Password: customer123
- **Email**: customer3@example.com, Password: customer123

### Demo Data Includes

#### Services (14 total)
- Haircut (₱100)
- Hair Spa (₱500)
- Hair Color (₱700)
- Hair & Make-Up (₱1,000)
- Keratin Treatment (₱1,000)
- Botox Hair Treatment (₱1,200)
- Brazilian Hair Treatment (₱1,500)
- Hair Rebond (₱1,500)
- Collagen Treatment (₱2,000)
- Manicure (₱250)
- Pedicure (₱350)
- Facial Treatment (₱600)
- Body Massage (₱800)
- Waxing Service (₱400)

#### Inventory Items (15 total)
- Hair Rebonding Solution
- Hair Coloring Cream
- Shampoo & Conditioner
- Hair Treatment Mask
- Nail Polish & Remover
- Facial Cleanser & Masks
- Massage Oil
- And more...

#### Appointments (40 total)
- 20 Past completed appointments
- 15 Upcoming appointments
- 5 Cancelled appointments

#### Chatbot Rules (107 total)
- Greetings (6 rules)
- Business hours (5 rules)
- Location & directions (5 rules)
- Service details (20+ rules)
- Pricing information (5 rules)
- Booking instructions (7 rules)
- Payment methods (6 rules)
- And 50+ more...

### Clear Demo Data

```bash
# Clear all demo data
python manage.py seed_demo --clear

# This deletes:
# - All appointments
# - All payments
# - All services
# - All inventory items
# - All chatbot rules
# - Demo user accounts
```

---

## Frontend Build

### Tailwind CSS Setup

```bash
# Install dependencies
npm install

# Build CSS once
npm run build:css

# Watch and rebuild on changes (development)
npm run build:css -- --watch
```

### Static Files

```bash
# Collect static files for production
python manage.py collectstatic --noinput

# Check static files
python manage.py findstatic filename
```

---

## Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'django'"

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

#### 2. "Port 8000 already in use"

```bash
# Use different port
python manage.py runserver 8001

# Or kill process using port 8000 (on Linux/macOS)
lsof -ti:8000 | xargs kill -9
```

#### 3. "Database connection refused"

```bash
# Check PostgreSQL is running
sudo service postgresql status

# Or start PostgreSQL
sudo service postgresql start

# Check connection string in .env
DATABASE_URL=postgres://user:password@localhost:5432/dbname
```

#### 4. "Static files not loading"

```bash
# Collect static files
python manage.py collectstatic --noinput

# In development, ensure DEBUG=True in .env
DEBUG=True
```

#### 5. "Migrations not applied"

```bash
# Check migration status
python manage.py showmigrations

# Apply pending migrations
python manage.py migrate

# Create missing migrations
python manage.py makemigrations
python manage.py migrate
```

### Debug Commands

```bash
# Check installed packages
pip list

# Check Django setup
python manage.py check

# Show database info
python manage.py dbshell

# Run tests
pytest

# Run tests with coverage
pytest --cov=.

# Format code
black .

# Check code style
flake8 .
```

---

## Production Deployment

### Pre-Deployment Checklist

```python
# In .env for production:
DEBUG=False
SECRET_KEY=your-very-secure-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgres://user:pass@prod-host:5432/salon_db

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Deploy with Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn salon_system.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Or with systemd service (Linux)
sudo nano /etc/systemd/system/salon.service
```

### Deploy with Docker (Optional)

```bash
# Build Docker image
docker build -t salon-app .

# Run container
docker run -p 8000:8000 salon-app

# With docker-compose
docker-compose up -d
```

### SSL/HTTPS Setup

```python
# In settings.py for production:
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

---

## API Endpoints

### Authentication

```
POST /api/auth/login/
GET  /api/auth/logout/
POST /api/auth/register/
```

### Appointments

```
GET    /api/appointments/             # List appointments
POST   /api/appointments/              # Create appointment
GET    /api/appointments/<id>/         # Get appointment details
PUT    /api/appointments/<id>/         # Update appointment
DELETE /api/appointments/<id>/         # Delete appointment
POST   /api/appointments/api/check-availability/  # Check slot availability
```

### Services

```
GET  /api/services/      # List all services
GET  /api/services/<id>/ # Get service details
```

### Payments

```
POST /api/payments/<appointment_id>/initiate/  # Initiate payment
GET  /api/payments/<id>/                       # Get payment details
```

### Chatbot

```
POST /api/chatbot/query/   # Send message to chatbot
GET  /api/chatbot/rules/   # Get all chatbot rules
```

---

## Project Structure

```
dreambook-salon/
├── appointments/          # Appointment booking system
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── utils.py
├── services/             # Service management
├── payments/             # Payment processing
├── inventory/            # Stock management
├── chatbot/              # AI chatbot system
├── core/                 # User & auth management
├── analytics/            # Statistics & reports
├── templates/            # HTML templates
├── static/               # CSS, JS, images
├── salon_system/         # Django settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py             # Django CLI
├── requirements.txt      # Python dependencies
├── package.json          # Node.js dependencies
├── README.md            # Overview
└── SETUP.md             # This file
```

---

## Development Commands

```bash
# Create app
python manage.py startapp app_name

# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Run development server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic

# Run tests
pytest
pytest tests/test_appointments.py
pytest --cov=appointments

# Format code
black .
black appointments/

# Lint code
flake8 .

# Check for issues
python manage.py check

# Load demo data
python manage.py seed_demo
```

---

## Getting Help

### Documentation
- Django: https://docs.djangoproject.com/
- Tailwind CSS: https://tailwindcss.com/docs
- PostgreSQL: https://www.postgresql.org/docs/

### Community
- Stack Overflow: Tag your questions with `django`
- Django Community: https://www.djangoproject.com/community/
- GitHub Issues: Report bugs and ask questions

### Contact
- Email: contact@dreambook.com
- Phone: (02) 1234-5678
- Hours: Mon-Sat, 9 AM - 6 PM

---

## Next Steps

After successful setup:

1. ✅ Login to admin panel
2. ✅ Explore the dashboard
3. ✅ Create your first service
4. ✅ Test booking process
5. ✅ Configure settings
6. ✅ Customize branding
7. ✅ Set up payment methods
8. ✅ Train on features

---

**Last Updated**: November 2024
**Version**: 1.0.0

For the latest updates, visit: https://github.com/property360-2/Dreambook-Salon
