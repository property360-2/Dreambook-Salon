# Dreambook Salon - Comprehensive Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Key Features](#key-features)
5. [Getting Started](#getting-started)
6. [Documentation Guides](#documentation-guides)
7. [Project Structure](#project-structure)

---

## Project Overview

**Dreambook Salon** is a comprehensive Django-based web application designed for modern salon management. It integrates artificial intelligence, advanced business intelligence, and real-time inventory management to provide a complete solution for salon operations.

### Project Objectives
- Streamline appointment booking and scheduling
- Automate inventory management with alerts
- Implement AI-powered customer service (Claude-based chatbot)
- Provide business intelligence and forecasting for salon management
- Maintain comprehensive audit trails for compliance
- Enable flexible payment processing with multiple methods

### Scope
- **14 Salon Services**: Hair, Beauty, and Wellness treatments
- **Multi-Role System**: Admin, Staff, and Customer roles
- **Real-Time Analytics**: Revenue, appointments, inventory, forecasting
- **AI Integration**: Claude API for natural language understanding
- **Audit System**: Complete action tracking and compliance logging

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                          │
│  (HTML5, CSS3/Tailwind, Vanilla JavaScript, Chart.js)      │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                   Django Web Application                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Views & URL Routing (URL Dispatcher)                │   │
│  │ ├─ Core (Auth, Users)                               │   │
│  │ ├─ Appointments                                      │   │
│  │ ├─ Services                                          │   │
│  │ ├─ Payments                                          │   │
│  │ ├─ Inventory                                         │   │
│  │ ├─ Chatbot & AI                                      │   │
│  │ ├─ Analytics                                         │   │
│  │ └─ Audit Logging                                     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Models & Business Logic (ORM)                        │   │
│  │ ├─ User (Custom Auth Model)                          │   │
│  │ ├─ Service & ServiceItem                             │   │
│  │ ├─ Appointment & SlotLimit                           │   │
│  │ ├─ Payment & GCashQRCode                             │   │
│  │ ├─ Inventory (Item)                                  │   │
│  │ ├─ ConversationHistory & ChatbotConfig               │   │
│  │ └─ AuditLog                                          │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ External Services & Integrations                     │   │
│  │ ├─ Anthropic Claude API (AI/NLU)                    │   │
│  │ └─ Payment Processors (Demo Mode)                   │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                  Data Layer                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ SQLite3 (Development) / PostgreSQL (Production)      │   │
│  │ ├─ Users & Authentication                            │   │
│  │ ├─ Appointments & Scheduling                         │   │
│  │ ├─ Services & Requirements                           │   │
│  │ ├─ Payments & Transactions                           │   │
│  │ ├─ Inventory & Stock Levels                          │   │
│  │ ├─ Chat Conversations & History                      │   │
│  │ └─ Audit Logs & Compliance Data                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Request** → Frontend (HTML/JS)
2. **HTTP Request** → Django URL Dispatcher
3. **View Processing** → Business Logic + Permission Checks
4. **ORM Query** → Database Operations
5. **Response** → JSON/HTML Response
6. **Frontend Update** → JavaScript DOM Manipulation

---

## Technology Stack

### Backend
```
Django 5.2.8              - Web framework
Python 3.10+              - Programming language
SQLite3 / PostgreSQL      - Database
Django ORM                - Object-relational mapping
Anthropic SDK             - Claude API integration
```

### Frontend
```
HTML5 & CSS3              - Markup & Styling
Tailwind CSS 3.4.18       - Utility-first CSS framework
Vanilla JavaScript        - DOM manipulation
Chart.js 4.0+             - Data visualization
Responsive Design         - Mobile-first approach
```

### AI/ML
```
Claude 3.5 Sonnet         - Large language model
Exponential Smoothing     - Time series forecasting
Holt-Winters Method       - Seasonal forecasting
Moving Averages           - Trend analysis
```

### Development & Deployment
```
pip                       - Python package manager
npm                       - Node.js package manager
Git                       - Version control
Docker (optional)         - Containerization
pytest                    - Testing framework
Black                     - Code formatter
Flake8                    - Linting
```

---

## Key Features

### 1. Intelligent Appointment Management
- Real-time slot availability checking
- Concurrent appointment limits per time slot
- Advance booking (configurable, default 30 days)
- Status tracking: Pending → Confirmed → In Progress → Completed
- Custom slot limits for staff absences
- Blocked time ranges for holidays/maintenance

### 2. AI-Powered Chatbot
- **Natural Language Understanding** using Claude API
- **107+ Intent Rules** for fallback responses
- **Service Information**: Prices, durations, availability
- **Booking Assistance**: Real-time appointment checking
- **Staff Analytics**: Revenue, trends, inventory insights
- **Multilingual Support**: English and Taglish
- **Conversation Memory**: Context-aware responses
- **Graceful Fallback**: Works without API key via regex-based bot

### 3. Flexible Payment Processing
- Multiple payment methods: GCash, PayMaya, Cash
- Admin-managed GCash QR codes
- Payment receipts with verification workflow
- Downpayment support for services
- Transaction tracking and status management
- Demo mode for testing

### 4. Smart Inventory Management
- Real-time stock tracking
- Service-based consumption rates
- Automatic stock deduction on completion
- Low-stock alerts (configurable threshold)
- Prevents booking if insufficient inventory
- Manual stock adjustments and restocking

### 5. Business Intelligence & Forecasting
- **Revenue Analytics**: Daily, weekly, monthly breakdown
- **Appointment Trends**: Status distribution, growth rates
- **Service Analytics**: Most booked, revenue per service
- **Inventory Forecasting**: Stock level predictions
- **Peak Hours Analysis**: Busiest time identification
- **Customer Insights**: Retention, loyalty, spending patterns
- **Staff Performance**: Productivity metrics
- **Trend Detection**: Exponential smoothing with seasonal adjustment

### 6. Comprehensive Audit Logging
- **15+ Action Types**: Create, update, delete, status changes
- **Complete Tracking**: Before/after JSON diffs
- **IP & Browser Logging**: Device and client tracking
- **Saved Filters**: Custom audit queries
- **CSV Export**: Download for external analysis
- **Role-Based Access**: Admin-only audit dashboard

### 7. User Management System
- **Three User Roles**: Admin, Staff, Customer
- **Email-Based Authentication**: No username required
- **Password Management**: Reset and change capabilities
- **User Status**: Active/Deactivated accounts
- **Bulk Operations**: Activate, deactivate, delete users

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Node.js 14 or higher
- Git
- pip and npm

### Installation Steps

1. **Clone the Repository**
```bash
git clone <repository-url>
cd Dreambook-Salon
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Frontend Dependencies**
```bash
npm install
```

5. **Build CSS**
```bash
npm run build:css
```

6. **Configure Environment**
Create `.env` file:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
ANTHROPIC_API_KEY=sk-ant-your-api-key

# Optional
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

7. **Database Setup**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo  # Optional: Load demo data
```

8. **Run Development Server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

### Demo Credentials
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@dreambook.com | admin123 |
| Staff | staff@dreambook.com | staff123 |
| Customer | customer1@example.com | customer123 |

---

## Documentation Guides

This documentation includes the following detailed guides:

### 1. **[LLM_INTEGRATION.md](./LLM_INTEGRATION.md)**
Complete documentation of the Claude AI integration:
- Claude API setup and configuration
- Intent detection and entity extraction
- Response generation and context management
- Error handling and graceful degradation
- Code examples and API structure

### 2. **[FORECASTING.md](./FORECASTING.md)**
Business intelligence and forecasting system:
- Exponential smoothing methods explained
- Holt-Winters seasonal forecasting
- Moving averages and trend detection
- Confidence metrics (MAE, MAPE)
- Usage examples and mathematical foundations

### 3. **[ARCHITECTURE.md](./ARCHITECTURE.md)**
System design and architecture:
- Component breakdown
- Data flow diagrams
- Model relationships (ERD)
- Design patterns used
- Scalability considerations

### 4. **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)**
Complete API reference:
- Chatbot API endpoints
- Authentication and permissions
- Request/response formats
- Error handling
- Code examples

### 5. **[FEATURES.md](./FEATURES.md)**
Detailed feature documentation:
- Appointment management
- Payment processing
- Inventory system
- Chatbot capabilities
- Analytics dashboard

### 6. **[INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md)**
Step-by-step setup guide:
- Environment setup
- Database configuration
- Running tests
- Deployment guides
- Troubleshooting

---

## Project Structure

```
Dreambook-Salon/
├── DOCUMENTATION/              # Documentation files (this folder)
│   ├── README.md              # Main overview (you are here)
│   ├── LLM_INTEGRATION.md     # Claude AI documentation
│   ├── FORECASTING.md         # Forecasting & BI docs
│   ├── ARCHITECTURE.md        # System architecture
│   ├── API_DOCUMENTATION.md   # API reference
│   ├── FEATURES.md            # Feature documentation
│   └── INSTALLATION_GUIDE.md  # Setup guide
│
├── core/                       # User authentication & management
│   ├── models.py              # User model (custom auth)
│   ├── views.py               # Auth views
│   ├── forms.py               # Auth forms
│   ├── mixins.py              # Permission mixins
│   └── decorators.py          # Custom decorators
│
├── services/                   # Service management
│   ├── models.py              # Service, ServiceItem models
│   ├── views.py               # Service CRUD views
│   └── forms.py               # Service forms
│
├── appointments/              # Appointment booking
│   ├── models.py              # Appointment, SlotLimit models
│   ├── views.py               # Booking & management views
│   ├── forms.py               # Booking forms
│   └── utils.py               # Availability checking
│
├── payments/                  # Payment processing
│   ├── models.py              # Payment, GCashQRCode models
│   ├── views.py               # Payment views
│   └── forms.py               # Payment forms
│
├── inventory/                 # Inventory management
│   ├── models.py              # Item model
│   ├── views.py               # Inventory views
│   └── forms.py               # Stock forms
│
├── chatbot/                   # AI Chatbot system
│   ├── llm_integration.py     # Claude API integration
│   ├── enhanced_bot.py        # Bot orchestrator
│   ├── intelligent_bot.py     # Regex-based fallback
│   ├── fuzzy_matcher.py       # Typo tolerance
│   ├── analytics.py           # Conversation analytics
│   ├── models.py              # ChatbotConfig, ConversationHistory
│   ├── views.py               # Chatbot API endpoints
│   └── urls.py                # Chatbot routes
│
├── analytics/                 # Business intelligence
│   ├── forecasting.py         # Exponential smoothing, forecasting
│   ├── models.py              # Analytics models
│   ├── views.py               # Analytics views & charts
│   └── utils.py               # BI calculations
│
├── audit_log/                 # Audit trail system
│   ├── models.py              # AuditLog model
│   ├── views.py               # Audit dashboard
│   └── signals.py             # Auto-logging signals
│
├── salon_system/              # Django configuration
│   ├── settings.py            # Settings & configuration
│   ├── urls.py                # URL routing
│   ├── wsgi.py                # WSGI application
│   └── asgi.py                # ASGI application
│
├── templates/                 # HTML templates
│   ├── base.html              # Main layout
│   ├── pages/                 # Page templates
│   └── components/            # Reusable components
│
├── static/                    # Static files
│   ├── css/                   # Stylesheets
│   ├── js/                    # JavaScript files
│   └── images/                # Images & assets
│
├── manage.py                  # Django CLI
├── requirements.txt           # Python dependencies
├── package.json               # Node.js dependencies
├── .env                       # Environment variables (gitignored)
├── db.sqlite3                 # SQLite database
└── README.md                  # Project README
```

---

## Key Concepts for Capstone

### 1. AI Integration (LLM)
- **Claude 3.5 Sonnet**: State-of-the-art language model by Anthropic
- **Intent Classification**: Understands user intent with confidence scores
- **Entity Extraction**: Identifies service names, dates, times in user input
- **Graceful Degradation**: Falls back to regex-based bot when API unavailable
- **Context Management**: Maintains conversation history for multi-turn interactions

### 2. Business Intelligence
- **Exponential Smoothing**: Mathematical method for forecasting time series data
- **Seasonal Adjustment**: Detects and accounts for periodic patterns
- **Trend Detection**: Identifies increasing/decreasing patterns
- **Confidence Metrics**: Measures forecast accuracy (MAE, MAPE)
- **Real-Time Analytics**: Dashboard with key performance indicators

### 3. System Design
- **MVC Pattern**: Clean separation of models, views, and logic
- **Mixins**: Reusable permission and functionality components
- **Generic Relations**: Flexible audit logging for any model
- **Signals**: Automatic event handling and logging
- **API-First**: JSON endpoints for frontend interaction

---

## Next Steps

1. **Review Documentation**: Read the specific guides for your areas of interest
2. **Explore Codebase**: Navigate the project structure
3. **Set Up Development**: Follow installation guide
4. **Run Tests**: Execute test suite
5. **Modify & Extend**: Customize for your needs

---

## Support & Contact

For questions or issues:
- Check the relevant documentation file
- Review code comments
- Examine test cases for usage examples
- Check Django and Anthropic official documentation

---

## License

This project is created for educational purposes (Capstone Project).

---

**Last Updated**: November 2025
**Version**: 1.0.0
**Status**: 70% Complete - Core Features Implemented
