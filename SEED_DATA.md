# 🌱 Seed Data Documentation

This document describes all the demo data created by the `seed_demo` management command.

## 📌 Command Usage

```bash
# Seed database with demo data
python manage.py seed_demo

# Clear existing data and reseed
python manage.py seed_demo --clear
```

---

## 👥 **Users** (5 users)

### Admin User
- **Email:** admin@dreambook.com
- **Password:** admin123
- **Name:** Admin User
- **Role:** ADMIN
- **Permissions:** Full system access, superuser

### Staff User
- **Email:** staff@dreambook.com
- **Password:** staff123
- **Name:** Staff Member
- **Role:** STAFF
- **Permissions:** Inventory, appointments, analytics access

### Customer Users (3)

1. **Maria Santos**
   - Email: customer1@example.com
   - Password: customer123

2. **Juan Dela Cruz**
   - Email: customer2@example.com
   - Password: customer123

3. **Ana Reyes**
   - Email: customer3@example.com
   - Password: customer123

---

## 📦 **Inventory Items** (15 items)

| Item | Unit | Stock | Threshold | Status |
|------|------|-------|-----------|--------|
| Hair Rebonding Solution | ml | 5000 | 1000 | ✅ In Stock |
| Hair Coloring Cream | ml | 3000 | 500 | ✅ In Stock |
| Shampoo | ml | 2000 | 500 | ✅ In Stock |
| Conditioner | ml | 1800 | 500 | ✅ In Stock |
| Hair Treatment Mask | ml | 1200 | 300 | ✅ In Stock |
| Nail Polish | pcs | 150 | 30 | ✅ In Stock |
| Nail Remover | ml | 500 | 100 | ✅ In Stock |
| Cotton Balls | pcs | 500 | 100 | ✅ In Stock |
| Facial Cleanser | ml | 800 | 200 | ✅ In Stock |
| Face Mask | pcs | 80 | 20 | ✅ In Stock |
| Massage Oil | ml | 600 | 150 | ✅ In Stock |
| Wax Strips | pcs | 200 | 50 | ✅ In Stock |
| Towels | pcs | 50 | 10 | ✅ In Stock |
| Hair Clips | pcs | 100 | 20 | ✅ In Stock |
| Gloves (pairs) | pcs | 200 | 50 | ✅ In Stock |

---

## 💇 **Services** (9 services)

### 1. Hair Rebond
- **Price:** ₱2,500.00
- **Duration:** 180 minutes (3 hours)
- **Inventory Required:**
  - Hair Rebonding Solution: 200ml
  - Shampoo: 50ml
  - Conditioner: 50ml
  - Towels: 2 pcs
  - Hair Clips: 4 pcs

### 2. Hair Color
- **Price:** ₱2,000.00
- **Duration:** 120 minutes (2 hours)
- **Inventory Required:**
  - Hair Coloring Cream: 150ml
  - Shampoo: 40ml
  - Conditioner: 40ml
  - Gloves: 2 pairs
  - Towels: 2 pcs

### 3. Hair Treatment
- **Price:** ₱800.00
- **Duration:** 60 minutes
- **Inventory Required:**
  - Hair Treatment Mask: 100ml
  - Shampoo: 30ml
  - Towels: 1 pc

### 4. Haircut
- **Price:** ₱300.00
- **Duration:** 45 minutes
- **Inventory Required:**
  - Shampoo: 20ml
  - Towels: 1 pc

### 5. Manicure
- **Price:** ₱250.00
- **Duration:** 45 minutes
- **Inventory Required:**
  - Nail Polish: 1 pc
  - Nail Remover: 10ml
  - Cotton Balls: 10 pcs
  - Towels: 1 pc

### 6. Pedicure
- **Price:** ₱350.00
- **Duration:** 60 minutes
- **Inventory Required:**
  - Nail Polish: 1 pc
  - Nail Remover: 15ml
  - Cotton Balls: 15 pcs
  - Towels: 2 pcs

### 7. Facial Treatment
- **Price:** ₱600.00
- **Duration:** 75 minutes
- **Inventory Required:**
  - Facial Cleanser: 30ml
  - Face Mask: 1 pc
  - Cotton Balls: 20 pcs
  - Towels: 2 pcs

### 8. Body Massage
- **Price:** ₱800.00
- **Duration:** 90 minutes
- **Inventory Required:**
  - Massage Oil: 50ml
  - Towels: 3 pcs

### 9. Waxing Service
- **Price:** ₱400.00
- **Duration:** 30 minutes
- **Inventory Required:**
  - Wax Strips: 20 pcs
  - Cotton Balls: 10 pcs
  - Towels: 1 pc

---

## ⚙️ **Appointment Settings** (1 singleton)

- **Max Concurrent Appointments:** 3
- **Booking Window:** 30 days in advance
- **Prevent Completion on Insufficient Stock:** Enabled

---

## 🚫 **Blocked Ranges** (1 range)

- **Next Sunday:** Entire day blocked
- **Reason:** Weekly day off

---

## 📅 **Appointments** (40 appointments)

### Past Completed Appointments (20)
- Created randomly over the last 30 days
- Status: COMPLETED
- Payment State: PAID
- Randomly assigned to customers
- Randomly assigned services

### Upcoming Appointments (15)
- Created for the next 14 days
- Status: PENDING or CONFIRMED (random)
- Payment State: PAID or UNPAID (random)
- Randomly assigned to customers
- Randomly assigned services

### Cancelled Appointments (5)
- Created randomly over the last 15 days
- Status: CANCELLED
- Payment State: UNPAID
- Randomly assigned to customers
- Randomly assigned services

---

## 💳 **Payments** (~20 payments)

Payments are created for all appointments with `payment_state='paid'`:

- **Transaction ID Format:** TXN-XXXXXXXXXXXX (12-character hex)
- **Methods:** GCash, PayMaya, or Onsite (random)
- **Amount:** Matches service price
- **Status:** PAID
- **Notes:** "{METHOD} payment successful"

---

## 🤖 **Chatbot Rules** (23 rules)

### Greetings (Priority: 5)
- **hello** → Welcome message
- **hi** → Welcome message
- **thank** / **thanks** → You're welcome

### General Info (Priority: 10)
- **hours** → Business hours (Mon-Sat, 9AM-6PM)
- **location** → Address information
- **contact** → Contact details
- **email** → Email address
- **phone** → Phone number

### Services (Priority: 10)
- **services** → Service overview
- **booking** / **book** → How to book

### Pricing (Priority: 8-10)
- **price** → General pricing info
- **payment** → Payment methods

### Specific Services (Priority: 9)
- **rebond** → Hair rebond details
- **color** → Hair color details
- **haircut** → Haircut details
- **manicure** → Manicure details
- **pedicure** → Pedicure details
- **facial** → Facial treatment details
- **massage** → Body massage details

### Actions (Priority: 8-10)
- **appointment** → Appointment info
- **cancel** → Cancellation policy

---

## 📊 **Data Statistics**

| Category | Count |
|----------|-------|
| Users | 5 (1 admin, 1 staff, 3 customers) |
| Inventory Items | 15 |
| Services | 9 |
| Service-Item Links | 41 |
| Appointments | 40 |
| Payments | ~20 (for paid appointments) |
| Chatbot Rules | 23 |
| Blocked Ranges | 1 |
| Settings | 1 |

---

## 🧪 **Testing Scenarios**

### Customer Workflow
1. Login as customer1@example.com / customer123
2. Browse services
3. View "My Appointments"
4. Book new appointment
5. Make payment
6. Chat with AI assistant about services

### Staff Workflow
1. Login as staff@dreambook.com / staff123
2. View all appointments
3. Manage inventory
4. Check analytics dashboard
5. Use AI assistant for stats queries
6. Mark appointments as completed

### Admin Workflow
1. Login as admin@dreambook.com / admin123
2. Access Django admin panel
3. Manage all resources
4. Configure settings
5. Create blocked ranges
6. View comprehensive analytics

---

## 🔄 **Reseeding**

To clear all demo data and reseed:

```bash
python manage.py seed_demo --clear
```

**Warning:** This will delete:
- All demo users
- All appointments
- All payments
- All services and inventory
- All chatbot rules
- All blocked ranges

**Note:** This will NOT delete:
- Users created manually
- Production data with different emails

---

## 💡 **Tips**

1. **Use the chatbot** to test both customer and staff experiences
2. **Test inventory deduction** by completing appointments as staff
3. **Check analytics** to see revenue charts with real data
4. **Try booking** appointments as different customers
5. **Test payment flow** with different payment methods

---

## 🎯 **Expected Results**

After seeding, the intelligent chatbot will have real data to query:

### Customer Queries:
- "What services do you have?" → Lists 9 services
- "What's the most popular?" → Shows services with most bookings
- "How much is a haircut?" → ₱300

### Staff/Admin Queries:
- "What's the revenue?" → Shows actual payment totals
- "Inventory status?" → Shows 15 items in stock
- "Top services?" → Ranks services by bookings
- "Today's summary?" → Real appointment and revenue data

---

**Last Updated:** November 9, 2025
**Version:** 2.0 - Intelligent Chatbot Ready
