# 🌸 Dreambook Salon - Modern Appointment Booking System

A full-featured salon management and appointment booking platform built with Django. Streamline your salon operations with real-time availability checking, inventory management, payment processing, and an intelligent chatbot.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Django](https://img.shields.io/badge/django-5.0+-darkgreen)
![Status](https://img.shields.io/badge/status-active-success)

## ✨ Key Features

### 📅 Appointment Management
- **Real-time Availability Checking** - Customers see slot availability instantly while booking
- **Calendar View** - Interactive calendar showing all appointments with color-coding
- **Available Slots Display** - See all available time slots for chosen date/service
- **Booking Confirmation** - Review details with available alternative time slots
- **Appointment Status Tracking** - Pending → Confirmed → In Progress → Completed
- **Advanced Booking** - Book up to 30 days in advance
- **Concurrent Appointment Limits** - Manage maximum concurrent bookings per slot

### 💇 Service Management
- **14 Comprehensive Services**:
  - Hair Services (Haircut, Hair Spa, Color, Hair & Make-Up, Keratin, Botox, Brazilian, Rebond, Collagen)
  - Nail Services (Manicure, Pedicure)
  - Beauty & Wellness (Facial, Massage, Waxing)
- **Flexible Pricing** - Starting prices from ₱100 to ₱2,000
- **Service Duration** - 30 minutes to 3 hours
- **Service Descriptions** - Detailed service information

### 💰 Payment System
- **Multiple Payment Methods**:
  - GCash (Online)
  - PayMaya (Online)
  - Cash at Salon
- **Payment Tracking** - Monitor payment status (Unpaid, Pending, Paid, Failed)
- **Transaction Management** - Complete payment history with transaction IDs

### 📦 Inventory Management
- **Real-time Stock Tracking** - Monitor inventory in real-time
- **Service Item Requirements** - Define items needed per service
- **Stock Threshold Alerts** - Get notified when stock is low
- **Inventory Deduction** - Automatic deduction when appointments are completed
- **Inventory Validation** - Prevent booking if insufficient stock

### 🤖 Intelligent Chatbot
- **107 Comprehensive Rules** - Covers all customer inquiries
- **Service Information** - Details about all 14 services
- **Pricing Information** - Clear pricing for each service
- **Booking Instructions** - How to book appointments
- **Payment Methods** - Accepted payment options
- **Business Hours** - Operating hours and location
- **Customer Support** - Quick access to support channels
- **Natural Language Processing** - Understands various keywords and phrases

### 👥 User Roles
- **Admin** - Full system access, user management, analytics
- **Staff** - Appointment management, inventory updates, customer support
- **Customer** - Browse services, book appointments, manage bookings, make payments

### 📊 Admin Dashboard
- **Appointment Analytics** - View appointment statistics
- **Calendar Overview** - See all appointments at a glance
- **Inventory Dashboard** - Monitor stock levels
- **User Management** - Manage staff and customer accounts
- **Settings Management** - Configure system-wide settings

### 🎨 User Interface
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Modern UI/UX** - Clean, intuitive interface
- **Real-time Feedback** - Instant validation and feedback
- **Accessibility** - WCAG compliant design
- **Dark-friendly** - Optimized for readability

## 🏗️ System Architecture

```
Dreambook Salon
├── Core (User Management & Authentication)
├── Services (Service Catalog & Details)
├── Appointments (Booking & Management)
├── Payments (Payment Processing)
├── Inventory (Stock Management)
├── Chatbot (AI Assistant)
├── Analytics (Statistics & Reports)
└── Static Files (Frontend Assets)
```

## 🛠️ Tech Stack

**Backend:**
- Django 5.0+ - Web framework
- PostgreSQL - Database (production)
- Django REST Framework - API endpoints
- Python 3.10+ - Programming language

**Frontend:**
- HTML5 & CSS3 - Markup & styling
- Tailwind CSS - Utility-first CSS framework
- JavaScript (Vanilla) - Frontend interactivity
- Responsive Design - Mobile-first approach

**Development Tools:**
- Git - Version control
- Docker - Containerization (optional)
- pytest - Testing framework
- Black - Code formatting
- flake8 - Linting

## 📋 System Requirements

- **Python**: 3.10 or higher
- **Node.js**: 14+ (for frontend assets)
- **Database**: PostgreSQL (recommended) or SQLite (development)
- **RAM**: 2GB minimum
- **Storage**: 1GB minimum

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- Virtual environment (recommended)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/dreambook-salon.git
   cd dreambook-salon
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   npm install  # For frontend dependencies
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Seed Demo Data (Optional)**
   ```bash
   python manage.py seed_demo
   python manage.py seed_demo --clear  # Clear and reseed
   ```

8. **Build Frontend Assets**
   ```bash
   npm run build:css
   ```

9. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` in your browser.

## 👤 Demo Credentials

After running `seed_demo`, use these credentials:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@dreambook.com | admin123 |
| Staff | staff@dreambook.com | staff123 |
| Customer 1 | customer1@example.com | customer123 |
| Customer 2 | customer2@example.com | customer123 |
| Customer 3 | customer3@example.com | customer123 |

## 📖 Documentation

For detailed setup instructions, see [SETUP.md](./SETUP.md)

## 🎯 Core Functionality

### For Customers
- Browse available services
- Check real-time slot availability
- Book appointments with instant confirmation
- View available time slots before and after booking
- Manage appointments (view, cancel, reschedule)
- Make online or cash payments
- Chat with AI assistant for information

### For Staff/Admin
- View all appointments
- Manage appointment status
- Mark appointments as completed
- Deduct inventory when completing services
- Update service information
- Manage customer accounts
- Access business analytics
- Configure system settings

## 📞 Contact & Support

- Email: contact@dreambook.com
- Phone: (02) 1234-5678
- Hours: Monday - Saturday, 9 AM - 6 PM
- Address: 123 Main Street, Metro Manila

## 🔐 Security Features

- User authentication & authorization
- CSRF protection on all forms
- Secure password hashing
- Role-based access control (RBAC)
- Input validation & sanitization
- SQL injection prevention

## 📝 Services & Pricing

| Service | Price | Duration |
|---------|-------|----------|
| Haircut | ₱100 | 45 min |
| Hair Spa | ₱500 | 75 min |
| Hair Color | ₱700+ | 120 min |
| Hair & Make-Up | ₱1,000 | 150 min |
| Keratin Treatment | ₱1,000 | 180 min |
| Botox Hair Treatment | ₱1,200 | 120 min |
| Brazilian Hair Treatment | ₱1,500 | 150 min |
| Hair Rebond | ₱1,500 | 180 min |
| Collagen Treatment | ₱2,000 | 120 min |
| Manicure | ₱250 | 45 min |
| Pedicure | ₱350 | 60 min |
| Facial Treatment | ₱600 | 75 min |
| Body Massage | ₱800 | 90 min |
| Waxing Service | ₱400 | 30 min |

## 🤝 Contributing

We welcome contributions! Please follow our coding standards and submit pull requests to improve the system.

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Django community for the excellent framework
- Tailwind CSS for beautiful styling
- All contributors and users

---

**Made with ❤️ for Dreambook Salon**

Last Updated: November 2024
