# 💇 Dreambook Salon Management System

A comprehensive salon management system built with Django and Tailwind CSS, featuring appointment booking, inventory management, payment processing, analytics with forecasting, and an AI-powered chatbot assistant with Filipino/Taglish support.

## 🌟 Features

### Customer Features
- **Online Booking** - Browse services and book appointments 24/7
- **Service Catalog** - View detailed service descriptions, pricing, and duration
- **Appointment Management** - View, reschedule, or cancel bookings
- **Payment Processing** - Secure payment options (Cash, GCash, Credit/Debit Card, Bank Transfer)
- **Booking History** - Track past and upcoming appointments
- **AI Chatbot Assistant** - Get help with booking, inquiries in English, Filipino, or Taglish

### Staff & Admin Features
- **Dashboard** - Comprehensive business overview with key metrics
- **Appointment Management** - View, confirm, and manage customer bookings
- **Service Management** - Full CRUD for services and categories
- **Inventory Management** - Track stock levels, restock items, adjust quantities
- **Inventory-Service Linking** - Associate products with services for automatic stock deduction
- **Payment Tracking** - Record and manage payments with multiple methods
- **Customer Database** - View customer history and preferences
- **Low Stock Alerts** - Automatic notifications for items below threshold
- **Role-Based Access** - Different permissions for Staff and Admin users

### Analytics & Business Intelligence
- **Revenue Analytics** - Track daily, weekly, and monthly revenue
- **Service Performance** - Identify top-performing services
- **Appointment Statistics** - Monitor booking trends and patterns
- **Inventory Analytics** - View stock levels and usage patterns
- **Payment Method Breakdown** - Analyze payment preferences
- **Forecasting with Holt-Winters** - 14-day revenue and demand predictions
- **Seasonality Analysis** - Detect weekly patterns and trends
- **Peak Period Detection** - Identify busiest hours and days
- **Growth Metrics** - Track business growth over time
- **KPI Dashboard** - Monitor key performance indicators

### Technical Features
- **Responsive Design** - Mobile-first UI with Tailwind CSS
- **Role-Based Authentication** - Customer, Staff, and Admin roles
- **Asynchronous Operations** - AJAX-powered forms with toast notifications
- **Soft Delete Pattern** - Preserve data integrity
- **Time Series Forecasting** - Advanced ETS algorithm implementation
- **Modern UI/UX** - Gradient accents, smooth animations, intuitive navigation
- **RESTful Architecture** - Clean, maintainable Django codebase

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ (optional, SQLite works for development)

### Installation

```bash
# Clone the repository
git clone https://github.com/property360-2/Dreambook-Salon.git
cd Dreambook-Salon

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Build Tailwind CSS
npm run build:css

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Visit **http://localhost:8000** to access the application.

For detailed setup instructions, see **[SETUP.md](SETUP.md)**.

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Complete installation and configuration guide
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details
- **[UI_UX_IMPROVEMENTS.md](UI_UX_IMPROVEMENTS.md)** - Design system and UI guidelines
- **[CHATBOT_ENHANCEMENTS.md](CHATBOT_ENHANCEMENTS.md)** - AI chatbot features and customization
- **[TODO.md](TODO.md)** - Development roadmap and known issues

## 🎨 Tech Stack

### Backend
- **Django 5.0+** - Web framework
- **PostgreSQL** - Production database
- **SQLite** - Development database
- **Django REST Framework** - API endpoints
- **Python-dateutil** - Date/time utilities

### Frontend
- **Tailwind CSS 3.4** - Utility-first CSS framework
- **Vanilla JavaScript** - Interactive components
- **AJAX/Fetch API** - Asynchronous operations

### Development Tools
- **Black** - Python code formatter
- **isort** - Import sorter
- **Flake8** - Linting
- **djlint** - Template formatter
- **pytest** - Testing framework

## 🏗️ Project Structure

```
Dreambook-Salon/
├── analytics/              # Analytics and forecasting
│   ├── forecasting.py     # Holt-Winters ETS implementation
│   └── views.py           # Analytics views
├── appointments/          # Appointment management
├── chatbot/              # AI chatbot with Filipino support
├── core/                 # Core app (auth, dashboard, home)
├── inventory/            # Inventory and stock management
├── payments/             # Payment processing
├── services/             # Service catalog and CRUD
├── static/               # Static files (CSS, JS, images)
│   ├── css/
│   │   ├── input.css     # Tailwind source
│   │   └── output.css    # Compiled CSS
│   └── js/
│       ├── async-utils.js       # AJAX helpers and toasts
│       └── ui-enhancements.js   # UI interactions
├── templates/            # Django templates
│   ├── components/       # Reusable components
│   │   ├── atoms/       # Buttons, inputs
│   │   ├── molecules/   # Cards, forms
│   │   └── organisms/   # Navbar, footer
│   └── pages/           # Page templates
├── salon_system/        # Django project settings
├── manage.py
├── requirements.txt
├── package.json
└── tailwind.config.js
```

## 👥 User Roles

### Customer
- Browse and book services
- Manage their appointments
- View booking history
- Make payments
- Chat with AI assistant

### Staff
- View dashboard with business metrics
- Manage appointments (confirm, complete, cancel)
- Manage services and inventory
- Process payments
- View analytics

### Admin
- All Staff permissions
- User management
- Advanced analytics and forecasting
- Business intelligence insights
- System configuration

## 🔑 Key Features Explained

### Inventory Management
- **Stock Tracking** - Real-time stock levels for all items
- **Restock Operations** - Add inventory with audit trail
- **Stock Adjustments** - Manual adjustments with reasons
- **Low Stock Alerts** - Automatic notifications
- **Service Integration** - Auto-deduct stock when services are completed
- **Async Operations** - AJAX forms with toast notifications

### Business Intelligence
- **Holt-Winters Forecasting** - Triple exponential smoothing (level, trend, seasonality)
- **14-Day Predictions** - Revenue and appointment demand forecasts
- **Seasonality Detection** - Identify weekly patterns
- **Trend Analysis** - Growth rates and trend direction
- **Peak Period Identification** - Busiest hours and days
- **Inventory Recommendations** - Restocking suggestions based on usage

### AI Chatbot
- **Multilingual Support** - English, Filipino, and Taglish
- **Context-Aware** - Understands appointment booking context
- **Service Inquiries** - Answer questions about services
- **Booking Assistance** - Help customers find and book services
- **Business Information** - Provide hours, location, contact details

## 🛠️ Development

### Run Development Server

```bash
# Terminal 1: Watch Tailwind CSS
npm run watch:css

# Terminal 2: Django development server
python manage.py runserver
```

### Make Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Code Formatting

```bash
# Format Python code
black .
isort .

# Lint code
flake8

# Format templates
djlint --reformat templates/
```

### Run Tests

```bash
pytest
```

## 🔒 Security Features

- **CSRF Protection** - All forms protected
- **Password Hashing** - Django's built-in password hashing
- **Role-Based Access Control** - Permission-based views
- **SQL Injection Prevention** - ORM-based queries
- **XSS Prevention** - Template auto-escaping
- **Secure Sessions** - Session-based authentication

## 📱 Responsive Design

The application is fully responsive and works on:
- **Desktop** - Full-featured dashboard and management
- **Tablet** - Optimized layouts
- **Mobile** - Touch-friendly booking and management

## 🌐 Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Opera

## 📊 Analytics Features

### Revenue Analytics
- Today's revenue
- Weekly revenue trends
- Monthly revenue summaries
- Payment method breakdown
- Revenue forecasting

### Service Analytics
- Top performing services
- Booking frequency
- Service revenue contribution
- Completion rates

### Inventory Analytics
- Stock levels
- Low stock alerts
- Usage patterns
- Restocking recommendations

## 🤝 Contributing

This is a private project. If you're part of the development team:

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Format code: `black . && isort .`
4. Test your changes
5. Commit: `git commit -m 'Add your feature'`
6. Push: `git push origin feature/your-feature`
7. Create a Pull Request

## 📝 License

This project is proprietary software. All rights reserved.

## 🐛 Troubleshooting

Common issues and solutions are documented in [SETUP.md](SETUP.md#troubleshooting).

For specific issues:
- Check error messages in terminal
- Review Django debug page (when DEBUG=True)
- Check browser console for JavaScript errors
- Verify environment variables in `.env`
- Ensure virtual environment is activated

## 📞 Support

For support and questions:
- Check documentation in the `/documentation` folder
- Review implementation summaries
- Check TODO.md for known issues

## 🎯 Roadmap

See [TODO.md](TODO.md) for planned features and improvements.

Current focus areas:
- Enhanced reporting features
- Email notification system
- SMS integration for appointment reminders
- Advanced analytics dashboards
- Multi-location support
- Integration with popular salon equipment

## ✨ Acknowledgments

Built with:
- Django - The web framework for perfectionists with deadlines
- Tailwind CSS - A utility-first CSS framework
- PostgreSQL - The world's most advanced open source database
- Python - Beautiful is better than ugly

---

**Dreambook Salon** - Streamlining salon management with modern technology. 💇✨
